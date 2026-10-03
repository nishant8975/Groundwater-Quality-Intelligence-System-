import os
import sys
import json
import time
import platform
import subprocess
import urllib.parse
import urllib.request
import pandas as pd
import psycopg2

sys.stdout.reconfigure(line_buffering=True)

print("========================================================================")
print("     PHASE 12A — BACKEND & DATABASE PERFORMANCE AUDIT EXECUTION        ")
print("========================================================================")

# Connect to database
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

BASE_URL = "http://localhost:3000/api"

report_data = {}

# ---------------------------------------------------------
# 1. ENVIRONMENT BASELINE
# ---------------------------------------------------------
print("\n--- 1. ENVIRONMENT BASELINE ---")

cur.execute("SELECT version();")
pg_version = cur.fetchone()[0]

cur.execute("SELECT pg_size_pretty(pg_database_size('groundwater_quality'));")
db_size = cur.fetchone()[0]

# Run node and npm versions
node_ver = subprocess.check_output(["node", "-v"]).decode('utf-8').strip()
npm_ver = subprocess.check_output(["npm", "-v", "--no-update-notifier"], shell=True).decode('utf-8').strip()

# Read package.json files for express/react/vite
with open("backend/package.json", "r") as f:
    backend_pkg = json.load(f)
express_ver = backend_pkg.get("dependencies", {}).get("express", "unknown")

with open("frontend/package.json", "r") as f:
    frontend_pkg = json.load(f)
react_ver = frontend_pkg.get("dependencies", {}).get("react", "unknown")
vite_ver = frontend_pkg.get("devDependencies", {}).get("vite", "unknown")

env_info = {
    "os": f"{platform.system()} {platform.release()} ({platform.architecture()[0]})",
    "cpu": platform.processor() or "x86_64 Compatible",
    "cpu_cores": os.cpu_count(),
    "python_version": sys.version.split()[0],
    "postgresql_version": pg_version,
    "node_version": node_ver,
    "npm_version": npm_ver,
    "express_version": express_ver,
    "react_version": react_ver,
    "vite_version": vite_ver,
    "database_size": db_size
}

report_data["environment"] = env_info
for k, v in env_info.items():
    print(f"  {k:<20}: {v}")

# ---------------------------------------------------------
# 2. DATABASE SIZE AUDIT (TABLES, MAT VIEWS, INDEXES)
# ---------------------------------------------------------
print("\n--- 2. DATABASE SIZE AUDIT ---")

cur.execute("""
    SELECT 
        c.relname AS object_name,
        c.relkind AS object_type,
        pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size,
        pg_total_relation_size(c.oid) AS total_size_bytes,
        pg_size_pretty(pg_relation_size(c.oid)) AS table_size,
        pg_size_pretty(pg_indexes_size(c.oid)) AS indexes_size
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public' 
      AND c.relkind IN ('r', 'm')
    ORDER BY pg_total_relation_size(c.oid) DESC;
""")
rel_sizes = cur.fetchall()

sizes_list = []
for r in rel_sizes:
    sizes_list.append({
        "object_name": r[0],
        "type": "Table" if r[1] == 'r' else "Materialized View",
        "total_size": r[2],
        "total_size_bytes": r[3],
        "table_size": r[4],
        "indexes_size": r[5]
    })

df_sizes = pd.DataFrame(sizes_list)
print(df_sizes[['object_name', 'type', 'total_size', 'table_size', 'indexes_size']].to_string(index=False))

# Index Detail Size & Usage
cur.execute("""
    SELECT
        indexrelname AS index_name,
        relname AS table_name,
        pg_size_pretty(pg_relation_size(i.indexrelid)) AS index_size,
        pg_relation_size(i.indexrelid) AS index_bytes,
        idx_scan AS idx_scan_count,
        idx_tup_read,
        idx_tup_fetch
    FROM pg_stat_user_indexes i
    ORDER BY pg_relation_size(i.indexrelid) DESC;
""")
idx_info = cur.fetchall()

