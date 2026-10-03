import psycopg2

conn = psycopg2.connect('dbname=groundwater_quality user=postgres password=Nishant@2003 host=localhost port=5432')
cur = conn.cursor()

queries = [
    ("1. Station Name / District / State ILIKE Search", "EXPLAIN ANALYZE SELECT * FROM mv_station_identity WHERE (station_name ILIKE '%Patna%' OR district ILIKE '%Patna%' OR state ILIKE '%Patna%') LIMIT 50"),
    ("2. State Filter Exact", "EXPLAIN ANALYZE SELECT * FROM mv_station_identity WHERE state = 'Bihar' LIMIT 50"),
    ("3. District Filter Exact", "EXPLAIN ANALYZE SELECT * FROM mv_station_identity WHERE district = 'Patna' LIMIT 50"),
    ("4. State + District + Search Combined", "EXPLAIN ANALYZE SELECT * FROM mv_station_identity WHERE state = 'Bihar' AND district = 'Patna' AND (station_name ILIKE '%Patna%' OR district ILIKE '%Patna%' OR state ILIKE '%Patna%') LIMIT 50")
]

for label, q in queries:
    print(f"=== {label} ===")
    cur.execute(q)
    plan = cur.fetchall()
    for line in plan:
        print(" ", line[0])
    print()
