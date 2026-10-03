import pandas as pd
from psycopg2.extras import RealDictCursor
from scripts.etl.loader import get_connection

conn = get_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)

print("--- EXTREME WQI INVESTIGATION ---")

# We want to see raw_value_string for samples 202 and 1419
# But wait, sample_id is an integer. Let's see how the raw data maps.
# The table sample_parameter_values has a numeric_value, but maybe we can join to the raw table if it exists?
# Let's check table structure first.
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'sample_parameter_values'
""")
print("Columns in sample_parameter_values:", [r['column_name'] for r in cur.fetchall()])

# Let's get the parameter values for sample 202
cur.execute("""
    SELECT p.canonical_name, spv.numeric_value
    FROM sample_parameter_values spv
    JOIN parameters p ON spv.parameter_id = p.parameter_id
    WHERE spv.sample_id = 202
""")
for r in cur.fetchall():
    print(f"Sample 202: {r['canonical_name']} = {r['numeric_value']}")

# Let's check the source datasets to see original units.
# The original CSVs are in data/raw. We can parse the dataset profile or query a few raw rows if the ETL keeps them.
cur.execute("""
    SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'
""")
print("Tables in public schema:", [r['table_name'] for r in cur.fetchall()])

# Are raw strings kept in sample_parameter_values? No, it just has numeric_value.
# Did the ETL log units? Let's check docs/DATASET_AUDIT.md or dataset_profile.csv.

print("\n--- DUPLICATE CHECK ---")
cur.execute("""
    SELECT sample_id, parameter_id, COUNT(*)
    FROM sample_parameter_values
    GROUP BY sample_id, parameter_id
    HAVING COUNT(*) > 1
""")
dups = cur.fetchall()
print(f"Duplicates in sample_parameter_values (same sample, same param): {len(dups)}")

cur.close()
conn.close()
