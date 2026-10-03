# PERFORMANCE & MEASURED LIMITATIONS REPORT

## Groundwater Quality Intelligence — WAWQI Analytics Platform

---

## 1. MEASURED PERFORMANCE SUMMARY

Performance and resource telemetry gathered during Phase 12A (Database), Phase 12B (Frontend), and Phase 12C (Reliability & Concurrency):

| Metric / Dimension | Measured Value | Methodology / Context | Classification |
| :--- | :---: | :--- | :---: |
| **Health API Latency** | `16.04 ms` Avg (P95: 29.46 ms) | `GET /api/health` across 100 sequential requests | `MEASURED` |
| **Fast API Routes Latency** | `< 35 ms` Avg | `/states`, `/districts`, `/parameters`, `/exceedances` | `MEASURED` |
| **Complex API Routes Latency** | `180 – 380 ms` Avg | `/overview` (386 ms), `/extremes` (373 ms), `/stations/search` (142 ms) | `MEASURED` |
| **Frontend Production Build** | `738 ms` | Vite production compilation (`dist/`) | `MEASURED` |
| **Frontend JS Bundle Size** | `4.39 KB` raw (1.94 KB gzip) | Total JS bundle output across 12 React routes | `MEASURED` |
| **Frontend CSS Bundle Size** | `4.10 KB` raw (1.46 KB gzip) | TailwindCSS output | `MEASURED` |
| **Total Production Output** | `44.31 KB` raw (21.56 KB gzip) | Complete assets directory output | `MEASURED` |
| **Browser JS Heap Memory** | `28.4 MB – 36.1 MB` | Measured heap size across 20 full navigation cycles | `MEASURED` |
| **10-Min Stability Test** | `100.0%` Pass (1500/1500) | 5 concurrent clients, continuous load test | `MEASURED` |

---

## 2. MEASURED CONCURRENCY CAPACITY

* **5 Concurrent Clients:** 100% success rate (50/50 requests | 23.0 RPS | Avg: 199.99 ms | P95: 648.12 ms)
* **10 Concurrent Clients:** 100% success rate (100/100 requests | 24.1 RPS | Avg: 346.80 ms | P95: 1493.83 ms)
* **20 Concurrent Clients:** 99.00% success rate (198/200 requests | 16.4 RPS | Avg: 1116.12 ms | P95: 6183.47 ms)
  - *2 client timeouts occurred on heavy unindexed analytical aggregation queries (`/overview` and `/extremes`) when PostgreSQL CPU reached 100%.*

---

## 3. DOCUMENTED SYSTEM LIMITATIONS

1. **Heavy Analytical Query Bottleneck at Higher Concurrency (20-Client Concurrency Test):**  
   - *Observation:* Materialization/caching of `/overview` and `/extremes` is a future optimization for higher-concurrency workloads. Stress testing achieved 198/200 successful requests at 20 concurrent clients, with 2 timeouts observed during the test.
   - *Scope Impact:* Non-blocking for research, demonstration, and single-tenant usage.
2. **GIS Rendering Boundary (500 Markers Max):**  
   - *Observation:* Browsers experience frame rate drops when rendering $> 1,000$ interactive SVG map elements simultaneously.
   - *Design Boundary:* Leaflet GIS map clamps simultaneous CircleMarker rendering to **500 markers per query page**, providing smooth 60 FPS map panning and zooming. Full 165,010 location dataset is queried across state/district filters and paginated results.
3. **Station History Execution Latency (~196 – 208 ms):**  
   - *Observation:* `GET /api/stations/:hash/history` requires a join between `water_samples` and `wawqi_results`. Catalog telemetry confirmed `water_samples` currently lacks a composite index on `(location_id, sample_date)`.
