import psycopg2
import json

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="groundwater_quality",
    user="postgres",
    password="Nishant@2003"
)
cur = conn.cursor()

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

def calculate_wawqi(sample_id):
    cur.execute("""
        SELECT p.canonical_name, spv.numeric_value
        FROM sample_parameter_values spv
        JOIN parameters p ON spv.parameter_id = p.parameter_id
        WHERE spv.sample_id = %s AND spv.numeric_value IS NOT NULL
    """, (sample_id,))
    rows = cur.fetchall()
    
    if not rows:
        return None
        
    valid_measurements = {r[0]: float(r[1]) for r in rows if r[0] in standards}
    
    sum_1_over_Si = sum(1.0 / standards[p]['Si'] for p in valid_measurements)
    K = 1.0 / sum_1_over_Si
    
    sum_Wi = 0.0
    sum_Wi_qi = 0.0
    param_calc = {}
    max_wi_qi = -1.0
    dominant_param = None
    
    for param, Vi in valid_measurements.items():
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
        
        if Wi_qi > max_wi_qi:
            max_wi_qi = Wi_qi
            dominant_param = param
            
        param_calc[param] = {
            "val": Vi,
            "std": Si,
            "qi": qi,
            "Wi": Wi,
            "wi_qi": Wi_qi
        }
        
    final_wqi = sum_Wi_qi / sum_Wi
    
    cur.execute("""
        SELECT wqi, calculation_status, parameter_sub_indices, data_quality_flags
        FROM wawqi_results WHERE sample_id = %s
    """, (sample_id,))
    stored = cur.fetchone()
    
    return {
        "sample_id": sample_id,
        "calculated_wqi": final_wqi,
        "dominant_param": dominant_param,
        "max_wi_qi": max_wi_qi,
        "param_calc": param_calc,
        "stored_wqi": float(stored[0]) if stored and stored[0] is not None else None,
        "stored_status": stored[1] if stored else None,
        "stored_sub_indices": stored[2] if stored else None,
        "stored_flags": stored[3] if stored else None
    }

target_samples = [1419, 408, 62753, 1, 2, 3]

for sid in target_samples:
    res = calculate_wawqi(sid)
    print("=" * 80)
    print(f"SAMPLE {sid}")
    print(f"Calculated WQI : {res['calculated_wqi']}")
    print(f"Stored WQI     : {res['stored_wqi']}")
    print(f"Calculated Dom : {res['dominant_param']} (Wi*qi = {res['max_wi_qi']})")
    print(f"Stored Status  : {res['stored_status']}")
    print(f"Stored Flags   : {res['stored_flags']}")
    print(f"Stored SubInd  : {res['stored_sub_indices']}")
    print("Parameter Breakdown:")
    for p, d in res['param_calc'].items():
        print(f"  {p:12s}: val={d['val']:<12.4f} std={d['std']:<8.4f} qi={d['qi']:<12.4f} Wi={d['Wi']:<8.6f} Wi*qi={d['wi_qi']:<12.4f}")

cur.close()
conn.close()
