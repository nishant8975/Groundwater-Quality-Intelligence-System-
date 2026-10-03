import os
import glob
import json
import time
import urllib.parse
import urllib.request
import pandas as pd
import psycopg2

conn = psycopg2.connect('dbname=groundwater_quality user=postgres password=Nishant@2003 host=localhost port=5432')
cur = conn.cursor()

print("========================================================================")
print("             PHASE 11B — API & ANALYTICS VALIDATION SCRIPT              ")
print("========================================================================")

# 2. PostgreSQL Analytics Object Inventory
print("\n--- 2. ANALYTICS OBJECT INVENTORY ---")
views = [
    "vw_wawqi_national_summary",
    "vw_wawqi_categories",
    "vw_wawqi_extreme_values",
    "vw_data_quality_analytics",
    "vw_gis_points",
    "vw_station_wawqi_history"
]

mat_views = [
    "mv_wawqi_state_summary",
    "mv_wawqi_district_summary",
    "mv_wawqi_location_summary",
    "mv_parameter_analytics",
    "mv_parameter_exceedance",
    "mv_temporal_analytics",
    "mv_station_identity",
    "mv_station_parameter_analytics"
]

inventory = []

for v in views:
    cur.execute("SELECT COUNT(*) FROM " + v)
    cnt = cur.fetchone()[0]
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", (v,))
    cols = [r[0] for r in cur.fetchall()]
    inventory.append({
        'object_name': v,
        'type': 'View',
        'row_count': cnt,
        'key_columns': cols[:4],
        'index_count': 0
    })

for mv in mat_views:
    cur.execute("SELECT COUNT(*) FROM " + mv)
    cnt = cur.fetchone()[0]
    cur.execute("""
        SELECT a.attname
        FROM pg_attribute a
        JOIN pg_class c ON a.attrelid = c.oid
        JOIN pg_namespace n ON c.relnamespace = n.oid
        WHERE c.relname = %s AND a.attnum > 0 AND NOT a.attisdropped
    """, (mv,))
    cols = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT COUNT(*) FROM pg_indexes WHERE tablename = %s", (mv,))
    idx_cnt = cur.fetchone()[0]
    inventory.append({
        'object_name': mv,
        'type': 'Materialized View',
        'row_count': cnt,
        'key_columns': cols[:4],
        'index_count': idx_cnt
    })

df_inv = pd.DataFrame(inventory)
print(df_inv.to_string(index=False))

# 3. National Analytics Reconciliation
print("\n--- 3. NATIONAL ANALYTICS RECONCILIATION ---")
cur.execute("SELECT total_samples, eligible_samples, unavailable_samples FROM vw_wawqi_national_summary")
nat_res = cur.fetchone()
print(f"vw_wawqi_national_summary -> Total: {nat_res[0]:,}, Eligible: {nat_res[1]:,}, Unavailable: {nat_res[2]:,}")

cur.execute("SELECT wqi_category, COUNT(*) FROM vw_wawqi_categories GROUP BY wqi_category ORDER BY COUNT(*) DESC")
cat_rows = cur.fetchall()
print("vw_wawqi_categories ->", cat_rows)
cat_sum = sum(r[1] for r in cat_rows if r[0] != 'UNAVAILABLE')
print(f"Category Sum (Available) = {cat_sum:,} | Target = 120,738 | Variance = {cat_sum - 120738}")

# 4. State Analytics Validation
print("\n--- 4. STATE ANALYTICS VALIDATION (30-State DB vs API Reconciliation) ---")
cur.execute("""
    SELECT 
        state, total_samples, eligible_samples, unavailable_samples,
        excellent_count, good_count, poor_count, very_poor_count, unsuitable_count,
        median_wqi, avg_wqi
    FROM mv_wawqi_state_summary
    ORDER BY state
""")
db_states = cur.fetchall()

base_url = "http://localhost:3000/api"
state_reconcile = []

