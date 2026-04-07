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
    
    cmd = '''curl -s "http://localhost:8000/api/v1/personnel/all/list"'''
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    response = stdout.read().decode('utf-8')
    
    data = json.loads(response)
    
    if data.get('code') == 200:
        personnel_list = data.get('data', [])
        
        print(f"\n共有 {len(personnel_list)} 条人员记录\n")
        
        zhang_gan_found = False
        for p in personnel_list:
            if '张干' in p.get('name', ''):
                zhang_gan_found = True
                print("=" * 60)
                print(f"找到用户: {p.get('name')}")
                print("=" * 60)
                print(f"ID: {p.get('id')}")
                print(f"姓名: {p.get('name')}")
                print(f"性别: {p.get('gender')}")
                print(f"电话: {p.get('phone')}")
                print(f"部门: {p.get('department')}")
                print(f"角色: {p.get('role')}")
                print(f"是否需要修改密码: {p.get('must_change_password')}")
                print(f"最后登录时间: {p.get('last_login_at')}")
                print(f"创建时间: {p.get('created_at')}")
                print("-" * 60)
        
        if not zhang_gan_found:
            print("未找到名为'张干'的用户")
            print("\n所有用户列表:")
            for p in personnel_list:
                print(f"  - {p.get('name')} ({p.get('role')}) - {p.get('department')}")
    else:
        print(f"API返回错误: {data}")
        
except Exception as e:
    print(f"错误: {e}")
finally:
    client.close()
    print("\n连接已关闭")
