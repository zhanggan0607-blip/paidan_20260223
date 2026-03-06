#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一键启动所有服务脚本
启动PC端、H5端和API后端服务
"""

import os
import sys
import time
import socket
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(r"D:\共享文件\SSTCP-paidan260120")

SERVICES = [
    {
        "name": "API后端",
        "port": 8000,
        "command": "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
        "working_dir": str(PROJECT_ROOT / "backend-python")
    },
    {
        "name": "PC端",
        "port": 3000,
        "command": "npm run dev",
        "working_dir": str(PROJECT_ROOT)
    },
    {
        "name": "H5端",
        "port": 5180,
        "command": "npm run dev",
        "working_dir": str(PROJECT_ROOT / "H5")
    }
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


def start_service(name: str, command: str, working_dir: str, port: int) -> bool:
    """启动服务"""
    if check_port(port):
        print(f"[WARN] {name} 已在运行中 (端口: {port})")
        return True
    
    print(f"[INFO] 正在启动 {name}...")
    
    if not os.path.exists(working_dir):
        print(f"[ERROR] 工作目录不存在: {working_dir}")
        return False
    
    try:
        if sys.platform == "win32":
            subprocess.Popen(
                command,
                shell=True,
                cwd=working_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            subprocess.Popen(
                command,
                shell=True,
                cwd=working_dir
            )
        
        print(f"[INFO] {name} 启动命令已执行")
        
        max_wait = 30
        waited = 0
        while waited < max_wait:
            if check_port(port):
                print(f"[INFO] {name} 启动成功!")
                return True
            time.sleep(2)
            waited += 2
            print(".", end="", flush=True)
        
        print(f"\n[WARN] {name} 启动超时，请检查日志")
        return False
    except Exception as e:
        print(f"[ERROR] 启动 {name} 时发生错误: {e}")
        return False


def main():
    """主函数"""
    print()
    print("=" * 40)
    print("      工程维保系统 - 服务启动脚本      ")
    print("=" * 40)
    print()
    
    results = {}
    
    for service in SERVICES:
        result = start_service(
            service["name"],
            service["command"],
            service["working_dir"],
            service["port"]
        )
        results[service["name"]] = result
        time.sleep(3)
    
    print()
    print("=" * 40)
    print("              启动结果汇总              ")
    print("=" * 40)
    
    for service in SERVICES:
        status = "成功" if results[service["name"]] else "失败"
        print(f"{service['name']} (端口 {service['port']}): {status}")
    
    print()
    print("访问地址:")
    print("  PC端:     http://localhost:3000")
    print("  H5端:     http://localhost:5180")
    print("  API:      http://localhost:8000")
    print("  API文档:  http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
