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

raw_dir = r"d:\PwC\Groundwater Quality Intelligence System\data\raw"
files = sorted(glob.glob(os.path.join(raw_dir, "*.csv")))

print("========================================================================")
print("             PHASE 11A — COMPREHENSIVE AUDIT SCRIPT                     ")
print("========================================================================")

# 1. Dataset Inventory & Raw to DB
print("\n--- 1 & 2 & 3. DATASET INVENTORY & RAW-TO-DB & SOURCE DATASETS ---")
raw_info = {}
total_raw_rows = 0
for f in files:
    fname = os.path.basename(f)
    try:
        df = pd.read_csv(f, low_memory=False)
        rows = len(df)
        cols = len(df.columns)
        total_raw_rows += rows
        raw_info[fname.lower()] = {
            'filename': fname,
            'raw_rows': rows,
            'cols': cols
        }
    except Exception as e:
        print(f"Error reading {fname}: {e}")

cur.execute("""
    SELECT 
        sd.dataset_id,
        sd.filename,
        sd.state_inferred,
        sd.row_count,
        COUNT(DISTINCT ws.sample_id) AS db_samples,
        COUNT(spv.sample_id) AS db_param_obs
    FROM source_datasets sd
    LEFT JOIN water_samples ws ON sd.dataset_id = ws.source_dataset_id
    LEFT JOIN sample_parameter_values spv ON ws.sample_id = spv.sample_id
    GROUP BY sd.dataset_id, sd.filename, sd.state_inferred, sd.row_count
    ORDER BY sd.dataset_id
""")
db_ds_summary = cur.fetchall()

ds_reconciliation = []
for row in db_ds_summary:
    s_id, f_name, st_name, sd_r_cnt, db_samples, param_obs = row
    r_item = raw_info.get(f_name.lower(), {'raw_rows': 0, 'cols': 0})
    raw_r = r_item['raw_rows']
    cols = r_item['cols']
    diff = db_samples - raw_r
    status = "EXACT MATCH" if diff == 0 else f"DIFF: {diff}"
    ds_reconciliation.append({
        'dataset_id': s_id,
        'filename': f_name,
        'state': st_name,
        'raw_rows': raw_r,
        'cols': cols,
        'db_samples': db_samples,
        'diff': diff,
        'param_obs': param_obs,
        'status': status
    })

df_ds = pd.DataFrame(ds_reconciliation)
print(df_ds.to_string(index=False))
print(f"\nTotal Raw Datasets: {len(raw_info)}")
print(f"Total Raw CSV Rows: {total_raw_rows:,}")
print(f"Total DB Samples across Datasets: {df_ds['db_samples'].sum():,}")
print(f"Total Source Dataset Records in DB: {len(db_ds_summary)}")

# 4 & 5 & 8 & 9 & 10. State Coverage, WAWQI, GIS, Station Reconciliation
print("\n--- 4 & 5 & 8 & 9 & 10. STATE COVERAGE, WAWQI, GIS, STATION BREAKDOWN ---")
cur.execute("""
    WITH station_stats AS (
        SELECT 
            state,
            COUNT(station_hash) AS station_count,
            COUNT(CASE WHEN data_quality_class = 'DATA RICH' THEN 1 END) AS data_rich,
            COUNT(CASE WHEN data_quality_class = 'DATA LIMITED' THEN 1 END) AS data_limited,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY sample_count) AS median_samples,
            MAX(sample_count) AS max_samples
        FROM mv_station_identity
        GROUP BY state
    )
    SELECT 
        l.state,
        COUNT(s.sample_id) AS total_samples,
        COUNT(DISTINCT s.location_id) AS location_count,
        COALESCE(st.station_count, 0) AS station_count,
        COUNT(w.wqi) AS wawqi_available,
        COUNT(s.sample_id) - COUNT(w.wqi) AS wawqi_unavailable,
        ROUND((COUNT(w.wqi)::numeric / COUNT(s.sample_id)::numeric) * 100, 2) AS eligibility_pct,
        COUNT(CASE WHEN w.wqi <= 25 THEN 1 END) AS excellent,
        COUNT(CASE WHEN w.wqi > 25 AND w.wqi <= 50 THEN 1 END) AS good,
        COUNT(CASE WHEN w.wqi > 50 AND w.wqi <= 75 THEN 1 END) AS poor,
        COUNT(CASE WHEN w.wqi > 75 AND w.wqi <= 100 THEN 1 END) AS very_poor,
        COUNT(CASE WHEN w.wqi > 100 THEN 1 END) AS unsuitable,
        COUNT(CASE WHEN l.latitude IS NOT NULL AND l.longitude IS NOT NULL AND l.coordinate_validity_flag = TRUE THEN 1 END) AS gis_valid_coords,
        COUNT(CASE WHEN l.latitude IS NULL OR l.longitude IS NULL OR l.coordinate_validity_flag = FALSE THEN 1 END) AS gis_invalid_coords,
        COALESCE(st.data_rich, 0) AS data_rich,
        COALESCE(st.data_limited, 0) AS data_limited,
        COALESCE(st.median_samples, 0) AS median_station_samples,
        COALESCE(st.max_samples, 0) AS max_station_samples
    FROM water_samples s
    JOIN locations l ON s.location_id = l.location_id
    LEFT JOIN wawqi_results w ON s.sample_id = w.sample_id
    LEFT JOIN station_stats st ON l.state = st.state
    GROUP BY l.state, st.station_count, st.data_rich, st.data_limited, st.median_samples, st.max_samples
    ORDER BY l.state
""")
state_rows = cur.fetchall()

