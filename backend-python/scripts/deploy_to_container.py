"""
同步后端代码到服务器容器内
"""
import paramiko
import os

server_host = "8.153.93.123"
server_user = "root"
server_password = "Lily421020"

local_files = [
    ("D:/共享文件/SSTCP-paidan260120/backend-python/app/api/v1/maintenance_log.py", "/app/app/api/v1/maintenance_log.py"),
    ("D:/共享文件/SSTCP-paidan260120/backend-python/app/models/maintenance_log.py", "/app/app/models/maintenance_log.py"),
]

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server_host, username=server_user, password=server_password)
    
    sftp = ssh.open_sftp()
    
    temp_dir = "/tmp/sstcp_update"
    stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {temp_dir}")
    stdout.read()
    
    for local_path, container_path in local_files:
        local_path_norm = os.path.normpath(local_path)
        filename = os.path.basename(local_path_norm)
        temp_path = f"{temp_dir}/{filename}"
        
        print(f"Uploading {local_path_norm} -> {temp_path}")
        sftp.put(local_path_norm, temp_path)
        print(f"  Done!")
        
        container_dir = os.path.dirname(container_path)
        cmd = f"podman exec sstcp-backend mkdir -p {container_dir}"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
        
        cmd = f"podman cp {temp_path} sstcp-backend:{container_path}"
        print(f"Copying to container: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"  Error: {error}")
        else:
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
