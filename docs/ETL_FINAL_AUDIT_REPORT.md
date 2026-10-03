# Phase 3 Final Audit Report

## 1. Duplicate Analysis
An active audit was performed against the `groundwater_quality` PostgreSQL database to identify duplicate parameters for the same physical sample (same station + date). 

**Query Results:**
- **Potential duplicate sample groups**: 2,896 groups of same `station_name` + `sample_date`.
- **Affected water samples**: 6,357 unique samples are involved in these duplicate groups.
- **Potential duplicate parameter observations**: 57,977 parameter records exist across 26,504 exact duplicate (station, date, parameter) groups.
- **Affected datasets**: Duplicates span across 25 of the 30 source datasets.

**Examples of Duplicate Groups:**
- Govindpur on 2016-05-25 (7 overlapping samples)
- Govindpur on 2015-05-25 (7 overlapping samples)
- Rampur on 2013-05-25 (7 overlapping samples)

**Provenance & Cardinality Validation:**
- **Source rows vs Water Samples**: 165,162 source rows perfectly map to 165,162 water samples (1-to-1).
- **Location Cardinality**: 165,162 location records created, containing 21,865 distinct `station_name` entities. The ETL intentionally creates 1 location record per source row to preserve exact original geography context (as same station name does not guarantee same physical coordinates without a proper ID).
- **Resolution**: Raw duplicates were intentionally loaded as-is to preserve data provenance. Deduplication/aggregation will occur dynamically in Phase 4 via BI-level SQL analysis.

## 2. Placeholder Analysis
The previous `Placeholders: 0` report accurately reflected the database state, but required clarification against Phase 1 profiling which noted `-`, `ND`, `NA`.

**Findings:**
- **Location of Placeholders in Raw Data**: The 3,804 instances of explicit placeholders (e.g., `-`, `ND`) identified during Phase 1 exist entirely within **metadata** columns (such as `River`, `Basin`, `Tributary`, `Subtributary`).
- **Water Quality Parameter Columns**: For the actual mapped water quality parameters (e.g., `ph`, `iron`, `nitrate`), missing values are represented exclusively as completely blank empty strings (`""`) in the source CSVs.
- **ETL Handling**: The canonical parameter schema uses a sparse Entity-Attribute-Value (EAV) model. Blank parameter measurements (`""`) are intentionally skipped during ingestion to prevent loading millions of meaningless `NULL` rows.
- **Conclusion**: Exactly 0 placeholders were inserted into the `sample_parameter_values` table because the mapped parameter columns did not contain explicit placeholder strings; they only contained empty blanks, which were natively skipped by the sparse ETL design. This respects the Phase 3 requirement to preserve raw data integrity while adhering to the sparse database model.

## 3. Non-Numeric Anomalies
The ETL successfully preserved edge-case string anomalies (e.g., multiple decimal points) as `NULL` in the `numeric_value` column while retaining the raw string in `raw_value_string` with an `INVALID_NUMERIC` flag.
Examples verified in DB:
- `Tamil_Nadu.csv`, Param: `ph`, Raw: `'7.47.75'`
- `Tamil_Nadu.csv`, Param: `alkalinity`, Raw: `'290.2575.4'`
