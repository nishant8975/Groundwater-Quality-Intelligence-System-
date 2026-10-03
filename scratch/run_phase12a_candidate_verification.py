import os
import sys
import json
import time
import pandas as pd
import psycopg2

sys.stdout.reconfigure(line_buffering=True)

print("========================================================================")
print("   PHASE 12A CORRECTION — PERFORMANCE CANDIDATE VERIFICATION SCRIPT    ")
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

# ---------------------------------------------------------
# 1. VERIFY EXISTING INDEXES ON TARGET TABLES
# ---------------------------------------------------------
print("\n--- 1. CATALOG INDEXES ON TARGET TABLES ---")

target_tables = ['water_samples', 'wawqi_results', 'sample_parameter_values']

cur.execute("""
    SELECT 
        c.relname AS table_name,
        i.relname AS index_name,
        pg_get_indexdef(idx.indexrelid) AS index_def,
        idx.indisunique AS is_unique,
        pg_get_expr(idx.indpred, idx.indrelid) AS partial_predicate,
        pg_size_pretty(pg_relation_size(idx.indexrelid)) AS index_size,
        pg_relation_size(idx.indexrelid) AS index_size_bytes,
        st.idx_scan AS scan_count
    FROM pg_index idx
    JOIN pg_class c ON c.oid = idx.indrelid
    JOIN pg_class i ON i.oid = idx.indexrelid
    JOIN pg_stat_user_indexes st ON st.indexrelid = idx.indexrelid
    WHERE c.relname IN ('water_samples', 'wawqi_results', 'sample_parameter_values')
    ORDER BY c.relname, pg_relation_size(idx.indexrelid) DESC;
""")

indexes_catalog = cur.fetchall()

idx_cat_list = []
for r in indexes_catalog:
    idx_cat_list.append({
        "table_name": r[0],
        "index_name": r[1],
        "index_def": r[2],
        "is_unique": r[3],
        "partial_pred": r[4] or "None",
        "index_size": r[5],
        "scan_count": r[7]
    })

df_idx_cat = pd.DataFrame(idx_cat_list)
for tab in target_tables:
    print(f"\nIndexes on table '{tab}':")
    sub = df_idx_cat[df_idx_cat['table_name'] == tab]
    for _, row in sub.iterrows():
        print(f"  - Name: {row['index_name']}")
        print(f"    Definition: {row['index_def']}")
        print(f"    Size: {row['index_size']} | Scans: {row['scan_count']} | Unique: {row['is_unique']} | Partial: {row['partial_pred']}")

# ---------------------------------------------------------
# 2. RESOLVE STATION HISTORY INDEX CLAIM
# ---------------------------------------------------------
print("\n--- 2. STATION HISTORY INDEX & VIEW ANALYSIS ---")

cur.execute("""
    SELECT definition 
    FROM pg_views 
    WHERE viewname = 'vw_station_wawqi_history';
""")
vw_hist_def = cur.fetchone()
print("Definition of 'vw_station_wawqi_history':")
if vw_hist_def:
    print(vw_hist_def[0])

# Check indexes on water_samples again specifically for (location_id, sample_date)
cur.execute("""
    SELECT i.relname, pg_get_indexdef(idx.indexrelid)
    FROM pg_index idx
    JOIN pg_class c ON c.oid = idx.indrelid
    JOIN pg_class i ON i.oid = idx.indexrelid
    WHERE c.relname = 'water_samples';
""")
ws_indexes = cur.fetchall()
print("\nExplicit water_samples index definitions:")
for r in ws_indexes:
    print(f"  {r[0]}: {r[1]}")

# ---------------------------------------------------------
# 3. VERIFY SAMPLE_PARAMETER_VALUES INDEX OVERLAP
# ---------------------------------------------------------
print("\n--- 3. VERIFY SAMPLE_PARAMETER_VALUES INDEX OVERLAP ---")

