from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一的API响应格式"""
    code: int
    message: str
    data: T | None = None

    @classmethod
    def success(cls, data=None, message="success"):
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, message="error", code=500):
        return cls(code=code, message=message, data=None)


class PaginatedResponse(BaseModel):
    code: int
    message: str
    data: dict

    @classmethod
    def success(cls, items, total, page, size, message="success"):
        total_pages = (total + size - 1) // size if size > 0 else 0
        return cls(
            code=200,
            message=message,
            data={
                'items': items,
                'content': items,
                'total': total,
                'totalElements': total,
                'page': page,
                'number': page,
                'size': size,
                'totalPages': total_pages,
                'first': page == 0,
                'last': size > 0 and page >= total_pages - 1,
            }
        )

    model_config = ConfigDict(from_attributes=True)
