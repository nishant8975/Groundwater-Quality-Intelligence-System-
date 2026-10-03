import psycopg2

conn = psycopg2.connect('dbname=groundwater_quality user=postgres password=Nishant@2003 host=localhost port=5432')
cur = conn.cursor()

tables = ['source_datasets', 'water_samples', 'sample_parameter_values', 'locations', 'parameters', 'wawqi_results', 'mv_station_identity']

for t in tables:
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", (t,))
    cols = [r[0] for r in cur.fetchall()]
    print(f"{t}: {cols}")
