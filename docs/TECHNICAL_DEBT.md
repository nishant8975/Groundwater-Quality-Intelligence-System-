# TECHNICAL DEBT & OPTIMIZATION CANDIDATES

## Groundwater Quality Intelligence — WAWQI Analytics Platform

---

## OVERVIEW

This document records the 5 non-blocking optimization candidates identified during Phase 12A (Backend), Phase 12B (Frontend), Phase 12C (Stress QA), and Phase 12D (Production Audit). 

Per strict project instructions, **no optimization has been implemented in Phase 12 or 13**. These candidates are documented for future production scaling.

---

## TECHNICAL DEBT MATRIX

| # | Issue / Candidate | Source Phase | Severity | Evidence / Baseline | Recommended Future Action |
| :-: | :--- | :---: | :---: | :--- | :--- |
| **1** | Missing Composite Index `water_samples(location_id, sample_date)` | Phase 12A | `MEDIUM` | Station history API latency ~196 – 208 ms; catalog confirms separate single-column indexes only. | Create composite index `CREATE INDEX idx_ws_loc_date ON water_samples(location_id, sample_date);` |
| **2** | Duplicate Single-Column Indexes on `location_id` and `sample_date` | Phase 12A | `LOW` | `idx_samples_location` & `idx_water_samples_location` exist simultaneously; consumes ~18 MB unnecessary disk. | Drop redundant duplicate index definitions via `DROP INDEX`. |
| **3** | Heavy Unindexed `/overview` and `/extremes` Queries | Phase 12A/12C | `MEDIUM` | Materialization/caching of `/overview` and `/extremes` is a future optimization for higher-concurrency workloads. Stress testing achieved 198/200 successful requests at 20 concurrent clients, with 2 timeouts observed during the test. | Materialize national overview query or add partial index `wawqi_results(wqi DESC) WHERE wqi > 100`. |
| **4** | Missing Express HTTP Response Compression | Phase 12B | `LOW` | Large JSON payloads (e.g. 500-station payload 396 KB) transmitted uncompressed over HTTP. | Add `compression()` middleware to Express backend (estimated 89% bandwidth reduction). |
| **5** | Root `.env.example` `API_PORT=8000` Mismatch | Phase 12D | `LOW` | Root `.env.example` specifies `API_PORT=8000`, while `backend/server.js` listens on port 3000. | Update root template `API_PORT` to `3000` for clarity. |
