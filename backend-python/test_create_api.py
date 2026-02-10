import requests
import json

url = "http://localhost:8080/api/project-info"

data = {
    "project_id": "PRJ006",
    "project_name": "测试项目",
    "completion_date": "2026-01-26T00:00:00",
    "maintenance_end_date": "2027-01-26T00:00:00",
    "maintenance_period": "1年",
    "client_name": "测试客户",
    "address": "测试地址",
    "project_abbr": "测试",
    "client_contact": "张三",
    "client_contact_position": "经理",
    "client_contact_info": "13800138000"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=data, headers=headers)

print(f"状态码: {response.status_code}")
print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")