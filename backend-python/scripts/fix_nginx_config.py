"""
修复nginx配置，使用正确的后端地址
"""
import paramiko

server_host = "8.153.93.123"
server_user = "root"
server_password = "Lily421020"

new_nginx_conf = '''server {
    listen 80;
    server_name localhost;

    client_max_body_size 50M;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    location /h5 {
        alias /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /h5/index.html;
    }

    location /api {
        proxy_pass http://host.containers.internal:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /uploads {
        proxy_pass http://host.containers.internal:8000;
        proxy_set_header Host $host;
    }
}
'''

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server_host, username=server_user, password=server_password)
    
    # 创建临时文件
    cmd = f'''cat > /tmp/nginx-h5.conf << 'NGINX_EOF'
{new_nginx_conf}
NGINX_EOF'''
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.read()
    print("Created temp nginx config")
    
    # 复制到容器
    cmd = "podman cp /tmp/nginx-h5.conf sstcp-frontend-h5-new:/etc/nginx/conf.d/default.conf"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode()
    error = stderr.read().decode()
    print(f"Copy to container: {output or 'done'}")
    if error:
        print(f"Error: {error}")
    
    # 重载nginx
    cmd = "podman exec sstcp-frontend-h5-new nginx -s reload"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode()
    error = stderr.read().decode()
    print(f"Reload nginx: {output or 'done'}")
    if error:
        print(f"Error: {error}")
    
    # 测试
    cmd = "podman exec sstcp-frontend-h5-new curl -s http://localhost/api/v1/project-info/all/list | head -c 200"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode()
    print(f"\nTest result: {output}")
    
    ssh.close()
    print("\nDone!")
    
except Exception as e:
    print(f"Error: {e}")
