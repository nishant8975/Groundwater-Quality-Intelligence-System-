import os
import glob
import pandas as pd
import psycopg2

conn = psycopg2.connect('dbname=groundwater_quality user=postgres password=Nishant@2003 host=localhost port=5432')
cur = conn.cursor()

raw_dir = r"d:\PwC\Groundwater Quality Intelligence System\data\raw"
files = sorted(glob.glob(os.path.join(raw_dir, "*.csv")))

print("=== 1. DISCOVER ALL DATASETS ===")
raw_info = []
total_raw_rows = 0
for f in files:
    fname = os.path.basename(f)
    try:
        df = pd.read_csv(f, low_memory=False)
        rows = len(df)
        cols = len(df.columns)
        total_raw_rows += rows
        raw_info.append({
            'filename': fname,
            'rows': rows,
            'cols': cols
        })
    except Exception as e:
        print(f"Error reading {fname}: {e}")

print(f"Discovered {len(raw_info)} raw CSV datasets.")
print(f"Total Raw CSV Rows: {total_raw_rows:,}")

print("\n=== 2 & 3. RAW TO DB & SOURCE DATASET RECONCILIATION ===")
cur.execute("""
    SELECT 
        sd.dataset_id,
        sd.filename,
        sd.state_inferred,
        sd.row_count,
        COUNT(DISTINCT ws.sample_id) AS db_samples,
        COUNT(spv.value_id) AS db_param_obs
    FROM source_datasets sd
    LEFT JOIN water_samples ws ON sd.dataset_id = ws.source_dataset_id
    LEFT JOIN sample_parameter_values spv ON ws.sample_id = spv.sample_id
    GROUP BY sd.dataset_id, sd.filename, sd.state_inferred, sd.row_count
    ORDER BY sd.dataset_id
""")
db_ds_summary = cur.fetchall()

print(f"{'Source ID':<10} | {'File Name':<30} | {'State':<25} | {'Raw Rows':<10} | {'DB Samples':<10} | {'Diff':<6} | {'Param Obs':<12}")
print("-" * 115)
for row in db_ds_summary:
    s_id, f_name, st_name, sd_r_cnt, db_samples, param_obs = row
    raw_r = next((item['rows'] for item in raw_info if item['filename'].lower() == f_name.lower()), 0)
    diff = db_samples - raw_r
    print(f"{s_id:<10} | {f_name:<30} | {st_name:<25} | {raw_r:<10} | {db_samples:<10} | {diff:<6} | {param_obs:<12}")

print("\n=== 4, 5, 8, 9, 10. STATE COVERAGE & WAWQI & GIS & STATION RECONCILIATION ===")
cur.execute("""
    SELECT 
        l.state,
        COUNT(s.sample_id) AS total_samples,
        COUNT(DISTINCT s.location_id) AS location_records_count,
        COUNT(DISTINCT msi.station_hash) AS station_identity_count,
        COUNT(w.wqi) AS wawqi_available,
        COUNT(s.sample_id) - COUNT(w.wqi) AS wawqi_unavailable,
        ROUND((COUNT(w.wqi)::numeric / COUNT(s.sample_id)::numeric) * 100, 2) AS eligibility_pct,
        COUNT(CASE WHEN w.wqi <= 25 THEN 1 END) AS excellent,
        COUNT(CASE WHEN w.wqi > 25 AND w.wqi <= 50 THEN 1 END) AS good,
        COUNT(CASE WHEN w.wqi > 50 AND w.wqi <= 75 THEN 1 END) AS poor,
        COUNT(CASE WHEN w.wqi > 75 AND w.wqi <= 100 THEN 1 END) AS very_poor,
        COUNT(CASE WHEN w.wqi > 100 THEN 1 END) AS unsuitable,
        COUNT(CASE WHEN l.latitude IS NOT NULL AND l.longitude IS NOT NULL AND l.coordinate_validity_flag = TRUE THEN 1 END) AS gis_valid_coords,
        COUNT(CASE WHEN l.latitude IS NULL OR l.longitude IS NULL OR l.coordinate_validity_flag = FALSE THEN 1 END) AS gis_invalid_coords
    FROM water_samples s
    JOIN locations l ON s.location_id = l.location_id
    LEFT JOIN wawqi_results w ON s.sample_id = w.sample_id
    LEFT JOIN mv_station_identity msi ON md5(concat_ws('||', TRIM(LOWER(l.station_name)), TRIM(LOWER(l.state)), TRIM(LOWER(l.district)))) = msi.station_hash
    GROUP BY l.state
    ORDER BY l.state
""")
state_full_rows = cur.fetchall()

