import pandas as pd
import numpy as np
from psycopg2.extras import RealDictCursor
from scripts.etl.loader import get_connection

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

def calculate_wqi(measurements):
    """
    measurements: dict of parameter_name: value
    """
    valid_measurements = {k: v for k, v in measurements.items() if v is not None and not np.isnan(v)}
    
    if len(valid_measurements) < 6:
        return None, None
        
    # Calculate K
    sum_1_over_Si = 0.0
    for param in valid_measurements:
        if param in standards:
            sum_1_over_Si += 1.0 / standards[param]['Si']
            
    if sum_1_over_Si == 0:
        return None, None
        
    K = 1.0 / sum_1_over_Si
    
    # Calculate W_i and q_i
    sum_Wi = 0.0
    sum_Wi_qi = 0.0
    
    details = {}
    
    for param, Vi in valid_measurements.items():
        if param not in standards:
            continue
            
        Si = standards[param]['Si']
        Vo = standards[param]['Vo']
        
        # W_i calculation
        Wi = K / Si
        sum_Wi += Wi
        
        # q_i calculation
        if param == 'ph':
            qi = 100.0 * abs(Vi - Vo) / (Si - Vo)
        else:
            qi = 100.0 * (Vi - Vo) / (Si - Vo)
            
        if qi < 0:
            qi = 0.0
            
        Wi_qi = Wi * qi
        sum_Wi_qi += Wi_qi
        
        details[param] = {
            'Vi': Vi,
            'Si': Si,
            'Vo': Vo,
            'Wi': Wi,
            'qi': qi,
            'Wi_qi': Wi_qi
        }
        
    if sum_Wi == 0:
        return None, None
        
    wqi = sum_Wi_qi / sum_Wi
    return wqi, details, sum_Wi

# Quality Rating Tests

print("--- QUALITY RATING TESTS ---")

# Normal parameter
print("Normal parameter: Iron (Si=0.3)")
res = calculate_wqi({'iron': 0.0, 'ph': 7, 'chloride': 250, 'sulphate': 200, 'hardness': 200, 'calcium': 75})
print(f"Vi = 0 -> qi = {res[1]['iron']['qi']:.2f}")
res = calculate_wqi({'iron': 0.3, 'ph': 7, 'chloride': 250, 'sulphate': 200, 'hardness': 200, 'calcium': 75})
print(f"Vi = Si -> qi = {res[1]['iron']['qi']:.2f}")
res = calculate_wqi({'iron': 0.6, 'ph': 7, 'chloride': 250, 'sulphate': 200, 'hardness': 200, 'calcium': 75})
print(f"Vi > Si -> qi = {res[1]['iron']['qi']:.2f}")

# pH
print("\npH (Si=8.5, Vo=7.0)")
for ph_val in [7.0, 6.5, 8.5, 6.0, 9.0]:
    res = calculate_wqi({'ph': ph_val, 'iron': 0, 'chloride': 250, 'sulphate': 200, 'hardness': 200, 'calcium': 75})
    print(f"pH = {ph_val} -> qi = {res[1]['ph']['qi']:.2f}")

# Missing parameter
print("\nMissing parameter")
res = calculate_wqi({'ph': 7.0, 'iron': None, 'chloride': 250, 'sulphate': 200, 'hardness': 200, 'calcium': 75, 'magnesium': 30})
print("Iron is None. Included in details? ", 'iron' in res[1])

# Six-parameter boundary
print("\nSix-parameter boundary")
res6 = calculate_wqi({'ph': 7.0, 'chloride': 250, 'sulphate': 200, 'hardness': 200, 'calcium': 75, 'magnesium': 30})
print(f"Exactly 6 valid parameters: WQI = {res6[0]}")
res5 = calculate_wqi({'ph': 7.0, 'chloride': 250, 'sulphate': 200, 'hardness': 200, 'calcium': 75})
print(f"Only 5 valid parameters: WQI = {res5[0]}")

# Conditional parameter
print("\nConditional parameter")
res7 = calculate_wqi({'ph': 7.0, 'chloride': 250, 'sulphate': 200, 'hardness': 200, 'calcium': 75, 'magnesium': 30, 'arsenic': 0.05})
print(f"Arsenic present: included = {'arsenic' in res7[1]}")
res_missing_arsenic = calculate_wqi({'ph': 7.0, 'chloride': 250, 'sulphate': 200, 'hardness': 200, 'calcium': 75, 'magnesium': 30})
print(f"Arsenic absent: included = {'arsenic' in res_missing_arsenic[1]}")


# Real samples validation
print("\n--- REAL SAMPLES VALIDATION ---")
conn = get_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)

query = '''
SELECT s.sample_id,
       json_object_agg(p.canonical_name, spv.numeric_value) FILTER (WHERE p.canonical_name IN ('ph', 'chloride', 'sulphate', 'hardness', 'calcium', 'magnesium', 'iron', 'arsenic', 'uranium')) as measurements
FROM water_samples s
JOIN sample_parameter_values spv ON s.sample_id = spv.sample_id
JOIN parameters p ON spv.parameter_id = p.parameter_id
GROUP BY s.sample_id
'''
cur.execute(query)
samples = cur.fetchall()

# Select samples matching criteria
selected = []
for row in samples:
    m = row['measurements']
    if m is None: continue
    m = {k: v for k, v in m.items() if v is not None}
    
    if len(selected) == 0 and len(m) == 6:
        selected.append((row['sample_id'], m, "Exactly 6 valid parameters"))
    elif len(selected) == 1 and len(m) >= 7 and 'ph' in m and m['ph'] < 7:
        selected.append((row['sample_id'], m, "7+ valid parameters, pH < 7"))
    elif len(selected) == 2 and 'arsenic' in m:
        selected.append((row['sample_id'], m, "Arsenic present"))
    elif len(selected) == 3 and 'uranium' in m:
        selected.append((row['sample_id'], m, "Uranium present"))
    elif len(selected) == 4 and 'ph' in m and m['ph'] > 7.5 and 'iron' in m and m['iron'] > 0.3:
        selected.append((row['sample_id'], m, "pH > 7, value > standard"))
        
    if len(selected) == 5:
        break

for sid, m, reason in selected:
    print(f"\nSample ID: {sid} ({reason})")
    print(f"Parameters included: {list(m.keys())}")
    wqi, details, sum_wi = calculate_wqi(m)
    
    for p, d in details.items():
        print(f"  {p}: Vi={d['Vi']}, Si={d['Si']}, Vo={d['Vo']}, Wi={d['Wi']:.6f}, qi={d['qi']:.2f}, Wi*qi={d['Wi_qi']:.4f}")
        
    print(f"Sum Wi: {sum_wi:.6f}")
    print(f"Final WQI: {wqi:.2f}")

cur.close()
conn.close()