cols_state = [
    'state', 'samples', 'locations', 'stations', 'wawqi_avail', 'wawqi_unavail', 'elig_pct',
    'excellent', 'good', 'poor', 'very_poor', 'unsuitable', 'gis_valid', 'gis_invalid',
    'data_rich', 'data_limited', 'median_station_samples', 'max_station_samples'
]
df_state = pd.DataFrame(state_rows, columns=cols_state)
print(df_state.to_string(index=False))

print("\nNATIONAL TOTALS FROM STATE BREAKDOWN:")
print(f"  Total Samples     : {df_state['samples'].sum():,}")
print(f"  Total Locations   : {df_state['locations'].sum():,}")
print(f"  Total Stations    : {df_state['stations'].sum():,}")
print(f"  WAWQI Available   : {df_state['wawqi_avail'].sum():,}")
print(f"  WAWQI Unavailable : {df_state['wawqi_unavail'].sum():,}")
print(f"  Excellent         : {df_state['excellent'].sum():,}")
print(f"  Good              : {df_state['good'].sum():,}")
print(f"  Poor              : {df_state['poor'].sum():,}")
print(f"  Very Poor         : {df_state['very_poor'].sum():,}")
print(f"  Unsuitable        : {df_state['unsuitable'].sum():,}")
print(f"  GIS Valid Coords  : {df_state['gis_valid'].sum():,}")
print(f"  GIS Invalid Coords: {df_state['gis_invalid'].sum():,}")
print(f"  DATA RICH         : {df_state['data_rich'].sum():,}")
print(f"  DATA LIMITED      : {df_state['data_limited'].sum():,}")

# 6 & 11. Parameter Observation & Coverage Reconciliation
print("\n--- 6 & 11. PARAMETER OBSERVATION RECONCILIATION ---")
cur.execute("""
    SELECT 
        p.canonical_name,
        p.display_name,
        COUNT(spv.numeric_value) AS numeric_observations,
        COUNT(*) FILTER (WHERE spv.is_missing) AS missing_count,
        COUNT(*) AS total_recorded_values,
        ROUND((COUNT(spv.numeric_value)::numeric / 165162.0) * 100, 2) AS national_coverage_pct
    FROM parameters p
    LEFT JOIN sample_parameter_values spv ON p.parameter_id = spv.parameter_id
    GROUP BY p.canonical_name, p.display_name
    ORDER BY numeric_observations DESC
""")
param_rows = cur.fetchall()
df_param = pd.DataFrame(param_rows, columns=['canonical_name', 'display_name', 'numeric_obs', 'missing_count', 'total_recorded', 'coverage_pct'])
print(df_param.to_string(index=False))

# Key Parameters by State Matrix
print("\n--- PARAMETER COVERAGE BY STATE (Key Parameters % Coverage) ---")
canonical_key_params = ['ph', 'electrical_conductivity', 'sodium', 'chloride', 'sulphate', 'hardness', 'calcium', 'magnesium', 'iron', 'arsenic', 'uranium']
cur.execute("""
    SELECT 
        l.state,
        p.canonical_name,
        COUNT(spv.numeric_value) AS obs_count
    FROM water_samples s
    JOIN locations l ON s.location_id = l.location_id
    JOIN sample_parameter_values spv ON s.sample_id = spv.sample_id
    JOIN parameters p ON spv.parameter_id = p.parameter_id
    WHERE p.canonical_name IN %s
    GROUP BY l.state, p.canonical_name
""", (tuple(canonical_key_params),))
st_p_obs = cur.fetchall()

st_p_dict = {}
for st, p_name, obs_cnt in st_p_obs:
    if st not in st_p_dict:
        st_p_dict[st] = {}
    st_p_dict[st][p_name] = obs_cnt

st_p_summary = []
for st in df_state['state']:
    st_total_s = df_state.loc[df_state['state'] == st, 'samples'].values[0]
    row_d = {'state': st, 'total_samples': st_total_s}
    for kp in canonical_key_params:
        cnt = st_p_dict.get(st, {}).get(kp, 0)
        pct = (cnt / st_total_s) * 100 if st_total_s > 0 else 0
        row_d[kp] = f"{cnt} ({pct:.1f}%)"
    st_p_summary.append(row_d)

df_st_p = pd.DataFrame(st_p_summary)
print(df_st_p.to_string(index=False))

