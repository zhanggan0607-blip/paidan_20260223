"""
检查容器挂载配置
"""
import paramiko

server_host = "8.153.93.123"
server_user = "root"
server_password = "Lily421020"

commands = [
    "podman inspect sstcp-frontend-h5-new --format '{{json .Mounts}}' | python -m json.tool",
    "podman exec sstcp-frontend-h5-new ls -la /usr/share/nginx/html/ | head -10",
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
