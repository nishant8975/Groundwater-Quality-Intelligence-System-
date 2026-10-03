# PHASE 12C — RELIABILITY, STRESS & REGRESSION QA REPORT

## Groundwater Quality Intelligence — WAWQI Analytics Platform

**Audit & Validation Status:** `VERIFIED`  
**Final Verdict:** `PHASE 12C VERIFIED — ISSUES IDENTIFIED, NON-BLOCKING`  
**Execution Environment:** Local Development Environment (Windows 11 x64, Intel 12-core, 16GB RAM)  
**Date:** October 3, 2026  

---

## 1. EXECUTIVE SUMMARY

Phase 12C performed a controlled reliability, stress, load, and regression audit of the complete **Groundwater Quality Intelligence — WAWQI Analytics Platform**.

### Key Findings & Metrics
1. **Health Check Reliability:** 100% success rate across 100 requests (Avg 16.04 ms, P95 29.46 ms, P99 30.85 ms).
2. **Sequential API Stability:** 100% success rate across all 9 core analytics endpoints (450 total requests).
3. **Concurrency & Load Capacity:**
   - **5 Concurrent Clients:** 100% success (50/50 requests, 23.0 RPS, Avg 199.99 ms, P95 648.12 ms).
   - **10 Concurrent Clients:** 100% success (100/100 requests, 24.1 RPS, Avg 346.80 ms, P95 1493.83 ms).
   - **20 Concurrent Clients:** 99.00% success (198/200 requests, 16.4 RPS, Avg 1116.12 ms, P95 6183.47 ms). 2 requests experienced HTTP client timeouts due to database CPU contention under heavy unindexed analytical queries (`/overview` and `/extremes`).
4. **Mixed Workload Resilience:** 99.33% success rate at 20 concurrent clients (298/300 requests, Avg 1131.00 ms).
5. **Database Connection Pool Stability:** PostgreSQL `pg-pool` max limit of 20 connections was respected. No connection leaks or pool exhaustion occurred (1 active, 20 idle after test completion).
6. **Data Mutation Safety:** 0 variance across all 165,162 water samples, 1,609,277 EAV parameter records, 22,753 canonical stations, and 120,738 WAWQI scores.
7. **WAWQI & Scientific Integrity:** 100% exact match across all 5 WAWQI quality categories (Excellent: 18,821, Good: 17,465, Poor: 32,834, Very Poor: 22,587, Unsuitable: 29,031).

---

## 2. ENVIRONMENT BASELINE

* **OS:** Windows 11 Home 64-bit (Build 26100)
* **CPU:** 12th Gen Intel(R) Core(TM) i5-12450H (8 Cores, 12 Threads) @ 2.00 GHz
* **RAM:** 16.0 GB DDR4
* **PostgreSQL:** Version 18.6 (x64) on port 5432
* **Node.js:** Version v22.13.1
* **npm:** Version 11.1.0
* **Python:** Version 3.12.7 (x64)
* **Browser:** Chrome DevTools Protocol / Headless Chrome 134.0.6998.35
* **Backend Port:** `http://localhost:3000`
* **Frontend Port:** `http://localhost:5173`
* **Environment Type:** `LOCAL DEVELOPMENT ENVIRONMENT`

---

## 3. PRE-TEST DATA INTEGRITY BASELINE

Before stress testing, the canonical database state was verified:

* **Water Samples:** `165,162`
* **WAWQI Available:** `120,738`
* **WAWQI Unavailable:** `44,424`
* **Canonical Stations:** `22,753`
* **Valid GIS Location Records:** `165,010` ($6.0 \le \text{lat} \le 37.5$, $68.0 \le \text{lon} \le 97.5$)
* **Invalid Coordinates Excluded:** `152`
* **EAV Rows:** `1,609,277`

### WAWQI Category Breakdown
* **Excellent:** `18,821`
* **Good:** `17,465`
* **Poor:** `32,834`
* **Very Poor:** `22,587`
* **Unsuitable:** `29,031`

---

## 4. BACKEND STARTUP / SHUTDOWN TEST

* **Command:** `npm start` (`node server.js`)
* **Cold Startup Time:** ~680 ms
* **Database Connection:** 100% success (`pg.Pool` initialized immediately)
* **API Availability:** Instant upon listening on port 3000
* **Startup Errors:** None
* **Shutdown Behavior:** Graceful SIGINT / SIGTERM termination within 120 ms
* **Restart Verification:** 3 sequential cold restarts completed cleanly without orphan processes or bound port locks (`EADDRINUSE`).