# 7. Extreme WAWQI Validation
print("\n--- 7. EXTREME WAWQI VALIDATION BY STATE ---")
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
extreme_rows = cur.fetchall()
df_extreme = pd.DataFrame(extreme_rows, columns=['state', 'extreme_gt_100_count', 'min_wqi', 'max_wqi'])
print(df_extreme.to_string(index=False))

print("\nBenchmark Extreme Samples Check:")
for sid in [1419, 62753, 408]:
    cur.execute("""
        SELECT w.sample_id, l.state, l.district, l.station_name, w.wqi, w.calculation_status, w.data_quality_flags
        FROM wawqi_results w
        JOIN water_samples s ON w.sample_id = s.sample_id
        JOIN locations l ON s.location_id = l.location_id
        WHERE w.sample_id = %s
    """, (sid,))
    res = cur.fetchone()
    print(f" Sample {sid}: {res}")

# 12 & 13. Database Integrity & Provenance Check
print("\n--- 12 & 13. DATABASE INTEGRITY & PROVENANCE CHECK ---")
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

# 14. Analytics View Reconciliation
print("\n--- 14. ANALYTICS VIEW RECONCILIATION ---")
views = [
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

for v in views:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {v}")
        cnt = cur.fetchone()[0]
        print(f"  - {v:<35} : EXISTS | Row Count: {cnt:,}")
    except Exception as e:
        print(f"  - {v:<35} : ERROR ({e})")

# 15. API Spot Checks
print("\n--- 15. API SPOT CHECKS ---")
endpoints = [
    "/overview",
    "/states",
    "/states/Bihar",
    "/states/Assam",
    "/states/Tamil Nadu",
    "/states/Punjab",
    "/states/Haryana",
    "/gis",
    "/stations",
    "/stations/search?q=Haryana"
]

base_url = "http://localhost:3000/api"
for ep in endpoints:
    encoded_ep = urllib.parse.quote(ep, safe='/?=')
    url = base_url + encoded_ep
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            status_code = resp.getcode()
            data = json.loads(resp.read().decode('utf-8'))
            success = data.get('success', True)
            if 'data' in data:
                d = data['data']
                if isinstance(d, list):
                    info = f"List len: {len(d)}"
                elif isinstance(d, dict):
                    info = f"Keys: {list(d.keys())[:5]}"
                else:
                    info = str(d)[:30]
            elif 'count' in data:
                info = f"Count: {data['count']}"
            else:
                info = f"Keys: {list(data.keys())[:5]}"
            print(f"  - GET {ep:<30} -> HTTP {status_code} | Success: {success} | {info}")
    except Exception as e:
        print(f"  - GET {ep:<30} -> ERROR: {e}")

# 16. Five-State Cross-Check
print("\n--- 16. FIVE-STATE CROSS-CHECK ---")
five_states = ['Bihar', 'Assam', 'Tamil Nadu', 'Punjab', 'Haryana']
cur.execute("""
    SELECT 
        l.state,
        COUNT(DISTINCT l.district) AS district_count,
        COUNT(DISTINCT md5(concat_ws('||', TRIM(LOWER(l.station_name)), TRIM(LOWER(l.state)), TRIM(LOWER(l.district))))) AS station_count,
        COUNT(s.sample_id) AS sample_count,
        COUNT(CASE WHEN l.latitude IS NOT NULL AND l.longitude IS NOT NULL AND l.coordinate_validity_flag = TRUE THEN 1 END) AS gis_point_count,
        COUNT(w.wqi) FILTER (WHERE w.wqi > 100) AS extreme_wawqi_count,
        COUNT(w.wqi) AS wawqi_available,
        COUNT(s.sample_id) - COUNT(w.wqi) AS wawqi_unavailable
    FROM water_samples s
    JOIN locations l ON s.location_id = l.location_id
    LEFT JOIN wawqi_results w ON s.sample_id = w.sample_id
    WHERE l.state IN %s
    GROUP BY l.state
    ORDER BY l.state
""", (tuple(five_states),))
five_rows = cur.fetchall()
df_five = pd.DataFrame(five_rows, columns=['state', 'district_count', 'station_count', 'sample_count', 'gis_point_count', 'extreme_wawqi_count', 'wawqi_available', 'wawqi_unavailable'])
print(df_five.to_string(index=False))

# 19. Performance Measurements (EXPLAIN ANALYZE)
print("\n--- 19. PERFORMANCE MEASUREMENTS (EXPLAIN ANALYZE) ---")
perf_queries = {
    "State Summary": "SELECT state, sample_count, wawqi_available_count FROM mv_wawqi_state_summary",
    "National Summary": "SELECT * FROM vw_wawqi_national_summary",
    "WAWQI Category Summary": "SELECT * FROM vw_wawqi_categories",
    "Station Aggregation": "SELECT state, data_quality_class, COUNT(*) FROM mv_station_identity GROUP BY state, data_quality_class",
    "GIS State Filtering": "SELECT location_id, latitude, longitude, state FROM vw_gis_points WHERE state = 'Haryana'"
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
print("                    AUDIT SCRIPT COMPLETED                              ")
print("========================================================================")
