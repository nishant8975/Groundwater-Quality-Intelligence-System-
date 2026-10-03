# WAWQI Standards, Ideal Values, and Weights

## Scientific Basis
This table establishes the foundational constants for the WAWQI methodology.
Every constant is strictly mapped to an official source with full traceability.

## Final BIS Parameter Limits Verification

Before finalizing $S_i$, every parameter in the primary candidate set must be verified against the cited standard to establish the exact limit type.

| Parameter | $S_i$ | Unit | Limit Type | Source | Edition |
| --------- | ----: | ---- | ---------- | ------ | ------- |
| pH        | 8.5   | —    | Acceptable limit | BIS IS 10500 | 2012 (Amended 2021) |
| Chloride  | 250.0 | mg/L | Acceptable limit | BIS IS 10500 | 2012 (Amended 2021) |
| Sulphate  | 200.0 | mg/L | Acceptable limit | BIS IS 10500 | 2012 (Amended 2021) |
| Hardness  | 200.0 | mg/L | Acceptable limit | BIS IS 10500 | 2012 (Amended 2021) |
| Calcium   | 75.0  | mg/L | Acceptable limit | BIS IS 10500 | 2012 (Amended 2021) |
| Magnesium | 30.0  | mg/L | Acceptable limit | BIS IS 10500 | 2012 (Amended 2021) |
| Iron      | 0.3   | mg/L | Acceptable limit (Aesthetic) | BIS IS 10500 | 2012 (Amended 2021) |
| Arsenic   | 0.01  | mg/L | Acceptable limit (Health-based) | BIS IS 10500 | 2012 (Amended 2021) |
| Uranium   | 0.03  | mg/L | Acceptable limit (Health-based) | BIS IS 10500 | 2012 (Amended 2021) |

*Note: Uranium was added to BIS IS 10500 in Amendment No. 2 (2021), establishing a 0.03 mg/L acceptable limit aligning with the WHO guideline. AERB defines a separate 0.06 mg/L radiological limit. The WAWQI uses the official BIS 0.03 mg/L chemical toxicity limit.*


## WHO Guidelines
| Parameter | Value ($S_i$) | Unit | Ideal ($V_0$) | Source Org | Source Doc | Edition/year | Type of limit | Limit Category |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sodium | 200.0 | mg/L | 0 | WHO | Drinking-water Quality | 4th Ed. | Taste/Acceptability ref | Aesthetic (NOT Health-based) |
| Electrical Conductivity | 300.0 | μS/cm | 0 | WHO | Drinking-water Quality | 4th Ed. | Taste/Acceptability ref | Aesthetic |

## Weight Calculation Methodology
The unit weight ($w_i$) for each parameter is calculated inversely proportional to its standard value ($S_i$):
$$w_i = \frac{K}{S_i}$$
Where K is the proportionality constant:
$$K = \frac{1}{\sum (1/S_i)}$$

---

## FINAL PROJECT METHODOLOGY DECISIONS

**SOURCE FACT**
- `Sodium` lacks a BIS standard and the WHO limit (200 mg/L) is purely aesthetic (taste).
- `EC` and `TDS` are highly correlated; BIS uses TDS (500 mg/L) and provides no EC standard. WHO also has no health-based EC standard.

**SCIENTIFIC SOURCE**
- BIS IS 10500:2012 defines formal limits for pH, TDS, Chloride, Sulphate, Hardness, Calcium, Magnesium, Iron, Arsenic, Nitrate, Fluoride, Cadmium, Lead, and Uranium.
- The Uranium limit is 0.03 mg/L (30 ppb) established by BIS IS 10500:2012 Amendment 2. (AERB's 60 ppb limit is radiological, not the primary chemical limit). The dataset unit `mg/L` correctly matches the standard.

**PROJECT DECISION**
- **EC**: Excluded from the primary WAWQI due to the lack of an authoritative reference standard ($S_i$) to support the unit weight calculation methodology.
- **TDS**: Excluded from the primary WAWQI due to extremely low coverage (17.83%).
- **Sodium**: Excluded from the primary WAWQI because its WHO reference (200 mg/L) is a taste acceptability reference rather than a permissible health limit.
- **Core Methodology Set**: The unit weight normalization ($K = 1 / \sum(1/S_i)$) will be dynamically calculated per-sample based only on the available **primary** WAWQI parameters (pH, Chloride, Sulphate, Hardness, Calcium, Magnesium, Iron, Arsenic, Uranium) and their BIS/AERB limits defined above.
