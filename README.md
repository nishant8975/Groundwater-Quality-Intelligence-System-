# Groundwater Quality Intelligence — WAWQI Analytics Platform

> **A Data-Driven Environmental Decision Support System for Multi-State Groundwater Quality Monitoring in India**

---

## OVERVIEW

**Groundwater Quality Intelligence — WAWQI Analytics Platform** is a web-based analytical platform designed to ingest, normalize, and evaluate complex multi-state groundwater quality data from Central Ground Water Board (CGWB) datasets across India.

The platform calculates a mathematically validated **Weighted Arithmetic Water Quality Index (WAWQI)** based on Bureau of Indian Standards (BIS IS 10500:2012) drinking water specifications, enabling researchers, environmental decision-makers, and policymakers to identify contamination hotspots, track temporal quality shifts, evaluate station-level compliance, and explore geographic risk distributions via an interactive GIS mapping interface.

---

## PROBLEM STATEMENT

Groundwater quality data collected across Indian States and Union Territories (UTs) is highly heterogeneous:
* Variable parameter coverage across sampling stations.
* Inconsistent reporting units, missing coordinates, and non-standard parameter naming conventions.
* Raw parameter measurements (e.g., pH, Nitrates, Fluoride, Heavy Metals) are difficult to interpret collectively without a unified scientific quality metric.
* Decision-makers lack state-aware, GIS-integrated analytics tools to pinpoint critical risk districts and canonical monitoring stations requiring urgent intervention.

---

## SYSTEM OBJECTIVES

1. **Multi-State Ingestion & Normalization:** Ingest 30 State/UT raw CSV datasets (~165,162 water samples across 27 canonical parameters) preserving raw data immutability and provenance.
2. **Validated WAWQI Engine:** Execute a scientific WAWQI algorithm employing 7 core parameters (pH, Cl, SO4, Hardness, Ca, Mg, Fe) and 2 conditional heavy-metal parameters (As, U) with dynamic weight calculation.
3. **Data Quality & Transparency:** Explicitly distinguish valid sample data from missing parameter coverage, coordinates errors, or extreme source-level anomalies.
4. **Interactive GIS Intelligence:** Map 165,010 valid coordinate locations onto an interactive Leaflet GIS interface with bounded rendering for performance optimization.
5. **Station Intelligence:** Group physical sampling records into 22,753 canonical station identities, classifying them into `DATA RICH` ($\ge 5$ parameters) and `DATA LIMITED` ($< 5$ parameters) tiers.
6. **High-Performance REST API & SPA Dashboard:** Expose 18 RESTful endpoints powering a React + TypeScript single-page application with rich charts, data tables, and URL-synchronized state filtering.

---

## VERIFIED DATASET BASELINE

All data metrics have been reconciled with **0 variance** across all platform layers:

| Entity / Metric | Quantity | Description / Scope |
| :--- | ---: | :--- |
| **Raw Datasets** | `30` | State/UT CGWB Groundwater Quality CSV Files |
| **Water Samples** | `165,162` | Immutably stored individual sampling records |
| **Location Records** | `165,162` | Geographic and administrative location entries |
| **Canonical Parameters** | `27` | Standardized water-chemistry parameters |
| **EAV Parameter Rows** | `1,609,277` | Individual chemical observation records |
| **WAWQI Available** | `120,738` | Samples with $\ge 6$ core parameters required for WAWQI |
| **WAWQI Unavailable** | `44,424` | Samples flagged `INSUFFICIENT_PARAMETER_COVERAGE` |
| **Canonical Stations** | `22,753` | Normalized unique physical monitoring stations |
| **Valid GIS Locations** | `165,010` | Valid coordinates ($6.0 \le \text{lat} \le 37.5$, $68.0 \le \text{lon} \le 97.5$) |
| **Invalid Coordinates** | `152` | Excluded coordinates outside India boundaries |