print("\n--- COMPLETE STATE COVERAGE & WAWQI BREAKDOWN ---")
print(f"{'State':<28} | {'Samples':<8} | {'Locations':<9} | {'Stations':<8} | {'WQI Avail':<9} | {'WQI Unavail':<11} | {'Elig %':<7} | {'GIS Valid':<9} | {'GIS Invalid':<11}")
print("-" * 115)
for r in state_full_rows:
    st, sam, loc, st_cnt, avail, unavail, elig, exc, g, p, vp, u, gis_val, gis_inval = r
    print(f"{st:<28} | {sam:<8} | {loc:<9} | {st_cnt:<8} | {avail:<9} | {unavail:<11} | {elig:<7.2f} | {gis_val:<9} | {gis_inval:<11}")

print("\n--- 30-STATE SUMMARY FROM MV_STATION_IDENTITY ---")
cur.execute("""
    SELECT 
        msi.state,
        SUM(msi.sample_count) AS samples,
        SUM(msi.wawqi_available_count) AS wawqi_avail,
        SUM(msi.wawqi_unavailable_count) AS wawqi_unavail,
        ROUND((SUM(msi.wawqi_available_count)::numeric / SUM(msi.sample_count)::numeric) * 100, 2) AS elig_pct,
        SUM(msi.excellent_count) AS exc,
        SUM(msi.good_count) AS good,
        SUM(msi.poor_count) AS poor,
        SUM(msi.very_poor_count) AS vpoor,
        SUM(msi.unsuitable_count) AS uns,
        COUNT(msi.station_hash) AS station_count,
        COUNT(CASE WHEN msi.data_quality_class = 'DATA RICH' THEN 1 END) AS data_rich,
        COUNT(CASE WHEN msi.data_quality_class = 'DATA LIMITED' THEN 1 END) AS data_limited
    FROM mv_station_identity msi
    GROUP BY msi.state
    ORDER BY msi.state
""")
mv_rows = cur.fetchall()

total_samples = 0
total_stations = 0
total_avail = 0
total_unavail = 0
total_exc = 0
total_good = 0
total_poor = 0
total_vpoor = 0
total_uns = 0
total_rich = 0
total_limited = 0

print(f"{'State':<28} | {'Samples':<8} | {'Stations':<8} | {'WQI Avail':<9} | {'WQI Unavail':<11} | {'Rich':<6} | {'Limited':<7}")
print("-" * 95)
for r in mv_rows:
    st, sam, avail, unavail, elig, exc, g, p, vp, u, st_cnt, rich, lim = r
    total_samples += sam
    total_stations += st_cnt
    total_avail += avail
    total_unavail += unavail
    total_exc += exc
    total_good += g
    total_poor += p
    total_vpoor += vp
    total_uns += u
    total_rich += rich
    total_limited += lim
    print(f"{st:<28} | {sam:<8} | {st_cnt:<8} | {avail:<9} | {unavail:<11} | {rich:<6} | {lim:<7}")

print("-" * 95)
print(f"{'NATIONAL TOTAL':<28} | {total_samples:<8} | {total_stations:<8} | {total_avail:<9} | {total_unavail:<11} | {total_rich:<6} | {total_limited:<7}")
print(f"Category Sums -> Excellent: {total_exc}, Good: {total_good}, Poor: {total_poor}, Very Poor: {total_vpoor}, Unsuitable: {total_uns}")