for r in db_states:
    st = r[0]
    encoded_st = urllib.parse.quote(st, safe='')
    url = f"{base_url}/states/{encoded_st}"
    api_samp = None
    api_avail = None
    api_unavail = None
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('success'):
                d = data.get('data', {})
                api_samp = int(d.get('total_samples')) if d.get('total_samples') is not None else None
                api_avail = int(d.get('eligible_samples')) if d.get('eligible_samples') is not None else None
                api_unavail = int(d.get('unavailable_samples')) if d.get('unavailable_samples') is not None else None
    except Exception as e:
        api_samp = f"ERROR: {e}"

    diff_samp = api_samp - r[1] if isinstance(api_samp, int) else 'N/A'
    diff_avail = api_avail - r[2] if isinstance(api_avail, int) else 'N/A'
    
    state_reconcile.append({
        'state': st,
        'db_samples': r[1],
        'api_samples': api_samp,
        'diff_samples': diff_samp,
        'db_avail': r[2],
        'api_avail': api_avail,
        'diff_avail': diff_avail,
        'db_unavail': r[3],
        'median_wqi': float(r[9]) if r[9] is not None else None,
        'status': 'MATCH' if diff_samp == 0 and diff_avail == 0 else 'MISMATCH'
    })

df_st_val = pd.DataFrame(state_reconcile)
print(df_st_val.to_string(index=False))

# 5. District Analytics Validation
print("\n--- 5. DISTRICT ANALYTICS VALIDATION ---")
cur.execute("SELECT COUNT(*) FROM mv_wawqi_district_summary")
print("Total districts in mv_wawqi_district_summary:", cur.fetchone()[0])

sample_districts = [
    ('Maharashtra', 'Pune'),
    ('Rajasthan', 'JAIPUR'),
    ('Karnataka', 'Mysore'),
    ('Haryana', 'GURUGRAM'),
    ('Tamil Nadu', 'Chennai')
]

for st, dist in sample_districts:
    cur.execute("SELECT district, total_samples, eligible_samples, unavailable_samples, median_wqi FROM mv_wawqi_district_summary WHERE state = %s AND district ILIKE %s", (st, dist))
    db_d = cur.fetchone()
    encoded_st = urllib.parse.quote(st)
    encoded_d = urllib.parse.quote(dist)
    url = f"{base_url}/districts/{encoded_d}?state={encoded_st}"
    api_d = None
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            api_d = data.get('data')
    except Exception as e:
        api_d = f"ERROR: {e}"
    print(f" District {dist} ({st}) -> DB: {db_d} | API: {api_d}")

# 6. Parameter Analytics Validation
print("\n--- 6. PARAMETER ANALYTICS VALIDATION ---")
cur.execute("SELECT COUNT(*), COUNT(numeric_value), COUNT(*) FILTER (WHERE is_missing = TRUE) FROM sample_parameter_values")
spv_counts = cur.fetchone()
print(f"EAV sample_parameter_values -> Total: {spv_counts[0]:,}, Numeric: {spv_counts[1]:,}, Null Markers: {spv_counts[2]}")

cur.execute("SELECT canonical_name, SUM(numeric_observation_count) AS total_obs FROM mv_parameter_analytics GROUP BY canonical_name ORDER BY total_obs DESC LIMIT 5")
print("Top 5 parameters in mv_parameter_analytics:")
for r in cur.fetchall():
    print(" ", r)

# 7. Exceedance Analytics Validation
print("\n--- 7. EXCEEDANCE ANALYTICS VALIDATION ---")
cur.execute("SELECT canonical_name, SUM(valid_measurement_count), SUM(exceedance_count) FROM mv_parameter_exceedance GROUP BY canonical_name ORDER BY SUM(exceedance_count) DESC LIMIT 5")
print("Top exceedance parameters in DB:")
for r in cur.fetchall():
    print(" ", r)

url = f"{base_url}/exceedances?parameter=ph"
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as resp:
    ph_exc = json.loads(resp.read().decode('utf-8'))
    print("pH Exceedance API Response:", ph_exc.get('data'))

# 8. Extreme WAWQI Validation
print("\n--- 8. EXTREME WAWQI VALIDATION ---")
cur.execute("SELECT COUNT(*) FROM vw_wawqi_extreme_values")
print("vw_wawqi_extreme_values total count:", cur.fetchone()[0])

benchmarks = [62753, 408, 1419]
for sid in benchmarks:
    cur.execute("SELECT sample_id, state, district, station_name, wqi, category, data_quality_flags FROM vw_wawqi_extreme_values WHERE sample_id = %s", (sid,))
    print(f" Extreme Sample {sid}:", cur.fetchone())

