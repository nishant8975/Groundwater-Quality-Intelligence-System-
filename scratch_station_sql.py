import psycopg2
import pandas as pd

conn_str = "dbname='groundwater_quality' user='postgres' host='localhost' password='Nishant@2003' port='5432'"

sql = """
WITH base_stations AS (
    SELECT 
        s.sample_id,
        l.station_name,
        l.state_name AS state,
        l.district_name AS district,
        s.sample_date,
        s.latitude,
        s.longitude,
        w.wqi,
        w.calculation_status,
        w.data_quality_flags,
        w.parameter_sub_indices,
        TRIM(LOWER(l.station_name)) AS norm_station,
        TRIM(LOWER(l.state_name)) AS norm_state,
        TRIM(LOWER(l.district_name)) AS norm_district
    FROM water_samples s
    JOIN locations l ON s.location_id = l.location_id
    LEFT JOIN wawqi_results w ON s.sample_id = w.sample_id
),
station_canonical AS (
    SELECT 
        *,
        md5(concat_ws('||', norm_station, norm_state, norm_district)) AS station_hash
    FROM base_stations
),
sample_dominant AS (
    SELECT 
        w.sample_id,
        (
            SELECT array_agg(key ORDER BY key)
            FROM jsonb_each_text(w.parameter_sub_indices)
            WHERE value::numeric = (
                SELECT max(value::numeric) FROM jsonb_each_text(w.parameter_sub_indices)
            )
        ) as dominant_parameters
    FROM wawqi_results w
    WHERE w.parameter_sub_indices IS NOT NULL
),
flat_dominant AS (
    SELECT 
        c.station_hash,
        c.sample_id,
        dp.dom_param
    FROM station_canonical c
    JOIN sample_dominant sd ON c.sample_id = sd.sample_id
    CROSS JOIN unnest(sd.dominant_parameters) AS dp(dom_param)
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
station_metrics AS (
    SELECT 
        station_hash,
        MAX(station_name) AS display_station_name,
        MAX(state) AS display_state,
        MAX(district) AS display_district,
        AVG(latitude) AS avg_latitude,
        AVG(longitude) AS avg_longitude,
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
        MAX(wqi) AS max_wqi,
        (
            SELECT w2.data_quality_flags 
            FROM station_canonical c2
            LEFT JOIN wawqi_results w2 ON c2.sample_id = w2.sample_id
            WHERE c2.station_hash = sc.station_hash 
            ORDER BY c2.sample_date DESC NULLS LAST, c2.sample_id DESC 
            LIMIT 1
        ) AS latest_source_warning
    FROM station_canonical sc
    GROUP BY station_hash
)
SELECT 
    sm.*,
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
LEFT JOIN station_dominant_tied sdt ON sm.station_hash = sdt.station_hash
"""

try:
    with psycopg2.connect(conn_str) as conn:
        df = pd.read_sql_query(f"SELECT * FROM ({sql}) t LIMIT 5", conn)
        print("Materialized view snippet:")
        pd.set_option('display.max_columns', None)
        print(df)
        
        print("\nChecking a known DATA LIMITED station:")
        df2 = pd.read_sql_query(f"SELECT * FROM ({sql}) t WHERE data_quality_class = 'DATA LIMITED' LIMIT 1", conn)
        print(df2[['display_station_name', 'sample_count', 'wawqi_eligibility_percentage', 'data_quality_reason']])
        
        print("\nChecking station counts:")
        count = pd.read_sql_query(f"SELECT COUNT(*) as c FROM ({sql}) t", conn)
        print(f"Total Unique Stations: {count['c'].iloc[0]}")
except Exception as e:
    print(f"Error: {e}")
