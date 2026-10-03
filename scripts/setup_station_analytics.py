import psycopg2
import time

conn_str = "dbname='groundwater_quality' user='postgres' host='localhost' password='Nishant@2003' port='5432'"

statements = [
    ("1. Extension pg_trgm", "CREATE EXTENSION IF NOT EXISTS pg_trgm;"),
    
    ("2. Drop mv_station_identity", "DROP MATERIALIZED VIEW IF EXISTS mv_station_identity CASCADE;"),
    
    ("3. Create mv_station_identity", """
CREATE MATERIALIZED VIEW mv_station_identity AS
WITH base_stations AS (
    SELECT 
        s.sample_id,
        l.station_name,
        l.state,
        l.district,
        s.sample_date,
        l.latitude,
        l.longitude,
        w.wqi,
        w.calculation_status,
        w.data_quality_flags,
        w.parameter_sub_indices,
        TRIM(LOWER(l.station_name)) AS norm_station,
        TRIM(LOWER(l.state)) AS norm_state,
        TRIM(LOWER(l.district)) AS norm_district
    FROM water_samples s
    JOIN locations l ON s.location_id = l.location_id
    LEFT JOIN wawqi_results w ON s.sample_id = w.sample_id
),
station_canonical AS (
    SELECT 
        *,
        md5(concat_ws('||', norm_station, norm_state, norm_district)) AS station_hash,
        ROW_NUMBER() OVER (
            PARTITION BY md5(concat_ws('||', norm_station, norm_state, norm_district)) 
            ORDER BY sample_date DESC NULLS LAST, sample_id DESC
        ) as sample_recency_rank
    FROM base_stations
),
sample_dominant AS (
    SELECT 
        w.sample_id,
        kv.key AS dom_param,
        RANK() OVER (PARTITION BY w.sample_id ORDER BY kv.value::numeric DESC, kv.key ASC) as param_rank
    FROM wawqi_results w,
    LATERAL jsonb_each_text(w.parameter_sub_indices) kv
    WHERE w.parameter_sub_indices IS NOT NULL
),
flat_dominant AS (
    SELECT 
        c.station_hash,
        c.sample_id,
        sd.dom_param
    FROM station_canonical c
    JOIN sample_dominant sd ON c.sample_id = sd.sample_id AND sd.param_rank = 1
),
station_dominant_agg AS (
    SELECT 
        station_hash,
        dom_param AS dominant_parameter,
        COUNT(*) AS dominant_parameter_sample_count,
        RANK() OVER(PARTITION BY station_hash ORDER BY COUNT(*) DESC, dom_param ASC) as rnk
    FROM flat_dominant
    GROUP BY station_hash, dom_param
),
station_best_dominant AS (
    SELECT * FROM station_dominant_agg WHERE rnk = 1
),
station_dominant_tied AS (
    SELECT 
        station_hash,
        array_agg(dominant_parameter ORDER BY dominant_parameter) as historically_dominant_parameters,
        MAX(dominant_parameter_sample_count) as dominant_parameter_sample_count
    FROM station_best_dominant
    GROUP BY station_hash
),
latest_warnings AS (
    SELECT 
        station_hash,
        data_quality_flags AS latest_source_warning
    FROM station_canonical
    WHERE sample_recency_rank = 1
),
station_metrics AS (
    SELECT 
        station_hash,
        MAX(station_name) AS station_name,
        MAX(state) AS state,
        MAX(district) AS district,
        AVG(latitude) AS latitude,
        AVG(longitude) AS longitude,
        COUNT(sample_id) AS sample_count,
        MIN(sample_date) AS first_sample_date,
        MAX(sample_date) AS last_sample_date,
        COUNT(wqi) AS wawqi_available_count,
        COUNT(sample_id) - COUNT(wqi) AS wawqi_unavailable_count,
        CASE WHEN COUNT(sample_id) > 0 THEN 
            ROUND((COUNT(wqi)::numeric / COUNT(sample_id)::numeric) * 100, 2)
        ELSE 0 END AS wawqi_eligibility_percentage,
        COUNT(CASE WHEN wqi <= 25 THEN 1 END) AS excellent_count,
        COUNT(CASE WHEN wqi > 25 AND wqi <= 50 THEN 1 END) AS good_count,
        COUNT(CASE WHEN wqi > 50 AND wqi <= 75 THEN 1 END) AS poor_count,
        COUNT(CASE WHEN wqi > 75 AND wqi <= 100 THEN 1 END) AS very_poor_count,
        COUNT(CASE WHEN wqi > 100 THEN 1 END) AS unsuitable_count,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY wqi) AS median_wqi,
        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY wqi) AS p90_wqi,
        MAX(wqi) AS max_wqi
    FROM station_canonical
    GROUP BY station_hash
)
SELECT 
    sm.*,
    lw.latest_source_warning,
    sdt.historically_dominant_parameters,
    sdt.dominant_parameter_sample_count,
    CASE WHEN sm.wawqi_available_count > 0 THEN
        ROUND((sdt.dominant_parameter_sample_count::numeric / sm.wawqi_available_count::numeric) * 100, 2)
    ELSE 0 END AS dominant_parameter_percentage,
    CASE 
        WHEN sm.sample_count < 3 OR sm.wawqi_eligibility_percentage < 50 THEN 'DATA LIMITED'
        ELSE 'DATA RICH'
    END AS data_quality_class,
    CASE 
        WHEN sm.sample_count < 3 THEN 'Fewer than 3 historical samples.'
        WHEN sm.wawqi_eligibility_percentage < 50 THEN 'WAWQI available for less than 50% of historical samples.'
        ELSE 'Sufficient historical coverage.'
    END AS data_quality_reason
FROM station_metrics sm
LEFT JOIN latest_warnings lw ON sm.station_hash = lw.station_hash
LEFT JOIN station_dominant_tied sdt ON sm.station_hash = sdt.station_hash;
"""),
    
    ("4. Indexes on mv_station_identity", """
CREATE UNIQUE INDEX idx_mv_station_identity_hash ON mv_station_identity (station_hash);
CREATE INDEX idx_mv_station_identity_state ON mv_station_identity (state);
CREATE INDEX idx_mv_station_identity_district ON mv_station_identity (district);
CREATE INDEX idx_mv_station_identity_data_quality ON mv_station_identity (data_quality_class);
CREATE INDEX idx_mv_station_identity_name ON mv_station_identity USING gin (station_name gin_trgm_ops);
"""),

    ("5. View vw_station_wawqi_history", """
CREATE OR REPLACE VIEW vw_station_wawqi_history AS
SELECT
    md5(concat_ws('||', TRIM(LOWER(l.station_name)), TRIM(LOWER(l.state)), TRIM(LOWER(l.district)))) AS station_hash,
    s.sample_id,
    s.sample_date,
    w.wqi,
    CASE 
        WHEN w.wqi <= 25 THEN 'Excellent'
        WHEN w.wqi > 25 AND w.wqi <= 50 THEN 'Good'
        WHEN w.wqi > 50 AND w.wqi <= 75 THEN 'Poor'
        WHEN w.wqi > 75 AND w.wqi <= 100 THEN 'Very Poor'
        WHEN w.wqi > 100 THEN 'Unsuitable'
        ELSE 'UNAVAILABLE'
    END AS category
FROM water_samples s
JOIN locations l ON s.location_id = l.location_id
JOIN wawqi_results w ON s.sample_id = w.sample_id
WHERE w.wqi IS NOT NULL;
"""),

    ("6. Drop mv_station_parameter_analytics", "DROP MATERIALIZED VIEW IF EXISTS mv_station_parameter_analytics CASCADE;"),

    ("7. Create mv_station_parameter_analytics", """
CREATE MATERIALIZED VIEW mv_station_parameter_analytics AS
WITH limits AS (
    SELECT 'ph' AS p_name, 6.5 AS limit_low, 8.5 AS limit_high
    UNION ALL SELECT 'chloride', 0, 250
    UNION ALL SELECT 'sulphate', 0, 200
    UNION ALL SELECT 'hardness', 0, 200
    UNION ALL SELECT 'calcium', 0, 75
    UNION ALL SELECT 'magnesium', 0, 30
    UNION ALL SELECT 'iron', 0, 0.3
    UNION ALL SELECT 'arsenic', 0, 0.01
    UNION ALL SELECT 'uranium', 0, 0.03
)
SELECT 
    md5(concat_ws('||', TRIM(LOWER(l.station_name)), TRIM(LOWER(l.state)), TRIM(LOWER(l.district)))) AS station_hash,
    p.canonical_name AS parameter,
    COUNT(spv.numeric_value) AS observation_count,
    COUNT(*) FILTER (WHERE spv.is_missing) AS missing_count,
    MIN(spv.numeric_value) AS minimum,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY spv.numeric_value) AS median,
    MAX(spv.numeric_value) AS maximum,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY spv.numeric_value) AS p75,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY spv.numeric_value) AS p90,
    COUNT(*) FILTER (
        WHERE (p.canonical_name = 'ph' AND (spv.numeric_value < lm.limit_low OR spv.numeric_value > lm.limit_high))
           OR (p.canonical_name != 'ph' AND spv.numeric_value > lm.limit_high)
    ) AS exceedance_count,
    ROUND(COUNT(*) FILTER (
        WHERE (p.canonical_name = 'ph' AND (spv.numeric_value < lm.limit_low OR spv.numeric_value > lm.limit_high))
           OR (p.canonical_name != 'ph' AND spv.numeric_value > lm.limit_high)
    ) * 100.0 / NULLIF(COUNT(spv.numeric_value), 0), 2) AS exceedance_percentage
FROM sample_parameter_values spv
JOIN parameters p ON spv.parameter_id = p.parameter_id
JOIN water_samples s ON spv.sample_id = s.sample_id
JOIN locations l ON s.location_id = l.location_id
JOIN limits lm ON p.canonical_name = lm.p_name
GROUP BY 
    md5(concat_ws('||', TRIM(LOWER(l.station_name)), TRIM(LOWER(l.state)), TRIM(LOWER(l.district)))),
    p.canonical_name;
"""),

    ("8. Indexes on mv_station_parameter_analytics", """
CREATE UNIQUE INDEX idx_mv_station_param_hash_param ON mv_station_parameter_analytics (station_hash, parameter);
CREATE INDEX idx_mv_station_param_hash ON mv_station_parameter_analytics (station_hash);
""")
]

try:
    conn = psycopg2.connect(conn_str)
    conn.autocommit = True
    print("Starting step-by-step setup...")
    for label, stmt in statements:
        t0 = time.time()
        print(f"Executing {label}...", flush=True)
        with conn.cursor() as cur:
            cur.execute(stmt)
        print(f"Finished {label} in {time.time() - t0:.2f}s", flush=True)
    conn.close()
    print("ALL STATION ANALYTICS VIEWS SUCCESSFULLY CREATED!", flush=True)
except Exception as e:
    print(f"Error executing setup: {e}", flush=True)