# 9. Data Quality API Validation
print("\n--- 9. DATA QUALITY API VALIDATION ---")
url = f"{base_url}/data-quality"
with urllib.request.urlopen(urllib.request.Request(url)) as resp:
    dq_api = json.loads(resp.read().decode('utf-8'))
    print("Data Quality API Response:", dq_api.get('data'))

# 10. GIS API Validation
print("\n--- 10. GIS API VALIDATION ---")
cur.execute("SELECT COUNT(*) FROM vw_gis_points")
print("vw_gis_points count:", cur.fetchone()[0])
url = f"{base_url}/gis?limit=10"
with urllib.request.urlopen(urllib.request.Request(url)) as resp:
    gis_api = json.loads(resp.read().decode('utf-8'))
    print(f"GIS API Response -> Count: {len(gis_api.get('data', []))}, Total in Pagination: {gis_api.get('pagination', {}).get('total')}")

# 11 & 12. Station API & Search Validation
print("\n--- 11 & 12. STATION API & SEARCH VALIDATION ---")
cur.execute("SELECT COUNT(*), SUM(sample_count), COUNT(CASE WHEN data_quality_class = 'DATA RICH' THEN 1 END), COUNT(CASE WHEN data_quality_class = 'DATA LIMITED' THEN 1 END) FROM mv_station_identity")
st_stats = cur.fetchone()
print(f"mv_station_identity -> Stations: {st_stats[0]:,}, Samples Sum: {st_stats[1]:,}, Rich: {st_stats[2]:,}, Limited: {st_stats[3]:,}")

t0 = time.time()
url1 = f"{base_url}/stations/search?q=Haryana&limit=10"
with urllib.request.urlopen(urllib.request.Request(url1)) as resp:
    s_res1 = json.loads(resp.read().decode('utf-8'))
t1 = time.time()

url2 = f"{base_url}/stations/search?search=Haryana&limit=10"
with urllib.request.urlopen(urllib.request.Request(url2)) as resp:
    s_res2 = json.loads(resp.read().decode('utf-8'))

print(f"Station Search API ?q=Haryana -> Len: {len(s_res1.get('data', []))}, Time: {(t1-t0)*1000:.2f} ms")
print(f"Station Search API ?search=Haryana -> Len: {len(s_res2.get('data', []))}")

# 13. Pagination Validation
print("\n--- 13. PAGINATION VALIDATION ---")
pag_tests = [
    ("limit=10", 10),
    ("limit=50", 50),
    ("limit=500", 500),
    ("limit=1000000", 500), # should cap at max limit 500
    ("limit=-5", 50), # fallback default
    ("limit=abc", 50)  # fallback default
]

for query_param, expected_len in pag_tests:
    url = f"{base_url}/stations?{query_param}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url)) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            returned_len = len(data.get('data', []))
            pag_info = data.get('pagination', {})
            print(f" Query ?{query_param:<15} -> Returned rows: {returned_len} | Limit in metadata: {pag_info.get('limit')} (Expected <= {expected_len})")
    except Exception as e:
        print(f" Query ?{query_param:<15} -> Error: {e}")

# 15. Error Handling Validation
print("\n--- 15. ERROR HANDLING VALIDATION ---")
error_tests = [
    ("/states/NonExistentState123", 404),
    ("/districts/NonExistentDistrict123", 404),
    ("/stations/invalidhash123", 404),
    ("/parameters/NonExistentParam", 404),
    ("/unknown_route", 404)
]

for ep, expected_code in error_tests:
    url = f"{base_url}{ep}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            code = resp.getcode()
            print(f" GET {ep:<35} -> HTTP {code} (Expected {expected_code})")
    except urllib.error.HTTPError as e:
        print(f" GET {ep:<35} -> HTTP {e.code} | Message: {e.reason}")