cur.execute("""
    SELECT i.relname, pg_get_indexdef(idx.indexrelid), pg_size_pretty(pg_relation_size(idx.indexrelid)), st.idx_scan
    FROM pg_index idx
    JOIN pg_class c ON c.oid = idx.indrelid
    JOIN pg_class i ON i.oid = idx.indexrelid
    JOIN pg_stat_user_indexes st ON st.indexrelid = idx.indexrelid
    WHERE c.relname = 'sample_parameter_values' AND i.relname IN ('idx_spv_parameter_numeric', 'idx_values_numeric', 'idx_values_parameter');
""")
spv_overlap_rows = cur.fetchall()
for r in spv_overlap_rows:
    print(f"  Index: {r[0]:<30} | Size: {r[2]:<8} | Scans: {r[3]:<6} | Def: {r[1]}")

# ---------------------------------------------------------
# 4. VERIFY WAWQI EXTREME INDEX CANDIDATE
# ---------------------------------------------------------
print("\n--- 4. VERIFY WAWQI EXTREME INDEX CANDIDATE ---")

cur.execute("""
    SELECT definition 
    FROM pg_views 
    WHERE viewname = 'vw_wawqi_extreme_values';
""")
vw_ext_def = cur.fetchone()
print("Definition of 'vw_wawqi_extreme_values':")
if vw_ext_def:
    print(vw_ext_def[0])

cur.execute("""
    EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
    SELECT sample_id, station_name, state, district, wqi, category 
    FROM vw_wawqi_extreme_values 
    ORDER BY wqi DESC 
    LIMIT 50;
""")
ext_plan = cur.fetchone()[0][0]
print(f"vw_wawqi_extreme_values EXPLAIN ANALYZE -> Execution Time: {ext_plan['Execution Time']} ms | Node: {ext_plan['Plan']['Node Type']}")

# ---------------------------------------------------------
# 5. RECHECK STATION HISTORY FOR REPRESENTATIVE STATIONS
# ---------------------------------------------------------
print("\n--- 5. RECHECK STATION HISTORY FOR REPRESENTATIVE STATIONS ---")

# Find representative station hashes
# 1. Few samples
# 2. Many samples
# 3. Unavailable samples
cur.execute("""
    SELECT station_hash, station_name, state, sample_count, data_quality_class 
    FROM mv_station_identity 
    ORDER BY sample_count DESC 
    LIMIT 3;
""")
stations_many = cur.fetchall()

cur.execute("""
    SELECT station_hash, station_name, state, sample_count, data_quality_class 
    FROM mv_station_identity 
    ORDER BY sample_count ASC 
    LIMIT 3;
""")
stations_few = cur.fetchall()

cur.execute("""
    SELECT m.station_hash, m.station_name, m.state, m.sample_count, m.wawqi_unavailable_count
    FROM mv_station_identity m
    WHERE m.wawqi_unavailable_count > 0
    ORDER BY m.wawqi_unavailable_count DESC
    LIMIT 3;
""")
stations_unavail = cur.fetchall()

test_stations = []
for s in stations_many[:1]:
    test_stations.append(("Many Samples", s[0], s[1], s[2], s[3]))
for s in stations_few[:1]:
    test_stations.append(("Few Samples", s[0], s[1], s[2], s[3]))
for s in stations_unavail[:1]:
    test_stations.append(("Unavailable Samples", s[0], s[1], s[2], s[3]))

