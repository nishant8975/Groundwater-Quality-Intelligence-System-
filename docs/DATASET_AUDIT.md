# Dataset Audit

## Executive Summary
Total files audited: 30
Total raw rows across files: 165162

## Dataset Inventory
- **Andaman Nicobar**: 634 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Andhra Pradesh**: 10950 rows, 46 columns, 118 invalid coords, 0 duplicates.
- **Arunachal Pradesh**: 104 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Assam**: 1874 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Bihar**: 3112 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Chandigarh**: 36 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Chhatisgarh**: 10350 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Dadra and nagar haveli**: 169 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Delhi**: 1169 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Goa**: 674 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Gujarat**: 9807 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Hariyana**: 7033 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Himachal Pradesh**: 1218 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Jammu and Kashmir**: 2894 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Jharkhand**: 1632 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Karnataka**: 13007 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Madhya Pradesh**: 19230 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **maharashtra**: 18249 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Meghalaya**: 235 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Nagaland**: 44 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Odisha**: 15400 rows, 46 columns, 1 invalid coords, 0 duplicates.
- **Panjab**: 5175 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Puducherry**: 83 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Rajasthan**: 12350 rows, 46 columns, 1 invalid coords, 0 duplicates.
- **Tamil Nadu**: 8419 rows, 46 columns, 22 invalid coords, 0 duplicates.
- **Telangana**: 5072 rows, 46 columns, 10 invalid coords, 0 duplicates.
- **Tripura**: 440 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Uttarakhand**: 903 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **Uttar Pradesh**: 7329 rows, 46 columns, 0 invalid coords, 0 duplicates.
- **West Bengal**: 7570 rows, 46 columns, 0 invalid coords, 0 duplicates.

## Schema Comparison
Columns vary widely between datasets. See `dataset_profile.json` for detailed schema differences.

## Parameter Availability Matrix
See `PARAMETER_AVAILABILITY_MATRIX.csv` for detailed valid observation counts per parameter per state.

## Haryana Validation
- Rows: 7033 (Expected: 7,033)
- Stations: 828 (Expected: 828)
- Districts: 22 (Expected: 22)
- Columns: 46 (Expected: 46)

## Important Findings
- Many placeholder values ('-', '0', 'ND') found in parameter columns.
- Coordinates have invalid entries (outside India bounds or missing).
- Parameters vary vastly in naming (e.g. EC vs Electric Conductivity).

## Phase 2 Implications
- Requires a flexible schema or a wide table approach.
- ETL must map standard parameters and normalize units.
- Missing value treatment must not treat '0' as missing blindly, but specific rules are needed per parameter.

## Open Questions
- What is the strict WAWQI missing-parameter policy?
- Which deduplication strategy should be applied?
