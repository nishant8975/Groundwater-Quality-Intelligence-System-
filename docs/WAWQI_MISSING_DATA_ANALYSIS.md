# WAWQI Missing-Data Analysis & Policy Options

## Missing Data Context
The groundwater database utilizes a sparse Entity-Attribute-Value (EAV) model, where empty parameter measurements are omitted entirely. Out of the 165,162 water samples, parameter availability is highly variable. Most notably:
- `nitrate` and `fluoride`, two of the most heavily weighted health-based parameters, are 100% missing.
- Heavy metals (`cadmium`, `manganese`, `nickel`, `chromium`, `zinc`, `copper`, `lead`) are 99.5% missing (only present in 2 states).
- Major ions (`calcium`, `magnesium`, `chloride`, `sulphate`) have high coverage (~75-93%).

Calculating a Weighted Arithmetic Water Quality Index (WAWQI) requires careful handling when parameters are missing.

## Policy Options for WAWQI Calculation

## Minimum Valid Parameter Coverage Analysis

Based on the 9 final candidate parameters (pH, Chloride, Sulphate, Hardness, Calcium, Magnesium, Iron, Arsenic, Uranium), the exact sample eligibility at varying inclusion thresholds is:

| Minimum Valid Parameters | Eligible Samples | Percentage of 165,162 |
| -----------------------: | ---------------: | --------------------: |
|                        1 |          160,523 |                97.19% |
|                        2 |          154,369 |                93.47% |
|                        3 |          145,488 |                88.09% |
|                        4 |          141,485 |                85.66% |
|                        5 |          134,612 |                81.50% |
|                        6 |          120,741 |                73.10% |
|                        7 |           35,405 |                21.44% |
|                        8 |            8,747 |                 5.30% |
|                        9 |            2,321 |                 1.41% |

### Percentage-Based Thresholds
| Threshold Requirement | Equivalent Parameters | Eligible Samples | Percentage of 165,162 |
| --------------------: | --------------------: | ---------------: | --------------------: |
|                  ≥ 50% |                    ≥ 5 |          134,612 |                81.50% |
|                  ≥ 60% |                    ≥ 6 |          120,741 |                73.10% |
|                  ≥ 75% |                    ≥ 7 |           35,405 |                21.44% |
|                  ≥ 80% |                    ≥ 8 |            8,747 |                 5.30% |

---

## FINAL PROJECT METHODOLOGY DECISIONS

**SOURCE FACT**
- Requiring a strict minimum coverage of exactly 6 final candidate parameters allows 120,741 samples (73.10%) to be successfully calculated.
- Requiring 7 parameters drops eligibility dramatically to 35,405 samples (21.44%).

**SCIENTIFIC SOURCE**
- Parameter subsetting rules are analytical/statistical project choices and are not mandated by BIS or WHO guidelines.

**PROJECT DECISION**
- **MINIMUM_VALID_PARAMETERS = 6**. A project-defined minimum coverage threshold selected to balance sample eligibility with multi-parameter representation. It is explicitly NOT a regulatory requirement.
- The threshold is applied against the final primary WAWQI parameters (including conditional heavy metals when they exist for the sample).
- Samples not meeting this threshold will have their WQI marked as UNAVAILABLE.

**IMPLEMENTATION DECISION**
- **Conditional Parameters**: Arsenic and Uranium conditionally contribute to the score if present. If missing, they are excluded from calculation (without imputation), and do NOT trigger sample rejection provided the sample has at least 6 other valid core parameters.
