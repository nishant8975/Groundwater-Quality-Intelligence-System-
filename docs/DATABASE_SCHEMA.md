# Canonical Database Schema

## Design Goals
- **Traceability:** Preserve the ability to trace any measurement back to its raw CSV file and row.
- **Flexibility (Sparse Data):** Use a normalized "Observation" model instead of a wide fact table to easily handle missing parameters and varying schema definitions across 30 states.
- **Data Quality Preservation:** Store raw values alongside parsed numeric values to identify placeholders without destroying the original context.
- **WAWQI Future-Proofing:** Support standard queries for sample parameters without hardcoding missing-data logic in the schema.

## Entity Relationship Model
```text
source_datasets
      | 1
      |
      | M
water_samples -------> locations
      | 1                   ^
      |                     |
      | M                   |
sample_parameter_values     |
      | M                   |
      |                     |
      | 1                   |
parameters -----------------+
```

## Table Descriptions

### 1. `source_datasets`
Records metadata for each parsed CSV file.
- `dataset_id` (PK)
- `filename`: Raw CSV filename.
- `row_count`: For ETL reconciliation.
- `ingestion_batch_id`: For tracking ETL batches.

### 2. `locations`
Records geographic station identities.
- `location_id` (PK)
- `state`, `district`, `tehsil`, `block`, `village`, `station_name`: The geographic hierarchy.
- `latitude`, `longitude`: Numeric coordinates.
- `coordinate_validity_flag`: Pre-calculated validation flag (e.g., Lat: 6-38).

### 3. `parameters`
The canonical parameter dictionary (e.g., pH, EC, Arsenic).
- `parameter_id` (PK)
- `canonical_name`: Standardized internal name (e.g., 'electric_conductivity').
- `display_name`: Human-readable name.

### 4. `water_samples`
Represents a single observation event (a row in the source file).
- `sample_id` (PK)
- `location_id` (FK -> locations)
- `source_dataset_id` (FK -> source_datasets)
- `source_row_index`: The exact 1-indexed line from the raw CSV.
- `sample_date`: Parsed DATE.
- `raw_date_string`: To preserve unparseable dates.

### 5. `sample_parameter_values`
The actual chemical measurements (Entity-Attribute-Value pattern).
- `sample_id` (PK, FK)
- `parameter_id` (PK, FK)
- `numeric_value`: Casted float value.
- `raw_value_string`: The uncasted string (e.g., "ND", "-").
- `is_placeholder`: Flag for known non-numeric placehoders.
- `is_missing`: Flag for empty cells.

## Sample Identity Strategy (Unresolved)
Phase 1 revealed that exact duplicate rows are rare, but it is unknown if `(station_name, sample_date)` constitutes a scientifically unique sample, because multiple depths or agencies might test the same spot on the same day. 
**Decision:** We are currently NOT enforcing a `UNIQUE(location_id, sample_date)` constraint. ETL deduplication rules remain a required human architectural decision before Phase 3.

## Parameter Storage Strategy
We chose a **Normalized Observation Model (Option B)** rather than a wide table (`pH`, `EC`, etc. as columns). The Phase 1 parameter matrix showed extreme sparsity (e.g., Fluoride missing entirely in some states). The EAV-style model allows us to easily add parameters, handle sparse data efficiently, and query parameter availability broadly.
