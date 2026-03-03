"""
服务健康检查脚本
用于监控服务状态并在必要时重启服务
"""
import requests
import subprocess
import time
import logging
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BACKEND_URL = "http://localhost:8000/health"
FRONTEND_URL = "http://localhost:5180"
PC_FRONTEND_URL = "http://localhost:3000"

MAX_FAILURES = 3
CHECK_INTERVAL = 60

failure_counts = {
    "backend": 0,
    "frontend": 0,
    "pc_frontend": 0
}


def check_service(url: str, service_name: str) -> bool:
    """
    检查服务是否健康
    
    Args:
        url: 服务健康检查URL
        service_name: 服务名称
    
    Returns:
        bool: 服务是否健康
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            logger.info(f"[{service_name}] 健康检查通过")
            return True
        else:
            logger.warning(f"[{service_name}] 健康检查失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error(f"[{service_name}] 无法连接到服务")
        return False
    except requests.exceptions.Timeout:
        logger.error(f"[{service_name}] 健康检查超时")
        return False
    except Exception as e:
        logger.error(f"[{service_name}] 健康检查异常: {e}")
        return False


def restart_service(service_name: str):
    """
    重启服务
    
    Args:
        service_name: 服务名称 (backend, frontend, pc_frontend)
    """
    logger.warning(f"[{service_name}] 尝试重启服务...")
    
    try:
        if service_name == "backend":
            subprocess.run(
                ["powershell", "-Command", "Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like '*python*'} | Stop-Process -Force"],
                capture_output=True,
                text=True
            )
            time.sleep(2)
            subprocess.Popen(
                ["python", "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
                cwd=str(Path(__file__).parent.parent),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        elif service_name == "frontend":
            subprocess.run(
                ["powershell", "-Command", "Get-NetTCPConnection -LocalPort 5180 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }"],
                capture_output=True,
                text=True
            )
            time.sleep(2)
            subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(Path(__file__).parent.parent / "H5"),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        elif service_name == "pc_frontend":
            subprocess.run(
                ["powershell", "-Command", "Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }"],
                capture_output=True,
                text=True
            )
            time.sleep(2)
            subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(Path(__file__).parent.parent),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        
        logger.info(f"[{service_name}] 重启命令已执行")
    except Exception as e:
        logger.error(f"[{service_name}] 重启失败: {e}")


def run_health_check():
    """
    运行健康检查循环
    """
    logger.info("启动服务健康检查...")
    logger.info(f"检查间隔: {CHECK_INTERVAL}秒")
    logger.info(f"最大失败次数: {MAX_FAILURES}")
    
    while True:
        logger.info(f"\n{'='*50}")
        logger.info(f"健康检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if check_service(BACKEND_URL, "后端服务"):
            failure_counts["backend"] = 0
        else:
            failure_counts["backend"] += 1
            if failure_counts["backend"] >= MAX_FAILURES:
                restart_service("backend")
                failure_counts["backend"] = 0
        
        if check_service(FRONTEND_URL, "H5前端"):
            failure_counts["frontend"] = 0
        else:
            failure_counts["frontend"] += 1
            if failure_counts["frontend"] >= MAX_FAILURES:
                restart_service("frontend")
                failure_counts["frontend"] = 0
        
        if check_service(PC_FRONTEND_URL, "PC前端"):
            failure_counts["pc_frontend"] = 0
        else:
            failure_counts["pc_frontend"] += 1
            if failure_counts["pc_frontend"] >= MAX_FAILURES:
                restart_service("pc_frontend")
                failure_counts["pc_frontend"] = 0
        
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        run_health_check()
    except KeyboardInterrupt:
        logger.info("\n健康检查已停止")
        sys.exit(0)
