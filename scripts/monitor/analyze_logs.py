#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志分析工具 - 分析服务错误日志并提供修复建议
分析监控日志、服务日志，识别常见问题并提供解决方案
"""

import os
import re
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(r"D:\共享文件\SSTCP-paidan260120")
LOG_DIR = PROJECT_ROOT / "logs" / "monitor"
MONITOR_LOG = LOG_DIR / "service-monitor.log"
ERROR_LOG = LOG_DIR / "service-errors.log"

KNOWN_ISSUES = [
    {
        "pattern": r"EADDRINUSE|端口.*被占用|address already in use",
        "description": "端口被占用",
        "solution": "终止占用端口的进程或更改服务端口配置",
        "auto_fix": True
    },
    {
        "pattern": r"ENOENT|no such file or directory|找不到.*文件",
        "description": "文件或目录不存在",
        "solution": "检查文件路径是否正确，确保依赖已安装",
        "auto_fix": False
    },
    {
        "pattern": r"ENOMEM|out of memory|内存不足",
        "description": "内存不足",
        "solution": "关闭不必要的程序，增加系统内存",
        "auto_fix": False
    },
    {
        "pattern": r"ECONNREFUSED|connection refused|连接被拒绝",
        "description": "连接被拒绝",
        "solution": "检查目标服务是否运行，防火墙设置是否正确",
        "auto_fix": True
    },
    {
        "pattern": r"PostgreSQL.*not running|数据库.*未运行|could not connect to server",
        "description": "数据库连接失败",
        "solution": "启动PostgreSQL服务，检查数据库配置",
        "auto_fix": True
    },
    {
        "pattern": r"node_modules.*not found|Cannot find module",
        "description": "Node模块缺失",
        "solution": "运行 npm install 安装依赖",
        "auto_fix": True
    },
    {
        "pattern": r"TypeError|ReferenceError|SyntaxError",
        "description": "代码错误",
        "solution": "检查代码语法和类型定义",
        "auto_fix": False
    },
    {
        "pattern": r"timeout|超时",
        "description": "请求超时",
        "solution": "检查网络连接，增加超时时间配置",
        "auto_fix": False
    },
    {
        "pattern": r"permission denied|权限不足|EACCES",
        "description": "权限不足",
        "solution": "以管理员身份运行或修改文件权限",
        "auto_fix": False
    }
]


def parse_log_line(line: str) -> dict:
    """解析日志行"""
    match = re.match(r'\[([^\]]+)\] \[([^\]]+)\] (.+)', line)
    if match:
        return {
            "timestamp": match.group(1),
            "level": match.group(2),
            "message": match.group(3),
            "raw": line
        }
    return None


def get_log_entries(log_file: Path, hours: int) -> list:
    """获取指定时间范围内的日志条目"""
    if not log_file.exists():
        return []
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    entries = []
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = parse_log_line(line.strip())
                if entry:
                    try:
                        log_time = datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S")
                        if log_time >= cutoff_time:
                            entries.append(entry)
                    except ValueError:
                        pass
    except Exception as e:
        print(f"[ERROR] 读取日志文件失败: {e}")
    
    return entries


def find_known_issues(entries: list) -> list:
    """查找已知问题"""
    found_issues = []
    
    for entry in entries:
        for issue in KNOWN_ISSUES:
            if re.search(issue["pattern"], entry["message"], re.IGNORECASE):
                found_issues.append({
                    "timestamp": entry["timestamp"],
                    "level": entry["level"],
                    "message": entry["message"],
                    "issue": issue["description"],
                    "solution": issue["solution"],
                    "auto_fix": issue["auto_fix"],
                    "pattern": issue["pattern"]
                })
    
    return found_issues


def get_statistics(entries: list) -> dict:
    """获取统计信息"""
    stats = {
        "total": len(entries),
        "errors": sum(1 for e in entries if e["level"] == "ERROR"),
        "warnings": sum(1 for e in entries if e["level"] == "WARN"),
        "info": sum(1 for e in entries if e["level"] == "INFO"),
        "restarts": sum(1 for e in entries if "重启" in e["message"] or "启动" in e["message"]),
        "failed_restarts": sum(1 for e in entries if ("重启失败" in e["message"] or "启动失败" in e["message"]))
    }
    return stats


def check_port(port: int, host: str = "localhost", timeout: float = 2.0) -> bool:
    """检查端口是否可用"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def auto_fix(issues: list) -> int:
    """尝试自动修复问题"""
    import subprocess
    import time
    
    fixed_count = 0
    
    for issue in issues:
        if not issue["auto_fix"]:
            continue
        
        print(f"\n尝试自动修复: {issue['issue']}")
        
        pattern = issue["pattern"]
        
        if re.search(r"EADDRINUSE|端口.*被占用", pattern):
            match = re.search(r"端口 (\d+)", issue["message"])
            if match:
                port = int(match.group(1))
                print(f"  检查端口 {port} 占用情况...")
                
                try:
                    result = subprocess.run(
                        ["netstat", "-ano"],
                        capture_output=True,
                        text=True,
                        encoding='gbk',
                        errors='ignore'
                    )
                    
                    for line in result.stdout.split('\n'):
                        if f":{port}" in line and "LISTENING" in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                print(f"  发现占用进程 PID: {pid}")
                except Exception:
                    pass
        
        elif re.search(r"PostgreSQL.*not running|数据库.*未运行", pattern):
            print("  尝试启动 PostgreSQL 服务...")
            try:
                subprocess.run(["net", "start", "postgresql-x64-14"], capture_output=True)
                print("  PostgreSQL 服务启动命令已执行")
                fixed_count += 1
            except Exception as e:
                print(f"  无法自动启动 PostgreSQL: {e}")
        
        elif re.search(r"node_modules.*not found|Cannot find module", pattern):
            print("  检查 node_modules 目录...")
            
            dirs = [
                str(PROJECT_ROOT),
                str(PROJECT_ROOT / "H5")
            ]
            
            for dir_path in dirs:
                node_modules = os.path.join(dir_path, "node_modules")
                if not os.path.exists(node_modules):
                    print(f"  缺少 node_modules: {dir_path}")
                    print(f"  请手动运行: cd {dir_path} && npm install")
        
        elif re.search(r"ECONNREFUSED|connection refused", pattern):
            print("  检查相关服务状态...")
            
            ports = [8000, 3000, 5180, 5432]
            for port in ports:
                status = "正常" if check_port(port) else "未响应"
                print(f"  端口 {port}: {status}")
    
    return fixed_count


