#!/usr/bin/env python
"""
服务器与本地系统一致性检查脚本
通过API和数据库直接检查服务器状态
"""
import os
import sys
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import urllib.request
import urllib.error

try:
    import psycopg2
except ImportError:
    print("正在安装 psycopg2...")
    subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"])
    import psycopg2

BASE_DIR = Path(__file__).parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend-python"
H5_DIR = BASE_DIR / "H5"
SRC_DIR = BASE_DIR / "src"

SERVER_URL = "http://8.153.93.123:8000"
LOCAL_URL = "http://localhost:8000"

LOCAL_DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "tq",
    "user": "postgres",
    "password": "123456"
}

SERVER_DB_CONFIG = {
    "host": "8.153.93.123",
    "port": 5432,
    "database": "tq",
    "user": "postgres",
    "password": "123456"
}


class ConsistencyChecker:
    def __init__(self):
        self.results = {
            "check_time": datetime.now().isoformat(),
            "local": {},
            "server": {},
            "differences": [],
            "status": "checking"
        }
        
    def fetch_api(self, url: str, timeout: int = 10) -> Dict:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            return {"error": str(e)}
    
    def check_local_files(self) -> Dict[str, Any]:
        print("\n=== 检查本地文件结构 ===")
        local_files = {
            "backend_files": [],
            "h5_files": [],
            "src_files": [],
            "models": [],
            "api_routes": [],
            "requirements": None,
            "env_vars": {}
        }
        
        for root, dirs, files in os.walk(BACKEND_DIR / "app"):
            for f in files:
                if f.endswith('.py'):
                    rel_path = os.path.relpath(os.path.join(root, f), BACKEND_DIR)
                    local_files["backend_files"].append(rel_path.replace("\\", "/"))
        
        for root, dirs, files in os.walk(BACKEND_DIR / "app" / "models"):
            for f in files:
                if f.endswith('.py') and f != '__init__.py':
                    local_files["models"].append(f.replace('.py', ''))
        
        for root, dirs, files in os.walk(BACKEND_DIR / "app" / "api" / "v1"):
            for f in files:
                if f.endswith('.py') and f != '__init__.py':
                    local_files["api_routes"].append(f.replace('.py', ''))
        
        for root, dirs, files in os.walk(H5_DIR / "src"):
            for f in files:
                if f.endswith(('.ts', '.vue', '.js')):
                    rel_path = os.path.relpath(os.path.join(root, f), H5_DIR)
                    local_files["h5_files"].append(rel_path.replace("\\", "/"))
        
        for root, dirs, files in os.walk(SRC_DIR):
            for f in files:
                if f.endswith(('.ts', '.vue', '.js')):
                    rel_path = os.path.relpath(os.path.join(root, f), SRC_DIR)
                    local_files["src_files"].append(rel_path.replace("\\", "/"))
        
        req_file = BACKEND_DIR / "requirements.txt"
        if req_file.exists():
            local_files["requirements"] = req_file.read_text(encoding='utf-8')
        
        env_file = BACKEND_DIR / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding='utf-8').split('\n'):
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    local_files["env_vars"][key.strip()] = value.strip()
        
        print(f"  后端Python文件: {len(local_files['backend_files'])} 个")
        print(f"  数据模型: {len(local_files['models'])} 个")
        print(f"  API路由: {len(local_files['api_routes'])} 个")
        print(f"  H5前端文件: {len(local_files['h5_files'])} 个")
        print(f"  PC前端文件: {len(local_files['src_files'])} 个")
        
        self.results["local"]["files"] = local_files
        return local_files
    
    def check_local_database(self) -> Dict[str, Any]:
        print("\n=== 检查本地数据库结构 ===")
        local_db = {
            "tables": {},
            "status": "unknown"
        }
        
        try:
            conn = psycopg2.connect(**LOCAL_DB_CONFIG)
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
                local_db["tables"][table] = columns
            
            cur.close()
            conn.close()
            local_db["status"] = "connected"
            print(f"  数据库表数量: {len(local_db['tables'])}")
            print(f"  表列表: {list(local_db['tables'].keys())}")
            
        except Exception as e:
            print(f"  连接失败: {e}")
            local_db["status"] = f"error: {e}"
        
        self.results["local"]["database"] = local_db
        return local_db
    
    def check_server_api(self) -> Dict[str, Any]:
        print("\n=== 检查服务器API状态 ===")
        server_api = {
            "health": {},
            "openapi": {},
            "status": "unknown"
        }
        
        health = self.fetch_api(f"{SERVER_URL}/health")
        server_api["health"] = health
        print(f"  健康检查: {health}")
        
        openapi = self.fetch_api(f"{SERVER_URL}/api/openapi.json")
        if "error" not in openapi:
            server_api["openapi"] = {
                "title": openapi.get("info", {}).get("title"),
                "version": openapi.get("info", {}).get("version"),
                "paths": list(openapi.get("paths", {}).keys())
            }
            server_api["status"] = "running"
            print(f"  API版本: {server_api['openapi']['version']}")
            print(f"  API路径数量: {len(server_api['openapi']['paths'])}")
        else:
            print(f"  OpenAPI获取失败: {openapi.get('error')}")
        
        self.results["server"]["api"] = server_api
        return server_api
    
    def check_server_database(self) -> Dict[str, Any]:
        print("\n=== 检查服务器数据库结构 ===")
        server_db = {
            "tables": {},
            "status": "unknown"
        }
        
        try:
            conn = psycopg2.connect(**SERVER_DB_CONFIG)
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
                server_db["tables"][table] = columns
            
            cur.close()
            conn.close()
            server_db["status"] = "connected"
            print(f"  数据库表数量: {len(server_db['tables'])}")
            print(f"  表列表: {list(server_db['tables'].keys())}")
            
        except Exception as e:
            print(f"  连接失败: {e}")
            server_db["status"] = f"error: {e}"
        
        self.results["server"]["database"] = server_db
        return server_db
    
    def check_status_constants(self) -> Dict[str, Any]:
        print("\n=== 检查状态常量 ===")
        
        status_info = {
            "local": {},
            "backend_config": {}
        }
        
        local_status_file = BASE_DIR / "packages" / "shared" / "src" / "utils" / "status.ts"
        if local_status_file.exists():
            content = local_status_file.read_text(encoding='utf-8')
            status_info["local"]["status_values"] = re.findall(r"STATUS_\w+\s*=\s*'([^']+)'", content)
            status_info["local"]["work_status"] = re.findall(r"WORK_STATUS\.\w+:\s*'([^']+)'", content)
        
        config_file = BACKEND_DIR / "app" / "config.py"
        if config_file.exists():
            content = config_file.read_text(encoding='utf-8')
            valid_statuses = re.search(r"VALID_STATUSES.*?\[(.*?)\]", content, re.DOTALL)
            if valid_statuses:
                status_info["backend_config"]["valid_statuses"] = re.findall(r"'([^']+)'", valid_statuses.group(1))
            completed_statuses = re.search(r"COMPLETED_STATUSES.*?\[(.*?)\]", content, re.DOTALL)
            if completed_statuses:
                status_info["backend_config"]["completed_statuses"] = re.findall(r"'([^']+)'", completed_statuses.group(1))
        
        print(f"  前端状态常量: {status_info['local'].get('status_values', [])}")
        print(f"  后端有效状态: {status_info['backend_config'].get('valid_statuses', [])}")
        print(f"  后端完成状态: {status_info['backend_config'].get('completed_statuses', [])}")
        
        self.results["status_constants"] = status_info
        return status_info
    
    def check_api_endpoints(self) -> Dict[str, Any]:
        print("\n=== 检查API路由 ===")
        
        api_info = {
            "local": [],
            "routes_detail": {}
        }
        
        local_main = BACKEND_DIR / "app" / "main.py"
        if local_main.exists():
            content = local_main.read_text(encoding='utf-8')
            routers = re.findall(r'app\.include_router\((\w+)\.router', content)
            api_info["local"] = routers
        
        api_dir = BACKEND_DIR / "app" / "api" / "v1"
        for f in api_dir.glob("*.py"):
            if f.name != "__init__.py":
                content = f.read_text(encoding='utf-8')
                routes = re.findall(r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']', content)
                api_info["routes_detail"][f.stem] = routes
        
        print(f"  API路由模块: {len(api_info['local'])} 个")
        print(f"  模块列表: {api_info['local']}")
        
        self.results["api_endpoints"] = api_info
        return api_info
    
    def check_environment(self) -> Dict[str, Any]:
        print("\n=== 检查环境依赖 ===")
        
        env_info = {
            "local_python": None,
            "local_packages": {},
        }
        
        try:
            result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
            env_info["local_python"] = result.stdout.strip()
        except:
            pass
        
        local_req = BACKEND_DIR / "requirements.txt"
        if local_req.exists():
            for line in local_req.read_text(encoding='utf-8').split('\n'):
                if line.strip() and not line.startswith('#'):
                    if '==' in line:
                        pkg, ver = line.split('==')
                        env_info["local_packages"][pkg.strip()] = ver.strip()
        
        print(f"  本地Python: {env_info['local_python']}")
        print(f"  依赖包数量: {len(env_info['local_packages'])}")
        
        self.results["environment"] = env_info
        return env_info
    
    def compare_databases(self, local_db: Dict, server_db: Dict):
        print("\n=== 对比数据库结构 ===")
        
        if local_db["status"] != "connected" or server_db["status"] != "connected":
            print("  无法对比：数据库连接失败")
            return
        
        local_tables = set(local_db.get("tables", {}).keys())
        server_tables = set(server_db.get("tables", {}).keys())
        
        missing_on_server = local_tables - server_tables
        missing_on_local = server_tables - local_tables
        
        if missing_on_server:
            self.results["differences"].append({
                "type": "db_tables_missing_server",
                "message": "服务器缺少表",
                "tables": list(missing_on_server)
            })
            print(f"  服务器缺少表: {missing_on_server}")
        
        if missing_on_local:
            self.results["differences"].append({
                "type": "db_tables_missing_local",
                "message": "本地缺少表",
                "tables": list(missing_on_local)
            })
            print(f"  本地缺少表: {missing_on_local}")
        
        common_tables = local_tables & server_tables
        column_differences = []
        
        for table in common_tables:
            local_cols = set(local_db["tables"][table].keys())
            server_cols = set(server_db["tables"][table].keys())
            
            missing_cols_server = local_cols - server_cols
            missing_cols_local = server_cols - local_cols
            
            if missing_cols_server or missing_cols_local:
                diff = {
                    "type": "db_columns_mismatch",
                    "message": f"表 {table} 字段不一致",
                    "table": table,
                    "local_only": list(missing_cols_server),
                    "server_only": list(missing_cols_local)
                }
                column_differences.append(diff)
                self.results["differences"].append(diff)
                print(f"  表 {table} 字段不一致:")
                if missing_cols_server:
                    print(f"    本地独有: {missing_cols_server}")
                if missing_cols_local:
                    print(f"    服务器独有: {missing_cols_local}")
        
        print(f"  共同表数量: {len(common_tables)}")
        print(f"  字段差异表数量: {len(column_differences)}")
    
    def check_model_definitions(self) -> Dict[str, Any]:
        print("\n=== 检查数据模型定义 ===")
        
        models_info = {}
        models_dir = BACKEND_DIR / "app" / "models"
        
        key_tables = ['periodic_inspection', 'temporary_repair', 'spot_work', 'maintenance_plan', 'personnel', 'project_info']
        
        for table in key_tables:
            model_file = models_dir / f"{table}.py"
            if model_file.exists():
                content = model_file.read_text(encoding='utf-8')
                columns = re.findall(r'(\w+)\s*=\s*Column\(([^)]+)\)', content)
                models_info[table] = {
                    "columns": [col[0] for col in columns],
                    "status_field": None
                }
                
                for col_name, col_def in columns:
                    if col_name == 'status':
                        default_match = re.search(r'default=["\']([^"\']+)["\']', col_def)
                        if default_match:
                            models_info[table]["status_field"] = default_match.group(1)
        
        for table, info in models_info.items():
            print(f"  {table}:")
            print(f"    字段数量: {len(info['columns'])}")
            print(f"    状态默认值: {info['status_field']}")
        
        self.results["models"] = models_info
        return models_info
    
    def run_all_checks(self):
        print("=" * 60)
        print("SSTCP维保系统 - 服务器一致性检查")
        print("=" * 60)
        
        local_files = self.check_local_files()
        local_db = self.check_local_database()
        server_api = self.check_server_api()
        server_db = self.check_server_database()
        
        self.check_status_constants()
        self.check_api_endpoints()
        self.check_environment()
        self.compare_databases(local_db, server_db)
        self.check_model_definitions()
        
        self.results["status"] = "completed"
        
        print("\n" + "=" * 60)
        print("检查完成!")
        print("=" * 60)
        
        if self.results["differences"]:
            print(f"\n发现 {len(self.results['differences'])} 处差异:")
            for diff in self.results["differences"]:
                print(f"  - [{diff['type']}] {diff['message']}")
        else:
            print("\n✓ 服务器与本地配置一致!")
        
        return self.results
    
    def save_report(self, filename: str = None):
        if not filename:
            filename = f"consistency_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_path = BASE_DIR / "scripts" / "check" / filename
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n报告已保存: {report_path}")
        return report_path


if __name__ == "__main__":
    checker = ConsistencyChecker()
    results = checker.run_all_checks()
    checker.save_report()
