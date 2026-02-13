from fastapi import APIRouter
from typing import Callable

api_v1_router = APIRouter()

def register_v1_route(path: str, **kwargs):
    def decorator(func: Callable):
        api_v1_router.add_api_route(path, func, **kwargs)
        return func
    return decorator

class APIVersion:
    V1 = "/api/v1"
    V2 = "/api/v2"
    
    CURRENT = V1
    DEPRECATED = []
    SUPPORTED = [V1]
