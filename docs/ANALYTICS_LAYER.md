# Analytics Layer Design

The Analytics Layer provides materialized views and efficient query interfaces to prevent expensive table scans on the raw observation data (`1.6M+ parameter observations` and `165,162 water samples`) during API calls.

## Views and Materialized Views

| Object Name | Type | Purpose | Refresh Requirement |
|-------------|------|---------|---------------------|
| `vw_wawqi_national_summary` | View | High-level national totals, WAWQI minimum, maximum, mean, and category distribution percentages. | Dynamic |
| `mv_wawqi_state_summary` | Materialized View | Summarizes WAWQI statistics, percentiles (P25-P99), and sample counts grouped by `state`. | Refresh after ETL or WAWQI recalculation |
| `mv_wawqi_district_summary` | Materialized View | Summarizes WAWQI statistics and counts grouped by `state` and `district`. | Refresh after ETL or WAWQI recalculation |
| `mv_wawqi_location_summary` | Materialized View | Summarizes WAWQI data at the station level, calculating median WAWQI across historical observations, and the single latest WAWQI. | Refresh after ETL or WAWQI recalculation |
| `vw_wawqi_categories` | View | Categorical mapping of WQI values to approved project classifications (Excellent, Good, Poor, Very Poor, Unsuitable, UNAVAILABLE). | Dynamic |
| `mv_parameter_analytics` | Materialized View | Aggregates parameter distribution statistics (min, max, mean, percentiles) globally and per location hierarchy. | Refresh after ETL |
| `mv_parameter_exceedance` | Materialized View | Compares numeric values against established BIS IS 10500:2012 standards, identifying exceedance counts and percentages. | Refresh after ETL |
| `vw_wawqi_extreme_values` | View | Efficiently identifies "Unsuitable" (WQI > 100) samples. Filters extreme limit-breach values without clamping. | Dynamic |
| `vw_data_quality_analytics` | View | Provides dashboard totals for flagged data, invalid/missing coordinates, and insufficient parameter coverage. | Dynamic |
| `mv_temporal_analytics` | Materialized View | Groups sample counts and WAWQI medians by year. Note: Most data only represents a snapshot or short timeline. | Refresh after ETL |
| `vw_gis_points` | View | Merges location coordinates with `mv_wawqi_location_summary` for plotting. Filters out invalid coordinates to optimize map payloads. | Dynamic |

## Indexes Implemented
- `wawqi_results(wqi)`
- `wawqi_results(calculation_status)`
- `locations(state, district)`
- `locations(latitude, longitude) WHERE latitude IS NOT NULL AND longitude IS NOT NULL`
- `water_samples(location_id)`
- `water_samples(sample_date)`
- `sample_parameter_values(parameter_id, numeric_value)`

## NULL Semantics and Missing Data
- **WAWQI NULL**: The system intentionally assigns `WQI = NULL` when valid parameter coverage < 6. These are categorized strictly as `UNAVAILABLE` and do not skew "Excellent" or numeric averages.
- **Missing Parameters**: Missing values are structurally excluded from aggregation counts. Zeros are never artificially imputed into parameter analytics.

## Category Logic (Project Standards)
- **Excellent**: WQI <= 25
- **Good**: 25 < WQI <= 50
- **Poor**: 50 < WQI <= 75
- **Very Poor**: 75 < WQI <= 100
- **Unsuitable**: WQI > 100
- **Unavailable**: WQI IS NULL

## Performance Findings
Query execution plans (`EXPLAIN ANALYZE`) confirm the effectiveness of the indexing strategy:
- `mv_wawqi_state_summary` Seq Scan executes in `0.033 ms`.
- `vw_gis_points` filtered by State leverages the `idx_locations_state` index + hash join against `mv_wawqi_location_summary`, computing 13,000 mapping points in `< 95 ms` total execution time, perfectly suited for the frontend visualization.
