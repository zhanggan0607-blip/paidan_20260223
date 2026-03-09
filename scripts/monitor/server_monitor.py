#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务器监控脚本 - 每30分钟自动检测服务器服务状态
监控服务器上的PC端、H5端和API后端服务，自动检测服务状态并在服务停止时自动修复
"""

import os
import sys
import time
import socket
import logging
import argparse
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(r"D:\共享文件\SSTCP-paidan260120")
LOG_DIR = PROJECT_ROOT / "logs" / "monitor"
LOG_FILE = LOG_DIR / "server-monitor.log"
ERROR_LOG_FILE = LOG_DIR / "server-errors.log"

SERVER_IP = "8.153.93.123"
SSH_PORT = 22
SSH_USER = "root"
SSH_PASSWORD = "Lily421020"

SERVER_SERVICES = [
    {
        "name": "PC端",
        "type": "docker",
        "container": "sstcp-frontend-pc",
        "port": 80,
        "url_path": "/"
    },
    {
        "name": "H5端",
        "type": "docker",
        "container": "sstcp-frontend-h5",
        "port": 81,
        "url_path": "/h5/"
    },
    {
        "name": "API后端",
        "type": "process",
        "process_pattern": "uvicorn",
        "port": 8000,
        "url_path": "/docs",
        "start_command": "cd /opt/sstcp/backend-python && nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /var/log/sstcp-backend.log 2>&1 &"
    },
    {
        "name": "数据库",
        "type": "docker",
        "container": "sstcp-db",
        "port": 5432,
        "url_path": None
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


def get_ssh_client():
    """
    获取SSH客户端连接
    
    Returns:
        paramiko.SSHClient: SSH客户端
    """
    try:
        import paramiko
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(SERVER_IP, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD, timeout=60)
        return client
    except ImportError:
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"])
        return get_ssh_client()
    except Exception as e:
        logger.error(f"SSH连接失败: {e}")
        return None


def run_ssh_command(command: str, timeout: int = 120) -> tuple:
    """
    执行SSH命令
    
    Args:
        command: 要执行的命令
        timeout: 超时时间（秒）
    
    Returns:
        tuple: (exit_code, stdout, stderr)
    """
    try:
        client = get_ssh_client()
        if client is None:
            return -1, "", "SSH连接失败"
        
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        client.close()
        return exit_code, output, error
    except Exception as e:
        logger.error(f"SSH命令执行失败: {e}")
        return -1, "", str(e)


def check_server_port(port: int, host: str = SERVER_IP, timeout: float = 10.0) -> bool:
    """
    检查服务器端口是否可用
    
    Args:
        port: 端口号
        host: 服务器IP
        timeout: 超时时间
    
    Returns:
        bool: 端口是否可用
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_http_endpoint(port: int, path: str, host: str = SERVER_IP, timeout: float = 10.0) -> bool:
    """
    检查HTTP端点是否可访问
    
    Args:
        port: 端口号
        path: URL路径
        host: 服务器IP
        timeout: 超时时间
    
    Returns:
        bool: 端点是否可访问
    """
    import urllib.request
    import urllib.error
    
    try:
        url = f"http://{host}:{port}{path}"
        req = urllib.request.Request(url, method='GET')
        req.add_header('User-Agent', 'SSTCP-Monitor/1.0')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status == 200
    except Exception:
        return False


def get_container_status(container_name: str) -> dict:
    """
    获取Docker容器状态
    
    Args:
        container_name: 容器名称
    
    Returns:
        dict: 容器状态信息
    """
    cmd = f"docker inspect --format='{{{{.State.Status}}}}' {container_name} 2>/dev/null || echo 'not_found'"
    exit_code, output, error = run_ssh_command(cmd)
    
    status = output.strip().strip("'")
    
    if exit_code != 0 or status == 'not_found':
        return {
            "exists": False,
            "status": "not_found",
            "running": False
        }
    
    return {
        "exists": True,
        "status": status,
        "running": status == "running"
    }


def get_process_status(port: int) -> dict:
    """
    获取端口对应的进程状态
    
    Args:
        port: 端口号
    
    Returns:
        dict: 进程状态信息
    """
    cmd = f"netstat -tlnp 2>/dev/null | grep ':{port}' | head -1"
    exit_code, output, error = run_ssh_command(cmd)
    
    if exit_code != 0 or not output.strip():
        return {
            "running": False,
            "pid": None,
            "process_name": None
        }
    
    parts = output.strip().split()
    pid = None
    process_name = None
    
    for part in parts:
        if '/' in part:
            pid_proc = part.split('/')
            if len(pid_proc) >= 2:
                pid = pid_proc[0]
                process_name = pid_proc[1]
                break
    
    return {
        "running": True,
        "pid": pid,
        "process_name": process_name
    }