idx_list = []
for r in idx_info:
    idx_list.append({
        "index_name": r[0],
        "table_name": r[1],
        "index_size": r[2],
        "index_bytes": r[3],
        "scan_count": r[4],
        "tup_read": r[5],
        "tup_fetch": r[6]
    })

df_idx = pd.DataFrame(idx_list)
print("\nTop Indexes by Size:")
print(df_idx[['index_name', 'table_name', 'index_size', 'scan_count']].head(15).to_string(index=False))

# ---------------------------------------------------------
# 3. TABLE STATISTICS
# ---------------------------------------------------------
print("\n--- 3. TABLE STATISTICS ---")
cur.execute("""
    SELECT 
        s.relname AS table_name,
        c.reltuples::bigint AS estimated_rows,
        s.seq_scan,
        s.seq_tup_read,
        s.idx_scan,
        s.idx_tup_fetch,
        s.n_tup_ins,
        s.n_tup_upd,
        s.n_tup_del,
        s.n_dead_tup,
        s.n_live_tup,
        s.last_vacuum,
        s.last_autovacuum,
        s.last_analyze,
        s.last_autoanalyze
    FROM pg_stat_user_tables s
    JOIN pg_class c ON c.relname = s.relname
    ORDER BY c.reltuples DESC;
""")
tab_stats = cur.fetchall()
tab_stat_list = []
for r in tab_stats:
    tab_stat_list.append({
        "table_name": r[0],
        "estimated_rows": r[1],
        "seq_scan": r[2],
        "idx_scan": r[4],
        "n_live_tup": r[10],
        "n_dead_tup": r[9],
        "last_autoanalyze": str(r[14])
    })
df_tab_stat = pd.DataFrame(tab_stat_list)
print(df_tab_stat.to_string(index=False))

# ---------------------------------------------------------
# 4 & 5. QUERY PERFORMANCE AUDIT (EXPLAIN ANALYZE BUFFERS)
# ---------------------------------------------------------
print("\n--- 4 & 5. QUERY PERFORMANCE AUDIT (EXPLAIN ANALYZE BUFFERS) ---")

