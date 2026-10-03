import pandas as pd
from psycopg2.extras import RealDictCursor
from scripts.etl.loader import get_connection

conn = get_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)

def print_extreme(sample_id):
    print(f"\n--- SAMPLE {sample_id} ---")
    cur.execute("""
        SELECT p.canonical_name, spv.raw_value_string, spv.numeric_value, spv.unit
        FROM sample_parameter_values spv
        JOIN parameters p ON spv.parameter_id = p.parameter_id
        WHERE spv.sample_id = %s
          AND p.canonical_name IN ('ph', 'chloride', 'sulphate', 'hardness', 'calcium', 'magnesium', 'iron', 'arsenic', 'uranium')
    """, (sample_id,))
    
    for r in cur.fetchall():
        print(f"{r['canonical_name']}: raw='{r['raw_value_string']}', num={r['numeric_value']}, unit='{r['unit']}'")

print_extreme(202)
print_extreme(1419)

# Now check Unit Consistency for all primary parameters
print("\n--- UNIT CONSISTENCY ---")
cur.execute("""
    SELECT p.canonical_name, 
           array_agg(DISTINCT spv.unit) as distinct_units
    FROM sample_parameter_values spv
    JOIN parameters p ON spv.parameter_id = p.parameter_id
    WHERE p.canonical_name IN ('ph', 'chloride', 'sulphate', 'hardness', 'calcium', 'magnesium', 'iron', 'arsenic', 'uranium')
    GROUP BY p.canonical_name
""")
for r in cur.fetchall():
    print(f"{r['canonical_name']}: {r['distinct_units']}")

cur.close()
conn.close()