def get_container_health(container_name: str) -> str:
    """
    获取容器健康状态
    
    Args:
        container_name: 容器名称
    
    Returns:
        str: 健康状态
    """
    cmd = f"docker inspect --format='{{{{.State.Health.Status}}}}' {container_name} 2>/dev/null || echo 'unknown'"
    exit_code, output, error = run_ssh_command(cmd)
    return output.strip().strip("'")


def get_container_stats(container_name: str) -> dict:
    """
    获取容器资源使用统计
    
    Args:
        container_name: 容器名称
    
    Returns:
        dict: 资源使用统计
    """
    cmd = f"docker stats --no-stream --format '{{{{.CPUPerc}}}},{{{{.MemUsage}}}},{{{{.NetIO}}}}' {container_name} 2>/dev/null"
    exit_code, output, error = run_ssh_command(cmd)
    
    if exit_code != 0 or not output.strip():
        return {"cpu": "N/A", "memory": "N/A", "network": "N/A"}
    
    parts = output.strip().split(',')
    if len(parts) >= 3:
        return {
            "cpu": parts[0],
            "memory": parts[1],
            "network": parts[2]
        }
    
    return {"cpu": "N/A", "memory": "N/A", "network": "N/A"}


def restart_container(container_name: str) -> bool:
    """
    重启Docker容器
    
    Args:
        container_name: 容器名称
    
    Returns:
        bool: 是否重启成功
    """
    logger.warning(f"正在重启容器 {container_name}...")
    
    cmd = f"docker restart {container_name}"
    exit_code, output, error = run_ssh_command(cmd, timeout=60)
    
    if exit_code == 0:
        logger.info(f"容器 {container_name} 重启命令已发送")
        time.sleep(10)
        
        status = get_container_status(container_name)
        if status["running"]:
            logger.info(f"容器 {container_name} 重启成功")
            return True
        else:
            logger.error(f"容器 {container_name} 重启后仍未运行")
            return False
    else:
        logger.error(f"容器 {container_name} 重启失败: {error}")
        return False


def start_container(container_name: str) -> bool:
    """
    启动Docker容器
    
    Args:
        container_name: 容器名称
    
    Returns:
        bool: 是否启动成功
    """
    logger.warning(f"正在启动容器 {container_name}...")
    
    cmd = f"docker start {container_name}"
    exit_code, output, error = run_ssh_command(cmd, timeout=60)
    
    if exit_code == 0:
        logger.info(f"容器 {container_name} 启动命令已发送")
        time.sleep(10)
        
        status = get_container_status(container_name)
        if status["running"]:
            logger.info(f"容器 {container_name} 启动成功")
            return True
        else:
            logger.error(f"容器 {container_name} 启动后仍未运行")
            return False
    else:
        logger.error(f"容器 {container_name} 启动失败: {error}")
        return False


def start_process_service(service: dict) -> bool:
    """
    启动进程类型的服务
    
    Args:
        service: 服务配置
    
    Returns:
        bool: 是否启动成功
    """
    name = service["name"]
    port = service["port"]
    start_command = service.get("start_command", "")
    
    if not start_command:
        logger.error(f"{name} 未配置启动命令")
        return False
    
    logger.warning(f"正在启动 {name}...")
    
    exit_code, output, error = run_ssh_command(start_command, timeout=30)
    
    if exit_code == 0:
        logger.info(f"{name} 启动命令已发送")
        time.sleep(5)
        
        proc_status = get_process_status(port)
        if proc_status["running"]:
            logger.info(f"{name} 启动成功 (PID: {proc_status['pid']})")
            return True
        else:
            logger.error(f"{name} 启动后端口仍不可用")
            return False
    else:
        logger.error(f"{name} 启动失败: {error}")
        return False


def check_docker_service() -> bool:
    """
    检查Docker服务是否运行
    
    Returns:
        bool: Docker服务是否运行
    """
    cmd = "systemctl is-active docker 2>/dev/null || service docker status 2>/dev/null | grep -q running"
    exit_code, output, error = run_ssh_command(cmd)
    return exit_code == 0


def restart_docker_service() -> bool:
    """
    重启Docker服务
    
    Returns:
        bool: 是否重启成功
    """
    logger.warning("正在重启Docker服务...")
    
    cmd = "systemctl restart docker 2>/dev/null || service docker restart"
    exit_code, output, error = run_ssh_command(cmd, timeout=120)
    
    if exit_code == 0:
        logger.info("Docker服务重启成功")
        time.sleep(15)
        return True
    else:
        logger.error(f"Docker服务重启失败: {error}")
        return False


