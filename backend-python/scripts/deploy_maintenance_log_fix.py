"""
同步后端代码到服务器并重启容器
"""
import paramiko
import os

server_host = "8.153.93.123"
server_user = "root"
server_password = "Lily421020"

local_files = [
    ("D:/共享文件/SSTCP-paidan260120/backend-python/app/api/v1/maintenance_log.py", "/opt/sstcp/backend/app/api/v1/maintenance_log.py"),
    ("D:/共享文件/SSTCP-paidan260120/backend-python/app/models/maintenance_log.py", "/opt/sstcp/backend/app/models/maintenance_log.py"),
]

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server_host, username=server_user, password=server_password)
    
    sftp = ssh.open_sftp()
    
    for local_path, remote_path in local_files:
        local_path_norm = os.path.normpath(local_path)
        print(f"Uploading {local_path_norm} -> {remote_path}")
        sftp.put(local_path_norm, remote_path)
        print(f"  Done!")
    
    sftp.close()
    
    print("\nRestarting backend container...")
    stdin, stdout, stderr = ssh.exec_command("podman restart sstcp-backend")
    output = stdout.read().decode()
    error = stderr.read().decode()
    print(f"Restart output: {output}")
    if error:
        print(f"Restart error: {error}")
    
    ssh.close()
    print("\nDeployment completed!")
    
except Exception as e:
    print(f"Error: {e}")
