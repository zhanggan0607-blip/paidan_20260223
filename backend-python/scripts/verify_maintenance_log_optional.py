"""
验证维保日志项目名称可选功能是否生效
"""
import paramiko

server_host = "8.153.93.123"
server_user = "root"
server_password = "Lily421020"

python_script = '''
import requests
import json

base_url = "http://localhost:8000/api/v1"

# 登录获取token
login_resp = requests.post(
    f"{base_url}/auth/login-json",
    json={"username": "张干", "password": "lily421020"},
    timeout=10
)

if login_resp.status_code == 200:
    token = login_resp.json()["data"]["access_token"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # 测试不传项目名称创建维保日志
    data = {
        "project_id": None,
        "project_name": None,
        "log_date": "2026-03-16",
        "work_content": "验证项目名称可选功能"
    }
    
    response = requests.post(
        f"{base_url}/maintenance-log",
        json=data,
        headers=headers,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    if response.status_code == 201:
        print("SUCCESS: 项目名称可选功能已生效!")
        print(f"创建的日志ID: {result['data']['log_id']}")
        print(f"project_id: {result['data']['project_id']}")
        print(f"project_name: {result['data']['project_name']}")
    else:
        print(f"FAILED: {result}")
else:
    print(f"Login failed: {login_resp.status_code}")
'''

cmd = f'''cat << 'EOF' | podman exec -i sstcp-backend python
{python_script}
EOF'''

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server_host, username=server_user, password=server_password)
    
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode()
    error = stderr.read().decode()
    
    print(output)
    if error:
        print("Error:", error)
    
    ssh.close()
except Exception as e:
    print(f"SSH connection error: {e}")