def show_report(entries: list, issues: list, stats: dict, hours: int):
    """显示分析报告"""
    print("\n" + "=" * 40)
    print(f"         日志分析报告 (最近 {hours} 小时)         ")
    print("=" * 40 + "\n")
    
    print("统计概览:")
    print(f"  总日志条目: {stats['total']}")
    print(f"  错误数量: {stats['errors']}")
    print(f"  警告数量: {stats['warnings']}")
    print(f"  信息数量: {stats['info']}")
    print(f"  服务重启: {stats['restarts']}")
    print(f"  重启失败: {stats['failed_restarts']}")
    
    if issues:
        print("\n发现的问题:")
        
        issue_counter = Counter(i["issue"] for i in issues)
        
        for issue_name, count in issue_counter.most_common():
            print(f"\n  [{count}次] {issue_name}")
            
            matching_issues = [i for i in issues if i["issue"] == issue_name]
            if matching_issues:
                last_issue = matching_issues[-1]
                print(f"    最后发生: {last_issue['timestamp']}")
                print(f"    解决方案: {last_issue['solution']}")
                
                if last_issue["auto_fix"]:
                    print("    [可自动修复]")
    else:
        print("\n未发现已知问题")
    
    recent_errors = [e for e in entries if e["level"] == "ERROR"][-5:]
    
    if recent_errors:
        print("\n最近的错误日志:")
        for err in recent_errors:
            print(f"  [{err['timestamp']}] {err['message']}")
    
    print("\n" + "=" * 40 + "\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="日志分析工具")
    parser.add_argument("-H", "--hours", type=int, default=24,
                       help="分析最近N小时的日志，默认24")
    parser.add_argument("--fix", action="store_true",
                       help="尝试自动修复已知问题")
    
    args = parser.parse_args()
    
    print("正在分析日志...")
    
    all_entries = []
    all_entries.extend(get_log_entries(MONITOR_LOG, args.hours))
    all_entries.extend(get_log_entries(ERROR_LOG, args.hours))
    
    all_entries.sort(key=lambda x: x["timestamp"])
    
    stats = get_statistics(all_entries)
    issues = find_known_issues(all_entries)
    
    show_report(all_entries, issues, stats, args.hours)
    
    if args.fix and issues:
        print("\n执行自动修复...")
        fixed_count = auto_fix(issues)
        print(f"\n自动修复完成，共处理 {fixed_count} 个问题")
    
    if issues and not args.fix:
        print("提示: 使用 --fix 参数尝试自动修复已知问题")


if __name__ == "__main__":
    main()
