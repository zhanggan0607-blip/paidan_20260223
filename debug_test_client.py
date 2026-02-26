import sys
sys.path.insert(0, 'D:\\共享文件\\SSTCP-paidan260120\\backend-python')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
response = client.get("/api/v1/work-plan/statistics", headers={"X-User-Name": "admin", "X-User-Role": "admin"})
print(response.json())
