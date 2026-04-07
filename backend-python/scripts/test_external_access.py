"""
验证外部访问
"""
import paramiko
import requests

server_host = "8.153.93.123"
server_user = "root"
server_password = "Lily421020"

# 从外部测试
print("Testing from external...")
try:
    response = requests.get(f"http://{server_host}:81/api/v1/project-info/all/list", timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Got {len(data.get('data', []))} projects")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
