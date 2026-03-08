#!/usr/bin/env python
"""
深度对比本地和服务器的一致性
包括：文件内容、数据库表结构、状态常量、API路由
"""
import os
import sys
import json
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime

try:
    import paramiko
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"])
    import paramiko

try:
    import psycopg2
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"])
    import psycopg2

BASE_DIR = Path(__file__).parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend-python"

SERVER_CONFIG = {
    "host": "8.153.93.123",
    "port": 22,
    "username": "root",
    "password": "Lily421020",
    "project_dir": "/opt/sstcp"
}

LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "database": "tq",
    "user": "postgres",
    "password": "123456"
}

SERVER_DB = {
    "host": "8.153.93.123",
    "port": 5432,
    "database": "tq",
    "user": "postgres",
    "password": "123456"
}

def get_file_hash(content):
    """计算文件内容的MD5哈希"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def compare_file_contents(ssh_client):
    """对比关键文件内容"""
    print("\n=== 对比关键文件内容 ===")
    
    key_files = [
        "backend-python/app/config.py",
        "backend-python/app/main.py",
        "backend-python/requirements.txt",
        "backend-python/.env",
        "packages/shared/src/utils/status.ts",
    ]
    
    differences = []
    
    for file_path in key_files:
        local_path = BASE_DIR / file_path
        server_path = f"{SERVER_CONFIG['project_dir']}/{file_path}"
        
        local_content = ""
        server_content = ""
        
        if local_path.exists():
            local_content = local_path.read_text(encoding='utf-8')
        
        stdin, stdout, stderr = ssh_client.exec_command(f"cat {server_path} 2>/dev/null", timeout=30)
        server_content = stdout.read().decode('utf-8')
        
        local_hash = get_file_hash(local_content)
        server_hash = get_file_hash(server_content)
        
        if local_hash != server_hash:
            differences.append({
                "file": file_path,
                "local_hash": local_hash[:8],
                "server_hash": server_hash[:8],
                "local_lines": len(local_content.split('\n')),
                "server_lines": len(server_content.split('\n'))
            })
            print(f"  ⚠️ {file_path}")
            print(f"     本地: {len(local_content.split(chr(10)))} 行, hash: {local_hash[:8]}")
            print(f"     服务器: {len(server_content.split(chr(10)))} 行, hash: {server_hash[:8]}")
        else:
            print(f"  ✓ {file_path} - 一致")
    
    return differences

def compare_database_structures():
    """对比数据库结构"""
    print("\n=== 对比数据库结构 ===")
    
    results = {
        "local": {"tables": {}, "status": "unknown"},
        "server": {"tables": {}, "status": "unknown"},
        "differences": []
    }
    
    for env, config in [("local", LOCAL_DB), ("server", SERVER_DB)]:
        try:
            conn = psycopg2.connect(**config)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cur.fetchall()]
            
            for table in tables:
                cur.execute(f"""
                    SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                columns = {}
                for row in cur.fetchall():
                    columns[row[0]] = {
                        "type": row[1],
                        "max_length": row[2],
                        "nullable": row[3],
                        "default": row[4]
                    }
                results[env]["tables"][table] = columns
            
            cur.close()
            conn.close()
            results[env]["status"] = "connected"
            print(f"  {env}: {len(tables)} 个表")
            
        except Exception as e:
            results[env]["status"] = f"error: {e}"
            print(f"  {env}: 连接失败 - {e}")
    
    if results["local"]["status"] == "connected" and results["server"]["status"] == "connected":
        local_tables = set(results["local"]["tables"].keys())
        server_tables = set(results["server"]["tables"].keys())
        
        missing_on_server = local_tables - server_tables
        missing_on_local = server_tables - local_tables
        
        if missing_on_server:
            results["differences"].append({
                "type": "tables_missing_on_server",
                "tables": list(missing_on_server)
            })
            print(f"\n  ⚠️ 服务器缺少表: {missing_on_server}")
        
        if missing_on_local:
            results["differences"].append({
                "type": "tables_missing_on_local",
                "tables": list(missing_on_local)
            })
            print(f"\n  ⚠️ 本地缺少表: {missing_on_local}")
        
        common_tables = local_tables & server_tables
        for table in common_tables:
            local_cols = set(results["local"]["tables"][table].keys())
            server_cols = set(results["server"]["tables"][table].keys())
            
            if local_cols != server_cols:
                results["differences"].append({
                    "type": "columns_mismatch",
                    "table": table,
                    "local_only": list(local_cols - server_cols),
                    "server_only": list(server_cols - local_cols)
                })
                print(f"\n  ⚠️ 表 {table} 字段不一致:")
                print(f"     本地独有: {local_cols - server_cols}")
                print(f"     服务器独有: {server_cols - local_cols}")
        
        if not results["differences"]:
            print("\n  ✓ 数据库结构完全一致!")
    
    return results