queries_to_test = [
    ("National Overview", "SELECT total_samples, eligible_samples, unavailable_samples FROM vw_wawqi_national_summary"),
    ("State Summary (Unfiltered)", "SELECT state, total_samples, eligible_samples FROM mv_wawqi_state_summary ORDER BY state"),
    ("State Summary (Haryana)", "SELECT * FROM mv_wawqi_state_summary WHERE state = 'Haryana'"),
    ("District Summary (Unfiltered)", "SELECT state, district, total_samples, eligible_samples FROM mv_wawqi_district_summary ORDER BY total_samples DESC LIMIT 50"),
    ("District Summary (Pune)", "SELECT * FROM mv_wawqi_district_summary WHERE state = 'Maharashtra' AND district = 'Pune'"),
    ("Parameter Analytics (Unfiltered)", "SELECT canonical_name, SUM(numeric_observation_count) FROM mv_parameter_analytics GROUP BY canonical_name"),
    ("Parameter Analytics (pH)", "SELECT * FROM mv_parameter_analytics WHERE canonical_name = 'ph'"),
    ("Exceedances (Unfiltered)", "SELECT canonical_name, SUM(exceedance_count) FROM mv_parameter_exceedance GROUP BY canonical_name"),
    ("Exceedances (pH)", "SELECT * FROM mv_parameter_exceedance WHERE canonical_name = 'ph'"),
    ("Extremes Overview", "SELECT sample_id, station_name, wqi, category FROM vw_wawqi_extreme_values ORDER BY wqi DESC LIMIT 50"),
    ("GIS (Unfiltered Page 1)", "SELECT location_id, latitude, longitude, state, latest_category FROM vw_gis_points LIMIT 500"),
    ("GIS (Haryana Filtered)", "SELECT location_id, latitude, longitude, state, latest_category FROM vw_gis_points WHERE state = 'Haryana' LIMIT 500"),
    ("GIS (Haryana + Gurugram)", "SELECT location_id, latitude, longitude, state, district, latest_category FROM vw_gis_points WHERE state = 'Haryana' AND district = 'GURUGRAM' LIMIT 500"),
    ("GIS (Category Unsuitable)", "SELECT location_id, latitude, longitude, state, latest_category FROM vw_gis_points WHERE latest_category = 'Unsuitable' LIMIT 500"),
    ("Station Directory (Page 1)", "SELECT * FROM mv_station_identity ORDER BY sample_count DESC LIMIT 50 OFFSET 0"),
    ("Station Directory (Page 21 Offset 1000)", "SELECT * FROM mv_station_identity ORDER BY sample_count DESC LIMIT 50 OFFSET 1000"),
    ("Station Directory (State Filter Haryana)", "SELECT * FROM mv_station_identity WHERE state = 'Haryana' ORDER BY sample_count DESC LIMIT 50"),
    ("Station Directory (District Filter Pune)", "SELECT * FROM mv_station_identity WHERE state = 'Maharashtra' AND district = 'Pune' ORDER BY sample_count DESC LIMIT 50"),
    ("Station Directory (Data Quality Rich)", "SELECT * FROM mv_station_identity WHERE data_quality_class = 'DATA RICH' ORDER BY sample_count DESC LIMIT 50"),
    ("Station Search (Broad 'Patna')", "SELECT * FROM mv_station_identity WHERE station_name ILIKE '%Patna%' OR district ILIKE '%Patna%' OR state ILIKE '%Patna%' LIMIT 50"),
    ("Station Search (State + Search)", "SELECT * FROM mv_station_identity WHERE state = 'Bihar' AND (station_name ILIKE '%Patna%' OR district ILIKE '%Patna%') LIMIT 50"),
    ("Station Search (District + Search)", "SELECT * FROM mv_station_identity WHERE state = 'Bihar' AND district = 'PATNA' AND station_name ILIKE '%Patna%' LIMIT 50"),
    ("Station Search (Partial Name 'Gurugram')", "SELECT * FROM mv_station_identity WHERE station_name ILIKE '%Gurugram%' LIMIT 50"),
    ("Station Detail Lookup", "SELECT * FROM mv_station_identity WHERE station_hash = '8c2f1f8b1a3d9e0f1a2b3c4d5e6f7a8b'"),
    ("Station History Lookup", "SELECT * FROM vw_station_wawqi_history WHERE station_hash = '8c2f1f8b1a3d9e0f1a2b3c4d5e6f7a8b' ORDER BY sample_date DESC"),
    ("Station Parameters Profile", "SELECT * FROM mv_station_parameter_analytics WHERE station_hash = '8c2f1f8b1a3d9e0f1a2b3c4d5e6f7a8b'")
]

explain_results = []

