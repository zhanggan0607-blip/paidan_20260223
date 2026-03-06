#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务监控脚本 - 每30分钟自动检测并重启服务
监控PC端、H5端和API后端服务，自动检测服务状态并在服务停止时自动重启
"""

import os
import sys
import time
import socket
import subprocess
import logging
import argparse
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(r"D:\共享文件\SSTCP-paidan260120")
LOG_DIR = PROJECT_ROOT / "logs" / "monitor"
LOG_FILE = LOG_DIR / "service-monitor.log"
ERROR_LOG_FILE = LOG_DIR / "service-errors.log"

SERVICES = [
    {
        "name": "PC端",
        "port": 3000,
        "start_command": "npm run dev",
        "working_dir": str(PROJECT_ROOT),
        "process_pattern": "vite"
    },
    {
        "name": "H5端",
        "port": 5180,
        "start_command": "npm run dev",
        "working_dir": str(PROJECT_ROOT / "H5"),
        "process_pattern": "vite"
    },
    {
        "name": "API后端",
        "port": 8000,
        "start_command": "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
        "working_dir": str(PROJECT_ROOT / "backend-python"),
        "process_pattern": "uvicorn"
    }
]


def setup_logging():
    """设置日志"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_FILE, encoding='utf-8')
        ]
    )
    
    error_handler = logging.FileHandler(ERROR_LOG_FILE, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(error_handler)
    
    return logging.getLogger()


logger = setup_logging()


def check_port(port: int, host: str = "localhost", timeout: float = 5.0) -> bool:
    """
    检查端口是否可用
    
    Args:
        port: 端口号
        host: 主机名
        timeout: 超时时间
    
    Returns:
        bool: 端口是否可用
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            return True
    except Exception:
        pass
    
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            encoding='gbk',
            errors='ignore',
            timeout=10
        )
        for line in result.stdout.split('\n'):
            if f":{port}" in line and "LISTENING" in line:
                return True
    except Exception:
        pass
    
    return False


def get_process_by_port(port: int) -> list:
    """
    获取占用端口的进程信息
    
    Args:
        port: 端口号
    
    Returns:
        list: 进程信息列表
    """
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            encoding='gbk',
            errors='ignore'
        )
        
        processes = []
        seen_pids = set()
        for line in result.stdout.split('\n'):
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid in seen_pids or not pid.isdigit():
                        continue
                    seen_pids.add(pid)
                    try:
                        proc_result = subprocess.run(
                            ["wmic", "process", "where", f"ProcessId={pid}", "get", "Name"],
                            capture_output=True,
                            text=True,
                            encoding='gbk',
                            errors='ignore'
                        )
                        lines = [l.strip() for l in proc_result.stdout.strip().split('\n') if l.strip()]
                        if len(lines) >= 2:
                            proc_name = lines[1]
                            processes.append({"pid": pid, "name": proc_name})
                    except Exception:
                        pass
        
        return processes
    except Exception as e:
        logger.error(f"获取进程信息失败: {e}")
        return []


def start_service(service: dict) -> bool:
    """
    启动服务
    
    Args:
        service: 服务配置
    
    Returns:
        bool: 是否启动成功
    """
    name = service["name"]
    port = service["port"]
    start_command = service["start_command"]
    working_dir = service["working_dir"]
    
    logger.warning(f"正在启动 {name} (端口: {port})...")
    
    if not os.path.exists(working_dir):
        logger.error(f"工作目录不存在: {working_dir}")
        return False
    
    try:
        if sys.platform == "win32":
            subprocess.Popen(
                start_command,
                shell=True,
                cwd=working_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            subprocess.Popen(
                start_command,
                shell=True,
                cwd=working_dir
            )
        
        logger.info(f"已发送启动命令")
        
        time.sleep(10)
        
        if check_port(port):
            logger.info(f"{name} 启动成功 (端口: {port})")
            return True
        else:
            logger.warning(f"{name} 启动后端口仍不可用，等待更长时间...")
            time.sleep(15)
            
            if check_port(port):
                logger.info(f"{name} 启动成功 (端口: {port})")
                return True
            
            logger.error(f"{name} 启动失败")
            return False
    except Exception as e:
        logger.error(f"启动 {name} 时发生错误: {e}")
        return False


def get_service_status(service: dict) -> dict:
    """
    获取服务状态
    
    Args:
        service: 服务配置
    
    Returns:
        dict: 服务状态信息
    """
    name = service["name"]
    port = service["port"]
    
    is_running = check_port(port)
    
    process_info = []
    if is_running:
        process_info = get_process_by_port(port)
    
    return {
        "name": name,
        "port": port,
        "is_running": is_running,
        "process_info": process_info,
        "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def analyze_failure(service: dict) -> dict:
    """
    分析服务故障原因
    
    Args:
        service: 服务配置
    
    Returns:
        dict: 分析结果
    """
    name = service["name"]
    port = service["port"]
    working_dir = service["working_dir"]
    
    analysis = {
        "possible_causes": [],
        "recommendations": [],
        "auto_fix_actions": []
    }
    
    processes = get_process_by_port(port)
    if processes:
        proc_names = ", ".join([p["name"] for p in processes])
        proc_pids = [p["pid"] for p in processes]
        analysis["possible_causes"].append(f"端口 {port} 被其他进程占用: {proc_names}")
        analysis["recommendations"].append("检查并终止占用端口的进程")
        analysis["auto_fix_actions"].append({
            "type": "kill_process",
            "pids": proc_pids,
            "description": f"终止占用端口 {port} 的进程"
        })
    
    if name == "API后端":
        if not check_port(5432):
            analysis["possible_causes"].append("PostgreSQL 数据库可能未运行 (端口 5432)")
            analysis["recommendations"].append("检查 PostgreSQL 服务状态")
            analysis["auto_fix_actions"].append({
                "type": "start_postgresql",
                "description": "启动 PostgreSQL 服务"
            })
    
    if name in ["PC端", "H5端"]:
        node_modules = os.path.join(working_dir, "node_modules")
        if not os.path.exists(node_modules):
            analysis["possible_causes"].append("node_modules 目录不存在")
            analysis["recommendations"].append("运行 npm install 安装依赖")
            analysis["auto_fix_actions"].append({
                "type": "npm_install",
                "working_dir": working_dir,
                "description": "安装 npm 依赖"
            })
    
    if not analysis["possible_causes"]:
        analysis["possible_causes"].append("未找到明确原因，可能是进程异常退出")
        analysis["recommendations"].append("检查系统资源使用情况")
        analysis["recommendations"].append("查看详细日志文件")
    
    return analysis


def auto_fix(analysis: dict) -> bool:
    """
    自动修复故障
    
    Args:
        analysis: 故障分析结果
    
    Returns:
        bool: 是否有执行修复操作
    """
    fixed = False
    
    for action in analysis.get("auto_fix_actions", []):
        action_type = action["type"]
        
        try:
            if action_type == "kill_process":
                for pid in action["pids"]:
                    logger.info(f"正在终止进程 PID: {pid}")
                    result = subprocess.run(
                        ["taskkill", "/F", "/PID", str(pid)],
                        capture_output=True,
                        text=True,
                        encoding='gbk',
                        errors='ignore'
                    )
                    if result.returncode == 0:
                        logger.info(f"已终止进程 PID: {pid}")
                        fixed = True
                    else:
                        logger.warning(f"无法终止进程 PID: {pid}")
            
            elif action_type == "start_postgresql":
                logger.info("正在启动 PostgreSQL 服务...")
                result = subprocess.run(
                    ["net", "start", "postgresql-x64-14"],
                    capture_output=True,
                    text=True,
                    encoding='gbk',
                    errors='ignore'
                )
                if result.returncode == 0:
                    logger.info("PostgreSQL 服务已启动")
                    fixed = True
                else:
                    result2 = subprocess.run(
                        ["net", "start", "postgresql-x64-15"],
                        capture_output=True,
                        text=True,
                        encoding='gbk',
                        errors='ignore'
                    )
                    if result2.returncode == 0:
                        logger.info("PostgreSQL 服务已启动")
                        fixed = True
                    else:
                        result3 = subprocess.run(
                            ["net", "start", "postgresql-x64-16"],
                            capture_output=True,
                            text=True,
                            encoding='gbk',
                            errors='ignore'
                        )
                        if result3.returncode == 0:
                            logger.info("PostgreSQL 服务已启动")
                            fixed = True
                        else:
                            logger.warning("无法自动启动 PostgreSQL，请手动检查")
            
            elif action_type == "npm_install":
                working_dir = action["working_dir"]
                logger.info(f"正在安装依赖: {working_dir}")
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=working_dir,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("npm 依赖安装完成")
                    fixed = True
                else:
                    logger.warning(f"npm install 执行失败: {result.stderr[:200]}")
        
        except Exception as e:
            logger.error(f"自动修复操作失败: {e}")
    
    return fixed


def show_status():
    """显示服务状态"""
    print("\n========== 服务状态概览 ==========")
    
    for service in SERVICES:
        status = get_service_status(service)
        
        status_text = "运行中" if status["is_running"] else "已停止"
        color_code = "\033[92m" if status["is_running"] else "\033[91m"
        reset_code = "\033[0m"
        
        print(f"{status['name']} (端口 {status['port']}): {color_code}{status_text}{reset_code}")
        
        if status["process_info"]:
            for proc in status["process_info"]:
                print(f"  - PID: {proc['pid']}, 进程: {proc['name']}")
    
    print("==================================\n")


def repair_all():
    """修复所有服务"""
    logger.warning("开始修复所有服务...")
    
    for service in SERVICES:
        status = get_service_status(service)
        
        if not status["is_running"]:
            logger.warning(f"{service['name']} 未运行，正在启动...")
            start_service(service)
        else:
            logger.info(f"{service['name']} 已在运行中")
    
    logger.info("服务修复完成")


def start_monitoring(interval_minutes: int = 30):
    """
    启动持续监控
    
    Args:
        interval_minutes: 检查间隔（分钟）
    """
    logger.info("=" * 40)
    logger.info("服务监控启动")
    logger.info(f"检查间隔: {interval_minutes} 分钟")
    logger.info(f"项目根目录: {PROJECT_ROOT}")
    logger.info("=" * 40)
    
    while True:
        check_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"\n---------- 开始检查 [{check_time}] ----------")
        
        for service in SERVICES:
            status = get_service_status(service)
            
            if status["is_running"]:
                process_info = "未知"
                if status["process_info"]:
                    proc = status["process_info"][0]
                    process_info = f"PID: {proc['pid']}, 进程: {proc['name']}"
                logger.info(f"{service['name']} 运行正常 - {process_info}")
            else:
                logger.error(f"{service['name']} 服务已停止!")
                
                analysis = analyze_failure(service)
                
                logger.warning("故障分析:")
                for cause in analysis["possible_causes"]:
                    logger.warning(f"  - {cause}")
                
                if analysis.get("auto_fix_actions"):
                    logger.warning("正在执行自动修复...")
                    auto_fix(analysis)
                    time.sleep(3)
                
                logger.warning(f"正在尝试重启 {service['name']}...")
                
                if start_service(service):
                    logger.info(f"{service['name']} 重启成功")
                else:
                    logger.error(f"{service['name']} 重启失败，需要人工干预!")
        
        logger.info("---------- 检查完成 ----------\n")
        
        logger.info(f"等待 {interval_minutes} 分钟后进行下一次检查...")
        time.sleep(interval_minutes * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="服务监控脚本")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["start", "status", "repair", "help"],
                       help="命令: start=启动监控, status=查看状态, repair=修复服务, help=帮助")
    parser.add_argument("-i", "--interval", type=int, default=30,
                       help="检查间隔（分钟），默认30")
    parser.add_argument("-p", "--project-root", type=str, default=str(PROJECT_ROOT),
                       help="项目根目录")
    
    args = parser.parse_args()
    
    if args.command == "start":
        start_monitoring(args.interval)
    elif args.command == "status":
        show_status()
    elif args.command == "repair":
        repair_all()
    else:
        print("""
服务监控脚本使用说明:
  python service_monitor.py start    - 启动持续监控 (每30分钟检查一次)
  python service_monitor.py status   - 查看当前服务状态
  python service_monitor.py repair   - 修复所有停止的服务

参数:
  -i, --interval      检查间隔(分钟)，默认30
  -p, --project-root  项目根目录

示例:
  python service_monitor.py start -i 15
  python service_monitor.py status
""")


if __name__ == "__main__":
    main()