def compare_status_constants():
    """对比状态常量"""
    print("\n=== 对比状态常量 ===")
    
    results = {
        "frontend": [],
        "backend_config": [],
        "database_values": []
    }
    
    status_file = BASE_DIR / "packages" / "shared" / "src" / "utils" / "status.ts"
    if status_file.exists():
        content = status_file.read_text(encoding='utf-8')
        import re
        results["frontend"] = re.findall(r"STATUS_\w+\s*=\s*'([^']+)'", content)
        print(f"  前端状态常量: {results['frontend']}")
    
    config_file = BACKEND_DIR / "app" / "config.py"
    if config_file.exists():
        content = config_file.read_text(encoding='utf-8')
        valid = re.search(r"VALID_STATUSES.*?\[(.*?)\]", content, re.DOTALL)
        if valid:
            results["backend_config"] = re.findall(r"'([^']+)'", valid.group(1))
        print(f"  后端配置状态: {results['backend_config']}")
    
    try:
        conn = psycopg2.connect(**LOCAL_DB)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT dict_value FROM dictionary WHERE dict_type LIKE '%status%' OR dict_key LIKE '%status%'")
        results["database_values"] = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        print(f"  数据库状态值: {results['database_values']}")
    except Exception as e:
        print(f"  数据库查询失败: {e}")
    
    return results

def compare_api_routes(ssh_client):
    """对比API路由"""
    print("\n=== 对比API路由 ===")
    
    local_main = BACKEND_DIR / "app" / "main.py"
    local_routes = []
    if local_main.exists():
        content = local_main.read_text(encoding='utf-8')
        import re
        local_routes = re.findall(r'app\.include_router\((\w+)\.router', content)
    
    stdin, stdout, stderr = ssh_client.exec_command(
        f"cat {SERVER_CONFIG['project_dir']}/backend-python/app/main.py 2>/dev/null",
        timeout=30
    )
    server_content = stdout.read().decode('utf-8')
    server_routes = re.findall(r'app\.include_router\((\w+)\.router', server_content)
    
    local_set = set(local_routes)
    server_set = set(server_routes)
    
    print(f"  本地路由模块: {len(local_routes)} 个")
    print(f"  服务器路由模块: {len(server_routes)} 个")
    
    if local_set != server_set:
        print(f"\n  ⚠️ 路由模块不一致:")
        print(f"     本地独有: {local_set - server_set}")
        print(f"     服务器独有: {server_set - local_set}")
        return False
    else:
        print("\n  ✓ API路由模块一致")
        return True

def main():
    print("=" * 60)
    print("深度对比本地和服务器一致性")
    print("=" * 60)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            SERVER_CONFIG["host"],
            port=SERVER_CONFIG["port"],
            username=SERVER_CONFIG["username"],
            password=SERVER_CONFIG["password"],
            timeout=10
        )
        print(f"\n✓ 已连接服务器: {SERVER_CONFIG['host']}")
        
        file_diff = compare_file_contents(ssh)
        api_match = compare_api_routes(ssh)
        ssh.close()
        
    except Exception as e:
        print(f"\n✗ SSH连接失败: {e}")
        file_diff = []
        api_match = None
    
    db_results = compare_database_structures()
    status_results = compare_status_constants()
    
    print("\n" + "=" * 60)
    print("检查结果汇总")
    print("=" * 60)
    
    all_ok = True
    
    if file_diff:
        print(f"\n⚠️ 文件内容差异: {len(file_diff)} 个文件")
        all_ok = False
    else:
        print("\n✓ 关键文件内容一致")
    
    if db_results["differences"]:
        print(f"⚠️ 数据库结构差异: {len(db_results['differences'])} 处")
        all_ok = False
    else:
        print("✓ 数据库结构一致")
    
    if api_match is False:
        print("⚠️ API路由不一致")
        all_ok = False
    elif api_match is True:
        print("✓ API路由一致")
    
    if all_ok:
        print("\n" + "=" * 60)
        print("✓✓✓ 服务器与本地系统完全一致！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("发现差异，建议同步更新服务器")
        print("=" * 60)
    
    report = {
        "check_time": datetime.now().isoformat(),
        "file_differences": file_diff,
        "database_results": {
            "local_tables": list(db_results["local"]["tables"].keys()),
            "server_tables": list(db_results["server"]["tables"].keys()),
            "differences": db_results["differences"]
        },
        "status_constants": status_results,
        "all_ok": all_ok
    }
    
    report_path = BASE_DIR / "scripts" / "check" / f"deep_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n详细报告已保存: {report_path}")

if __name__ == "__main__":
    main()
