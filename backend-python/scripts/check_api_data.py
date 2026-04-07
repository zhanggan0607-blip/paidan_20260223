"""
通过API检查线上服务器数据库数据
"""
import paramiko
import json

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
    print("通过API检查数据")
    print("=" * 60)
    
    apis = [
        ("零星用工单列表", "curl -s 'http://localhost:8000/api/v1/spot-work/all/list'"),
        ("临时维修工单列表", "curl -s 'http://localhost:8000/api/v1/temporary-repair/all/list'"),
    ]
    
    for name, cmd in apis:
        print(f"\n--- {name} ---")
        stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
        output = stdout.read().decode('utf-8')
        try:
            data = json.loads(output)
            if 'data' in data:
                items = data['data']
                if isinstance(items, list):
                    print(f"总数: {len(items)}")
                    if items:
                        print(f"数据示例: {json.dumps(items[:2], ensure_ascii=False, indent=2)}")
                else:
                    print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
            else:
                print(output[:500])
        except:
            print(output[:500])
    
    client.close()


if __name__ == "__main__":
    main()
