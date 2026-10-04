# Supabase PostgreSQL Database Migration Guide
**Groundwater Quality Intelligence — WAWQI Analytics Platform**

---

## 1. Overview & Objectives
This document provides the exact, production-tested procedure for migrating the local PostgreSQL database (`groundwater_quality`, ~524 MB) to Supabase Cloud PostgreSQL while preserving 100% data fidelity, table structures, indexes, views, and materialized views.

---

## 2. Required PostgreSQL Extensions
Before restoring the database dump, the following extension must be enabled on Supabase:
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```
*(Used by station search for high-performance trigram pattern matching on station names).*

---

## 3. Database Migration Command Procedure

### Step A: Create Local Database Dump
Run PostgreSQL `pg_dump` from your local machine to export a clean custom-format archive excluding local role ownerships:
```powershell
pg_dump `
  -h localhost `
  -p 5432 `
  -U postgres `
  -d groundwater_quality `
  --no-owner `
  --no-privileges `
  -Fc `
  -f groundwater_quality.dump
```

### Step B: Restore Archive to Supabase
Obtain your Supabase database host, user, and port from the **Supabase Dashboard → Settings → Database → Connection String (Session Pooler / Direct)**.

Run `pg_restore` to populate your Supabase database:
```powershell
pg_restore `
  -h db.YOUR-SUPABASE-ID.supabase.co `
  -p 5432 `
  -U postgres.YOUR-SUPABASE-PROJECT `
  -d postgres `
  --no-owner `
  --no-privileges `
  groundwater_quality.dump
```

---

## 4. Post-Restore Refresh & Materialized Views
If materialized views require a refresh after restore, execute:
```sql
REFRESH MATERIALIZED VIEW mv_station_identity;
REFRESH MATERIALIZED VIEW mv_parameter_analytics;
REFRESH MATERIALIZED VIEW mv_parameter_exceedance;
REFRESH MATERIALIZED VIEW mv_temporal_analytics;
```

---

## 5. Authoritative Database Reconciliation Script

Run the following SQL verification query on Supabase to ensure 100% data reconciliation:

```sql
SELECT 'Datasets' as metric, COUNT(*) as count FROM source_datasets
UNION ALL
SELECT 'Samples', COUNT(*) FROM water_samples
UNION ALL
SELECT 'EAV Observations', COUNT(*) FROM sample_parameter_values
UNION ALL
SELECT 'WAWQI Available', COUNT(*) FROM wawqi_results WHERE wqi IS NOT NULL
UNION ALL
SELECT 'WAWQI Unavailable', COUNT(*) FROM wawqi_results WHERE wqi IS NULL
UNION ALL
SELECT 'Canonical Stations', COUNT(*) FROM mv_station_identity
UNION ALL
SELECT 'Valid GIS', COUNT(*) FROM vw_gis_points
UNION ALL
SELECT 'Invalid Coordinates', COUNT(*) FROM water_samples WHERE latitude IS NULL OR longitude IS NULL;
```

### Expected Reconciliation Results:
| Metric | Expected Count |
| :--- | :--- |
| **Datasets** | 30 |
| **Samples** | 165,162 |
| **EAV Observations** | 1,609,277 |
| **WAWQI Available** | 120,738 |
| **WAWQI Unavailable** | 44,424 |
| **Canonical Stations** | 22,753 |
| **Valid GIS Records** | 165,010 |
| **Invalid Coordinates** | 152 |

---

## 6. WAWQI Category Breakdown Reconciliation Query

```sql
SELECT wqi_category as category, COUNT(*) as count
FROM vw_wawqi_categories
GROUP BY wqi_category
ORDER BY count DESC;
```

### Expected Category Counts:
| Category | Expected Count |
| :--- | :--- |
| **Poor** | 32,834 |
| **Unsuitable** | 29,031 |
| **Very Poor** | 22,587 |
| **Excellent** | 18,821 |
| **Good** | 17,465 |
| **Total Available** | **120,738** |

---

## 7. Migration Verification Sign-off
If any metric count differs from the authoritative table above, halt deployment immediately and verify `pg_restore` log outputs.