### WAWQI Quality Category Distribution
* **Excellent (0 $\le$ WQI $\le$ 25):** `18,821` (15.59%)
* **Good (26 $\le$ WQI $\le$ 50):** `17,465` (14.47%)
* **Poor (51 $\le$ WQI $\le$ 75):** `32,834` (27.19%)
* **Very Poor (76 $\le$ WQI $\le$ 100):** `22,587` (18.71%)
* **Unsuitable (WQI > 100):** `29,031` (24.04%)

---

## SYSTEM ARCHITECTURE

```text
  Raw CGWB CSV Files (30 Datasets)
                 │
                 ▼
     Python Data Engineering ETL
                 │
                 ▼
       PostgreSQL 15+ Database
  (Base Tables + Materialized Views)
                 │
                 ▼
     Express.js Node.js REST API
                 │
                 ▼
      React 18 + TypeScript + Vite
                 │
   ┌─────────────┼─────────────┐
   ▼             ▼             ▼
Dashboard       GIS         Station
 Analytics     Map       Intelligence
```

---

## TECHNOLOGY STACK

* **Database & Data Warehouse:** PostgreSQL 15+ (Relational EAV schema covering 6 persistent project tables, 6 views, 8 materialized views)
* **Backend API Server:** Node.js (v22), Express.js (^5.2.1), `pg` connection pool
* **Frontend Web Application:** React (v18.3), TypeScript (v5.5), Vite (v8.3), TailwindCSS (v3.4), Lucide React
* **Data Visualization & GIS:** Recharts (^2.12), Leaflet (^1.9), React-Leaflet (^4.2), CartoDB Dark Matter tiles
* **Data Engineering & Science:** Python (3.12), Pandas, Psycopg2

---

## KEY FEATURES

* **National & State Analytics:** Real-time state and district quality rankings, parameter exceedances, and category distributions.
* **Parameter Exceedance Explorer:** Interactive comparison of measured chemical concentrations against BIS IS 10500:2012 acceptable and permissible limits.
* **GIS Spatial Intelligence:** Interactive dark-mode map visualizing monitoring locations with custom color-coded category markers, popup info, and district boundary filtering.
* **Canonical Station Intelligence:** Explorer for 22,753 stations providing temporal quality timelines, dominant contamination parameter identification, and data richness tiers.
* **Extreme Value & Data Quality Audit:** Full transparency for extreme WQI values (unclamped up to WQI $> 8,000,000$) with source anomaly warning flags.

---

## WAWQI METHODOLOGY

The Weighted Arithmetic Water Quality Index is calculated as:
$$\text{WAWQI} = \frac{\sum_{i=1}^{n} w_i \cdot q_i}{\sum_{i=1}^{n} w_i}$$

Where:
* $q_i = \left( \frac{V_i - V_{ideal}}{S_i - V_{ideal}} \right) \cdot 100$ (Quality Rating for parameter $i$)
* $w_i = \frac{K}{S_i}$ (Unit Weight, where $K = \frac{1}{\sum (1 / S_i)}$)
* $S_i$: BIS IS 10500:2012 Acceptable Limit
* $V_{ideal}$: 7.0 for pH, 0.0 for chemical parameters

