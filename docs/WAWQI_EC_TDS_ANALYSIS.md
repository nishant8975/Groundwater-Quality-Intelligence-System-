# WAWQI EC vs TDS Analysis

## Context
This analysis evaluates Electrical Conductivity (EC) and Total Dissolved Solids (TDS) as candidates for the Weighted Arithmetic Water Quality Index (WAWQI) to inform methodology decisions regarding double-counting salinity and parameter coverage.

## Statistical Findings (from 165,162 total samples)

- **Electrical Conductivity (EC):**
  - Numeric observations: 163,557
  - Coverage: 99.03%
  - Source Units: μS/cm (consistent across all datasets)
  - Canonical Units: μS/cm

- **Total Dissolved Solids (TDS):**
  - Numeric observations: 29,447
  - Coverage: 17.83%
  - Source Units: mg/L
  - Canonical Units: mg/L

- **Intersection Analysis:**
  - Samples with ONLY EC: 134,119
  - Samples with ONLY TDS: 9
  - Samples with BOTH EC and TDS: 29,438

- **Correlation (on the 29,438 common samples):**
  - Pearson Correlation: 0.9977
  - EC Mean: 1793.40 μS/cm
  - TDS Mean: 781.94 mg/L
  - *Note: TDS is generally ~0.55 to 0.70 of EC. The ratio here (781.94 / 1793.40 ≈ 0.43) demonstrates they are highly correlated measurements of the same underlying physical property (salinity/dissolved ions).*

## Methodological Distinction

**FACT:**
EC and TDS are related measurements representing the total concentration of dissolved ionized solids in water.

**METHODOLOGICAL QUESTION:**
Whether both should contribute independently to this WAWQI, given they represent the same health/aesthetic risk (salinity) and their inclusion mathematically double-counts this risk in the index.

**DECISION:**
[HUMAN DECISION REQUIRED]
Must be based on the documented methodology and dataset evidence. Dropping EC would drop 134,119 samples that lack TDS. Dropping TDS would discard empirical mg/L data for 29,438 samples. The methodology must determine whether to use EC, TDS, both, or an either/or conditional logic.

---

## FINAL PROJECT METHODOLOGY DECISIONS

**SOURCE FACT**
- EC and TDS are related measurements representing salinity. Pearson correlation in this dataset is 0.9977. 
- EC covers 99.03% of samples; TDS covers 17.83%.

**SCIENTIFIC SOURCE**
- BIS IS 10500:2012 relies entirely on TDS (limit 500 mg/L) for drinking water.
- BIS IS 10500:2012 provides **no** standard or limit for Electrical Conductivity (EC).
- WHO guidelines do not establish a health-based limit for EC, using TDS for aesthetic/taste concerns.

**PROJECT DECISION**
- Do NOT include both EC and TDS in the primary WAWQI.
- **TDS**: NO for primary WAWQI due to extremely low dataset coverage (17.83%).
- **EC**: EXCLUDED FROM PRIMARY WAWQI because no defensible, authoritative drinking water reference standard ($S_i$) exists in BIS or WHO to use for the unit weight calculation.
- **Retention**: EC is retained in the database for dashboard analytics, salinity mapping, GIS, and correlation analytics, but will not contribute to the mathematical WQI index.
