from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.dictionary import DictionaryService
from app.schemas.common import ApiResponse, PaginatedResponse


router = APIRouter(prefix="/dictionary", tags=["Dictionary Management"])


@router.get("/type/{dict_type}", response_model=ApiResponse)
def get_dictionary_by_type(
    dict_type: str,
    db: Session = Depends(get_db)
):
    service = DictionaryService(db)
    items = service.get_by_type(dict_type)
    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_dict() for item in items]
    )


@router.get("/all/list", response_model=ApiResponse)
def get_all_dictionaries_unpaginated(
    dict_type: Optional[str] = Query(None, description="Dictionary type filter"),
    db: Session = Depends(get_db)
):
    service = DictionaryService(db)
    items = service.get_all_unpaginated(dict_type)
    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_dict() for item in items]
    )


@router.get("", response_model=ApiResponse)
def get_dictionaries_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=2000, description="Page size"),
    dict_type: Optional[str] = Query(None, description="Dictionary type filter"),
    db: Session = Depends(get_db)
):
    service = DictionaryService(db)
    items, total = service.get_all(page=page, size=size, dict_type=dict_type)
    items_dict = [item.to_dict() for item in items]
    return ApiResponse(
        code=200,
        message="success",
        data={
            'content': items_dict,
            'totalElements': total,
            'totalPages': (total + size - 1) // size,
            'size': size,
            'number': page,
            'first': page == 0,
            'last': page >= (total + size - 1) // size
        }
    )


@router.get("/{id}", response_model=ApiResponse)
def get_dictionary_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    service = DictionaryService(db)
    dictionary = service.get_by_id(id)
    return ApiResponse(
        code=200,
        message="success",
        data=dictionary.to_dict()
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_dictionary(
    dto: dict,
    db: Session = Depends(get_db)
):
    service = DictionaryService(db)
    dictionary = service.create(dto)
    return ApiResponse(
        code=200,
        message="Created successfully",
        data=dictionary.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_dictionary(
    id: int,
    dto: dict,
    db: Session = Depends(get_db)
):
    service = DictionaryService(db)
    dictionary = service.update(id, dto)
    return ApiResponse(
        code=200,
        message="Updated successfully",
        data=dictionary.to_dict()
    )


@router.delete("/{id}", response_model=ApiResponse)
def delete_dictionary(
    id: int,
    db: Session = Depends(get_db)
):
    service = DictionaryService(db)
    service.delete(id)
    return ApiResponse(
        code=200,
        message="Deleted successfully",
        data=None
    )
