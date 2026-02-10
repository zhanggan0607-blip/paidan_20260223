import os
import sys

print("=" * 80)
print("检查数据插入流程和定期维护任务")
print("=" * 80)

print("\n1. 检查后端项目目录结构\n")

backend_dir = "d:\\共享文件\\SSTCP-paidan260120\\backend-python"

def find_files(directory, pattern, exclude_dirs=None):
    """查找匹配模式的文件"""
    if exclude_dirs is None:
        exclude_dirs = ['__pycache__', 'node_modules', '.git', 'venv', 'env']
    
    matches = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for filename in files:
            if pattern in filename:
                matches.append(os.path.join(root, filename))
    return matches

print("=" * 80)
print("2. 检查数据初始化脚本")
print("=" * 80)

init_scripts = find_files(backend_dir, 'init')
seed_scripts = find_files(backend_dir, 'seed')
data_scripts = find_files(backend_dir, 'data')

print(f"\n初始化脚本 ({len(init_scripts)} 个):")
for script in init_scripts:
    print(f"  - {script}")

print(f"\n种子数据脚本 ({len(seed_scripts)} 个):")
for script in seed_scripts:
    print(f"  - {script}")

print(f"\n数据脚本 ({len(data_scripts)} 个):")
for script in data_scripts:
    print(f"  - {script}")

print("\n" + "=" * 80)
print("3. 检查定时任务脚本")
print("=" * 80)

cron_files = find_files(backend_dir, 'cron')
schedule_files = find_files(backend_dir, 'schedule')
task_files = find_files(backend_dir, 'task')

print(f"\n定时任务相关文件 ({len(cron_files)} 个):")
for f in cron_files:
    print(f"  - {f}")

print(f"\n调度相关文件 ({len(schedule_files)} 个):")
for f in schedule_files:
    print(f"  - {f}")

print(f"\n任务相关文件 ({len(task_files)} 个):")
for f in task_files:
    print(f"  - {f}")

print("\n" + "=" * 80)
print("4. 检查API路由文件")
print("=" * 80)

api_dir = os.path.join(backend_dir, "app", "api")
if os.path.exists(api_dir):
    api_files = []
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py') and filename not in ['__init__.py']:
                api_files.append(os.path.join(root, filename))
    
    print(f"\nAPI路由文件 ({len(api_files)} 个):")
    for f in api_files:
        print(f"  - {f}")

print("\n" + "=" * 80)
print("5. 检查Service层文件")
print("=" * 80)

services_dir = os.path.join(backend_dir, "app", "services")
if os.path.exists(services_dir):
    service_files = []
    for root, dirs, files in os.walk(services_dir):
        for filename in files:
            if filename.endswith('.py') and filename not in ['__init__.py']:
                service_files.append(os.path.join(root, filename))
    
    print(f"\nService文件 ({len(service_files)} 个):")
    for f in service_files:
        print(f"  - {f}")

print("\n" + "=" * 80)
print("6. 检查Repository层文件")
print("=" * 80)

repo_dir = os.path.join(backend_dir, "app", "repositories")
if os.path.exists(repo_dir):
    repo_files = []
    for root, dirs, files in os.walk(repo_dir):
        for filename in files:
            if filename.endswith('.py') and filename not in ['__init__.py']:
                repo_files.append(os.path.join(root, filename))
    
    print(f"\nRepository文件 ({len(repo_files)} 个):")
    for f in repo_files:
        print(f"  - {f}")

print("\n" + "=" * 80)
print("7. 检查配置文件")
print("=" * 80)

config_files = find_files(backend_dir, '.env')
config_files.extend(find_files(backend_dir, 'config'))

print(f"\n配置文件 ({len(config_files)} 个):")
for f in config_files:
    print(f"  - {f}")

print("\n" + "=" * 80)
print("8. 检查main.py中的路由注册")
print("=" * 80)

main_file = os.path.join(backend_dir, "app", "main.py")
if os.path.exists(main_file):
    print(f"\n读取 {main_file}...")
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'maintenance_plan' in content.lower():
            print("✅ main.py 中包含 maintenance_plan 相关代码")
            
            import re
            router_patterns = re.findall(r'from app\.api\.v1 import (.+)', content)
            print(f"\n导入的路由模块: {router_patterns}")
            
            include_patterns = re.findall(r'app\.include_router\((.+)\)', content)
            print(f"\n注册的路由:")
            for pattern in include_patterns:
                print(f"  - {pattern}")
        else:
            print("❌ main.py 中未找到 maintenance_plan 相关代码")
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")

print("\n" + "=" * 80)
print("9. 检查requirements.txt")
print("=" * 80)

req_file = os.path.join(backend_dir, "requirements.txt")
if os.path.exists(req_file):
    print(f"\n读取 {req_file}...")
    try:
        with open(req_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        scheduler_packages = [line for line in content.split('\n') 
                             if any(pkg in line.lower() for pkg in ['schedule', 'celery', 'apscheduler', 'cron'])]
        
        if scheduler_packages:
            print("✅ 找到定时任务相关包:")
            for pkg in scheduler_packages:
                print(f"  - {pkg}")
        else:
            print("ℹ️  未找到定时任务相关包")
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
