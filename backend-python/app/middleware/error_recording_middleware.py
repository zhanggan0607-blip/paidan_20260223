"""
错误记录中间件模块

功能：
1. 自动捕获 FastAPI 应用中的异常
2. 自动记录错误到 TROUBLESHOOTING.md
3. 提供错误分类和解决方案建议
4. 记录后发送通知提醒

作者：系统自动生成
日期：2026-03-19
"""

import traceback
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from datetime import datetime
import os

from app.utils.troubleshooting_manager import get_troubleshooting_manager

logger = logging.getLogger(__name__)


def _notify_error_recorded(result: dict, error_message: str):
    """
    发送错误记录通知
    
    Args:
        result: 记录结果
        error_message: 错误信息
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    is_duplicate = result.get("is_duplicate", False)
    error_code = result.get("error_code", "N/A")
    
    notification_lines = [
        "",
        "=" * 70,
        "  🔔 错误自动记录通知",
        "=" * 70,
        f"  ⏰ 时间: {timestamp}",
        f"  📋 状态: {'重复错误（已跳过）' if is_duplicate else '新错误（已记录）'}",
        f"  🔢 编号: {error_code}",
        f"  💬 信息: {error_message[:80]}{'...' if len(error_message) > 80 else ''}",
    ]
    
    if not is_duplicate:
        notification_lines.extend([
            f"  📁 文件: TROUBLESHOOTING.md 已更新",
            f"  💡 建议: 请查看文档获取解决方案",
        ])
    
    notification_lines.extend([
        "=" * 70,
        ""
    ])
    
    notification = "\n".join(notification_lines)
    
    print(notification)
    
    logger.info(f"[错误记录通知] {timestamp} - {'重复' if is_duplicate else '新'}错误: {error_message[:50]}...")
    
    _write_notification_log(timestamp, result, error_message)


def _write_notification_log(timestamp: str, result: dict, error_message: str):
    """
    写入通知日志文件
    
    Args:
        timestamp: 时间戳
        result: 记录结果
        error_message: 错误信息
    """
    try:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "error_notifications.log")
        
        log_entry = (
            f"[{timestamp}] "
            f"{'重复' if result.get('is_duplicate') else '新'}错误 | "
            f"编号: {result.get('error_code', 'N/A')} | "
            f"信息: {error_message}\n"
        )
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
            
    except Exception as e:
        logger.warning(f"写入通知日志失败: {e}")


class ErrorRecordingMiddleware(BaseHTTPMiddleware):
    """
    错误记录中间件
    
    自动捕获应用中的异常并记录到 TROUBLESHOOTING.md
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并捕获异常
        
        Args:
            request: 请求对象
            call_next: 下一个处理函数
            
        Returns:
            Response: 响应对象
        """
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            await self._record_error(request, e)
            
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "服务器内部错误",
                    "error_type": type(e).__name__,
                    "message": str(e)
                }
            )
    
    async def _record_error(self, request: Request, error: Exception):
        """
        记录错误到 TROUBLESHOOTING.md
        
        Args:
            request: 请求对象
            error: 异常对象
        """
        try:
            manager = get_troubleshooting_manager()
            
            error_message = self._format_error_message(error)
            category = self._categorize_error(error, request)
            reason = self._analyze_reason(error)
            solution = self._suggest_solution(error)
            stack_trace = traceback.format_exc()
            file_path = self._extract_file_path(stack_trace)
            
            result = manager.record_error(
                error_message=error_message,
                category=category,
                reason=reason,
                solution=solution,
                stack_trace=stack_trace,
                file_path=file_path,
                auto_update_md=True
            )
            
            _notify_error_recorded(result, error_message)
                
        except Exception as record_error:
            logger.error(f"记录错误失败: {record_error}")
    
    def _format_error_message(self, error: Exception) -> str:
        """
        格式化错误信息
        
        Args:
            error: 异常对象
            
        Returns:
            str: 格式化后的错误信息
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        return f"{error_type}: {error_msg}"
    
    def _categorize_error(self, error: Exception, request: Request) -> str:
        """
        对错误进行分类
        
        Args:
            error: 异常对象
            request: 请求对象
            
        Returns:
            str: 错误类别
        """
        error_type = type(error).__name__
        error_msg = str(error).lower()
        path = request.url.path.lower()
        
        if "database" in error_msg or "sql" in error_msg or "psycopg" in error_msg:
            return "数据库错误"
        
        if "auth" in error_msg or "token" in error_msg or "permission" in error_msg:
            return "权限错误"
        
        if "file" in error_msg or "upload" in error_msg or "notfounderror" in error_type.lower():
            return "文件错误"
        
        if "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
            return "网络错误"
        
        if "/api/" in path:
            return "API错误"
        
        return "后端错误"
    
    def _analyze_reason(self, error: Exception) -> str:
        """
        分析错误原因
        
        Args:
            error: 异常对象
            
        Returns:
            str: 错误原因描述
        """
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        reasons = {
            "KeyError": "访问了不存在的字典键",
            "TypeError": "数据类型不匹配或操作不支持",
            "ValueError": "传入的值不符合预期格式或范围",
            "AttributeError": "访问了不存在的对象属性",
            "IndexError": "访问了不存在的列表索引",
            "FileNotFoundError": "请求的文件不存在",
            "PermissionError": "没有足够的权限执行操作",
            "ConnectionError": "网络连接失败",
            "TimeoutError": "操作超时",
            "IntegrityError": "数据库完整性约束违反",
            "ProgrammingError": "SQL语法错误或数据库编程错误"
        }
        
        if error_type in reasons:
            return reasons[error_type]
        
        if "foreign key" in error_msg:
            return "外键约束违反，引用的数据不存在"
        
        if "unique" in error_msg:
            return "唯一约束违反，数据已存在"
        
        if "not null" in error_msg:
            return "非空约束违反，必填字段为空"
        
        return f"发生 {error_type} 类型的错误"
    
    def _suggest_solution(self, error: Exception) -> str:
        """
        建议解决方案
        
        Args:
            error: 异常对象
            
        Returns:
            str: 解决方案建议
        """
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        solutions = {
            "KeyError": "检查字典键是否存在，使用 .get() 方法提供默认值",
            "TypeError": "检查数据类型，添加类型转换或类型检查",
            "ValueError": "验证输入数据的格式和范围",
            "AttributeError": "检查对象是否具有该属性，使用 hasattr() 进行检查",
            "IndexError": "检查列表长度，确保索引在有效范围内",
            "FileNotFoundError": "检查文件路径是否正确，确保文件存在",
            "PermissionError": "检查文件或目录权限，以管理员身份运行",
            "ConnectionError": "检查网络连接，确认服务是否运行",
            "TimeoutError": "增加超时时间，优化处理逻辑"
        }
        
        if error_type in solutions:
            return solutions[error_type]
        
        if "foreign key" in error_msg:
            return "确保外键引用的数据存在，或设置级联删除/更新"
        
        if "unique" in error_msg:
            return "检查是否重复插入相同数据，使用 UPSERT 或先查询后插入"
        
        if "not null" in error_msg:
            return "确保必填字段有值，添加默认值或前端验证"
        
        return "查看详细错误信息，根据具体情况进行修复"
    
    def _extract_file_path(self, stack_trace: str) -> str:
        """
        从堆栈跟踪中提取文件路径
        
        Args:
            stack_trace: 堆栈跟踪字符串
            
        Returns:
            str: 文件路径
        """
        import re
        
        pattern = r'File "([^"]+\.py)"'
        matches = re.findall(pattern, stack_trace)
        
        if matches:
            for match in matches:
                if "site-packages" not in match and "lib/python" not in match:
                    return match
        
        return matches[0] if matches else ""


class ErrorCheckMiddleware(BaseHTTPMiddleware):
    """
    操作前检查中间件
    
    在处理请求前检查是否有相关错误记录
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求前进行检查
        
        Args:
            request: 请求对象
            call_next: 下一个处理函数
            
        Returns:
            Response: 响应对象
        """
        error_hint = request.headers.get("X-Error-Hint", "")
        
        if error_hint:
            try:
                manager = get_troubleshooting_manager()
                result = manager.check_before_operation(error_hint)
                
                if result.get("has_record"):
                    logger.info(f"检测到已知错误: {result.get('suggestion')}")
                    
                    request.state.error_check_result = result
            except Exception as e:
                logger.warning(f"错误检查失败: {e}")
        
        response = await call_next(request)
        return response
