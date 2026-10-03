# WAWQI Manual Validation Case

To ensure the WAWQI methodology implementation is mathematically sound before building the full Python engine, a real test case from the database (Sample ID 1000) was validated manually.

## Source Data (Sample ID 1000)
- `ph`: 7.7
- `tds`: 389.35 mg/L
- `chloride`: 17.75 mg/L
- `sulphate`: 10.12 mg/L
- `hardness`: 160.0 mg/L
- `calcium`: 18.0 mg/L
- `magnesium`: 27.945 mg/L

## 1. Constants & Weight Calculation
*Assuming a "core" parameter set for this example. Nitrates and Fluorides are absent.*

| Parameter | $S_i$ (Limit) | $V_0$ (Ideal) | $1/S_i$ |
| --- | --- | --- | --- |
| pH | 8.5 | 7.0 | 0.1176 |
| TDS | 500 | 0 | 0.0020 |
| Chloride | 250 | 0 | 0.0040 |
| Sulphate | 200 | 0 | 0.0050 |
| Hardness | 200 | 0 | 0.0050 |
| Calcium | 75 | 0 | 0.0133 |
| Magnesium | 30 | 0 | 0.0333 |

**Proportionality Constant ($K$)**: 
$\sum (1/S_i)$ = 0.1802
$K = 1 / 0.1802 = 5.549$

## 2. Parameter Computations

| Parameter | $V_i$ | Unit Weight ($w_i = K/S_i$) | Quality Rating ($q_i$) | $w_i \times q_i$ |
| --- | --- | --- | --- | --- |
| pH | 7.7 | 0.6528 | $100 \times \frac{(7.7 - 7.0)}{(8.5 - 7.0)} = 46.67$ | 30.46 |
| TDS | 389.35 | 0.0111 | $100 \times \frac{389.35}{500} = 77.87$ | 0.86 |
| Chloride | 17.75 | 0.0222 | $100 \times \frac{17.75}{250} = 7.10$ | 0.16 |
| Sulphate | 10.12 | 0.0277 | $100 \times \frac{10.12}{200} = 5.06$ | 0.14 |
| Hardness | 160.0 | 0.0277 | $100 \times \frac{160.0}{200} = 80.00$ | 2.22 |
| Calcium | 18.0 | 0.0740 | $100 \times \frac{18.0}{75} = 24.00$ | 1.78 |
| Magnesium | 27.95 | 0.1850 | $100 \times \frac{27.95}{30} = 93.15$ | 17.23 |

## 3. Final WQI Assembly

- $\sum (w_i \times q_i) = 52.85$
- $\sum w_i = 1.0005$
- **$WQI = 52.82$**

## Classification
A WQI of 52.82 falls into the **Poor** category (51-75). The primary mathematical drivers for this result were Magnesium (high unit weight + high relative concentration) and pH (very high unit weight).

---

## FINAL PROJECT METHODOLOGY DECISIONS

**SOURCE FACT**
- Sample 1000 successfully calculates a WAWQI without errors.

**SCIENTIFIC SOURCE**
- The $K$ scaling methodology correctly balances missing parameters mathematically.

**PROJECT DECISION**
- The manual mathematical trace is verified as successful. The Python engine must replicate this exact rounding and algorithmic order.

---

## FINAL MATHEMATICAL VERIFICATION (Real Samples)

**SOURCE FACT**
A python implementation explicitly enforcing the absolute-value pH formula and dynamic weights was executed against PostgreSQL real samples.

**IMPLEMENTATION DECISION**
Numerical tolerance for WQI verification is set to `0.01`.

### 1. Quality Rating Tests
- **Vi = 0**: $q_i = 0$
- **Vi = Si**: $q_i = 100$
- **Vi > Si**: $q_i > 100$ (e.g. 200)
- **pH = 7.0**: $q_i = 0.00$
- **pH = 6.5**: $q_i = 33.33$
- **pH = 8.5**: $q_i = 100.00$
- **pH = 6.0**: $q_i = 66.67$
- **pH = 9.0**: $q_i = 133.33$
- **Missing parameters**: Evaluated to NULL and safely ignored.
- **Minimum 6 Valid Parameters**: Evaluated strictly. 5 parameters returns NULL.

