# POSTGRESQL DATA DICTIONARY

## Groundwater Quality Intelligence — WAWQI Analytics Platform

> PostgreSQL schema reference covering the 6 persistent project tables (`source_datasets`, `locations`, `parameters`, `water_samples`, `sample_parameter_values`, `wawqi_results`) and analytical views.

---

## 1. PERSISTENT BASE TABLES

### 1.1 `source_datasets`
* **Purpose:** Stores provenance and metadata for ingested CGWB raw CSV files.
* **Row Count:** 30

| Column | Data Type | Nullable | Description |
| :--- | :--- | :---: | :--- |
| `dataset_id` | `INTEGER` | NO | Primary key (Auto-incrementing ID) |
| `state_name` | `VARCHAR(100)` | NO | Name of Indian State or Union Territory |
| `file_name` | `VARCHAR(255)` | NO | Original raw CSV filename |
| `ingested_at` | `TIMESTAMP` | NO | Timestamp of ETL ingestion |
| `total_records` | `INTEGER` | NO | Total raw rows present in source file |

---

### 1.2 `locations`
* **Purpose:** Stores spatial coordinates and administrative hierarchy for sampling points.
* **Row Count:** 165,162

| Column | Data Type | Nullable | Description |
| :--- | :--- | :---: | :--- |
| `location_id` | `INTEGER` | NO | Primary key |
| `state_name` | `VARCHAR(100)` | NO | Standardized state name |
| `district_name` | `VARCHAR(100)` | NO | Standardized district name |
| `block_name` | `VARCHAR(100)` | YES | Sub-district / block name |
| `location_name` | `VARCHAR(255)` | NO | Station / village location description |
| `latitude` | `NUMERIC(10,6)` | YES | WGS84 Latitude coordinate |
| `longitude` | `NUMERIC(10,6)` | YES | WGS84 Longitude coordinate |

---

### 1.3 `parameters`
* **Purpose:** Master catalog of water quality chemical parameters and BIS limits.
* **Row Count:** 27

| Column | Data Type | Nullable | Description |
| :--- | :--- | :---: | :--- |
| `parameter_id` | `INTEGER` | NO | Primary key |
| `parameter_code` | `VARCHAR(20)` | NO | Canonical chemical symbol / code (e.g., `PH`, `CL`, `NO3`) |
| `parameter_name` | `VARCHAR(100)` | NO | Full parameter title |
| `unit` | `VARCHAR(20)` | NO | Standardized unit of measure (e.g., `mg/L`, `pH units`) |
| `bis_standard` | `NUMERIC(10,3)` | YES | BIS IS 10500:2012 Acceptable Limit ($S_i$) |
| `bis_permissible` | `NUMERIC(10,3)` | YES | BIS IS 10500:2012 Permissible Limit |
| `is_wawqi_core` | `BOOLEAN` | NO | `TRUE` if core parameter for WAWQI calculation |

---

### 1.4 `water_samples`
* **Purpose:** Core sampling events representing individual groundwater measurements.
* **Row Count:** 165,162

| Column | Data Type | Nullable | Description |
| :--- | :--- | :---: | :--- |
| `sample_id` | `INTEGER` | NO | Primary key |
| `location_id` | `INTEGER` | NO | Foreign key referencing `locations.location_id` |
| `dataset_id` | `INTEGER` | NO | Foreign key referencing `source_datasets.dataset_id` |
| `sample_date` | `DATE` | YES | Date of water sample collection |
| `station_hash` | `VARCHAR(64)` | NO | Canonical station hash identifier |

---

### 1.5 `sample_parameter_values`
* **Purpose:** EAV observation table storing measured parameter values for each sample.
* **Row Count:** 1,609,277

| Column | Data Type | Nullable | Description |
| :--- | :--- | :---: | :--- |
| `value_id` | `BIGINT` | NO | Primary key |
| `sample_id` | `INTEGER` | NO | Foreign key referencing `water_samples.sample_id` |
| `parameter_id` | `INTEGER` | NO | Foreign key referencing `parameters.parameter_id` |
| `numeric_value` | `NUMERIC(12,4)` | YES | Measured chemical concentration value |

---

### 1.6 `wawqi_results`
* **Purpose:** Computations, scores, categories, and sub-indices derived by the WAWQI engine.
* **Row Count:** 165,162

| Column | Data Type | Nullable | Description |
| :--- | :--- | :---: | :--- |
| `sample_id` | `INTEGER` | NO | Primary key & FK referencing `water_samples.sample_id` |
| `wqi` | `NUMERIC(12,4)` | YES | Calculated WAWQI score |
| `valid_parameter_count` | `INTEGER` | NO | Number of valid core parameters available |
| `parameters_used` | `TEXT[]` | YES | Array of parameter codes utilized |
| `calculation_status` | `VARCHAR(50)` | NO | `SUCCESS` or `INSUFFICIENT_PARAMETER_COVERAGE` |
| `data_quality_flags` | `JSONB` | YES | Anomaly warnings and data quality notes |
| `parameter_sub_indices` | `JSONB` | YES | Individual $q_i$ and $w_i$ sub-index breakdown |

---

## 2. KEY ANALYTICAL & MATERIALIZED VIEWS

* **`mv_station_identity` (22,753 rows):** Groups 165,162 samples into canonical stations based on latitude/longitude proximity and station name.
* **`mv_wawqi_state_summary` (30 rows):** Aggregates state-level sample counts, mean WQI, category breakdown, and unsuitable percentages.
* **`mv_wawqi_district_summary` (584 rows):** District-level risk metrics and contamination rankings.
* **`vw_gis_points` (165,010 rows):** Filters valid coordinates ($6.0 \le \text{lat} \le 37.5$, $68.0 \le \text{lon} \le 97.5$) for spatial GIS map rendering.
