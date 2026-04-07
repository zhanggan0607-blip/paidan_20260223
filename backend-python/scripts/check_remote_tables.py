"""
检查线上服务器数据库所有表的数据量
"""
import paramiko

SERVER_IP = "8.153.93.123"
SSH_USER = "root"
SSH_PASSWORD = "Lily421020"

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "tq"
DB_USER = "postgres"
DB_PASSWORD = "123456"


def main():
    print("连接服务器...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SERVER_IP, port=22, username=SSH_USER, password=SSH_PASSWORD, timeout=60)
    print("连接成功!\n")
    
    psql_base = f"PGPASSWORD={DB_PASSWORD} psql -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DB_NAME}"
    
    print("=" * 60)
    print("线上服务器数据库所有表数据量统计")
    print("=" * 60)
    
    cmd = f'''{psql_base} -c "
    SELECT 
        schemaname,
        tablename,
        (xpath('/row/cnt/text()', xml_count))[1]::text::int as row_count
    FROM (
        SELECT 
            schemaname,
            tablename,
            query_to_xml(format('SELECT COUNT(*) as cnt FROM %I.%I', schemaname, tablename), false, true, '') as xml_count
        FROM pg_tables 
        WHERE schemaname = 'public'
    ) t
    ORDER BY row_count DESC;
    "'''
    
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if error:
        print(f"错误: {error}")
    print(output)
    
    client.close()


if __name__ == "__main__":
    main()
