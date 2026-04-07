"""
检查服务器容器状态和nginx配置
"""
import paramiko

server_host = "8.153.93.123"
server_user = "root"
server_password = "Lily421020"

commands = [
    "podman ps -a | grep sstcp",
    "podman logs --tail 30 sstcp-backend 2>&1",
    "cat /opt/sstcp/nginx-h5.conf",
    "curl -s http://localhost:8000/api/v1/health || echo 'backend not responding'",
]

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server_host, username=server_user, password=server_password)
    
    for cmd in commands:
        print(f"\n{'='*60}")
        print(f">>> {cmd}")
        print('='*60)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        print(output)
        if error:
            print(f"Error: {error}")
    
    ssh.close()
    
except Exception as e:
    print(f"Error: {e}")
