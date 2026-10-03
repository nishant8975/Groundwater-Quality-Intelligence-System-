# WAWQI Parameter Inventory

## Overview
This inventory audits the exact parameter availability natively loaded in the `groundwater_quality` PostgreSQL database (165,162 water samples across 30 datasets).

## Final Parameter Classification

| Parameter | Coverage | Primary WAWQI        | Reason                             |
| --------- | -------: | -------------------- | ---------------------------------- |
| pH        |   94.25% | YES                  | Core chemical property             |
| Chloride  |   92.69% | YES                  | Major anion                        |
| Sulphate  |   73.78% | YES                  | Major anion                        |
| Hardness  |   82.47% | YES                  | Core water property                |
| Calcium   |   85.64% | YES                  | Major cation                       |
| Magnesium |   86.08% | YES                  | Major cation                       |
| Iron      |   23.12% | YES                  | Operational/Aesthetic limit exists |
| Arsenic   |    5.71% | CONDITIONAL          | Sparse but scientifically relevant |
| Uranium   |    3.41% | CONDITIONAL          | BIS 0.03 mg/L (chemical toxicity)  |
| EC        |   99.03% | NO                   | Standard must be defensible        |
| TDS       |   17.83% | NO                   | Low coverage                       |
| Sodium    |   83.88% | NO                   | No health-based guideline          |
| Nitrate   |       0% | NO                   | Unavailable                        |
| Fluoride  |       0% | NO                   | Unavailable                        |
| Potassium |       0% | NO                   | Unavailable                        |

## Heavy Metals

These parameters have extremely sparse observations but are not automatically excluded, as their presence indicates significant health risks.
| Parameter | Numeric observation count | Coverage % | Datasets/states with observations |
| --- | --- | --- | --- |
| Arsenic | 9,431 | 5.71% | 22 |
| Cadmium | 797 | 0.48% | 2 |
| Manganese | 797 | 0.48% | 2 |
| Nickel | 797 | 0.48% | 2 |
| Chromium | 797 | 0.48% | 2 |
| Zinc | 796 | 0.48% | 2 |
| Copper | 796 | 0.48% | 2 |
| Lead | 794 | 0.48% | 2 |

## Unavailable Parameters

The following parameters appear in source CSV headers but have completely empty data columns across all datasets.

**Nitrate, Fluoride, Potassium:**
- Methodological relevance: YES
- Current dataset availability: NONE
- Primary WAWQI contribution: NONE
- Numeric observations: 0

---

## FINAL PROJECT METHODOLOGY DECISIONS

**SOURCE FACT**
- Arsenic (5.71%) and Uranium (3.41%) have sparse coverage but indicate significant health risks.
- Lead, Cadmium, Manganese, Nickel, Chromium, Zinc, and Copper have extremely sparse coverage (0.48%).

**SCIENTIFIC SOURCE**
- Arsenic and Uranium have documented authoritative standard/guidelines (BIS and AERB). Uranium's 0.03 mg/L limit was formalized in BIS IS 10500 Amendment No. 2 (2021).

**PROJECT DECISION**
- **Arsenic & Uranium**: Allow to conditionally contribute to the primary WAWQI when a valid numeric observation exists. Do not impute if missing. Do not reject the sample solely because they are missing.
- **Other Heavy Metals**: Retain observations in the database for separate contaminant-risk analytics. Do NOT automatically include in the primary WAWQI due to extreme sparsity and lack of methodological minimum-coverage compatibility.

**IMPLEMENTATION DECISION**
- **Conditional Handling**: If unavailable, do not impute. Do not treat missing as zero. Do not reject a sample solely because a conditional parameter is missing (provided it meets the `MINIMUM_VALID_PARAMETERS = 6` threshold using core parameters).
