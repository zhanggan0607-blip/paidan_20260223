"""
检查线上服务器容器和数据库配置
"""
import paramiko

SERVER_IP = "8.153.93.123"
SSH_USER = "root"
SSH_PASSWORD = "Lily421020"


def main():
    print("连接服务器...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SERVER_IP, port=22, username=SSH_USER, password=SSH_PASSWORD, timeout=60)
    print("连接成功!\n")
    
    print("=" * 60)
    print("检查运行中的容器")
    print("=" * 60)
    stdin, stdout, stderr = client.exec_command("docker ps", timeout=30)
    print(stdout.read().decode('utf-8'))
    
    print("\n" + "=" * 60)
    print("检查后端环境变量")
    print("=" * 60)
    stdin, stdout, stderr = client.exec_command("cat /opt/sstcp/backend-python/.env 2>/dev/null || echo '文件不存在'", timeout=30)
    print(stdout.read().decode('utf-8'))
    
    print("\n" + "=" * 60)
    print("检查podman容器")
    print("=" * 60)
    stdin, stdout, stderr = client.exec_command("podman ps", timeout=30)
    print(stdout.read().decode('utf-8'))
    
    client.close()


if __name__ == "__main__":
    main()
