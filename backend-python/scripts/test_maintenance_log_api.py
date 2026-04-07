"""
验证维保日志API是否允许不传项目名称 - 使用真实登录
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
print(f"Login Status: {login_resp.status_code}")

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
        "work_content": "测试不传项目名称",
        "remark": "API测试"
    }
    
    response = requests.post(
        f"{base_url}/maintenance-log",
        json=data,
        headers=headers,
        timeout=10
    )
    print(f"Create Status: {response.status_code}")
    print(f"Create Response: {response.text}")
else:
    print(f"Login failed: {login_resp.text}")
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
    
    print("Output:", output)
    if error:
        print("Error:", error)
    
    ssh.close()
except Exception as e:
    print(f"SSH connection error: {e}")
