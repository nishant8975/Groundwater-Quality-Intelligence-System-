
-- 02_analytics_views.sql

-- A. National Overview View
CREATE OR REPLACE VIEW vw_wawqi_national_summary AS
SELECT
    (SELECT COUNT(*) FROM water_samples) AS total_samples,
    (SELECT COUNT(*) FROM wawqi_results WHERE wqi IS NOT NULL) AS eligible_samples,
    (SELECT COUNT(*) FROM wawqi_results WHERE wqi IS NULL) AS unavailable_samples,
    (SELECT COUNT(DISTINCT state) FROM locations) AS state_count,
    (SELECT COUNT(DISTINCT district) FROM locations) AS district_count,
    (SELECT COUNT(DISTINCT location_id) FROM locations) AS location_count,
    MIN(wqi) AS min_wqi,
    MAX(wqi) AS max_wqi,
    AVG(wqi) AS avg_wqi,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY wqi) AS median_wqi,
    COUNT(*) FILTER (WHERE wqi <= 25) AS excellent_count,
    COUNT(*) FILTER (WHERE wqi > 25 AND wqi <= 50) AS good_count,
    COUNT(*) FILTER (WHERE wqi > 50 AND wqi <= 75) AS poor_count,
    COUNT(*) FILTER (WHERE wqi > 75 AND wqi <= 100) AS very_poor_count,
    COUNT(*) FILTER (WHERE wqi > 100) AS unsuitable_count,
    ROUND(COUNT(*) FILTER (WHERE wqi <= 25) * 100.0 / NULLIF(COUNT(wqi), 0), 2) AS excellent_pct,
    ROUND(COUNT(*) FILTER (WHERE wqi > 25 AND wqi <= 50) * 100.0 / NULLIF(COUNT(wqi), 0), 2) AS good_pct,
    ROUND(COUNT(*) FILTER (WHERE wqi > 50 AND wqi <= 75) * 100.0 / NULLIF(COUNT(wqi), 0), 2) AS poor_pct,
    ROUND(COUNT(*) FILTER (WHERE wqi > 75 AND wqi <= 100) * 100.0 / NULLIF(COUNT(wqi), 0), 2) AS very_poor_pct,
    ROUND(COUNT(*) FILTER (WHERE wqi > 100) * 100.0 / NULLIF(COUNT(wqi), 0), 2) AS unsuitable_pct
FROM wawqi_results;

-- B. State-level Analytics (Materialized View)
DROP MATERIALIZED VIEW IF EXISTS mv_wawqi_state_summary CASCADE;
CREATE MATERIALIZED VIEW mv_wawqi_state_summary AS
SELECT
    l.state,
    COUNT(s.sample_id) AS total_samples,
    COUNT(w.wqi) AS eligible_samples,
    COUNT(*) FILTER (WHERE w.wqi IS NULL) AS unavailable_samples,
    AVG(w.wqi) AS avg_wqi,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY w.wqi) AS median_wqi,
    MIN(w.wqi) AS min_wqi,
    MAX(w.wqi) AS max_wqi,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY w.wqi) AS p25_wqi,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY w.wqi) AS p75_wqi,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY w.wqi) AS p90_wqi,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY w.wqi) AS p95_wqi,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY w.wqi) AS p99_wqi,
    COUNT(*) FILTER (WHERE w.wqi <= 25) AS excellent_count,
    COUNT(*) FILTER (WHERE w.wqi > 25 AND w.wqi <= 50) AS good_count,
    COUNT(*) FILTER (WHERE w.wqi > 50 AND w.wqi <= 75) AS poor_count,
    COUNT(*) FILTER (WHERE w.wqi > 75 AND w.wqi <= 100) AS very_poor_count,
    COUNT(*) FILTER (WHERE w.wqi > 100) AS unsuitable_count,
    ROUND(COUNT(*) FILTER (WHERE w.wqi <= 25) * 100.0 / NULLIF(COUNT(w.wqi), 0), 2) AS excellent_pct,
    ROUND(COUNT(*) FILTER (WHERE w.wqi > 25 AND w.wqi <= 50) * 100.0 / NULLIF(COUNT(w.wqi), 0), 2) AS good_pct,
    ROUND(COUNT(*) FILTER (WHERE w.wqi > 50 AND w.wqi <= 75) * 100.0 / NULLIF(COUNT(w.wqi), 0), 2) AS poor_pct,
    ROUND(COUNT(*) FILTER (WHERE w.wqi > 75 AND w.wqi <= 100) * 100.0 / NULLIF(COUNT(w.wqi), 0), 2) AS very_poor_pct,
    ROUND(COUNT(*) FILTER (WHERE w.wqi > 100) * 100.0 / NULLIF(COUNT(w.wqi), 0), 2) AS unsuitable_pct