### 2. Real PostgreSQL Sample Tests

**Sample ID: 1 (Exactly 6 valid parameters)**
- Parameters: `ph`, `chloride`, `sulphate`, `hardness`, `calcium`, `magnesium`
- $\sum W_i$: 1.000000
- Final WQI: 27.74 (Good)

**Sample ID: 176 (7+ parameters, pH < 7.0)**
- Parameters: `ph`, `chloride`, `sulphate`, `hardness`, `calcium`, `magnesium`, `iron`, `arsenic`
- Vi for pH = 6.999, $q_i$ correctly evaluates to 0.07 (absolute deviation).
- $\sum W_i$: 1.000000
- Final WQI: 0.01 (Excellent)

**Sample ID: 202 (Arsenic present)**
- Parameters include Arsenic (Vi = 16.97, massive limit breach).
- $W_i$ for Arsenic dominates at 0.966.
- $\sum W_i$: 1.000000
- Final WQI: 163949.15 (Unsuitable)

**Sample ID: 1419 (Uranium present)**
- Parameters include Uranium (Vi = 450.0).
- $W_i$ for Uranium dominates at 0.998.
- $\sum W_i$: 1.000000
- Final WQI: 1497275.16 (Unsuitable)

**Sample ID: 1472 (pH > 7, Iron > 0.3)**
- Parameters include pH = 7.6, Iron = 0.33.
- $\sum W_i$: 1.000000
- Final WQI: 116.92 (Unsuitable)

**Validation Result:** Python mathematical verification confirmed. $\sum W_i = 1$ is mathematically guaranteed for all real sample tests.

---

## PRODUCTION EXECUTION VALIDATION

**Execution Date:** 2026-10-02
**Methodology Version:** Phase4_Final
**Idempotency Status:** PASS (UPSERT correctly preserves exactly 165,162 unique records)
**Raw Data Integrity:** PASS (0 changes to `water_samples` or `sample_parameter_values`)

### 1. Row Count & Coverage
- **Total Samples:** 165,162
- **WQI Calculated (Eligible):** 120,738 (73.10%)
- **WQI NULL (Ineligible):** 44,424
- **Coverage Breakdown:**
  - Exactly 6 parameters: 85,334
  - 7 parameters: 26,657
  - 8 parameters: 6,426
  - 9 parameters: 2,321

### 2. WQI Distribution
- **Minimum:** 0.01
- **Maximum:** 8,053,585.15
- **Mean:** 392.42
- **Median (P50):** 68.52
- **P25:** 43.38
- **P75:** 98.15
- **P90:** 177.21
- **P95:** 376.64
- **P99:** 2,719.21

**Categorical Distribution:**
- **Excellent (≤ 25):** 18,821 (15.59%)
- **Good (26–50):** 17,465 (14.47%)
- **Poor (51–75):** 32,834 (27.19%)
- **Very Poor (76–100):** 22,587 (18.71%)
- **Unsuitable (> 100):** 29,031 (24.04%)

### 3. Extreme Value Analysis
The highest observed WAWQI scores reach > 8 million. This mathematically verifies the formulation constraints:
- `qi` does not artificially clamp at 100.
- Massive limit breaches in trace metals with tiny $S_i$ limits (e.g. Arsenic 0.01 mg/L) generate functionally limitless quality ratings, aggressively pushing the sample into the "Unsuitable" (>100) category exactly as intended by the formulation.
- **Top 5 Samples:**
  1. Sample 62753 (Saligrama) - 8,053,585.15
  2. Sample 408 (Manu) - 3,337,354.25
  3. Sample 1419 (Alampur) - 1,497,275.16
  4. Sample 53644 (Basapur2) - 838,183.25
  5. Sample 56582 (Hanchinal) - 828,899.84

### 4. Data Quality Flags
- **Sample 1419 (Uranium = 450 mg/L)**: Retained as mathematically accurate per the database ETL. Flagged internally as a possible source-level unit anomaly (450 mg/L could be 450 ppb).
- No samples were imputed. No zeros were fabricated.