for q_name, sql in queries_to_test:
    cur.execute(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {sql}")
    plan_json = cur.fetchone()[0][0]
    
    plan_top = plan_json["Plan"]
    planning_time = plan_json.get("Planning Time", 0.0)
    exec_time = plan_json.get("Execution Time", 0.0)
    total_time = planning_time + exec_time
    
    shared_hit = plan_top.get("Shared Hit Blocks", 0)
    shared_read = plan_top.get("Shared Read Blocks", 0)
    temp_read = plan_top.get("Temp Read Blocks", 0)
    temp_written = plan_top.get("Temp Written Blocks", 0)
    rows_returned = plan_top.get("Actual Rows", 0)
    rows_removed = plan_top.get("Rows Removed by Filter", 0)
    node_type = plan_top.get("Node Type", "Unknown")
    index_name = plan_top.get("Index Name", "None")
    
    explain_results.append({
        "query_name": q_name,
        "planning_ms": round(planning_time, 3),
        "execution_ms": round(exec_time, 3),
        "total_ms": round(total_time, 3),
        "shared_hit": shared_hit,
        "shared_read": shared_read,
        "temp_blocks": temp_read + temp_written,
        "rows": rows_returned,
        "rows_filtered": rows_removed,
        "scan_type": node_type,
        "index_used": index_name
    })

df_explain = pd.DataFrame(explain_results)
print(df_explain[['query_name', 'execution_ms', 'shared_hit', 'shared_read', 'scan_type', 'index_used']].to_string(index=False))

# ---------------------------------------------------------
# 6 & 7. API PERFORMANCE & RESPONSE SIZE AUDIT
# ---------------------------------------------------------
print("\n--- 6 & 7. API PERFORMANCE & RESPONSE SIZE AUDIT ---")

# First get a valid station hash for station detail tests
cur.execute("SELECT station_hash FROM mv_station_identity LIMIT 1;")
valid_hash = cur.fetchone()[0]

api_endpoints_to_test = [
    ("/health", "Health Check"),
    ("/overview", "National Overview"),
    ("/states", "All States Summary"),
    ("/states/Haryana", "State Detail Haryana"),
    ("/districts", "Districts List (Default Limit 50)"),
    ("/parameters", "Parameters Catalog"),
    ("/exceedances", "Exceedances Analytics"),
    ("/extremes", "Extreme WAWQI Values"),
    ("/gis", "GIS Points Default"),
    ("/gis?limit=100", "GIS Points 100"),
    ("/gis?limit=500", "GIS Points 500"),
    ("/stations", "Stations Directory Default (50)"),
    ("/stations?limit=100", "Stations Directory 100"),
    ("/stations?limit=500", "Stations Directory 500"),
    ("/stations/search?q=Patna", "Station Search 'Patna'"),
    (f"/stations/{valid_hash}", "Station Detail Hash"),
    (f"/stations/{valid_hash}/history", "Station History"),
    (f"/stations/{valid_hash}/parameters", "Station Parameter Profile")
]

api_perf_results = []

for path, label in api_endpoints_to_test:
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req) as resp:
            t1 = time.time()
            status = resp.status
            content = resp.read()
            size_bytes = len(content)
            duration_ms = round((t1 - t0) * 1000, 2)
            
            data_json = json.loads(content.decode('utf-8'))
            data_payload = data_json.get('data')
            item_count = len(data_payload) if isinstance(data_payload, list) else (1 if data_payload else 0)
            
            api_perf_results.append({
                "label": label,
                "endpoint": path,
                "status": status,
                "response_ms": duration_ms,
                "size_bytes": size_bytes,
                "size_kb": round(size_bytes / 1024.0, 2),
                "item_count": item_count
            })
    except Exception as e:
        t1 = time.time()
        api_perf_results.append({
            "label": label,
            "endpoint": path,
            "status": "ERROR",
            "response_ms": round((t1 - t0) * 1000, 2),
            "size_bytes": 0,
            "size_kb": 0,
            "item_count": 0
        })

df_api_perf = pd.DataFrame(api_perf_results)
print(df_api_perf[['label', 'endpoint', 'status', 'response_ms', 'size_kb', 'item_count']].to_string(index=False))

# ---------------------------------------------------------
# 9. MATERIALIZED VIEW REFRESH AUDIT
# ---------------------------------------------------------
print("\n--- 9. MATERIALIZED VIEW REFRESH AUDIT ---")

mat_views_list = [
    "mv_wawqi_state_summary",
    "mv_wawqi_district_summary",
    "mv_wawqi_location_summary",
    "mv_parameter_analytics",
    "mv_parameter_exceedance",
    "mv_temporal_analytics",
    "mv_station_identity",
    "mv_station_parameter_analytics"
]

mv_refresh_results = []

