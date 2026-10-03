# Phase 10: Station Intelligence Design

## 1. Station Identity Findings
The current `locations` table contains 165,162 records, matching the 165,162 rows in `water_samples`. There is currently a 1:1 relationship between samples and locations because the Phase 3 ETL loaded each row's location data natively without deduplicating the geographic entity.
There are **21,865 unique station names**, and **22,797 unique stations** when defined by `(station_name, state, district)`.

## 2. Station/Location Relationship
Because `locations` maps 1:1 to `water_samples`, a true "Station" entity does not exist in the relational structure yet.
To treat multiple samples as belonging to the same physical station, they must be grouped dynamically by a composite identity key.

## 3. Station Name Ambiguity
`station_name` cannot be used as a unique identifier:
- **445** station names span multiple states.
- **669** station names span multiple districts.
- **980** station names have slightly varying coordinates.
Conclusion: A station's true identity must be defined by `station_name + state + district`. Variations in coordinates for the same text identity must be handled by taking the centroid or the most recent coordinates.

## 4. Temporal Coverage
When grouped by `(station_name, state, district)`, stations have between **1 and 25 samples**.
The overall temporal coverage spans from **May 25, 2000** to **August 5, 2025**.
Many stations have only a single observation, but thousands of stations have 3+ observations spanning multiple years.

## 5. WAWQI Station Metrics
Instead of arbitrary risk scores, stations should be profiled using transparent descriptive metrics:
- Total Sample Count
- WAWQI Available Count
- Median WAWQI
- P90 WAWQI
- Maximum WAWQI
- Count of samples in Excellent / Good / Poor / Very Poor / Unsuitable categories.

## 6. Parameter-level Station Metrics
For the Core and Conditional parameters (pH, Chloride, Sulphate, Hardness, Calcium, Magnesium, Iron, Arsenic, Uranium), we must support:
- Valid observation count
- Minimum, Median, Maximum
- Number of exceedances against the BIS limit over time.

## 7. Dominant Parameter Methodology
The `wawqi_results` table stores the raw parameters in a `parameters_used` `jsonb` column. Currently, it does not explicitly rank the "dominant parameter".
**Methodology decision:** The dominant parameter for a single sample is defined as the parameter with the highest individual `Wi × qi` sub-index contribution.
For a **Station**, the dominant parameter will be defined as the *most frequent* dominant parameter across all historical WAWQI-eligible samples for that station.

## 8. Data-Quality Intelligence
A station will be classified as **DATA LIMITED** if less than 50% of its historical samples contain enough parameters to compute a valid WAWQI, or if it has fewer than 3 samples historically.
Otherwise, it is **DATA RICH**.
Source-level warnings (like the Sample 1419 Uranium anomaly) stored in `data_quality_flags` will bubble up to the station level if they occur in the most recent sample.

## 9. Station Search Requirements
Given ~23,000 distinct stations, a frontend-only search is infeasible.
The backend will require a `GET /api/stations/search` endpoint.
It must search `station_name`, filtering by `state` and `district`, and limit results to the top 50 matches. Performance requires a `pg_trgm` index or a standard composite B-tree index on `(state, district, station_name)`.

## 10. Station Detail Design
The Station Detail page (`/stations/:id`) will feature:
- **Header:** Station Name, State, District, Map Context.
- **Summary:** Sample count, Median WAWQI, Unsuitable %.
- **WAWQI History:** A time-series chart showing WAWQI over time.
- **Parameter Profile:** Aggregated min/median/max for core parameters.
- **Data Quality:** Explicit warnings if the station is Data Limited.

## 11. Temporal Trend Feasibility
Temporal trends are statistically meaningless for stations with only 1 or 2 observations.
**Rule:** A time-series trend line (historical WQI or historical parameter) will ONLY be drawn for stations that possess **3 or more valid samples**. For stations with 1-2 samples, discrete points will be plotted without connecting lines.

## 12. Hotspot Analysis Feasibility
Hotspot analysis (e.g. Kernel Density Estimation) is feasible given the precise coordinates. A simplified spatial clustering based on "density of Unsuitable WAWQI samples" within a 10km radius could be implemented via PostGIS, or approximated on the frontend by aggregating overlapping extreme categories.
*Decision:* Hotspot implementation is deferred to future spatial phases.

## 13. Station Scoring Decision
**DO NOT IMPLEMENT YET.** No arbitrary "Risk Score", "Health Score", or "Predictive Score" will be invented. The platform will rely exclusively on Median WAWQI, P90 WAWQI, and Exceedance Counts to rank severity.

## 14. Proposed API Endpoints
- `GET /api/stations` (paginated list of distinct stations)
- `GET /api/stations/search?q={query}` (search endpoint)
- `GET /api/stations/:station_hash` (station summary)
- `GET /api/stations/:station_hash/history` (time-series WAWQI data)

*(Since there is no primary key for a station, the `station_hash` will be a url-safe base64 or md5 hash of `station_name|state|district`)*

## 15. Proposed Database Changes
Instead of mutating the immutable 1:1 `locations` table, we will create a Materialized View:
`mv_station_identity`
- **Primary Key:** `station_hash` (MD5 of `station_name`, `state`, `district`).
- **Fields:** `station_name`, `state`, `district`, `centroid_latitude`, `centroid_longitude`, `sample_count`, `earliest_date`, `latest_date`.
This preserves the source data integrity while establishing a clean dimensional entity for the API.

## 16. Performance Findings
Querying 165,162 records with grouping is extremely fast on PostgreSQL 15+ (~40ms execution time). However, to support sub-10ms UI latency, `mv_station_identity` will be heavily indexed. 
Required index: `CREATE INDEX idx_locations_station_identity ON locations (station_name, state, district);`

## 17. Scientific/Human Decisions Required
1. Do we approve generating a synthetic `station_hash` primary key using `MD5(station_name + state + district)` to bind isolated location records together?
2. Do we approve the "Dominant Parameter" definition (`MAX(Wi × qi)`)?
3. Do we approve the "Data Limited" definition (<3 samples or <50% valid)?

## 18. Phase 10 Status
**DESIGN COMPLETE — IMPLEMENTATION PENDING APPROVAL**
