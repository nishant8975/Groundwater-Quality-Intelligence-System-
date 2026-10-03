# WAWQI Methodology

## Overview
This document defines the mathematical methodology for calculating the Weighted Arithmetic Water Quality Index (WAWQI) for the Groundwater Quality Intelligence System.

## Exact WAWQI Formula
The methodology relies on a normalized weighted average of quality ratings.

### 1. Quality Rating ($q_i$)
The quality rating calculates the relative parameter concentration compared to its standard.
For typical parameters where the ideal value ($V_0$) is $0$:
$$q_i = 100 \times (V_i / S_i)$$

**CRITICAL — pH Special Handling**:
For pH, the ideal value $V_0 = 7.0$. Acidic deviations ($V_i < 7.0$) must not produce negative numbers, which would mathematically lower (improve) the final WQI improperly. The formula uses the absolute deviation:
$$q_{pH} = 100 \times \frac{|V_{pH} - 7.0|}{8.5 - 7.0}$$
*Source: Standard weighted arithmetic implementations (e.g., Brown et al., 1970).*

### 2. Unit Weight ($W_i$)
The unit weight ensures that parameters with lower acceptable limits (higher toxicity) exert a stronger influence on the final index:
$$W_i = \frac{K}{S_i}$$
Where $K$ is the proportionality constant:
$$K = \frac{1}{\sum (1/S_i)}$$

- **Dynamic Normalization**: Because parameter availability varies between samples, $K$ is dynamically recalculated per sample using ONLY the parameters actually included in that specific sample. This mathematically guarantees that for every eligible sample, $\sum W_i = 1$. This is a necessary mathematical normalization, not an arbitrary subjective weighting.

### 3. Final WQI
The index aggregates the weighted quality ratings:
$$WQI = \frac{\sum (W_i \times q_i)}{\sum W_i}$$

## Edge Cases & Analytical Handling

1. **Observed Value = Ideal Value ($V_i = V_0$)**: $q_i = 0$. Indicates perfect water quality for that parameter.
2. **Observed Value = Standard Value ($V_i = S_i$)**: $q_i = 100$. Indicates the parameter is exactly at the limit.
3. **Observed Value > Standard ($V_i > S_i$)**: $q_i > 100$. Positively contributes to raising the WQI (worse water quality).
4. **Observed Value < Ideal ($V_i < V_0$)**: Handled using absolute difference (e.g., pH).
5. **Missing Parameter**: The formula is dynamically calculated (Partial WQI). Both $K$ and $\sum W_i$ are scaled to include ONLY the available primary WAWQI parameters for a given sample.
6. **Minimum Parameter Rule**: `MINIMUM_VALID_PARAMETERS = 6`. A sample must possess at least 6 valid core or conditional parameters to be eligible. This is a project-defined methodological threshold. It is explicitly NOT a BIS/WHO requirement. If fewer than 6 valid numeric parameters exist, `WAWQI = NULL`. Missing values are never fabricated or imputed.
7. **Conditional Parameters**: Arsenic and Uranium. If a valid numeric measurement exists, include it. If unavailable, do not impute it. Do not treat missing as zero. Do not reject a sample solely because a conditional parameter is missing.
8. **Negative/Physically Impossible Measurement**: Capped to $0$ or dropped as invalid.
8. **Zero Standard or Denominator Risk**: The BIS standards do not contain $S_i = 0$. $V_0 = S_i$ is impossible.
9. **Unit Mismatch**: The ETL guarantees standard units (mg/L, μS/cm).
10. **Duplicate Observations**: [IMPLEMENTATION DECISION] - If multiple observations exist for the same parameter on the same station/date, the **Median** value will be used analytically prior to calculation, preserving raw variance in the database.

## Category Thresholds
*PROJECT DECISION:*
- **0–25**: Excellent
- **26–50**: Good
- **51–75**: Poor
- **76–100**: Very Poor
- **>100**: Unsuitable for drinking

---

## FINAL PROJECT METHODOLOGY DECISIONS

**SOURCE FACT**
- Source dataset completeness is highly variable per sample.

**SCIENTIFIC SOURCE**
- WAWQI literature often uses dynamic denominator scaling to accommodate missing field measurements, provided enough core parameters exist to define the water character.

**PROJECT DECISION**
- Missing parameters trigger dynamic $K$ and $w_i$ recalculation for the specific sample.
- **Minimum Valid Parameter Coverage** is established at `6` primary WAWQI parameters. This rejects ~26.9% of samples but prevents misleading indices based on 1-2 parameters.

## Scientific Sources
- **IS 10500:2012**: Bureau of Indian Standards, Drinking Water Specifications (Second Revision).
- **WAWQI Mathematical Basis**: Standard weighted arithmetic indexing methodology widely published in peer-reviewed hydrology journals (e.g., Brown et al., 1970; Horton, 1965).

---

## FINAL MATHEMATICAL VERIFICATION

**SOURCE FACT**
- The algebraic equation for pH $q_i$ will return negative values for $V_i < 7.0$ without absolute value notation.

**SCIENTIFIC SOURCE**
- Published hydrological WAWQI index formulations use absolute value deviations for pH specifically to penalize both acidity and alkalinity relative to neutrality.

**PROJECT DECISION**
- pH absolute value formula is enforced.
- Missing values will NOT be imputed or fabricated.
- `MINIMUM_VALID_PARAMETERS = 6` is mathematically enforced as a project threshold before dynamic weighting $K$ is calculated.

**IMPLEMENTATION DECISION**
- Python analytics engine validates $\sum W_i = 1$ internally before outputting score.
- The engine computes conditional parameters dynamically without penalizing the sample if absent.
