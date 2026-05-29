import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)
queries = ['?page=1&limit=2', '?department=Engineering', '?sort_by=name&order=asc']
for q in queries:
    r = client.get('/api/v1/employees' + q)
    print('Q', q)
    print('status', r.status_code)
    print(json.dumps(r.json(), indent=2))
    print('---')
