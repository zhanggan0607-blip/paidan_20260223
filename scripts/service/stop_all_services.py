#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
停止所有服务脚本
停止PC端、H5端和API后端服务
"""

import subprocess
import socket
from pathlib import Path

PROJECT_ROOT = Path(r"D:\共享文件\SSTCP-paidan260120")

SERVICES = [
    {"name": "PC端", "port": 3000},
    {"name": "H5端", "port": 5180},
    {"name": "API后端", "port": 8000}
]


def check_port(port: int, host: str = "localhost", timeout: float = 3.0) -> bool:
    """检查端口是否可用"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def get_process_by_port(port: int) -> list:
    """获取占用端口的进程PID列表"""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            encoding='gbk',
            errors='ignore'
        )
        
        pids = set()
        for line in result.stdout.split('\n'):
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids.add(pid)
        
        return list(pids)
    except Exception:
        return []


def stop_service(name: str, port: int) -> bool:
    """停止服务"""
    if not check_port(port):
        print(f"[WARN] {name} 未运行 (端口: {port})")
        return False
    
    pids = get_process_by_port(port)
    
    if not pids:
        print(f"[WARN] {name} 未找到占用端口的进程")
        return False
    
    print(f"[INFO] 正在停止 {name} (PID: {', '.join(pids)})...")
    
    for pid in pids:
        try:
            subprocess.run(
                ["taskkill", "/F", "/PID", pid],
                capture_output=True,
                text=True,
                encoding='gbk',
                errors='ignore'
            )
            print(f"[INFO] 已终止进程 PID: {pid}")
        except Exception as e:
            print(f"[ERROR] 无法终止进程 {pid}: {e}")
    
    import time
    time.sleep(2)
    
    if not check_port(port):
        print(f"[INFO] {name} 已停止")
        return True
    else:
        print(f"[ERROR] {name} 停止失败，端口仍被占用")
        return False


def main():
    """主函数"""
    print()
    print("=" * 40)
    print("      工程维保系统 - 停止服务脚本      ")
    print("=" * 40)
    print()
    
    for service in SERVICES:
        stop_service(service["name"], service["port"])
    
    print()
    print("所有服务已停止")
    print()


if __name__ == "__main__":
    main()
