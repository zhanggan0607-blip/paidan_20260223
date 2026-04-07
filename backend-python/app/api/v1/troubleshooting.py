"""
错误记录管理 API 端点

提供错误记录的查询、记录和管理功能

作者：系统自动生成
日期：2026-03-19
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.utils.troubleshooting_manager import get_troubleshooting_manager

router = APIRouter(prefix="/troubleshooting", tags=["错误记录管理"])


class ErrorRecordRequest(BaseModel):
    """
    错误记录请求模型
    """
    error_message: str = Field(..., description="错误信息")
    category: str = Field(..., description="错误类别")
    reason: str = Field(..., description="错误原因")
    solution: str = Field(..., description="解决方案")
    title: Optional[str] = Field("", description="错误标题")
    related_files: Optional[str] = Field("", description="相关文件")
    code_example: Optional[str] = Field("", description="代码示例")
    stack_trace: Optional[str] = Field("", description="堆栈跟踪")
    file_path: Optional[str] = Field("", description="相关文件路径")


class ErrorCheckRequest(BaseModel):
    """
    错误检查请求模型
    """
    error_message: str = Field(..., description="错误信息")
    category: Optional[str] = Field("", description="错误类别")


@router.post("/record", summary="记录新错误")
async def record_error(request: ErrorRecordRequest):
    """
    记录新的错误信息
    
    自动检测重复并记录到 TROUBLESHOOTING.md
    
    Args:
        request: 错误记录请求
        
    Returns:
        dict: 记录结果
    """
    try:
        manager = get_troubleshooting_manager()
        
        result = manager.record_error(
            error_message=request.error_message,
            category=request.category,
            reason=request.reason,
            solution=request.solution,
            title=request.title,
            related_files=request.related_files,
            code_example=request.code_example,
            stack_trace=request.stack_trace,
            file_path=request.file_path,
            auto_update_md=True
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"记录错误失败: {str(e)}")


@router.post("/check", summary="检查错误是否已记录")
async def check_error(request: ErrorCheckRequest):
    """
    检查错误是否已经记录
    
    在进行操作前检查是否有相关错误记录
    
    Args:
        request: 错误检查请求
        
    Returns:
        dict: 检查结果
    """
    try:
        manager = get_troubleshooting_manager()
        
        result = manager.check_before_operation(
            error_message=request.error_message,
            category=request.category
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查错误失败: {str(e)}")


@router.get("/search", summary="搜索错误记录")
async def search_errors(
    keyword: Optional[str] = Query("", description="搜索关键词"),
    category: Optional[str] = Query("", description="错误类别"),
    error_code: Optional[str] = Query("", description="错误编码")
):
    """
    搜索错误记录
    
    支持按关键词、类别和错误编码搜索
    
    Args:
        keyword: 搜索关键词
        category: 错误类别
        error_code: 错误编码
        
    Returns:
        list: 匹配的错误记录列表
    """
    try:
        manager = get_troubleshooting_manager()
        
        results = manager.search_records(
            keyword=keyword,
            category=category,
            error_code=error_code
        )
        
        return {
            "total": len(results),
            "records": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/statistics", summary="获取错误统计")
async def get_statistics():
    """
    获取错误统计信息
    
    包括总数、按类别统计、频繁错误和最近错误
    
    Returns:
        dict: 统计信息
    """
    try:
        manager = get_troubleshooting_manager()
        
        stats = manager.get_statistics()
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.get("/categories", summary="获取错误类别列表")
async def get_categories():
    """
    获取所有错误类别
    
    Returns:
        list: 错误类别列表
    """
    categories = [
        {"code": "BE", "name": "后端错误", "description": "后端服务相关错误"},
        {"code": "FE", "name": "前端错误", "description": "前端应用相关错误"},
        {"code": "DEPLOY", "name": "部署错误", "description": "部署和运维相关错误"},
        {"code": "DB", "name": "数据库错误", "description": "数据库操作相关错误"},
        {"code": "ENV", "name": "环境配置错误", "description": "环境配置相关错误"},
        {"code": "API", "name": "API错误", "description": "API接口相关错误"},
        {"code": "BIZ", "name": "业务逻辑错误", "description": "业务逻辑相关错误"},
        {"code": "AUTH", "name": "权限错误", "description": "权限认证相关错误"},
        {"code": "FILE", "name": "文件错误", "description": "文件操作相关错误"},
        {"code": "NET", "name": "网络错误", "description": "网络通信相关错误"}
    ]
    
    return categories


@router.get("/{error_code}", summary="获取错误详情")
async def get_error_detail(error_code: str):
    """
    获取指定错误的详细信息
    
    Args:
        error_code: 错误编码（如 BE-001）
        
    Returns:
        dict: 错误详情
    """
    try:
        manager = get_troubleshooting_manager()
        
        results = manager.search_records(error_code=error_code)
        
        if not results:
            raise HTTPException(status_code=404, detail=f"未找到错误记录: {error_code}")
        
        return results[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取错误详情失败: {str(e)}")