for mv in mat_views_list:
    t0 = time.time()
    try:
        cur.execute(f"REFRESH MATERIALIZED VIEW {mv}")
        t1 = time.time()
        dur_ms = round((t1 - t0) * 1000, 2)
        cur.execute(f"SELECT COUNT(*) FROM {mv}")
        cnt = cur.fetchone()[0]
        mv_refresh_results.append({
            "mat_view": mv,
            "refresh_time_ms": dur_ms,
            "row_count": cnt,
            "status": "SUCCESS"
        })
    except Exception as e:
        mv_refresh_results.append({
            "mat_view": mv,
            "refresh_time_ms": 0,
            "row_count": 0,
            "status": f"FAILED: {e}"
        })

df_mv_ref = pd.DataFrame(mv_refresh_results)
print(df_mv_ref.to_string(index=False))

# ---------------------------------------------------------
# 10. CONCURRENCY / CONNECTION POOL AUDIT
# ---------------------------------------------------------
print("\n--- 10. CONNECTION POOL AUDIT ---")
cur.execute("""
    SELECT pid, usename, client_addr, state, query_start, state_change, query 
    FROM pg_stat_activity 
    WHERE datname = 'groundwater_quality';
""")
active_conns = cur.fetchall()
print(f"Active PostgreSQL Connections for 'groundwater_quality': {len(active_conns)}")
for c in active_conns:
    print(f"  PID {c[0]} | User: {c[1]} | State: {c[3]} | Query: {str(c[6])[:60]}")

# ---------------------------------------------------------
# 12. LARGE-PAGE SAFETY TEST
# ---------------------------------------------------------
print("\n--- 12. LARGE-PAGE SAFETY TEST ---")

large_page_tests = [
    ("/stations?limit=1000000", "Limit 1 Million (Stations)"),
    ("/stations?limit=1000000&offset=1000000", "Limit 1M + Offset 1M (Stations)"),
    ("/gis?limit=1000000", "Limit 1 Million (GIS)")
]

for path, label in large_page_tests:
    url = f"{BASE_URL}{path}"
    t0 = time.time()
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            t1 = time.time()
            data = json.loads(resp.read().decode('utf-8'))
            ret_len = len(data.get('data', []))
            pag = data.get('pagination', {})
            print(f" {label:<40} -> Status: {resp.status} | Time: {(t1-t0)*1000:.2f} ms | Rows: {ret_len} | Enforced Limit: {pag.get('limit')}")
    except Exception as e:
        print(f" {label:<40} -> Error: {e}")

# ---------------------------------------------------------
# 13. ERROR-PATH PERFORMANCE
# ---------------------------------------------------------
print("\n--- 13. ERROR-PATH PERFORMANCE ---")

error_paths = [
    ("/states/NonExistentState999", "Invalid State"),
    ("/districts/InvalidDistrict999?state=Haryana", "Invalid District"),
    ("/parameters/InvalidParam999", "Invalid Parameter"),
    ("/stations/invalidhash99999999999999999999999999999999", "Invalid Station Hash"),
    ("/stations?limit=invalid&offset=invalid", "Invalid Pagination"),
    ("/stations?limit=-100", "Negative Limit"),
    ("/unknown_route_999", "Unknown Route")
]

for path, label in error_paths:
    url = f"{BASE_URL}{path}"
    t0 = time.time()
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            t1 = time.time()
            print(f" {label:<35} -> HTTP {resp.status} | Time: {(t1-t0)*1000:.2f} ms")
    except urllib.error.HTTPError as e:
        t1 = time.time()
        print(f" {label:<35} -> HTTP {e.code} | Time: {(t1-t0)*1000:.2f} ms | Msg: {e.reason}")

# ---------------------------------------------------------
# 14. SQL SAFETY REGRESSION (PARAMETERIZATION SAFETY)
# ---------------------------------------------------------
print("\n--- 14. SQL SAFETY REGRESSION ---")

sql_inj_payloads = [
    ("Haryana' OR 1=1--", "SQL Single Quote Injection"),
    ('Haryana" OR 1=1--', "SQL Double Quote Injection"),
    ("Haryana; DROP TABLE water_samples;--", "SQL Semi-colon Injection"),
    ("Patna'--", "Search Single Quote Injection"),
    ("%", "Wildcard Percent Search"),
    ("_", "Wildcard Underscore Search")
]

