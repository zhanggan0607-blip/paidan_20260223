from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List, Any
from pydantic import ConfigDict

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一的API响应格式"""
    code: int
    message: str
    data: Optional[T] = None

    @classmethod
    def success(cls, data=None, message="success"):
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, message="error", code=500):
        return cls(code=code, message=message, data=None)


class PaginatedResponse(BaseModel):
    """分页响应格式"""
    code: int
    message: str
    data: dict

    @classmethod
    def success(cls, items, total, page, size, message="success"):
        return cls(
            code=200,
            message=message,
            data={
                'content': items,
                'totalElements': total,
                'totalPages': (total + size - 1) // size,
                'size': size,
                'number': page,
                'first': page == 0,
                'last': page >= (total + size - 1) // size - 1,
            }
        )

    model_config = ConfigDict(from_attributes=True)