*Detailed scientific documentation is available in [`docs/WAWQI_METHODOLOGY.md`](file:///d:/PwC/Groundwater%20Quality%20Intelligence%20System/docs/WAWQI_METHODOLOGY.md).*

---

## PERFORMANCE & MEASURED TELEMETRY

* **Backend Sequential Latency:** Fast endpoints (`/states`, `/districts`, `/parameters`) execute in $< 35 \text{ ms}$; complex analytics (`/overview`, `/extremes`) respond in $180 - 380 \text{ ms}$.
* **Frontend Production Build:** Compiled with Vite in **738 ms**. Bundle size totals **44.31 KB raw / 21.56 KB gzip** (total JS output is 4.39 KB raw).
* **Browser Memory:** JS Heap remains stable at **28.4 MB – 36.1 MB** across 20 continuous navigation cycles.
* **Reliability:** 100% success rate across 100 health requests and 1,500 continuous 10-minute stability test requests.

---

## DOCUMENTED SYSTEM LIMITATIONS

1. **Concurrency Limitation:** Materialization/caching of `/overview` and `/extremes` is a future optimization for higher-concurrency workloads. Stress testing achieved 198/200 successful requests at 20 concurrent clients, with 2 timeouts observed during the test.
2. **GIS Rendering Boundary:** Leaflet map bounds simultaneous CircleMarker rendering to 500 points per query page to preserve 60 FPS browser rendering performance.
3. **Deployment Scope:** System is verified for Academic Research, Executive Demonstration, Local Analytical Workstations, and Single-Tenant Deployments.

---

## QUICK START & SETUP

### Prerequisites
* **Node.js:** v18+ (Recommended v22)
* **PostgreSQL:** v15+ (Running on localhost:5432)
* **Python:** v3.10+ (For data pipeline execution)

### 1. Database Setup
```bash
# Create PostgreSQL database
createdb -U postgres groundwater_quality

# Execute DDL schema and views
psql -U postgres -d groundwater_quality -f sql/01_schema.sql
psql -U postgres -d groundwater_quality -f sql/02_views.sql
psql -U postgres -d groundwater_quality -f sql/03_materialized_views.sql
psql -U postgres -d groundwater_quality -f sql/04_station_intelligence.sql
```

### 2. Backend API Setup
```bash
cd backend
npm install
cp .env.example .env
npm start
# Server running at http://localhost:3000
```

### 3. Frontend Application Setup
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
# Dashboard accessible at http://localhost:5173
```

---

## DOCUMENTATION INDEX

All detailed documentation is located in the [`docs/`](file:///d:/PwC/Groundwater%20Quality%20Intelligence%20System/docs/) directory:
* [`SETUP_GUIDE.md`](file:///d:/PwC/Groundwater%20Quality%20Intelligence%20System/docs/SETUP_GUIDE.md) — Step-by-step installation instructions.
* [`ARCHITECTURE.md`](file:///d:/PwC/Groundwater%20Quality%20Intelligence%20System/docs/ARCHITECTURE.md) — Full technical architecture and data flow.
* [`DATA_DICTIONARY.md`](file:///d:/PwC/Groundwater%20Quality%20Intelligence%20System/docs/DATA_DICTIONARY.md) — PostgreSQL schema reference covering the 6 persistent project tables and analytical views.
* [`WAWQI_METHODOLOGY.md`](file:///d:/PwC/Groundwater%20Quality%20Intelligence%20System/docs/WAWQI_METHODOLOGY.md) — Scientific formulas and BIS standards.
* [`API.md`](file:///d:/PwC/Groundwater%20Quality%20Intelligence%20System/docs/API.md) — Complete REST API route specifications.
* [`GIS_INTELLIGENCE.md`](file:///d:/PwC/Groundwater%20Quality%20Intelligence%20System/docs/GIS_INTELLIGENCE.md) — Spatial mapping design and rendering rules.
* [`PERFORMANCE_AND_LIMITATIONS.md`](file:///d:/PwC/Groundwater%20Quality%20Intelligence%20System/docs/PERFORMANCE_AND_LIMITATIONS.md) — Measured performance telemetry.
* [`TECHNICAL_DEBT.md`](file:///d:/PwC/Groundwater%20Quality%20Intelligence%20System/docs/TECHNICAL_DEBT.md) — Non-blocking optimization candidates.
* [`DEMO_CHECKLIST.md`](file:///d:/PwC/Groundwater%20Quality%20Intelligence%20System/docs/DEMO_CHECKLIST.md) — 17-step presentation guide.

---

## LICENSE

No license declared. All source datasets remain subject to original Central Ground Water Board (CGWB) government open-data terms.
