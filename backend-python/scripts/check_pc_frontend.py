"""
检查PC端前端部署状态
"""
import paramiko

server_host = "8.153.93.123"
server_user = "root"
server_password = "Lily421020"

commands = [
    "ls -la /opt/sstcp/dist/assets/*.js | head -10",
    "podman exec sstcp-web ls -la /usr/share/nginx/html/assets/*.js 2>/dev/null | head -10",
    "cat /opt/sstcp/dist/index.html | head -20",
]

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server_host, username=server_user, password=server_password)
    
    for cmd in commands:
        print(f"\n>>> {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        print(output)
        if error:
            print(f"Error: {error}")
    
    ssh.close()
    
except Exception as e:
    print(f"Error: {e}")
