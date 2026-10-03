from scripts.etl.loader import get_connection
from psycopg2.extras import RealDictCursor

conn = get_connection()
conn.autocommit = True
cur = conn.cursor(cursor_factory=RealDictCursor)

def execute_sql_file(filepath):
    print(f"Executing {filepath}...")
    with open(filepath, 'r') as f:
        sql = f.read()
    # Execute commands in script
    cur.execute(sql)
    print("Done.\n")

# Run indexes first
execute_sql_file('sql/03_analytics_indexes.sql')
# Run views
execute_sql_file('sql/02_analytics_views.sql')

# Validation
print("--- VALIDATION ---")
with open('sql/04_analytics_validation.sql', 'r') as f:
    sql = f.read()
    
# Manual validation runs
cur.execute("SELECT total_samples, eligible_samples, unavailable_samples FROM vw_wawqi_national_summary;")
nat = cur.fetchone()
print(f"National Totals: {nat}")

cur.execute("""
SELECT 
    SUM(excellent_count) as c_exc,
    SUM(good_count) as c_good,
    SUM(poor_count) as c_poor,
    SUM(very_poor_count) as c_vp,
    SUM(unsuitable_count) as c_uns
FROM mv_wawqi_state_summary;
""")
state_cats = cur.fetchone()
print(f"State summary categories sum: {state_cats}")

# Test Parameter Exceedance
# Wait, p_name isn't there, it's canonical_name.
# Wait, p_name isn't there, it's canonical_name. Let's fix that query in the script or just use canonical_name.
cur.execute("SELECT canonical_name, SUM(exceedance_count) as tot_exceed FROM mv_parameter_exceedance GROUP BY canonical_name;")
print("Exceedances:", cur.fetchall())

# EXPLAIN ANALYZE
print("\n--- EXPLAIN ANALYZE vw_gis_points ---")
cur.execute("EXPLAIN ANALYZE SELECT * FROM vw_gis_points WHERE state = 'Karnataka';")
for r in cur.fetchall():
    print(r['QUERY PLAN'])

print("\n--- EXPLAIN ANALYZE mv_wawqi_state_summary ---")
cur.execute("EXPLAIN ANALYZE SELECT * FROM mv_wawqi_state_summary;")
for r in cur.fetchall():
    print(r['QUERY PLAN'])

cur.close()
conn.close()
