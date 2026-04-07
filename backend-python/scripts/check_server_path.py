"""
检查服务器上的文件路径
"""
import paramiko

server_host = "8.153.93.123"
server_user = "root"
server_password = "Lily421020"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server_host, username=server_user, password=server_password)
    
    commands = [
        "ls -la /opt/sstcp/",
        "ls -la /opt/sstcp/backend/ 2>/dev/null || echo 'backend not found'",
        "podman exec sstcp-backend ls -la /app/app/api/v1/ 2>/dev/null || echo 'container path check failed'",
    ]
    
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
