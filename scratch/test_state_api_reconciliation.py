import psycopg2
import urllib.request
import urllib.parse
import json

conn = psycopg2.connect('dbname=groundwater_quality user=postgres password=Nishant@2003 host=localhost port=5432')
cur = conn.cursor()

cur.execute("SELECT state, total_samples, eligible_samples, unavailable_samples, median_wqi FROM mv_wawqi_state_summary ORDER BY state")
db_rows = cur.fetchall()

print(f"{'State':<30} | {'DB Samples':<10} | {'API Samples':<11} | {'Diff':<5} | {'DB Avail':<9} | {'API Avail':<9} | {'Diff':<5} | {'Status':<6}")
print("-" * 105)

mismatch_count = 0
for st, db_tot, db_el, db_un, db_med in db_rows:
    url = f"http://localhost:3000/api/states/{urllib.parse.quote(st)}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        d = data.get('data', {})
        api_tot = int(d.get('total_samples'))
        api_el = int(d.get('eligible_samples'))
        api_un = int(d.get('unavailable_samples'))
        diff_tot = api_tot - db_tot
        diff_el = api_el - db_el
        status = "PASS" if diff_tot == 0 and diff_el == 0 else "FAIL"
        if status == "FAIL":
            mismatch_count += 1
        print(f"{st:<30} | {db_tot:<10} | {api_tot:<11} | {diff_tot:<5} | {db_el:<9} | {api_el:<9} | {diff_el:<5} | {status:<6}")

print("-" * 105)
print(f"Total Mismatches across 30 states: {mismatch_count}")
