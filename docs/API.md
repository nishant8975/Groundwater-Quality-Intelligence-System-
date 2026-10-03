# Groundwater Quality Intelligence API

This internal REST API (Express.js) provides access to the PostgreSQL analytical views generated in Phase 5 and Phase 10.

## Architecture & Principles
- **Direct Analytical Reads**: To guarantee performance on 165,162 water samples, the API primarily queries the `vw_` (Views) and `mv_` (Materialized Views) layer.
- **Stateless**: Uses connection pooling via `pg`.
- **Consistent Response Wrappers**:
  - `{"data": [...], "pagination": { "page": 1, "limit": 50, "total": 100, "totalPages": 2 }}`
  - `{"error": { "code": "...", "message": "..." }}`
- **Security & Validation**: Safe defaults for pagination (max 500 rows). Uses strictly parameterized queries for all `WHERE` clauses. Limits queries to validated `state` or `district` filters.

---

## Endpoints

### 1. Health Check
- **`GET /api/health`**
- **Purpose**: Verify database pool connectivity.
- **Response**: `{"status": "ok", "database": "connected", "timestamp": "...", "service": "groundwater-quality-api"}`

### 2. National Overview
- **`GET /api/overview`**
- **Purpose**: High-level national totals matching authoritative Phase 4 statistics exactly.
- **Response**: `{"data": { "total_samples": 165162, "eligible_samples": 120738, "unavailable_samples": 44424, "min_wqi": 0.01, ... }}`

### 3. WAWQI Categories
- **`GET /api/wawqi/categories`**
- **Purpose**: National category distribution (Excellent -> Unsuitable + UNAVAILABLE).
- **Response**: `{"data": [ { "category": "Excellent", "count": 18821, "percentage": 15.59 }, ... ]}`

### 4. States
- **`GET /api/states`**
- **Purpose**: Aggregate WAWQI statistics grouped by state.
- **Response**: `{"data": [ { "state": "Andhra Pradesh", "total_samples": 123, "eligible_samples": 100, "median_wqi": 45.2, ... } ]}`

- **`GET /api/states/:state`**
- **Purpose**: Fetch detailed statistics for a single state.
- **Response**: `{"data": { "state": "Karnataka", "total_samples": ... }}`
- **Error**: `404` if state not found.

### 5. Districts
- **`GET /api/districts`**
- **Query Params**: `?state=Karnataka`
- **Purpose**: Retrieve district summaries, optionally filtered by state.

- **`GET /api/districts/:district`**
- **Query Params**: `?state=Karnataka`
- **Purpose**: Fetch statistics for a single district.

### 6. Parameters
- **`GET /api/parameters`**
- **Purpose**: Canonical dictionary of the 9 final WAWQI parameters, explicitly injecting BIS 10500 limit metadata for the frontend.

- **`GET /api/parameters/:parameter`**
- **Query Params**: `?state=Karnataka&district=Mysuru`
- **Purpose**: Distribution (min, max, mean, percentiles) for a specific parameter based on `mv_parameter_analytics`.

### 7. Exceedances
- **`GET /api/exceedances`**
- **Query Params**: `?state=Karnataka&district=Mysuru&parameter=iron`
- **Purpose**: Count and percentage of valid measurements violating BIS IS 10500 standards. Retains exact Phase 5 upper and lower bound logic for pH.

### 8. Extreme Values
- **`GET /api/extremes`**
- **Query Params**: `?state=Karnataka&min_wqi=200&page=1&limit=50`
- **Purpose**: Retrieve historical extreme breach events (WQI > 100).
- **Pagination**: Yes. Max limit 500.

### 9. GIS Points
- **`GET /api/gis`**
- **Query Params**: `?state=Karnataka&category=Unsuitable&page=1&limit=100`
- **Purpose**: Extract only the subset of parameters strictly required for plotting on the Map (id, coordinates, wqi, category). Filters invalid coordinates natively.
- **Pagination**: Yes. Max limit 500.

### 10. Temporal
- **`GET /api/temporal`**
- **Purpose**: Groups samples and median WAWQI by sample extraction year. Warning: May reflect disparate collection regimes rather than longitudinal monitoring.

### 11. Data Quality
- **`GET /api/data-quality`**
- **Purpose**: Count of `UNAVAILABLE` WQI, missing coordinates, and flagged observations (including Sample 1419 Uranium source-level warning).

### 12. Station Intelligence Listing & Search
- **`GET /api/stations`**
- **`GET /api/stations/search`**
- **Query Params**: `?q=Haryana` or `?search=patna&state=Bihar&district=Patna&data_quality=DATA_RICH&sort_by=sample_count&order=desc&page=1&limit=50`
- **Purpose**: Paginated directory and search endpoint for monitoring stations backed by `mv_station_identity`. Supports trigram ILIKE search across `station_name`, `district`, and `state` via query parameters `search` or `q`.


### 13. Station Detail Profile
- **`GET /api/stations/:hash`**
- **Purpose**: Fetch detailed station intelligence for a single station by `station_hash` (`MD5(norm_station || norm_state || norm_district)`), including complete historical sample timeline (`vw_station_wawqi_history`) and parameter statistical breakdown (`mv_station_parameter_analytics`).

### 14. Station Sample History Timeline
- **`GET /api/stations/:hash/history`**
- **Purpose**: Retrieve historical sample dates and calculated WAWQI scores/categories for a station.

### 15. Station Parameter Profile Analytics
- **`GET /api/stations/:hash/parameters`**
- **Purpose**: Retrieve parameter-by-parameter statistical profile (observation count, min, median, max, percentiles, BIS limit violations, exceedance percentage) for a station.
