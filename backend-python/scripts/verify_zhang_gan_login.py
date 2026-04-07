import paramiko
import json

server_ip = '8.153.93.123'
ssh_username = 'root'
ssh_password = 'Lily421020'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(server_ip, username=ssh_username, password=ssh_password, timeout=30)
    print(f"已连接到服务器 {server_ip}")
    
    cmd = '''curl -s -X POST "http://localhost:8000/api/v1/auth/login-json" -H "Content-Type: application/json" -d '{"username": "张干", "password": "lily421020"}' '''
    
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    result = stdout.read().decode('utf-8').strip()
    
    data = json.loads(result)
    
    print("\n登录验证结果 (login-json接口):")
    print("=" * 80)
    if data.get('code') == 200:
        print("✓ 登录成功!")
        user_data = data.get('data', {}).get('user', {})
        print(f"用户ID: {user_data.get('id')}")
        print(f"姓名: {user_data.get('name')}")
        print(f"角色: {user_data.get('role')}")
        print(f"部门: {user_data.get('department')}")
        print(f"电话: {user_data.get('phone')}")
    else:
        print(f"✗ 登录失败: {data.get('message', data)}")
    print("=" * 80)
        
except Exception as e:
    print(f"错误: {e}")
finally:
    client.close()
    print("\n连接已关闭")
