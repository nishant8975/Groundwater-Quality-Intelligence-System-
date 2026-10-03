import os
import sys
import json
import psycopg2
import pandas as pd

sys.stdout.reconfigure(line_buffering=True)

print("========================================================================")
print("  PHASE 12D — FINAL PRODUCTION-READINESS AUDIT SCRIPT                  ")
print("========================================================================")

DB_CONFIG = {
    'dbname': 'groundwater_quality',
    'user': 'postgres',
    'password': 'Nishant@2003',
    'host': 'localhost',
    'port': 5432
}

conn = psycopg2.connect(**DB_CONFIG)
conn.autocommit = True
cur = conn.cursor()

# 1. DATA BASELINE RECONCILIATION
print("\n--- 1. DATA BASELINE RECONCILIATION ---")

cur.execute("SELECT COUNT(*) FROM source_datasets;")
cnt_ds = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM water_samples;")
cnt_ws = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM locations;")
cnt_loc = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM parameters;")
cnt_params = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM sample_parameter_values;")
cnt_eav = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM wawqi_results;")
cnt_wawqi_total = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM wawqi_results WHERE calculation_status = 'SUCCESS';")
cnt_wawqi_avail = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM wawqi_results WHERE calculation_status = 'INSUFFICIENT_PARAMETER_COVERAGE';")
cnt_wawqi_unavail = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM mv_station_identity;")
cnt_stations = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM vw_gis_points;")
cnt_gis_valid = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM locations WHERE latitude IS NULL OR longitude IS NULL OR latitude < 6.0 OR latitude > 37.5 OR longitude < 68.0 OR longitude > 97.5;")
cnt_gis_invalid = cur.fetchone()[0]

cur.execute("SELECT wqi_category, COUNT(*) FROM vw_wawqi_categories GROUP BY wqi_category;")
cats = dict(cur.fetchall())

print(f"Source Datasets: {cnt_ds} (Expected: 30)")
print(f"Water Samples: {cnt_ws} (Expected: 165162)")
print(f"Locations: {cnt_loc} (Expected: 165162)")
print(f"Parameters: {cnt_params} (Expected: 27)")
print(f"EAV Rows: {cnt_eav} (Expected: 1609277)")
print(f"WAWQI Results: {cnt_wawqi_total} (Expected: 165162)")
print(f"WAWQI Available: {cnt_wawqi_avail} (Expected: 120738)")
print(f"WAWQI Unavailable: {cnt_wawqi_unavail} (Expected: 44424)")
print(f"Canonical Stations: {cnt_stations} (Expected: 22753)")
print(f"Valid GIS Records: {cnt_gis_valid} (Expected: 165010)")
print(f"Invalid Coordinates: {cnt_gis_invalid} (Expected: 152)")

print("Category Breakdown:")
for c in ['Excellent', 'Good', 'Poor', 'Very Poor', 'Unsuitable']:
    print(f"  {c}: {cats.get(c, 0)}")

# 2. DATABASE OBJECT COMPLETENESS AUDIT
print("\n--- 2. DATABASE OBJECT COMPLETENESS AUDIT ---")
cur.execute("""
    SELECT table_name, table_type 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_type, table_name;
""")
tables_and_views = cur.fetchall()
print(f"Total Public DB Objects: {len(tables_and_views)}")
for name, ttype in tables_and_views:
    print(f"  [{ttype}] {name}")

# 3. EXTREME SAMPLE AUDIT (1419, 408, 62753)
print("\n--- 3. EXTREME SAMPLE AUDIT ---")
for sample_id in [1419, 408, 62753]:
    cur.execute("SELECT w.sample_id, w.wqi, c.wqi_category, w.calculation_status, w.data_quality_flags FROM wawqi_results w JOIN vw_wawqi_categories c ON w.sample_id = c.sample_id WHERE w.sample_id = %s;", (sample_id,))
    row = cur.fetchone()
    print(f"Sample {sample_id}: WQI={row[1]}, Category={row[2]}, Status={row[3]}, Flags={row[4]}")


# 4. GIT & SECRET HYGIENE AUDIT
print("\n--- 4. GIT & SECRET HYGIENE AUDIT ---")
gitignore_exists = os.path.exists('.gitignore')
print(f".gitignore exists: {gitignore_exists}")
if gitignore_exists:
    with open('.gitignore', 'r') as f:
        git_content = f.read()
        print(f"'.env' in .gitignore: {'.env' in git_content}")

print("========================================================================")
print("  PHASE 12D READINESS AUDIT EXECUTED SUCCESSFULLY                       ")
print("========================================================================")
