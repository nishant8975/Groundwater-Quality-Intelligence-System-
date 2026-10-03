import urllib.request, urllib.parse, json

BASE = 'http://localhost:3000/api'

def test_endpoint(url):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return resp.status, data
    except urllib.error.HTTPError as e:
        data = json.loads(e.read().decode('utf-8'))
        return e.code, data

tests = [
    ("1. GET /api/stations/search?q=Haryana", f"{BASE}/stations/search?q=Haryana"),
    ("2. GET /api/stations/search?search=Patna", f"{BASE}/stations/search?search=Patna"),
    ("3. Empty search: GET /api/stations/search", f"{BASE}/stations/search"),
    ("4. Station-name search: GET /api/stations/search?q=Alampur", f"{BASE}/stations/search?q=Alampur"),
    ("5. State search: GET /api/stations/search?q=Bihar", f"{BASE}/stations/search?q=Bihar"),
    ("6. District search: GET /api/stations/search?q=Gadag", f"{BASE}/stations/search?q=Gadag"),
    ("7. Pagination: GET /api/stations/search?q=Bihar&page=2&limit=10", f"{BASE}/stations/search?q=Bihar&page=2&limit=10"),
    ("8. Invalid limit (negative): GET /api/stations/search?limit=-5", f"{BASE}/stations/search?limit=-5"),
    ("9. Invalid limit (excessive): GET /api/stations/search?limit=9999", f"{BASE}/stations/search?limit=9999"),
    ("10. Special characters: GET /api/stations/search?q=%27%22%3B--", f"{BASE}/stations/search?q=" + urllib.parse.quote('\'";--')),
    ("11. Nonexistent term: GET /api/stations/search?q=NonexistentStation12345", f"{BASE}/stations/search?q=NonexistentStation12345"),
    ("12. Verify existing endpoint: GET /api/stations?search=Patna", f"{BASE}/stations?search=Patna")
]

print("=== RUNNING SEARCH API VALIDATION TESTS ===")
for label, url in tests:
    status, res = test_endpoint(url)
    data_count = len(res.get('data', [])) if isinstance(res.get('data'), list) else 'N/A'
    total = res.get('pagination', {}).get('total', 'N/A')
    limit = res.get('pagination', {}).get('limit', 'N/A')
    print(f"{label}")
    print(f"   Status: {status} | Returned Rows: {data_count} | Total Match: {total} | Limit: {limit}")