FROM locations l
JOIN water_samples s ON l.location_id = s.location_id
LEFT JOIN wawqi_results w ON s.sample_id = w.sample_id
GROUP BY l.state;

-- C. District-level Analytics (Materialized View)
DROP MATERIALIZED VIEW IF EXISTS mv_wawqi_district_summary CASCADE;
CREATE MATERIALIZED VIEW mv_wawqi_district_summary AS
SELECT
    l.state,
    l.district,
    COUNT(s.sample_id) AS total_samples,
    COUNT(w.wqi) AS eligible_samples,
    COUNT(*) FILTER (WHERE w.wqi IS NULL) AS unavailable_samples,
    AVG(w.wqi) AS avg_wqi,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY w.wqi) AS median_wqi,
    MIN(w.wqi) AS min_wqi,
    MAX(w.wqi) AS max_wqi,
    COUNT(*) FILTER (WHERE w.wqi <= 25) AS excellent_count,
    COUNT(*) FILTER (WHERE w.wqi > 25 AND w.wqi <= 50) AS good_count,
    COUNT(*) FILTER (WHERE w.wqi > 50 AND w.wqi <= 75) AS poor_count,
    COUNT(*) FILTER (WHERE w.wqi > 75 AND w.wqi <= 100) AS very_poor_count,
    COUNT(*) FILTER (WHERE w.wqi > 100) AS unsuitable_count,
    ROUND(COUNT(*) FILTER (WHERE w.wqi > 100) * 100.0 / NULLIF(COUNT(w.wqi), 0), 2) AS unsuitable_pct
FROM locations l
JOIN water_samples s ON l.location_id = s.location_id
LEFT JOIN wawqi_results w ON s.sample_id = w.sample_id
GROUP BY l.state, l.district;

-- D. Station/Location Analytics (Materialized View)
DROP MATERIALIZED VIEW IF EXISTS mv_wawqi_location_summary CASCADE;
CREATE MATERIALIZED VIEW mv_wawqi_location_summary AS
WITH ranked_samples AS (
    SELECT 
        s.location_id,
        s.sample_id,
        s.sample_date,
        w.wqi,
        ROW_NUMBER() OVER(PARTITION BY s.location_id ORDER BY s.sample_date DESC NULLS LAST, s.sample_id DESC) as rn
    FROM water_samples s
    LEFT JOIN wawqi_results w ON s.sample_id = w.sample_id
)
SELECT 
    l.location_id,
    l.station_name,
    l.state,
    l.district,
    l.latitude,
    l.longitude,
    COUNT(s.sample_id) AS sample_count,
    MAX(s.sample_date) AS latest_sample_date,
    MAX(rs.wqi) FILTER (WHERE rs.rn = 1) AS latest_wqi,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY w.wqi) AS median_wqi,
    COUNT(*) FILTER (WHERE w.wqi <= 25) AS excellent_count,
    COUNT(*) FILTER (WHERE w.wqi > 25 AND w.wqi <= 50) AS good_count,
    COUNT(*) FILTER (WHERE w.wqi > 50 AND w.wqi <= 75) AS poor_count,
    COUNT(*) FILTER (WHERE w.wqi > 75 AND w.wqi <= 100) AS very_poor_count,
    COUNT(*) FILTER (WHERE w.wqi > 100) AS unsuitable_count
FROM locations l
JOIN water_samples s ON l.location_id = s.location_id
LEFT JOIN wawqi_results w ON s.sample_id = w.sample_id
LEFT JOIN ranked_samples rs ON l.location_id = rs.location_id AND rs.rn = 1
GROUP BY l.location_id, l.station_name, l.state, l.district, l.latitude, l.longitude;

-- 4. WAWQI DISTRIBUTION ANALYTICS (Category view)
CREATE OR REPLACE VIEW vw_wawqi_categories AS
SELECT 
    sample_id,
    wqi,
    CASE 
        WHEN wqi <= 25 THEN 'Excellent'
        WHEN wqi > 25 AND wqi <= 50 THEN 'Good'
        WHEN wqi > 50 AND wqi <= 75 THEN 'Poor'
        WHEN wqi > 75 AND wqi <= 100 THEN 'Very Poor'
        WHEN wqi > 100 THEN 'Unsuitable'
        ELSE 'UNAVAILABLE'
    END AS wqi_category
FROM wawqi_results;

-- 5. PARAMETER ANALYTICS (Materialized View)
DROP MATERIALIZED VIEW IF EXISTS mv_parameter_analytics CASCADE;
CREATE MATERIALIZED VIEW mv_parameter_analytics AS
SELECT
    l.state,
    l.district,
    p.canonical_name,
    COUNT(spv.numeric_value) AS numeric_observation_count,
    COUNT(*) FILTER (WHERE spv.is_missing) AS missing_count,
    MIN(spv.numeric_value) AS min_val,
    MAX(spv.numeric_value) AS max_val,
    AVG(spv.numeric_value) AS mean_val,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY spv.numeric_value) AS median_val,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY spv.numeric_value) AS p25_val,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY spv.numeric_value) AS p75_val,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY spv.numeric_value) AS p90_val,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY spv.numeric_value) AS p95_val,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY spv.numeric_value) AS p99_val