for label, st_hash, st_name, state, sample_cnt in test_stations:
    sql = f"SELECT * FROM vw_station_wawqi_history WHERE station_hash = '{st_hash}' ORDER BY sample_date DESC"
    cur.execute(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {sql}")
    p = cur.fetchone()[0][0]
    top_p = p["Plan"]
    plan_t = p.get("Planning Time", 0.0)
    exec_t = p.get("Execution Time", 0.0)
    buf_hit = top_p.get("Shared Hit Blocks", 0)
    buf_read = top_p.get("Shared Read Blocks", 0)
    rows_ret = top_p.get("Actual Rows", 0)
    scan_type = top_p.get("Node Type", "Unknown")
    
    print(f" [{label}] Station: '{st_name}' ({state}) | Hash: {st_hash[:12]}... | SampleCount: {sample_cnt}")
    print(f"   Planning: {plan_t:.3f} ms | Exec: {exec_t:.3f} ms | Total: {plan_t+exec_t:.3f} ms | Buffers Hit: {buf_hit} Read: {buf_read} | Scan: {scan_type} | Rows Returned: {rows_ret}")

# ---------------------------------------------------------
# 6. RECHECK EXTREME QUERY AT LIMITS
# ---------------------------------------------------------
print("\n--- 6. RECHECK EXTREME QUERY AT LIMITS ---")

ext_limits = [50, 100, 500]
for lim in ext_limits:
    sql = f"SELECT * FROM vw_wawqi_extreme_values ORDER BY wqi DESC LIMIT {lim}"
    cur.execute(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {sql}")
    p = cur.fetchone()[0][0]
    top_p = p["Plan"]
    plan_t = p.get("Planning Time", 0.0)
    exec_t = p.get("Execution Time", 0.0)
    buf_hit = top_p.get("Shared Hit Blocks", 0)
    buf_read = top_p.get("Shared Read Blocks", 0)
    rows_ret = top_p.get("Actual Rows", 0)
    scan_type = top_p.get("Node Type", "Unknown")
    
    print(f" Extreme Query Limit {lim}:")
    print(f"   Planning: {plan_t:.3f} ms | Exec: {exec_t:.3f} ms | Total: {plan_t+exec_t:.3f} ms | Buffers Hit: {buf_hit} Read: {buf_read} | Scan: {scan_type} | Rows Returned: {rows_ret}")

# ---------------------------------------------------------
# 8. DATA INTEGRITY REGRESSION
# ---------------------------------------------------------
print("\n--- 8. DATA INTEGRITY REGRESSION ---")

cur.execute("SELECT COUNT(*) FROM water_samples;")
cnt_ws = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM wawqi_results WHERE calculation_status = 'SUCCESS';")
cnt_wawqi_avail = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM wawqi_results WHERE calculation_status = 'INSUFFICIENT_PARAMETER_COVERAGE';")
cnt_wawqi_unavail = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM mv_station_identity;")
cnt_stations = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM vw_gis_points;")
cnt_gis_valid = cur.fetchone()[0]

cur.execute("""
    SELECT COUNT(*) 
    FROM locations 
    WHERE latitude IS NULL OR longitude IS NULL 
       OR latitude NOT BETWEEN 6.0 AND 37.5 
       OR longitude NOT BETWEEN 68.0 AND 97.5;
""")
cnt_gis_invalid = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM sample_parameter_values;")
cnt_eav = cur.fetchone()[0]

cur.execute("SELECT wqi_category, COUNT(*) FROM vw_wawqi_categories WHERE wqi_category != 'UNAVAILABLE' GROUP BY wqi_category;")
cat_counts_raw = dict(cur.fetchall())

recon_matrix = [
    ("Total Water Samples", 165162, cnt_ws, cnt_ws - 165162),
    ("WAWQI Available", 120738, cnt_wawqi_avail, cnt_wawqi_avail - 120738),
    ("WAWQI Unavailable", 44424, cnt_wawqi_unavail, cnt_wawqi_unavail - 44424),
    ("Canonical Stations", 22753, cnt_stations, cnt_stations - 22753),
    ("Valid GIS Points", 165010, cnt_gis_valid, cnt_gis_valid - 165010),
    ("Invalid Coordinates", 152, cnt_gis_invalid, cnt_gis_invalid - 152),
    ("EAV Rows", 1609277, cnt_eav, cnt_eav - 1609277),
    ("Category: Excellent", 18821, cat_counts_raw.get('Excellent', 0), cat_counts_raw.get('Excellent', 0) - 18821),
    ("Category: Good", 17465, cat_counts_raw.get('Good', 0), cat_counts_raw.get('Good', 0) - 17465),
    ("Category: Poor", 32834, cat_counts_raw.get('Poor', 0), cat_counts_raw.get('Poor', 0) - 32834),
    ("Category: Very Poor", 22587, cat_counts_raw.get('Very Poor', 0), cat_counts_raw.get('Very Poor', 0) - 22587),
    ("Category: Unsuitable", 29031, cat_counts_raw.get('Unsuitable', 0), cat_counts_raw.get('Unsuitable', 0) - 29031)
]

df_recon = pd.DataFrame(recon_matrix, columns=["Metric", "Expected", "Actual", "Variance"])
df_recon["Status"] = df_recon["Variance"].apply(lambda v: "PASS" if v == 0 else "FAIL")
print(df_recon.to_string(index=False))

print("\n========================================================================")
print("   PHASE 12A VERIFICATION COMPLETED SUCCESSFULLY                       ")
print("========================================================================")

conn.close()
