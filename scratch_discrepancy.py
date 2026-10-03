from scripts.etl.loader import get_connection
from psycopg2.extras import RealDictCursor

conn = get_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)

# Let's count how many samples have >= 6 parameters out of the 9 WAWQI parameters.
cur.execute('''
    SELECT s.sample_id, 
           COUNT(spv.numeric_value) as num_params,
           json_object_agg(p.canonical_name, spv.numeric_value) FILTER (WHERE spv.numeric_value IS NOT NULL) as vals
    FROM water_samples s
    JOIN sample_parameter_values spv ON s.sample_id = spv.sample_id
    JOIN parameters p ON spv.parameter_id = p.parameter_id
    WHERE p.canonical_name IN ('ph', 'chloride', 'sulphate', 'hardness', 'calcium', 'magnesium', 'iron', 'arsenic', 'uranium')
      AND spv.numeric_value IS NOT NULL
      AND spv.is_missing = FALSE
    GROUP BY s.sample_id
    HAVING COUNT(spv.numeric_value) >= 6
''')

samples = cur.fetchall()
print(f"Total >= 6: {len(samples)}")

# Compare this with the results in wawqi_results
cur.execute('SELECT COUNT(*) as c FROM wawqi_results WHERE wqi IS NOT NULL')
print(f"Total in wawqi_results: {cur.fetchone()['c']}")

cur.close()
conn.close()
