"""
分页响应构建工具
统一管理分页响应的构造
"""
from typing import List, Any, Dict, Generic, TypeVar, Optional
from dataclasses import dataclass

T = TypeVar('T')


@dataclass
class PageMeta:
    """
    分页元数据
    """
    total_elements: int
    total_pages: int
    size: int
    number: int
    first: bool
    last: bool


@dataclass
class PaginatedResult(Generic[T]):
    """
    分页结果
    """
    content: List[T]
    page_meta: PageMeta
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'content': self.content,
            'totalElements': self.page_meta.total_elements,
            'totalPages': self.page_meta.total_pages,
            'size': self.page_meta.size,
            'number': self.page_meta.number,
            'first': self.page_meta.first,
            'last': self.page_meta.last
        }


def build_paginated_response(
    items: List[Any],
    total: int,
    page: int,
    size: int
) -> Dict[str, Any]:
    """
    构建分页响应数据
    
    Args:
        items: 数据项列表
        total: 总数量
        page: 当前页码（从0开始）
        size: 每页大小
        
    Returns:
        分页响应字典
    """
    total_pages = (total + size - 1) // size if size > 0 else 0
    
    return {
        'content': items,
        'totalElements': total,
        'totalPages': total_pages,
        'size': size,
        'number': page,
        'first': page == 0,
        'last': page >= total_pages - 1 if total_pages > 0 else True
    }


def build_paginated_result(
    items: List[T],
    total: int,
    page: int,
    size: int
) -> PaginatedResult[T]:
    """
    构建分页结果对象
    
    Args:
        items: 数据项列表
        total: 总数量
        page: 当前页码（从0开始）
        size: 每页大小
        
    Returns:
        PaginatedResult 实例
    """
    total_pages = (total + size - 1) // size if size > 0 else 0
    
    page_meta = PageMeta(
        total_elements=total,
        total_pages=total_pages,
        size=size,
        number=page,
        first=page == 0,
        last=page >= total_pages - 1 if total_pages > 0 else True
    )
    
    return PaginatedResult(content=items, page_meta=page_meta)


def calculate_total_pages(total: int, size: int) -> int:
    """
    计算总页数
    
    Args:
        total: 总数量
        size: 每页大小
        
    Returns:
        总页数
    """
    if size <= 0:
        return 0
    return (total + size - 1) // size


def is_first_page(page: int) -> bool:
    """
    判断是否为第一页
    
    Args:
        page: 页码
        
    Returns:
        是否为第一页
    """
    return page == 0


def is_last_page(page: int, total: int, size: int) -> bool:
    """
    判断是否为最后一页
    
    Args:
        page: 页码
        total: 总数量
        size: 每页大小
        
    Returns:
        是否为最后一页
    """
    total_pages = calculate_total_pages(total, size)
    return page >= total_pages - 1 if total_pages > 0 else True
