from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List
from pydantic import ConfigDict

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    code: int
    message: str
    data: Optional[T] = None

class PaginatedResponse(BaseModel):
    code: int
    message: str
    content: List[T]
    totalElements: int
    totalPages: int
    size: int
    number: int
    first: bool
    last: bool

    model_config = ConfigDict(from_attributes=True)
