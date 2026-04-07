"""
检查容器网络配置
"""
import paramiko

server_host = "8.153.93.123"
server_user = "root"
server_password = "Lily421020"

commands = [
    "podman network ls",
    "podman inspect sstcp-backend --format '{{.NetworkSettings.IPAddress}}' 2>/dev/null || echo 'no ip'",
    "podman inspect sstcp-frontend-h5-new --format '{{.NetworkSettings.IPAddress}}' 2>/dev/null || echo 'no ip'",
    "podman exec sstcp-frontend-h5-new cat /etc/nginx/nginx.conf 2>/dev/null || echo 'cannot read nginx.conf'",
    "podman exec sstcp-frontend-h5-new curl -s http://172.17.0.1:8000/api/v1/project-info/all/list 2>&1 | head -5",
    "podman exec sstcp-frontend-h5-new curl -s http://localhost:8000/api/v1/project-info/all/list 2>&1 | head -5",
    "podman exec sstcp-frontend-h5-new curl -s http://host.containers.internal:8000/api/v1/project-info/all/list 2>&1 | head -5",
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