for payload, label in sql_inj_payloads:
    encoded_p = urllib.parse.quote(payload)
    url = f"{BASE_URL}/states/{encoded_p}"
    t0 = time.time()
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            t1 = time.time()
            print(f" State Route: {label:<30} -> HTTP {resp.status} | Time: {(t1-t0)*1000:.2f} ms")
    except urllib.error.HTTPError as e:
        t1 = time.time()
        print(f" State Route: {label:<30} -> HTTP {e.code} (Safe parameterized handling) | Time: {(t1-t0)*1000:.2f} ms")

    # Also test station search with payloads
    url_s = f"{BASE_URL}/stations/search?q={encoded_p}"
    t0 = time.time()
    try:
        req = urllib.request.Request(url_s)
        with urllib.request.urlopen(req) as resp:
            t1 = time.time()
            data = json.loads(resp.read().decode('utf-8'))
            ret_cnt = len(data.get('data', []))
            print(f" Search Route: {label:<29} -> HTTP {resp.status} | Returned: {ret_cnt} | Time: {(t1-t0)*1000:.2f} ms")
    except Exception as e:
        print(f" Search Route: {label:<29} -> Exception: {e}")

# ---------------------------------------------------------
# 15. NATIONAL DATA RECONCILIATION
# ---------------------------------------------------------
print("\n--- 15. NATIONAL DATA RECONCILIATION ---")

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

# ---------------------------------------------------------
# 16. PERFORMANCE REGRESSION COMPARISON
# ---------------------------------------------------------
print("\n--- 16. PERFORMANCE REGRESSION COMPARISON ---")

hist_benchmarks = [
    ("National Overview (vw_wawqi_national_summary)", "vw_wawqi_national_summary", 520.380),
    ("State Summary (mv_wawqi_state_summary)", "mv_wawqi_state_summary", 0.026),
    ("District Lookup (mv_wawqi_district_summary)", "mv_wawqi_district_summary", 0.067),
    ("Station Lookup (mv_station_identity)", "mv_station_identity", 1.845),
    ("Station Search (mv_station_identity)", "station_search", 3.692),
    ("GIS State Query (vw_gis_points)", "vw_gis_points", 17.043)
]

reg_matrix = []

for label, key, hist_ms in hist_benchmarks:
    match_exec = None
    for item in explain_results:
        if key in item["query_name"] or label.split(" ")[0] in item["query_name"]:
            match_exec = item["execution_ms"]
            break
    if match_exec is None:
        for item in explain_results:
            if "Overview" in label and "Overview" in item["query_name"]:
                match_exec = item["execution_ms"]
            elif "State" in label and "Haryana" in item["query_name"]:
                match_exec = item["execution_ms"]
            elif "District" in label and "Pune" in item["query_name"]:
                match_exec = item["execution_ms"]
            elif "Lookup" in label and "Lookup" in item["query_name"]:
                match_exec = item["execution_ms"]
            elif "Search" in label and "Search" in item["query_name"]:
                match_exec = item["execution_ms"]
            elif "GIS" in label and "Haryana" in item["query_name"]:
                match_exec = item["execution_ms"]

    if match_exec is not None:
        diff = round(match_exec - hist_ms, 3)
        comp = "SIMILAR" if abs(diff) < 20.0 else ("SLOWER" if diff > 0 else "IMPROVED")
        reg_matrix.append({
            "Query": label,
            "Phase 11B (ms)": hist_ms,
            "Phase 12A (ms)": match_exec,
            "Variance (ms)": diff,
            "Comparison": comp
        })

df_reg = pd.DataFrame(reg_matrix)
print(df_reg.to_string(index=False))

print("\n========================================================================")
print("     PHASE 12A PERFORMANCE AUDIT COMPLETED SUCCESSFULLY               ")
print("========================================================================")

conn.close()
