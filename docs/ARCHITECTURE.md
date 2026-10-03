# SYSTEM ARCHITECTURE DOCUMENT

## Groundwater Quality Intelligence — WAWQI Analytics Platform

---

## 1. END-TO-END DATA FLOW DIAGRAM

```text
[ Raw CGWB Datasets (30 State CSVs) ]
                │
                ▼
[ Python ETL & Normalization Pipeline (etl/01_ingest_cgwb.py) ]
                │
                ├──────────────────────────┐
                ▼                          ▼
   [ locations (165,162) ]      [ water_samples (165,162) ]
                │                          │
                └────────────┬─────────────┘
                             ▼
            [ sample_parameter_values (1,609,277) ]
                             │
                             ▼
      [ WAWQI Calculation Engine (etl/02_wawqi_engine.py) ]
                             │
                             ▼
             [ wawqi_results (165,162 Scores) ]
                             │
                             ▼
         [ PostgreSQL Materialized Analytics Views ]
         (mv_station_identity, mv_wawqi_state_summary, etc.)
                             │
                             ▼
         [ Express REST API Server (backend/app.js) ]
                             │
                             ▼
     [ React 18 + TypeScript SPA (frontend/src) ]
         ├── Overview Dashboard (/)
         ├── State & District Analytics (/states, /districts)
         ├── GIS Spatial Map (/map)
         └── Station Intelligence (/stations, /stations/:hash)
```

---

## 2. DATABASE ARCHITECTURE (ENTITY-ATTRIBUTE-VALUE MODEL)

To accommodate highly variable chemical parameter coverage across 30 states without sparse columns, PostgreSQL employs a normalized **Entity-Attribute-Value (EAV)** schema:

* **`source_datasets` (30 rows):** Provenance tracking for original CGWB CSV files.
* **`locations` (165,162 rows):** Geographic coordinates (latitude, longitude), state, district, block, and village attributes.
* **`parameters` (27 rows):** Master registry of water quality parameters with BIS IS 10500:2012 acceptable limits ($S_i$) and unit definitions.
* **`water_samples` (165,162 rows):** Core sampling events indexed by location and sample date.
* **`sample_parameter_values` (1,609,277 rows):** EAV storage mapping `sample_id` and `parameter_id` to numeric chemical concentrations.
* **`wawqi_results` (165,162 rows):** Computed WQI scores, valid parameter counts, parameters used, calculation status, and `parameter_sub_indices` JSONB payload.

---

## 3. ANALYTICS & MATERIALIZED VIEW LAYER

The platform uses 6 standard views and 8 materialized views to deliver sub-50 ms analytical queries:

1. **`mv_station_identity` (22,753 rows):** Groups 165,162 sample events into canonical physical stations based on coordinate proximity ($\pm 0.001^\circ$) and station name hashing.
2. **`mv_wawqi_state_summary` (30 rows):** Pre-calculated state-level aggregates (mean WQI, sample count, category counts, unsuitable percentage).
3. **`mv_wawqi_district_summary` (584 rows):** Pre-calculated district-level risk metrics and ranking data.
4. **`mv_parameter_analytics` (27 rows):** National parameter exceedance rates and min/max/average concentrations.
5. **`vw_gis_points` (165,010 rows):** Filters valid coordinates within geographic bounds ($6.0 \le \text{lat} \le 37.5$, $68.0 \le \text{lon} \le 97.5$).

---

## 4. REST API ARCHITECTURE

Built with Express.js using a modular controller-service-db pattern:
* **Stateless Communication:** JSON HTTP requests and responses.
* **Database Connection Pooling:** Managed via `pg.Pool` with `max: 20` client connection cap.
* **Input Sanitization & Parameterization:** 100% of queries use `$1`, `$2` placeholders. Pagination limits capped at `500`.
* **Centralized Error Handling:** Uniform structured error payloads with stack trace suppression in production.

---

## 5. FRONTEND SPA ARCHITECTURE

The client application is built with React 18, TypeScript, Vite, and TailwindCSS:
* **State & Query Management:** `@tanstack/react-query` handles server response caching, stale-time management, and background refetching.
* **URL-Driven Filter State:** Search, state, district, and category filters synchronize directly with `window.location.search`.
* **GIS Map Integration:** `react-leaflet` consumes CartoDB Dark Matter vector/raster tiles, displaying custom SVG CircleMarkers color-coded by WAWQI status.
* **Station Intelligence Explorer:** Visualizes individual station temporal trends using Recharts `ResponsiveContainer` and `LineChart`.

---

## 6. SECURITY & SECRET MANAGEMENT ARCHITECTURE

* **Zero Hardcoded Secrets:** DB connection settings read strictly from environment variables (`process.env`).
* **Version Control Boundaries:** `.env` files explicitly git-ignored. Template `.env.example` contains non-sensitive placeholders.
* **CORS Protection:** Express CORS middleware restricts cross-origin access to configured frontend domain origins.
