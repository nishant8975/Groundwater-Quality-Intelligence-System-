# ACADEMIC PROJECT REPORT CONTENT

## Groundwater Quality Intelligence — WAWQI Analytics Platform

---

## CHAPTER OUTLINE

### CHAPTER 1: INTRODUCTION
* **Background:** Groundwater as a vital drinking and agricultural resource in India.
* **Motivation:** The challenge of interpreting heterogeneous water-chemistry measurements across diverse geography.
* **Scope:** 30 Indian States/UTs, 165,162 water samples, 27 parameters, 22,753 canonical monitoring stations.

### CHAPTER 2: PROBLEM STATEMENT AND OBJECTIVES
* **Problem:** Fragmented data schemas, inconsistent reporting units, missing coordinates, and lack of integrated GIS decision support.
* **Objectives:** Build an end-to-end platform for data ingestion, WAWQI calculation, spatial GIS visualization, and station intelligence.

### CHAPTER 3: LITERATURE REVIEW AND WAWQI FORMULATION
* Review of Weighted Arithmetic Water Quality Index methodology.
* Bureau of Indian Standards (BIS IS 10500:2012) drinking water quality specifications.
* Dynamic unit weight calculation ($w_i = K / S_i$) and quality rating rating ($q_i$).

### CHAPTER 4: DATASET AUDIT AND PREPROCESSING
* Ingestion of 30 CGWB State/UT raw CSV files.
* Data quality audit: 165,162 total samples, 1,609,277 EAV parameter observation rows.
* Preservation of raw data immutability and audit provenance.

### CHAPTER 5: SYSTEM ARCHITECTURE
* 3-Tier Web Architecture: PostgreSQL Database $\rightarrow$ Express REST API $\rightarrow$ React SPA Frontend.
* Modular design separating data engineering, database views, backend REST routing, and UI components.

### CHAPTER 6: DATABASE DESIGN AND ETL PIPELINE
* Relational Entity-Attribute-Value (EAV) schema (`source_datasets`, `locations`, `parameters`, `water_samples`, `sample_parameter_values`, `wawqi_results`).
* Python ETL scripts (`01_ingest_cgwb.py`, `02_wawqi_engine.py`) and PostgreSQL materialized views.

### CHAPTER 7: WAWQI CALCULATION ENGINE
* Implementation details of 7 core parameters (pH, Cl, SO4, Hardness, Ca, Mg, Fe) and 2 conditional parameters (As, U).
* Dynamic weight allocation, minimum parameter threshold ($\ge 6$), and unclamped WQI score output.

### CHAPTER 8: ANALYTICS AND REST API
* Implementation of 18 RESTful endpoints.
* Parameterized SQL queries, pagination cap enforcement (500 max), and centralized error handling.

### CHAPTER 9: DASHBOARD, GIS, AND STATION INTELLIGENCE
* React + TypeScript SPA interface featuring state/district filters, parameter exceedance charts, and temporal station timelines.
* Leaflet GIS integration rendering 165,010 valid points with bounded 500-marker max rendering caps.
* Canonical station grouping (22,753 stations) into `DATA RICH` and `DATA LIMITED` tiers.

### CHAPTER 10: TESTING AND VALIDATION
* Phase 11 Full-System Reconciliation: 0 variance across all 12 platform entities and WAWQI category breakdown.
* Golden record traces from raw CSV to rendered UI components.

### CHAPTER 11: PERFORMANCE AND RELIABILITY AUDIT
* Phase 12 Telemetry: Fast routes $< 35 \text{ ms}$; Vite build 738 ms (44.31 KB output); JS heap 28 – 36 MB.
* 100% pass rate across 100 health requests and 1,500 continuous stability test requests.

### CHAPTER 12: RESULTS AND DISCUSSION
* National water quality findings: 24.04% Unsuitable, 18.71% Very Poor, 27.19% Poor, 14.47% Good, 15.59% Excellent.
* Primary contamination drivers identified: Nitrates, Fluoride, and Electrical Conductivity.

### CHAPTER 13: LIMITATIONS AND FUTURE WORK
* Concurrency limitations (> 10 clients) under unindexed analytical group-by queries.
* Technical debt roadmap: Composite station history index, Express Gzip compression, overview materialization.

### CHAPTER 14: CONCLUSION
* Summary of project achievements, scientific rigor, zero-variance data integrity, and readiness for research/demonstration.
