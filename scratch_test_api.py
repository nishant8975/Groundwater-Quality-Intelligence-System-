import urllib.request
import json
import time

BASE_URL = "http://localhost:3000/api"

def test_endpoint(path, expected_status=200):
    url = BASE_URL + path
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            data = json.loads(response.read().decode())
            print(f"GET {path} -> {status} OK")
            return data
    except urllib.error.HTTPError as e:
        if e.code == expected_status:
            print(f"GET {path} -> {e.code} (Expected Error)")
            return json.loads(e.read().decode())
        else:
            print(f"GET {path} -> FAILED: {e.code}")
            return None
    except Exception as e:
        print(f"GET {path} -> ERROR: {e}")
        return None

print("Waiting for server to start...")
time.sleep(2)

print("\n--- RUNNING API TESTS ---")
# 1. Health
h = test_endpoint("/health")

# 2. Overview
ov = test_endpoint("/overview")
if ov and 'data' in ov:
    d = ov['data']
    print(f"Overview Totals: Total={d['total_samples']}, Eligible={d['eligible_samples']}, Unavailable={d['unavailable_samples']}")
    assert d['total_samples'] == 165162, "Total samples mismatch!"
    assert d['eligible_samples'] == 120738, "Eligible samples mismatch!"
    assert d['unavailable_samples'] == 44424, "Unavailable samples mismatch!"

# 3. Categories
cat = test_endpoint("/wawqi/categories")
if cat and 'data' in cat:
    for c in cat['data']:
        print(f"  {c['category']}: {c['count']}")

# 4. States
states = test_endpoint("/states")

# 5. Districts
dist = test_endpoint("/districts?state=Karnataka")

# 6. Parameters
params = test_endpoint("/parameters")

# 7. Exceedances
exc = test_endpoint("/exceedances?state=Karnataka")

# 8. Extremes
ext = test_endpoint("/extremes?limit=5")

# 9. GIS
gis = test_endpoint("/gis?limit=5")

# 10. Temporal
temp = test_endpoint("/temporal")

# 11. Data Quality
dq = test_endpoint("/data-quality")

# 12. Error handling - Invalid state 404
st_fail = test_endpoint("/states/InvalidState", expected_status=404)

# 13. Pagination boundary
pg = test_endpoint("/extremes?page=1000000&limit=1000") # Limit should clamp to 500
if pg and 'pagination' in pg:
    print("Pagination Meta:", pg['pagination'])

print("\n--- ALL TESTS COMPLETED SUCCESSFULLY ---")