def get_docker_containers() -> list:
    """
    获取所有Docker容器列表
    
    Returns:
        list: 容器列表
    """
    cmd = "docker ps -a --format '{{.Names}}|{{.Status}}|{{.Ports}}'"
    exit_code, output, error = run_ssh_command(cmd)
    
    if exit_code != 0:
        return []
    
    containers = []
    for line in output.strip().split('\n'):
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 2:
                containers.append({
                    "name": parts[0],
                    "status": parts[1],
                    "ports": parts[2] if len(parts) > 2 else ""
                })
    
    return containers


def analyze_container_failure(service: dict) -> dict:
    """
    分析容器故障原因
    
    Args:
        service: 服务配置
    
    Returns:
        dict: 分析结果
    """
    container_name = service["container"]
    
    analysis = {
        "possible_causes": [],
        "recommendations": [],
        "auto_fix_actions": []
    }
    
    cmd = f"docker logs --tail 50 {container_name} 2>&1"
    exit_code, logs, error = run_ssh_command(cmd)
    
    if exit_code == 0 and logs:
        logs_lower = logs.lower()
        
        if "out of memory" in logs_lower or "oom" in logs_lower:
            analysis["possible_causes"].append("容器内存不足")
            analysis["recommendations"].append("增加容器内存限制或检查内存泄漏")
        
        if "connection refused" in logs_lower:
            analysis["possible_causes"].append("数据库连接失败")
            analysis["recommendations"].append("检查数据库容器状态")
            analysis["auto_fix_actions"].append({
                "type": "restart_dependency",
                "container": "sstcp-db",
                "description": "重启数据库容器"
            })
        
        if "host not found in upstream" in logs_lower:
            analysis["possible_causes"].append("Nginx配置中后端服务不可达")
            analysis["recommendations"].append("检查后端服务是否运行")
            analysis["auto_fix_actions"].append({
                "type": "check_backend",
                "description": "检查并重启后端服务"
            })
        
        if "port is already allocated" in logs_lower:
            analysis["possible_causes"].append("端口被占用")
            analysis["recommendations"].append("检查端口占用情况")
        
        if "no such file" in logs_lower or "file not found" in logs_lower:
            analysis["possible_causes"].append("文件缺失")
            analysis["recommendations"].append("检查容器挂载卷配置")
        
        if "permission denied" in logs_lower:
            analysis["possible_causes"].append("权限问题")
            analysis["recommendations"].append("检查文件权限配置")
    
    container_status = get_container_status(container_name)
    
    if not container_status["exists"]:
        analysis["possible_causes"].append("容器不存在")
        analysis["recommendations"].append("检查docker-compose配置并重新创建容器")
    elif container_status["status"] == "exited":
        analysis["possible_causes"].append("容器已退出")
        analysis["recommendations"].append("重启容器")
        analysis["auto_fix_actions"].append({
            "type": "start_container",
            "container": container_name,
            "description": f"启动容器 {container_name}"
        })
    elif container_status["status"] == "paused":
        analysis["possible_causes"].append("容器已暂停")
        analysis["recommendations"].append("恢复容器")
    
    if not analysis["possible_causes"]:
        analysis["possible_causes"].append("未找到明确原因，可能是容器异常退出")
        analysis["recommendations"].append("查看详细日志")
    
    return analysis


def auto_fix_service(service: dict, analysis: dict) -> bool:
    """
    自动修复服务故障
    
    Args:
        service: 服务配置
        analysis: 故障分析结果
    
    Returns:
        bool: 是否有执行修复操作
    """
    fixed = False
    
    for action in analysis.get("auto_fix_actions", []):
        action_type = action["type"]
        
        try:
            if action_type == "restart_dependency":
                container = action["container"]
                logger.info(f"正在重启依赖容器 {container}...")
                if restart_container(container):
                    fixed = True
                    time.sleep(5)
            
            elif action_type == "start_container":
                container = action["container"]
                logger.info(f"正在启动容器 {container}...")
                if start_container(container):
                    fixed = True
            
            elif action_type == "check_backend":
                logger.info("检查后端服务状态...")
                backend_status = get_process_status(8000)
                if not backend_status["running"]:
                    logger.warning("后端服务未运行，尝试启动...")
                    for svc in SERVER_SERVICES:
                        if svc["name"] == "API后端":
                            if start_process_service(svc):
                                fixed = True
                                time.sleep(5)
                            break
        
        except Exception as e:
            logger.error(f"自动修复操作失败: {e}")
    
    return fixed