print("\n=== 6 & 11. PARAMETER COVERAGE & OBSERVATION RECONCILIATION ===")
cur.execute("""
    SELECT 
        p.canonical_name,
        COUNT(spv.numeric_value) AS numeric_observations,
        COUNT(*) FILTER (WHERE spv.is_missing) AS missing_count,
        COUNT(spv.value_id) AS total_recorded_values
    FROM parameters p
    LEFT JOIN sample_parameter_values spv ON p.parameter_id = spv.parameter_id
    GROUP BY p.canonical_name
    ORDER BY numeric_observations DESC
""")
param_summary = cur.fetchall()
print(f"{'Parameter':<20} | {'Numeric Observations':<20} | {'Missing Count':<15} | {'Total Recorded':<15}")
print("-" * 75)
for p_row in param_summary:
    print(f"{p_row[0]:<20} | {p_row[1]:<20} | {p_row[2]:<15} | {p_row[3]:<15}")

print("\n=== 7. EXTREME WAWQI VALIDATION ===")
cur.execute("""
    SELECT 
        l.state,
        COUNT(w.wqi) FILTER (WHERE w.wqi > 100) AS extreme_count,
        MIN(w.wqi) AS min_wqi,
        MAX(w.wqi) AS max_wqi
    FROM wawqi_results w
    JOIN water_samples s ON w.sample_id = s.sample_id
    JOIN locations l ON s.location_id = l.location_id
    WHERE w.wqi IS NOT NULL
    GROUP BY l.state
    ORDER BY max_wqi DESC
""")
extreme_summary = cur.fetchall()
print(f"{'State':<28} | {'Min WAWQI':<12} | {'Max WAWQI':<15} | {'WAWQI > 100 Count':<18}")
print("-" * 80)
for ex_row in extreme_summary:
    print(f"{ex_row[0]:<28} | {ex_row[1]:<12.2f} | {ex_row[2]:<15.2f} | {ex_row[3]:<18}")

# Verify extreme benchmark samples 1419, 62753, 408
print("\nBenchmark Extreme Samples Status:")
for sid in [1419, 62753, 408]:
    cur.execute("SELECT sample_id, wqi, calculation_status, data_quality_flags FROM wawqi_results WHERE sample_id = %s", (sid,))
    print(" ", cur.fetchone())

print("\n=== 12 & 13. DATABASE INTEGRITY & PROVENANCE AUDIT ===")
cur.execute("SELECT COUNT(*) FROM water_samples WHERE source_dataset_id IS NULL OR source_row_index IS NULL OR location_id IS NULL")
print("Orphaned water_samples count:", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM sample_parameter_values WHERE sample_id NOT IN (SELECT sample_id FROM water_samples)")
print("Orphaned sample_parameter_values count:", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM wawqi_results WHERE sample_id NOT IN (SELECT sample_id FROM water_samples)")
print("Orphaned wawqi_results count:", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM locations WHERE location_id NOT IN (SELECT location_id FROM water_samples)")
print("Orphaned locations count:", cur.fetchone()[0])

cur.execute("SELECT sample_id, parameter_id, COUNT(*) FROM sample_parameter_values GROUP BY sample_id, parameter_id HAVING COUNT(*) > 1")
dup_spv = cur.fetchall()
print("Duplicate (sample_id, parameter_id) records count:", len(dup_spv))

print("\n=== 14. ANALYTICS VIEW RECONCILIATION ===")
views_to_check = [
    "vw_wawqi_national_summary",
    "vw_wawqi_categories",
    "vw_wawqi_extreme_values",
    "vw_data_quality_analytics",
    "vw_gis_points",
    "mv_wawqi_state_summary",
    "mv_wawqi_district_summary",
    "mv_wawqi_location_summary",
    "mv_parameter_analytics",
    "mv_parameter_exceedance",
    "mv_temporal_analytics",
    "mv_station_identity",
    "vw_station_wawqi_history",
    "mv_station_parameter_analytics"
]

for v in views_to_check:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {v}")
        cnt = cur.fetchone()[0]
        print(f"  - {v:<35} : EXISTS (Rows: {cnt:,})")
    except Exception as e:
        print(f"  - {v:<35} : ERROR ({e})")
