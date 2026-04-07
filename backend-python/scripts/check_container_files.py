"""
检查容器内实际加载的文件
"""
import paramiko

server_host = "8.153.93.123"
server_user = "root"
server_password = "Lily421020"

commands = [
    "podman exec sstcp-frontend-h5-new cat /usr/share/nginx/html/index.html | head -20",
    "podman exec sstcp-frontend-h5-new ls -la /usr/share/nginx/html/assets/js/MaintenanceLogFillPage*.js 2>/dev/null | head -5",
    "ls -la /opt/sstcp/H5/dist/assets/js/MaintenanceLogFillPage-7-eUzTA1.js",
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
