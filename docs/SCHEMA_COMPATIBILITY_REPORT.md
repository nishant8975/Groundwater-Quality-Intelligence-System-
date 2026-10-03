# Schema Compatibility Report

## Overview
This report verifies that the proposed canonical data model (`sql/01_schema.sql`) can correctly represent all critical source structures discovered in Phase 1 across all 30 state/UT datasets.

## Findings by Category

### Geographic Fields Supported
- The schema includes `state`, `state_lgd_code`, `district`, `district_lgd_code`, `tehsil`, `block`, `village`, `station_name`, and `agency`.
- **Compatibility:** **100%**. All datasets map cleanly into these hierarchical buckets. For datasets missing `block` or `tehsil`, the values will remain `NULL` without breaking the schema.

### Date Fields Supported
- The schema includes `sample_date` (DATE) and `raw_date_string` (VARCHAR).
- **Compatibility:** **100%**. By retaining the `raw_date_string`, we ensure no data loss occurs when a state dataset contains malformed or unparseable date formats.

### Station Identity Supported
- Station identity relies on geographic fields + `station_name`.
- **Compatibility:** **100%**. Station identity is currently deferred to ETL deduplication logic. The schema places no arbitrary uniqueness constraints on location rows, ensuring no records are prematurely discarded.

### Parameters Supported
- Parameters are mapped via an Entity-Attribute-Value (EAV) table (`sample_parameter_values`), storing `parameter_id`, `numeric_value`, and `raw_value_string`.
- **Compatibility:** **100%**. Because the model is vertical rather than horizontal (wide), new parameters unique to a single state (e.g., Uranium, Cadmium) do not require schema alterations. 

### Source Identifiers & Provenance
- `water_samples` includes `source_dataset_id` and `source_row_index`.
- `source_datasets` tracks `filename` and `ingestion_batch_id`.
- **Compatibility:** **100%**. Any computed sample or invalid row can be traced directly back to the exact line in the raw CSV.

### Special Fields
- Some datasets include `river`, `basin`, `tributary`, `subtributary`, etc. 
- **Compatibility:** **Partial Information Loss.** The current `locations` table does not have columns for river/basin. As noted in Phase 1 (Haryana analysis), these are frequently populated with placeholders (`-`). If river-based analytics become essential in Phase 5, these columns will need to be added to `locations`.

## Unresolved Source-Specific Fields
- State-specific arbitrary metadata (like unique state internal identifiers or lab names) are not currently tracked in the canonical schema.

## Conclusion
The schema successfully avoids "Haryana Bias" by using a generic, normalized observation model. No critical water-quality information, location data, or measurement timestamps will be silently lost during ingestion.