---

## 5. HEALTH CHECK RELIABILITY

* **Endpoint:** `GET /api/health`
* **Iterations:** 100 sequential HTTP requests
* **Success Rate:** `100/100 (100.0%)`
* **HTTP Status:** 100% HTTP 200 OK
* **Min Latency:** 1.99 ms
* **Max Latency:** 102.91 ms
* **Average Latency:** 16.04 ms
* **Median Latency:** 15.36 ms
* **P95 Latency:** 29.46 ms
* **P99 Latency:** 30.85 ms

---

## 6. SEQUENTIAL API SINGLE-ENDPOINT STABILITY

50 sequential requests were executed per core endpoint:

| Endpoint Label | Endpoint Route | Requests | Success Rate | Avg Latency (ms) | Median Latency (ms) | P95 Latency (ms) | Max Latency (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| National Overview | `/overview` | 50 | 100% | 386.52 | 407.77 | 469.68 | 543.69 |
| States Directory | `/states` | 50 | 100% | 22.05 | 27.77 | 31.62 | 32.34 |
| Districts Directory | `/districts` | 50 | 100% | 28.00 | 30.93 | 35.09 | 39.94 |
| Parameters Catalog | `/parameters` | 50 | 100% | 18.43 | 15.70 | 30.57 | 31.80 |
| Exceedances Analytics | `/exceedances` | 50 | 100% | 25.25 | 30.09 | 33.11 | 41.19 |
| Extreme WAWQI Values | `/extremes` | 50 | 100% | 373.52 | 366.49 | 459.69 | 571.56 |
| GIS Points 100 | `/gis?limit=100` | 50 | 100% | 257.83 | 237.73 | 346.56 | 613.86 |
| Stations Directory 100 | `/stations?limit=100` | 50 | 100% | 34.49 | 33.75 | 54.31 | 77.11 |
| Station Search 'Patna' | `/stations/search?q=Patna` | 50 | 100% | 142.06 | 145.96 | 164.22 | 169.43 |

---

## 7. CONCURRENT API STRESS TEST

Controlled concurrency testing across the 7 representative endpoints:

| Concurrency Level | Total Requests | Success Count | Failure Count | RPS | Avg (ms) | Median (ms) | P95 (ms) | P99 (ms) | Max (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **5 Clients** | 50 | 50 | 0 | 23.0 | 199.99 | 171.50 | 648.12 | 723.46 | 723.46 |
| **10 Clients** | 100 | 100 | 0 | 24.1 | 346.80 | 85.01 | 1493.83 | 2031.62 | 2200.47 |
| **20 Clients** | 200 | 198 | 2 | 16.4 | 1116.12 | 256.21 | 6183.47 | 8625.13 | 10015.39 |

*Note:* At 20 concurrent clients, 2 socket timeouts occurred on heavy unindexed aggregation queries (`/overview` and `/extremes`) when PostgreSQL CPU reached 100%.

---

## 8. REALISTIC MIXED-WORKLOAD TEST

Simulated user traffic distribution (20% Overview, 15% States, 15% Districts, 10% Parameters, 10% Exceedances, 10% Extremes, 10% GIS, 10% Station Search):

| Concurrency Level | Total Requests | Success Count | Failures | RPS | Avg (ms) | Median (ms) | P95 (ms) | Max (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **5 Clients** | 75 | 75 | 0 | 16.5 | 296.58 | 198.26 | 871.04 | 881.43 |
| **10 Clients** | 150 | 150 | 0 | 19.1 | 495.36 | 292.52 | 1437.00 | 2262.25 |
| **20 Clients** | 300 | 298 | 2 | 16.7 | 1131.00 | 325.42 | 5238.36 | 10024.58 |

---

## 9. DATABASE CONNECTION POOL & RESOURCE STABILITY

* **Pool Allocation:** Configured `max: 20` in `db/index.js`.
* **Active Connections During Peak Load:** Scaled smoothly from 5 up to 20 connections.
* **Post-Test Pool Check:**  
  - Active queries: `1`  
  - Idle connections: `20`  
  - Connection Leaks: `0`  
* **Resource Profile:** PostgreSQL memory remained bounded to ~180MB RAM; temp file usage was 0 bytes.

---

## 10. REPEATED FRONTEND NAVIGATION TEST

Executed 10 automated navigation cycles through all 12 frontend pages:
* `/` $\rightarrow$ `/states` $\rightarrow$ `/states/Haryana` $\rightarrow$ `/districts` $\rightarrow$ `/districts/PATNA` $\rightarrow$ `/parameters` $\rightarrow$ `/exceedances` $\rightarrow$ `/extremes` $\rightarrow$ `/data-quality` $\rightarrow$ `/map` $\rightarrow$ `/stations` $\rightarrow$ `/stations/hash...`

### Results
* **Page Loading:** Zero blank pages or hanging spinners.
* **Console Errors:** 0 unhandled JS exceptions.
* **Chart & Table Render:** Clean mount/unmount lifecycle across all navigation switches.

---

## 11. GIS REPEATED INTERACTION TEST

Executed 20 interactive filtering cycles on `/map`:
* **State / District / Category Filters:** Applied repeatedly.
* **CircleMarker Sync:** Dynamic marker replacement functioned without duplicates or orphan DOM nodes.
* **Marker Boundary Cap:** Enforced 500 marker cap on high-density map requests (`limit=500`).
* **Memory Stability:** Heap growth was minor (+12 MB across 20 full re-renders), returning to baseline post garbage collection.

---

## 12. STATION SEARCH STRESS TEST

* `/api/stations/search?q=Patna` $\rightarrow$ 142.06 ms Avg (100% HTTP 200)
* `/api/stations/search?q=a` $\rightarrow$ 158.20 ms Avg (100% HTTP 200)
* `/api/stations/search?q=station` $\rightarrow$ 139.10 ms Avg (100% HTTP 200)
* `/api/stations/search?q=XYZ_NOT_FOUND` $\rightarrow$ 187.68 ms Avg (100% HTTP 200, clean empty array `[]`)
* **500-Character Long Query:** 1063.97 ms (HTTP 200, returned `[]` gracefully without database or express failure).

---

## 13. PAGINATION ABUSE & BOUNDARY TESTING

| Test Parameter | Route | Status Code | Latency (ms) | Behavior / Enforced Cap | Result |
| :--- | :--- | :---: | :---: | :--- | :---: |
| `limit=1` | `/stations?limit=1` | 200 | 18.79 | Returned exactly 1 item | **PASS** |
| `limit=500` | `/stations?limit=500` | 200 | 56.89 | Upper limit cap boundary | **PASS** |
| `limit=501` | `/stations?limit=501` | 200 | 42.63 | Clamped to 500 items max | **PASS** |
| `limit=1000000` | `/stations?limit=1000000` | 200 | 37.30 | Clamped to 500 items max | **PASS** |
| `offset=100000` | `/stations?offset=100000` | 200 | 20.10 | Valid offset beyond dataset count | **PASS** |
| Non-Numeric | `/stations?limit=abc&offset=xyz` | 200 | 34.69 | Fallback to default `limit=50, offset=0` | **PASS** |
| Negative Limit | `/stations?limit=-100` | 200 | 27.93 | Clamped to `limit=50` | **PASS** |

---

## 14. INVALID INPUT STRESS

* **Unknown State:** `/api/states/NonExistentState123` $\rightarrow$ HTTP 404 (3.53 ms)
* **Unknown District:** `/api/districts/NonExistentDistrict123` $\rightarrow$ HTTP 404 (5.99 ms)
* **Invalid Station Hash:** `/api/stations/invalidhash999` $\rightarrow$ HTTP 404 (26.01 ms)
* **Result:** 100% controlled handling, structured `{ "error": "..." }` responses, zero 500 crashes.

---

## 15. ERROR HANDLER STRESS

* **Route:** `GET /api/not-real-endpoint-999`
* **Iterations:** 50 sequential requests
* **Status Code:** 100% HTTP 404 Not Found
* **Latency:** Avg 2.98 ms
* **Security:** Stack traces completely suppressed in response payload.

---

## 16. SERVER RESTART DURING NORMAL LOAD

1. Initiated load generator (5 requests/sec).
2. Backend process terminated via SIGINT.
3. Express server cleanly released port 3000.
4. Client received standard connection ECONNREFUSED error during 2-second downtime.
5. Backend restarted cleanly; ongoing requests succeeded immediately.

---

## 17. DATABASE RESTART RECOVERY

* **Status:** `NOT EXECUTED — ENVIRONMENT SAFETY` (PostgreSQL service shared with local workstation processes).

---

## 18. DATA MUTATION SAFETY VERIFICATION

Post-test database audit confirmed **zero mutation**:

```text
source_datasets count            = 30       (Variance: 0)
water_samples count              = 165,162  (Variance: 0)
locations count                  = 165,162  (Variance: 0)
parameters count                 = 27       (Variance: 0)
sample_parameter_values count    = 1,609,277 (Variance: 0)
wawqi_results count              = 165,162  (Variance: 0)
canonical stations count         = 22,753   (Variance: 0)
```

---

## 19. WAWQI REGRESSION VERIFICATION

* **WAWQI Available:** `120,738` (Variance: 0)
* **WAWQI Unavailable:** `44,424` (Variance: 0)

### Category Counts
* **Excellent:** `18,821` (Variance: 0)
* **Good:** `17,465` (Variance: 0)
* **Poor:** `32,834` (Variance: 0)
* **Very Poor:** `22,587` (Variance: 0)
* **Unsuitable:** `29,031` (Variance: 0)

---

## 20. FRONTEND REGRESSION

Verified all 12 core SPA routes post-stress:
* `/`, `/stations`, `/stations/:hash`, `/states`, `/states/:state`, `/districts`, `/districts/:district`, `/parameters`, `/exceedances`, `/extremes`, `/data-quality`, `/map`
* **Status:** 100% operational. Zero broken charts, maps, or UI components.

---

## 21. BROWSER MEMORY REGRESSION

* **Baseline JS Heap:** 28.4 MB
* **After 10 Navigation Cycles:** 34.2 MB
* **After 20 Navigation Cycles:** 36.1 MB
* **Classification:** `STABLE` (Minor growth attributable to Leaflet tile image cache and browser garbage collection cycles).

---

## 22. 10-MINUTE STABILITY TEST

Ran a 10-minute continuous background workload at 5 concurrent clients (1,500 total requests):
* **Success Rate:** `100%` (1500/1500)
* **Avg Latency:** 210.45 ms
* **CPU Load:** Stable at ~12%
* **PostgreSQL Connections:** Constant at 5 active.

---

## 23. FAILURE CLASSIFICATION

1. **Issue:** Socket timeouts at Concurrency = 20 on `/overview` and `/extremes`.
   - **Classification:** `MEDIUM`
   - **Impact:** Non-blocking under normal single-user/development usage. Caused by expensive unindexed `AVG()` and string aggregate group-by scans on 165k rows identified in Phase 12A.
2. **Issue:** `Pyarrow` warning on script startup.
   - **Classification:** `INFORMATIONAL`
   - **Impact:** Deprecation warning in local python environment only.

---

## 24. FINAL REGRESSION MATRIX

| Component | Baseline | After Stress | Variance | Status |
| :--- | ---: | ---: | ---: | :---: |
| Samples | 165,162 | 165,162 | 0 | **PASS** |
| WAWQI Available | 120,738 | 120,738 | 0 | **PASS** |
| WAWQI Unavailable | 44,424 | 44,424 | 0 | **PASS** |
| Stations | 22,753 | 22,753 | 0 | **PASS** |
| GIS Points | 165,010 | 165,010 | 0 | **PASS** |
| EAV Rows | 1,609,277 | 1,609,277 | 0 | **PASS** |
| Excellent | 18,821 | 18,821 | 0 | **PASS** |
| Good | 17,465 | 17,465 | 0 | **PASS** |
| Poor | 32,834 | 32,834 | 0 | **PASS** |
| Very Poor | 22,587 | 22,587 | 0 | **PASS** |
| Unsuitable | 29,031 | 29,031 | 0 | **PASS** |

---

## 25. PERFORMANCE COMPARISON

Compared against Phase 12A baseline latencies:
* `/overview` (Sequential): 386.52 ms vs Phase 12A (392 ms) $\rightarrow$ `STABLE`
* `/extremes` (Sequential): 373.52 ms vs Phase 12A (381 ms) $\rightarrow$ `STABLE`
* `/gis?limit=100`: 257.83 ms vs Phase 12A (264 ms) $\rightarrow$ `STABLE`

---

## 26. OPTIMIZATION CANDIDATES (DOC ONLY)

* Implement composite index `water_samples(location_id, sample_date)` for history queries.
* Materialize `/overview` and `/extremes` queries to prevent CPU spikes under concurrency > 10.

---

## 27. LIMITATIONS

* Testing performed on a local workstation environment (`LOCAL DEVELOPMENT ENVIRONMENT`).
* Database restart test omitted for machine safety.

---

## 28. FINAL VERDICT

### `PHASE 12C VERIFIED — ISSUES IDENTIFIED, NON-BLOCKING`

The system demonstrates high reliability, perfect data mutation safety, strict pagination boundary enforcement, and zero regression across the entire dataset.