def get_service_status(service: dict) -> dict:
    """
    获取服务状态
    
    Args:
        service: 服务配置
    
    Returns:
        dict: 服务状态信息
    """
    name = service["name"]
    service_type = service.get("type", "docker")
    port = service["port"]
    url_path = service.get("url_path")
    
    port_accessible = check_server_port(port)
    
    if service_type == "docker":
        container_name = service["container"]
        container_status = get_container_status(container_name)
        
        http_accessible = False
        if url_path and port_accessible:
            http_accessible = check_http_endpoint(port, url_path)
        
        health = "unknown"
        if container_status["running"]:
            health = get_container_health(container_name)
        
        stats = {}
        if container_status["running"]:
            stats = get_container_stats(container_name)
        
        is_healthy = (
            container_status["running"] and 
            port_accessible and 
            (http_accessible or url_path is None) and
            health in ["healthy", "unknown"]
        )
        
        return {
            "name": name,
            "type": "docker",
            "container": container_name,
            "port": port,
            "container_status": container_status,
            "port_accessible": port_accessible,
            "http_accessible": http_accessible if url_path else None,
            "health": health,
            "stats": stats,
            "is_healthy": is_healthy,
            "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    else:
        process_status = get_process_status(port)
        
        http_accessible = False
        if url_path and port_accessible:
            http_accessible = check_http_endpoint(port, url_path)
        
        is_healthy = process_status["running"] and port_accessible
        
        return {
            "name": name,
            "type": "process",
            "port": port,
            "process_status": process_status,
            "port_accessible": port_accessible,
            "http_accessible": http_accessible if url_path else None,
            "is_healthy": is_healthy,
            "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


def show_status():
    """显示服务器服务状态"""
    print("\n" + "=" * 60)
    print(f"服务器监控状态 - {SERVER_IP}")
    print("=" * 60)
    
    docker_ok = check_docker_service()
    print(f"\nDocker服务: {'✅ 运行中' if docker_ok else '❌ 未运行'}")
    
    print("\n服务状态:")
    print("-" * 60)
    
    for service in SERVER_SERVICES:
        status = get_service_status(service)
        
        status_icon = "✅" if status["is_healthy"] else "❌"
        port_status = "✅" if status["port_accessible"] else "❌"
        
        if status["type"] == "docker":
            container_status = status["container_status"]["status"]
            print(f"\n{status_icon} {status['name']} ({status['container']})")
            print(f"   容器状态: {container_status}")
            print(f"   端口 {status['port']}: {port_status}")
            
            if status.get("http_accessible") is not None:
                http_status = "✅" if status["http_accessible"] else "❌"
                print(f"   HTTP访问: {http_status}")
            
            if status["health"] != "unknown":
                health_icon = "✅" if status["health"] == "healthy" else "⚠️"
                print(f"   健康检查: {health_icon} {status['health']}")
            
            if status["stats"]:
                print(f"   CPU: {status['stats'].get('cpu', 'N/A')}")
                print(f"   内存: {status['stats'].get('memory', 'N/A')}")
        else:
            process_status = status["process_status"]
            print(f"\n{status_icon} {status['name']} (进程)")
            print(f"   进程状态: {'运行中' if process_status['running'] else '已停止'}")
            if process_status["pid"]:
                print(f"   PID: {process_status['pid']}")
            print(f"   端口 {status['port']}: {port_status}")
            
            if status.get("http_accessible") is not None:
                http_status = "✅" if status["http_accessible"] else "❌"
                print(f"   HTTP访问: {http_status}")
    
    print("\n" + "=" * 60 + "\n")


def repair_all():
    """修复所有服务器服务"""
    logger.warning("开始修复所有服务器服务...")
    
    if not check_docker_service():
        logger.error("Docker服务未运行，尝试启动...")
        if not restart_docker_service():
            logger.error("Docker服务启动失败，无法继续修复")
            return
    
    for service in SERVER_SERVICES:
        status = get_service_status(service)
        
        if not status["is_healthy"]:
            logger.warning(f"{service['name']} 服务异常，正在修复...")
            
            if service.get("type") == "docker":
                if not status["container_status"]["running"]:
                    if status["container_status"]["exists"]:
                        if restart_container(service["container"]):
                            logger.info(f"{service['name']} 重启成功")
                        else:
                            logger.error(f"{service['name']} 重启失败")
                    else:
                        logger.error(f"{service['name']} 容器不存在")
                else:
                    logger.info(f"{service['name']} 容器运行中但服务不可用，尝试重启...")
                    restart_container(service["container"])
            else:
                if start_process_service(service):
                    logger.info(f"{service['name']} 启动成功")
                else:
                    logger.error(f"{service['name']} 启动失败")
        else:
            logger.info(f"{service['name']} 服务正常")
    
    logger.info("服务器服务修复完成")


def start_monitoring(interval_minutes: int = 30):
    """
    启动持续监控
    
    Args:
        interval_minutes: 检查间隔（分钟）
    """
    logger.info("=" * 60)
    logger.info("服务器监控启动")
    logger.info(f"服务器: {SERVER_IP}")
    logger.info(f"检查间隔: {interval_minutes} 分钟")
    logger.info(f"日志文件: {LOG_FILE}")
    logger.info("=" * 60)
    
    while True:
        check_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"\n{'='*20} 开始检查 [{check_time}] {'='*20}")
        
        docker_ok = check_docker_service()
        if not docker_ok:
            logger.error("Docker服务未运行!")
            if restart_docker_service():
                logger.info("Docker服务已重启")
            else:
                logger.error("Docker服务重启失败，等待下次检查")
                logger.info(f"等待 {interval_minutes} 分钟后进行下一次检查...")
                time.sleep(interval_minutes * 60)
                continue
        
        for service in SERVER_SERVICES:
            status = get_service_status(service)
            
            if status["is_healthy"]:
                if status["type"] == "docker" and status["stats"]:
                    stats_info = f"CPU: {status['stats'].get('cpu', 'N/A')}, 内存: {status['stats'].get('memory', 'N/A')}"
                elif status["type"] == "process" and status["process_status"]["pid"]:
                    stats_info = f"PID: {status['process_status']['pid']}"
                else:
                    stats_info = "运行中"
                logger.info(f"✅ {service['name']} 运行正常 - {stats_info}")
            else:
                logger.error(f"❌ {service['name']} 服务异常!")
                
                if status["type"] == "docker":
                    container_status = status["container_status"]
                    logger.warning(f"   容器状态: {container_status['status']}")
                else:
                    process_status = status["process_status"]
                    logger.warning(f"   进程状态: {'运行中' if process_status['running'] else '已停止'}")
                
                logger.warning(f"   端口 {status['port']}: {'可访问' if status['port_accessible'] else '不可访问'}")
                
                if service.get("type") == "docker":
                    analysis = analyze_container_failure(service)
                    
                    logger.warning("故障分析:")
                    for cause in analysis["possible_causes"]:
                        logger.warning(f"  - {cause}")
                    
                    if analysis.get("auto_fix_actions"):
                        logger.warning("正在执行自动修复...")
                        auto_fix_service(service, analysis)
                        time.sleep(5)
                    
                    if not container_status["running"]:
                        logger.warning(f"正在尝试重启 {service['name']}...")
                        if restart_container(service["container"]):
                            logger.info(f"{service['name']} 重启成功")
                        else:
                            logger.error(f"{service['name']} 重启失败，需要人工干预!")
                    else:
                        logger.warning(f"容器运行中但服务不可用，尝试重启...")
                        if restart_container(service["container"]):
                            logger.info(f"{service['name']} 重启成功")
                else:
                    logger.warning(f"正在尝试启动 {service['name']}...")
                    if start_process_service(service):
                        logger.info(f"{service['name']} 启动成功")
                    else:
                        logger.error(f"{service['name']} 启动失败，需要人工干预!")
        
        logger.info(f"{'='*20} 检查完成 {'='*20}\n")
        
        logger.info(f"等待 {interval_minutes} 分钟后进行下一次检查...")
        time.sleep(interval_minutes * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="服务器监控脚本")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["start", "status", "repair", "help"],
                       help="命令: start=启动监控, status=查看状态, repair=修复服务, help=帮助")
    parser.add_argument("-i", "--interval", type=int, default=30,
                       help="检查间隔（分钟），默认30")
    
    args = parser.parse_args()
    
    if args.command == "start":
        start_monitoring(args.interval)
    elif args.command == "status":
        show_status()
    elif args.command == "repair":
        repair_all()
    else:
        print("""
服务器监控脚本使用说明:
  python server_monitor.py start    - 启动持续监控 (每30分钟检查一次)
  python server_monitor.py status   - 查看当前服务器服务状态
  python server_monitor.py repair   - 修复所有停止的服务

参数:
  -i, --interval      检查间隔(分钟)，默认30

示例:
  python server_monitor.py start -i 15
  python server_monitor.py status

监控服务:
  - PC端前端 (sstcp-frontend-pc, 端口 80)
  - H5端前端 (sstcp-frontend-h5, 端口 81)
  - API后端 (进程模式, 端口 8000)
  - 数据库 (sstcp-db, 端口 5432)
""")


if __name__ == "__main__":
    main()
