import pandas as pd
import numpy as np
import json
from psycopg2.extras import RealDictCursor
from scripts.etl.loader import get_connection

def setup_wawqi_table(conn):
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS wawqi_results (
            sample_id INTEGER PRIMARY KEY REFERENCES water_samples(sample_id),
            wqi NUMERIC(20, 6),
            valid_parameter_count INTEGER,
            parameters_used JSONB,
            calculation_status VARCHAR(50),
            data_quality_flags JSONB,
            calculation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            methodology_version VARCHAR(50)
        );
    ''')
    cur.execute('ALTER TABLE wawqi_results ADD COLUMN IF NOT EXISTS parameter_sub_indices JSONB;')
    conn.commit()
    cur.close()

# Standards Definition
standards = {
    'ph': {'Si': 8.5, 'Vo': 7.0},
    'chloride': {'Si': 250.0, 'Vo': 0.0},
    'sulphate': {'Si': 200.0, 'Vo': 0.0},
    'hardness': {'Si': 200.0, 'Vo': 0.0},
    'calcium': {'Si': 75.0, 'Vo': 0.0},
    'magnesium': {'Si': 30.0, 'Vo': 0.0},
    'iron': {'Si': 0.3, 'Vo': 0.0},
    'arsenic': {'Si': 0.01, 'Vo': 0.0},
    'uranium': {'Si': 0.03, 'Vo': 0.0},
}

def calculate_wqi_for_sample(measurements, sample_id=None):
    valid_measurements = {k: v for k, v in measurements.items() if v is not None and not np.isnan(v)}
    
    if len(valid_measurements) < 6:
        return None, len(valid_measurements), list(valid_measurements.keys()), 'INSUFFICIENT_PARAMETER_COVERAGE', None
        
    sum_1_over_Si = 0.0
    for param in valid_measurements:
        if param in standards:
            sum_1_over_Si += 1.0 / standards[param]['Si']
            
    if sum_1_over_Si == 0:
        return None, len(valid_measurements), list(valid_measurements.keys()), 'CALCULATION_ERROR', None
        
    K = 1.0 / sum_1_over_Si
    
    sum_Wi = 0.0
    sum_Wi_qi = 0.0
    sub_indices = {}
    
    for param, Vi in valid_measurements.items():
        if param not in standards:
            continue
            
        Si = standards[param]['Si']
        Vo = standards[param]['Vo']
        
        Wi = K / Si
        sum_Wi += Wi
        
        if param == 'ph':
            qi = 100.0 * abs(Vi - Vo) / (Si - Vo)
        else:
            qi = 100.0 * (Vi - Vo) / (Si - Vo)
            
        if qi < 0:
            qi = 0.0
            
        Wi_qi = Wi * qi
        sum_Wi_qi += Wi_qi
        sub_indices[param] = float(Wi_qi)
        
    wqi = sum_Wi_qi / sum_Wi
    
    status = 'SUCCESS'
    return wqi, len(valid_measurements), list(valid_measurements.keys()), status, sub_indices

def run_production_wawqi():
    conn = get_connection()
    setup_wawqi_table(conn)
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Pre-flight row counts
    cur.execute("SELECT COUNT(*) as c FROM water_samples")
    pre_water_samples = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) as c FROM sample_parameter_values")
    pre_spv = cur.fetchone()['c']
    
    # Fetch all samples
    query = '''
    SELECT s.sample_id,
           json_object_agg(p.canonical_name, spv.numeric_value) FILTER (WHERE p.canonical_name IN ('ph', 'chloride', 'sulphate', 'hardness', 'calcium', 'magnesium', 'iron', 'arsenic', 'uranium')) as measurements
    FROM water_samples s
    LEFT JOIN sample_parameter_values spv ON s.sample_id = spv.sample_id
    LEFT JOIN parameters p ON spv.parameter_id = p.parameter_id
    GROUP BY s.sample_id
    '''
    cur.execute(query)
    samples = cur.fetchall()
    
    results = []
    for row in samples:
        m = row['measurements']
        if m is None:
            m = {}
            
        wqi, count, used, status, sub_indices = calculate_wqi_for_sample(m, row['sample_id'])
        
        flags = None
        if row['sample_id'] == 1419 and 'uranium' in m:
            flags = json.dumps({"uranium": "Potential source-level unit anomaly (450 mg/L). Retained raw per ETL rules."})
            
        results.append((
            row['sample_id'],
            wqi,
            count,
            json.dumps(used),
            status,
            flags,
            'Phase4_Final',
            json.dumps(sub_indices) if sub_indices is not None else None
        ))
    
    # Insert results (UPSERT for idempotency)
    insert_query = '''
        INSERT INTO wawqi_results (sample_id, wqi, valid_parameter_count, parameters_used, calculation_status, data_quality_flags, methodology_version, parameter_sub_indices)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (sample_id) DO UPDATE SET
            wqi = EXCLUDED.wqi,
            valid_parameter_count = EXCLUDED.valid_parameter_count,
            parameters_used = EXCLUDED.parameters_used,
            calculation_status = EXCLUDED.calculation_status,
            data_quality_flags = EXCLUDED.data_quality_flags,
            methodology_version = EXCLUDED.methodology_version,
            parameter_sub_indices = EXCLUDED.parameter_sub_indices,
            calculation_timestamp = CURRENT_TIMESTAMP
    '''
    cur.executemany(insert_query, results)
    conn.commit()
    
    # --- PRODUCTION VALIDATION ---
    print("--- PRODUCTION VALIDATION ---")
    
    # A. Row-count validation
    cur.execute("SELECT COUNT(*) as c FROM wawqi_results")
    total_results = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) as c FROM wawqi_results WHERE wqi IS NOT NULL")
    wqi_calculated = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) as c FROM wawqi_results WHERE wqi IS NULL")
    wqi_null = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) as c FROM wawqi_results WHERE calculation_status = 'INSUFFICIENT_PARAMETER_COVERAGE'")
    insufficient = cur.fetchone()['c']
    
    print(f"Total water_samples: {pre_water_samples}")
    print(f"Eligible samples: {wqi_calculated}")
    print(f"WQI calculated: {wqi_calculated}")
    print(f"WQI NULL: {wqi_null}")
    print(f"fewer-than-6 samples: {insufficient}")
    
    # B. Parameter coverage
    print("\n--- PARAMETER COVERAGE ---")
    for i in range(6, 10):
        cur.execute("SELECT COUNT(*) as c FROM wawqi_results WHERE valid_parameter_count = %s AND wqi IS NOT NULL", (i,))
        c = cur.fetchone()['c']
        print(f"{i} parameters: {c}")
        
    # C. WQI distribution
    print("\n--- WQI DISTRIBUTION ---")
    cur.execute("SELECT wqi FROM wawqi_results WHERE wqi IS NOT NULL")
    wqis = [float(r['wqi']) for r in cur.fetchall()]
    if wqis:
        wqis = np.array(wqis)
        print(f"Minimum: {np.min(wqis):.2f}")
        print(f"Maximum: {np.max(wqis):.2f}")
        print(f"Mean: {np.mean(wqis):.2f}")
        print(f"Median: {np.median(wqis):.2f}")
        print(f"P25: {np.percentile(wqis, 25):.2f}")
        print(f"P75: {np.percentile(wqis, 75):.2f}")
        print(f"P90: {np.percentile(wqis, 90):.2f}")
        print(f"P95: {np.percentile(wqis, 95):.2f}")
        print(f"P99: {np.percentile(wqis, 99):.2f}")
        
        c_excellent = np.sum(wqis <= 25)
        c_good = np.sum((wqis > 25) & (wqis <= 50))
        c_poor = np.sum((wqis > 50) & (wqis <= 75))
        c_vpoor = np.sum((wqis > 75) & (wqis <= 100))
        c_unsuitable = np.sum(wqis > 100)
        t = len(wqis)
        print(f"WQI <= 25: {c_excellent} ({c_excellent/t*100:.2f}%)")
        print(f"25 < WQI <= 50: {c_good} ({c_good/t*100:.2f}%)")
        print(f"50 < WQI <= 75: {c_poor} ({c_poor/t*100:.2f}%)")
        print(f"75 < WQI <= 100: {c_vpoor} ({c_vpoor/t*100:.2f}%)")
        print(f"WQI > 100: {c_unsuitable} ({c_unsuitable/t*100:.2f}%)")
        
    # D. Extreme-value inspection
    print("\n--- TOP 20 EXTREME WQI SAMPLES ---")
    cur.execute("""
        SELECT w.sample_id, l.station_name, w.wqi, w.parameters_used
        FROM wawqi_results w
        JOIN water_samples s ON w.sample_id = s.sample_id
        JOIN locations l ON s.location_id = l.location_id
        WHERE w.wqi IS NOT NULL
        ORDER BY w.wqi DESC LIMIT 20
    """)
    for r in cur.fetchall():
        print(f"Sample: {r['sample_id']}, Station: {r['station_name']}, WQI: {r['wqi']:.2f}")
        
    # 11. REPRODUCIBILITY TEST
    print("\n--- REPRODUCIBILITY TEST ---")
    # Fetch 10 samples from different coverages
    cur.execute("""
        (SELECT sample_id FROM wawqi_results WHERE valid_parameter_count = 6 AND wqi IS NOT NULL LIMIT 2)
        UNION
        (SELECT sample_id FROM wawqi_results WHERE valid_parameter_count = 7 AND wqi IS NOT NULL LIMIT 2)
        UNION
        (SELECT sample_id FROM wawqi_results WHERE valid_parameter_count = 8 AND wqi IS NOT NULL LIMIT 2)
        UNION
        (SELECT sample_id FROM wawqi_results WHERE valid_parameter_count = 9 AND wqi IS NOT NULL LIMIT 2)
        UNION
        (SELECT sample_id FROM wawqi_results WHERE parameters_used::text LIKE '%arsenic%' AND wqi IS NOT NULL LIMIT 2)
    """)
    test_ids = [r['sample_id'] for r in cur.fetchall()]
    
    for tid in test_ids[:10]:
        # get raw DB value
        cur.execute('''
        SELECT json_object_agg(p.canonical_name, spv.numeric_value) FILTER (WHERE p.canonical_name IN ('ph', 'chloride', 'sulphate', 'hardness', 'calcium', 'magnesium', 'iron', 'arsenic', 'uranium')) as measurements
        FROM sample_parameter_values spv
        JOIN parameters p ON spv.parameter_id = p.parameter_id
        WHERE spv.sample_id = %s
        ''', (tid,))
        m = cur.fetchone()['measurements']
        m = {k: v for k, v in m.items() if v is not None}
        recalc_wqi, _, _, _, _ = calculate_wqi_for_sample(m)
        
        cur.execute("SELECT wqi FROM wawqi_results WHERE sample_id = %s", (tid,))
        db_wqi = float(cur.fetchone()['wqi'])
        diff = abs(recalc_wqi - db_wqi)
        print(f"Sample {tid}: DB={db_wqi:.4f}, Recalc={recalc_wqi:.4f}, Diff={diff:.6f} -> {'PASS' if diff <= 0.01 else 'FAIL'}")

    # 12. IDEMPOTENCY
    print("\n--- IDEMPOTENCY TEST ---")
    cur.execute("SELECT COUNT(*) as c FROM wawqi_results")
    count_before = cur.fetchone()['c']
    # run exactly same insert
    cur.executemany(insert_query, results)
    conn.commit()
    cur.execute("SELECT COUNT(*) as c FROM wawqi_results")
    count_after = cur.fetchone()['c']
    print(f"Count before: {count_before}, Count after: {count_after} -> {'PASS' if count_before == count_after else 'FAIL'}")

    # 13. RAW DATA PROTECTION
    print("\n--- RAW DATA PROTECTION ---")
    cur.execute("SELECT COUNT(*) as c FROM water_samples")
    post_water_samples = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) as c FROM sample_parameter_values")
    post_spv = cur.fetchone()['c']
    print(f"Water samples: pre={pre_water_samples}, post={post_water_samples} -> {'PASS' if pre_water_samples == post_water_samples else 'FAIL'}")
    print(f"SPV values: pre={pre_spv}, post={post_spv} -> {'PASS' if pre_spv == post_spv else 'FAIL'}")

    cur.close()
    conn.close()

if __name__ == '__main__':
    run_production_wawqi()