FROM sample_parameter_values spv
JOIN parameters p ON spv.parameter_id = p.parameter_id
JOIN water_samples s ON spv.sample_id = s.sample_id
JOIN locations l ON s.location_id = l.location_id
GROUP BY l.state, l.district, p.canonical_name;

-- 6. PARAMETER EXCEEDANCE ANALYTICS (Materialized View)
DROP MATERIALIZED VIEW IF EXISTS mv_parameter_exceedance CASCADE;
CREATE MATERIALIZED VIEW mv_parameter_exceedance AS
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
    l.state,
    l.district,
    p.canonical_name,
    COUNT(spv.numeric_value) AS valid_measurement_count,
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
GROUP BY l.state, l.district, p.canonical_name;

-- 7. EXTREME WAWQI ANALYTICS View
CREATE OR REPLACE VIEW vw_wawqi_extreme_values AS
SELECT
    s.sample_id,
    l.state,
    l.district,
    l.station_name,
    l.latitude,
    l.longitude,
    s.sample_date,
    w.wqi,
    c.wqi_category AS category,
    w.valid_parameter_count,
    w.data_quality_flags
FROM wawqi_results w
JOIN water_samples s ON w.sample_id = s.sample_id
JOIN locations l ON s.location_id = l.location_id
JOIN vw_wawqi_categories c ON w.sample_id = c.sample_id
WHERE w.wqi > 100
ORDER BY w.wqi DESC;

-- 8. DATA-QUALITY ANALYTICS View
CREATE OR REPLACE VIEW vw_data_quality_analytics AS
SELECT
    (SELECT COUNT(*) FROM locations WHERE latitude IS NULL OR longitude IS NULL) AS missing_coordinates_count,
    (SELECT COUNT(*) FROM locations WHERE coordinate_validity_flag = FALSE) AS invalid_coordinates_count,
    (SELECT COUNT(*) FROM wawqi_results WHERE wqi IS NULL) AS wawqi_unavailable_count,
    (SELECT COUNT(*) FROM wawqi_results WHERE calculation_status = 'INSUFFICIENT_PARAMETER_COVERAGE') AS insufficient_parameter_coverage_count,
    (SELECT COUNT(*) FROM wawqi_results WHERE data_quality_flags IS NOT NULL) AS flagged_observations_count
;

-- 9. TIME ANALYTICS View
DROP MATERIALIZED VIEW IF EXISTS mv_temporal_analytics CASCADE;
CREATE MATERIALIZED VIEW mv_temporal_analytics AS
SELECT 
    EXTRACT(YEAR FROM s.sample_date) AS sample_year,
    COUNT(s.sample_id) AS total_samples,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY w.wqi) AS median_wqi,
    COUNT(*) FILTER (WHERE w.wqi <= 25) AS excellent_count,
    COUNT(*) FILTER (WHERE w.wqi > 25 AND w.wqi <= 50) AS good_count,
    COUNT(*) FILTER (WHERE w.wqi > 50 AND w.wqi <= 75) AS poor_count,
    COUNT(*) FILTER (WHERE w.wqi > 75 AND w.wqi <= 100) AS very_poor_count,
    COUNT(*) FILTER (WHERE w.wqi > 100) AS unsuitable_count
FROM water_samples s
LEFT JOIN wawqi_results w ON s.sample_id = w.sample_id
WHERE s.sample_date IS NOT NULL
GROUP BY EXTRACT(YEAR FROM s.sample_date);

-- 10. GIS QUERY SUPPORT View
CREATE OR REPLACE VIEW vw_gis_points AS
SELECT 
    l.location_id,
    l.station_name,
    l.state,
    l.district,
    l.latitude,
    l.longitude,
    ls.latest_wqi,
    ls.median_wqi,
    ls.latest_sample_date,
    ls.sample_count,
    CASE 
        WHEN ls.latest_wqi <= 25 THEN 'Excellent'
        WHEN ls.latest_wqi > 25 AND ls.latest_wqi <= 50 THEN 'Good'
        WHEN ls.latest_wqi > 50 AND ls.latest_wqi <= 75 THEN 'Poor'
        WHEN ls.latest_wqi > 75 AND ls.latest_wqi <= 100 THEN 'Very Poor'
        WHEN ls.latest_wqi > 100 THEN 'Unsuitable'
        ELSE 'UNAVAILABLE'
    END AS latest_category
FROM mv_wawqi_location_summary ls
JOIN locations l ON ls.location_id = l.location_id
WHERE l.latitude IS NOT NULL 
  AND l.longitude IS NOT NULL
  AND l.coordinate_validity_flag = TRUE;

