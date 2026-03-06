#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建Windows计划任务，自动运行服务监控
创建一个Windows计划任务，每30分钟自动运行服务监控脚本
"""

import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(r"D:\共享文件\SSTCP-paidan260120")
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "service_monitor.py"
TASK_NAME = "SSTCP-ServiceMonitor"


def create_task(interval_minutes: int = 30):
    """创建Windows计划任务"""
    
    print("正在创建Windows计划任务...")
    
    delete_cmd = f'schtasks /delete /tn "{TASK_NAME}" /f'
    subprocess.run(delete_cmd, shell=True, capture_output=True)
    
    python_exe = sys.executable
    script_path = str(SCRIPT_PATH)
    
    create_cmd = f'''schtasks /create /tn "{TASK_NAME}" /tr "python \\"{script_path}\\" start -i {interval_minutes}" /sc minute /mo {interval_minutes} /rl HIGHEST /f'''
    
    result = subprocess.run(create_cmd, shell=True, capture_output=True, text=True, encoding='gbk', errors='ignore')
    
    if result.returncode == 0:
        print("\n计划任务创建成功!")
    else:
        print(f"\n创建计划任务时出现警告: {result.stderr}")
        print("任务可能已创建，请检查任务计划程序")
    
    print("")
    print(f"任务名称: {TASK_NAME}")
    print(f"检查间隔: {interval_minutes} 分钟")
    print(f"脚本路径: {script_path}")
    print("")
    print("管理命令:")
    print(f"  查看任务: schtasks /query /tn \"{TASK_NAME}\"")
    print(f"  手动运行: schtasks /run /tn \"{TASK_NAME}\"")
    print(f"  删除任务: schtasks /delete /tn \"{TASK_NAME}\" /f")
    print("")
    
    run_result = subprocess.run(f'schtasks /run /tn "{TASK_NAME}"', shell=True, capture_output=True)
    if run_result.returncode == 0:
        print("已启动监控任务!")
    else:
        print("请手动启动监控任务")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="创建Windows计划任务")
    parser.add_argument("-i", "--interval", type=int, default=30,
                       help="检查间隔（分钟），默认30")
    
    args = parser.parse_args()
    
    create_task(args.interval)


if __name__ == "__main__":
    main()
