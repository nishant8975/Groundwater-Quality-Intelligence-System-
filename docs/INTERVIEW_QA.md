# TECHNICAL INTERVIEW PREPARATION & QUESTIONS

## Groundwater Quality Intelligence — WAWQI Analytics Platform

---

## 1. DATA ARCHITECTURE & DATABASE DESIGN

### Q1: Why did you choose an Entity-Attribute-Value (EAV) schema instead of a single wide table?
**Answer:**  
In groundwater datasets across 30 states, parameter coverage is sparse and heterogeneous. A single wide table with 27 parameter columns would result in millions of empty/NULL cells, high storage bloat, and rigid schema alteration whenever a new parameter is monitored. The EAV model (`sample_parameter_values`) allows dynamic parameter storage per sample, storing 1,609,277 actual measured values efficiently without schema changes.

### Q2: How did you optimize query performance on an EAV schema?
**Answer:**  
EAV queries require joins or aggregations. We created 8 PostgreSQL materialized views (e.g., `mv_station_identity`, `mv_wawqi_state_summary`, `mv_wawqi_district_summary`) and 6 standard views (`vw_gis_points`). These materialized pre-aggregated state, district, and station metrics, reducing API query execution times from $> 500 \text{ ms}$ to $< 35 \text{ ms}$.

---

## 2. WAWQI METHODOLOGY & SCIENTIFIC DATA ENGINEERING

### Q3: How is the Weighted Arithmetic Water Quality Index (WAWQI) calculated?
**Answer:**  
WAWQI is computed as $\text{WAWQI} = \frac{\sum w_i q_i}{\sum w_i}$, where $q_i$ is the quality rating for parameter $i$ relative to its BIS IS 10500:2012 acceptable limit ($S_i$), and $w_i = K / S_i$ is the unit weight ($K = 1 / \sum (1/S_i)$). We evaluate 7 core parameters (pH, Cl, SO4, Hardness, Ca, Mg, Fe) and 2 conditional heavy metals (As, U).

### Q4: How did you handle samples with missing parameters?
**Answer:**  
If a sample contains fewer than 6 core parameters, computing WAWQI would produce biased weights. Rather than setting missing values to zero (which distorts chemistry), our engine flags the sample status as `INSUFFICIENT_PARAMETER_COVERAGE` and sets WQI to `NULL`. This resulted in 120,738 available WAWQI scores and 44,424 explicitly flagged unavailable samples.

### Q5: Did you clamp or clip extreme WQI values?
**Answer:**  
No. Clamping extreme WQI values ($> 100$) hides severe contamination hotspots. We preserved unclamped WQI values (up to WQI $> 8,000,000$) while attaching JSONB data quality flags to inform users of source-level anomalies (such as Sample 1419 with Uranium 450 mg/L).

---

## 3. REST API & FRONTEND PERFORMANCE

### Q6: How did you ensure REST API security and resource protection?
**Answer:**  
All 18 Express REST endpoints use 100% parameterized SQL queries (`$1`, `$2`), eliminating SQL injection. Pagination limit parameters are capped at `500` max items to prevent memory exhaustion, and zero database passwords or secrets are committed in source code (`.env` is git-ignored).

### Q7: Why is the Vite production frontend build so small (44.31 KB)?
**Answer:**  
We leveraged tree-shaking, modular component design, and dynamic import bundling in Vite. By avoiding heavy monolithic UI frameworks and utilizing light icon sets (Lucide React) and targeted chart primitives (Recharts), the compiled production JS bundle is only 4.39 KB raw (1.94 KB gzip).

---

## 4. GIS & SYSTEM LIMITATIONS

### Q8: How did you handle spatial mapping of 165,000 locations without browser lagging?
**Answer:**  
Rendering 165,000 SVG elements simultaneously crashes browser DOM layout engines. We implemented a bounded GIS architecture: `vw_gis_points` filters valid geographic points (165,010 valid), and the Leaflet map bounds simultaneous CircleMarker rendering to 500 markers per query page. Users query the entire dataset across state/district filters seamlessly.

### Q9: What are the main system limitations?
**Answer:**  
At concurrency $> 10$ simultaneous heavy analytical queries (`/overview` + `/extremes`), PostgreSQL CPU reaches 100% on unindexed sequential group-by scans, leading to occasional client timeouts. This is documented as technical debt requiring future query materialization.