# 16. API vs Database Reconciliation Matrix
print("\n--- 16. API vs DATABASE RECONCILIATION MATRIX ---")
api_db_tests = [
    ("overview", "vw_wawqi_national_summary", "total_samples", "SELECT total_samples FROM vw_wawqi_national_summary"),
    ("states", "mv_wawqi_state_summary", "state_count", "SELECT COUNT(*) FROM mv_wawqi_state_summary"),
    ("districts", "mv_wawqi_district_summary", "district_count", "SELECT COUNT(*) FROM mv_wawqi_district_summary"),
    ("parameters", "parameters", "parameter_count", "SELECT COUNT(*) FROM parameters"),
    ("extremes", "vw_wawqi_extreme_values", "extreme_count", "SELECT COUNT(*) FROM vw_wawqi_extreme_values"),
    ("gis", "vw_gis_points", "valid_gis_count", "SELECT COUNT(*) FROM vw_gis_points"),
    ("stations", "mv_station_identity", "station_count", "SELECT COUNT(*) FROM mv_station_identity"),
    ("temporal", "mv_temporal_analytics", "temporal_row_count", "SELECT COUNT(*) FROM mv_temporal_analytics")
]

matrix = []
for ep, source_obj, metric, sql in api_db_tests:
    cur.execute(sql)
    db_val = cur.fetchone()[0]
    url = f"{base_url}/{ep}"
    api_val = None
    try:
        with urllib.request.urlopen(urllib.request.Request(url)) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if ep == "overview":
                api_val = int(data.get('data', {}).get('total_samples'))
            elif ep == "gis":
                api_val = int(data.get('pagination', {}).get('total'))
            elif ep == "stations":
                api_val = int(data.get('pagination', {}).get('total'))
            elif ep == "extremes":
                api_val = int(data.get('pagination', {}).get('total'))
            elif isinstance(data.get('data'), list):
                api_val = len(data.get('data'))
            elif 'count' in data:
                api_val = int(data.get('count'))
    except Exception as e:
        api_val = f"ERROR: {e}"

    variance = api_val - db_val if isinstance(api_val, int) else 'N/A'
    status = 'PASS' if variance == 0 else 'CHECK'
    matrix.append({
        'endpoint': f"/api/{ep}",
        'source_object': source_obj,
        'metric_name': metric,
        'db_value': db_val,
        'api_value': api_val,
        'variance': variance,
        'status': status
    })

df_matrix = pd.DataFrame(matrix)
print(df_matrix.to_string(index=False))

# 17. Temporal Analytics
print("\n--- 17. TEMPORAL ANALYTICS VALIDATION ---")
cur.execute("SELECT COUNT(*), MIN(sample_year), MAX(sample_year) FROM mv_temporal_analytics")
t_row = cur.fetchone()
print(f"mv_temporal_analytics -> Total Years: {t_row[0]}, Min Year: {t_row[1]}, Max Year: {t_row[2]}")

# 19. Performance Sampling (EXPLAIN ANALYZE)
print("\n--- 19. PERFORMANCE SAMPLING (EXPLAIN ANALYZE) ---")
perf_queries = {
    "State Summary": "SELECT state, total_samples, eligible_samples FROM mv_wawqi_state_summary",
    "National Summary": "SELECT * FROM vw_wawqi_national_summary",
    "Category Summary": "SELECT * FROM vw_wawqi_categories",
    "Station Lookup": "SELECT * FROM mv_station_identity WHERE station_hash = '8c2f1f8b1a3d9e0f1a2b3c4d5e6f7a8b'",
    "Station Search": "SELECT * FROM mv_station_identity WHERE station_name ILIKE '%Haryana%' OR district ILIKE '%Haryana%' OR state ILIKE '%Haryana%' LIMIT 50",
    "GIS State Filter": "SELECT location_id, latitude, longitude, state FROM vw_gis_points WHERE state = 'Haryana' LIMIT 100",
    "District Lookup": "SELECT * FROM mv_wawqi_district_summary WHERE state = 'Maharashtra' AND district = 'Pune'"
}

for q_name, q_sql in perf_queries.items():
    conn.rollback()
    try:
        cur.execute(f"EXPLAIN ANALYZE {q_sql}")
        plan_lines = cur.fetchall()
        exec_time = [line[0] for line in plan_lines if 'Execution Time' in line[0]]
        planning_time = [line[0] for line in plan_lines if 'Planning Time' in line[0]]
        print(f"  - {q_name:<25} : {exec_time[0] if exec_time else 'N/A'} | {planning_time[0] if planning_time else 'N/A'}")
    except Exception as e:
        print(f"  - {q_name:<25} : EXPLAIN ERROR ({e})")

print("\n========================================================================")
print("             PHASE 11B VALIDATION SCRIPT COMPLETED                      ")
print("========================================================================")
