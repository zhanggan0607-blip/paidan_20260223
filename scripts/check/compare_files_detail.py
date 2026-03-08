#!/usr/bin/env python
"""
详细对比本地和服务器文件差异
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

try:
    import paramiko
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"])
    import paramiko

BASE_DIR = Path(__file__).parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend-python"

SERVER_CONFIG = {
    "host": "8.153.93.123",
    "port": 22,
    "username": "root",
    "password": "Lily421020",
    "project_dir": "/opt/sstcp"
}

def get_local_files():
    """获取本地所有代码文件"""
    local_files = {
        "backend_py": [],
        "backend_models": [],
        "backend_api": [],
        "backend_services": [],
        "backend_schemas": [],
        "backend_repositories": [],
        "backend_utils": [],
        "migrations": [],
    }
    
    backend_app = BACKEND_DIR / "app"
    
    for root, dirs, files in os.walk(backend_app):
        for f in files:
            if f.endswith('.py'):
                rel_path = os.path.relpath(os.path.join(root, f), backend_app)
                local_files["backend_py"].append(rel_path.replace("\\", "/"))
                
                if "models" in rel_path:
                    local_files["backend_models"].append(f)
                elif "api" in rel_path and "v1" in rel_path:
                    local_files["backend_api"].append(f)
                elif "services" in rel_path:
                    local_files["backend_services"].append(f)
                elif "schemas" in rel_path:
                    local_files["backend_schemas"].append(f)
                elif "repositories" in rel_path:
                    local_files["backend_repositories"].append(f)
                elif "utils" in rel_path:
                    local_files["backend_utils"].append(f)
    
    migrations_dir = BACKEND_DIR / "migrations"
    if migrations_dir.exists():
        for f in migrations_dir.glob("*.sql"):
            local_files["migrations"].append(f.name)
    
    return local_files

def get_server_files(ssh_client):
    """获取服务器所有代码文件"""
    server_files = {
        "backend_py": [],
        "backend_models": [],
        "backend_api": [],
        "backend_services": [],
        "backend_schemas": [],
        "backend_repositories": [],
        "backend_utils": [],
        "migrations": [],
    }
    
    project_dir = SERVER_CONFIG['project_dir']
    
    commands = {
        "backend_py": f"find {project_dir}/backend-python/app -name '*.py' 2>/dev/null | sed 's|{project_dir}/backend-python/app/||'",
        "backend_models": f"ls {project_dir}/backend-python/app/models/*.py 2>/dev/null | xargs -n1 basename",
        "backend_api": f"ls {project_dir}/backend-python/app/api/v1/*.py 2>/dev/null | xargs -n1 basename",
        "backend_services": f"ls {project_dir}/backend-python/app/services/*.py 2>/dev/null | xargs -n1 basename",
        "backend_schemas": f"ls {project_dir}/backend-python/app/schemas/*.py 2>/dev/null | xargs -n1 basename",
        "backend_repositories": f"ls {project_dir}/backend-python/app/repositories/*.py 2>/dev/null | xargs -n1 basename",
        "backend_utils": f"ls {project_dir}/backend-python/app/utils/*.py 2>/dev/null | xargs -n1 basename",
        "migrations": f"ls {project_dir}/backend-python/migrations/*.sql 2>/dev/null | xargs -n1 basename",
    }
    
    for key, cmd in commands.items():
        stdin, stdout, stderr = ssh_client.exec_command(cmd, timeout=30)
        result = stdout.read().decode('utf-8').strip()
        if result:
            server_files[key] = [f.strip() for f in result.split('\n') if f.strip()]
    
    return server_files

def compare_files(local, server):
    """对比文件差异"""
    differences = {}
    
    all_keys = set(local.keys()) | set(server.keys())
    
    for key in all_keys:
        local_set = set(local.get(key, []))
        server_set = set(server.get(key, []))
        
        missing_on_server = local_set - server_set
        missing_on_local = server_set - local_set
        
        if missing_on_server or missing_on_local:
            differences[key] = {
                "local_count": len(local_set),
                "server_count": len(server_set),
                "missing_on_server": sorted(list(missing_on_server)),
                "missing_on_local": sorted(list(missing_on_local))
            }
    
    return differences

def main():
    print("=" * 60)
    print("详细对比本地和服务器文件差异")
    print("=" * 60)
    
    print("\n[1] 获取本地文件列表...")
    local_files = get_local_files()
    for key, files in local_files.items():
        print(f"   {key}: {len(files)} 个文件")
    
    print("\n[2] 连接服务器...")
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
        print("   ✓ 连接成功")
        
        print("\n[3] 获取服务器文件列表...")
        server_files = get_server_files(ssh)
        for key, files in server_files.items():
            print(f"   {key}: {len(files)} 个文件")
        
        print("\n[4] 对比文件差异...")
        differences = compare_files(local_files, server_files)
        
        print("\n" + "=" * 60)
        print("对比结果")
        print("=" * 60)
        
        print("\n文件数量对比:")
        print("-" * 50)
        print(f"{'类别':<25} {'本地':>10} {'服务器':>10} {'差异':>10}")
        print("-" * 50)
        
        all_keys = set(local_files.keys()) | set(server_files.keys())
        for key in sorted(all_keys):
            local_count = len(local_files.get(key, []))
            server_count = len(server_files.get(key, []))
            diff = local_count - server_count
            diff_str = f"+{diff}" if diff > 0 else str(diff)
            print(f"{key:<25} {local_count:>10} {server_count:>10} {diff_str:>10}")
        
        if differences:
            print(f"\n发现 {len(differences)} 个类别存在差异:\n")
            for key, diff in differences.items():
                print(f"【{key}】")
                print(f"   本地数量: {diff['local_count']}")
                print(f"   服务器数量: {diff['server_count']}")
                
                if diff['missing_on_server']:
                    print(f"   ⚠️ 服务器缺少 {len(diff['missing_on_server'])} 个文件:")
                    for f in diff['missing_on_server'][:10]:
                        print(f"      - {f}")
                    if len(diff['missing_on_server']) > 10:
                        print(f"      ... 还有 {len(diff['missing_on_server']) - 10} 个")
                
                if diff['missing_on_local']:
                    print(f"   ⚠️ 本地缺少 {len(diff['missing_on_local'])} 个文件:")
                    for f in diff['missing_on_local'][:10]:
                        print(f"      - {f}")
                    if len(diff['missing_on_local']) > 10:
                        print(f"      ... 还有 {len(diff['missing_on_local']) - 10} 个")
                print()
        else:
            print("\n✓ 本地和服务器文件完全一致!")
        
        ssh.close()
        
        report = {
            "check_time": datetime.now().isoformat(),
            "local": {k: {"count": len(v), "files": v} for k, v in local_files.items()},
            "server": {k: {"count": len(v), "files": v} for k, v in server_files.items()},
            "differences": differences
        }
        
        report_path = BASE_DIR / "scripts" / "check" / f"file_diff_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n报告已保存: {report_path}")
        
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
