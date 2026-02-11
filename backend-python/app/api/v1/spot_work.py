from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.spot_work import SpotWorkService
from app.schemas.common import ApiResponse, PaginatedResponse


router = APIRouter(prefix="/spot-work", tags=["Spot Work Management"])


@router.get("/all/list", response_model=ApiResponse)
def get_all_spot_works(
    db: Session = Depends(get_db)
):
    service = SpotWorkService(db)
    items = service.get_all_unpaginated()
    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_dict() for item in items]
    )


@router.get("", response_model=ApiResponse)
def get_spot_works_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    project_name: Optional[str] = Query(None, description="Project name (fuzzy search)"),
    client_name: Optional[str] = Query(None, description="Client name (fuzzy search)"),
    status: Optional[str] = Query(None, description="Status"),
    db: Session = Depends(get_db)
):
    service = SpotWorkService(db)
    items, total = service.get_all(
        page=page, size=size, project_name=project_name, client_name=client_name, status=status
    )
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
def get_spot_work_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    service = SpotWorkService(db)
    work = service.get_by_id(id)
    return ApiResponse(
        code=200,
        message="success",
        data=work.to_dict()
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_spot_work(
    dto: dict,
    db: Session = Depends(get_db)
):
    from app.services.spot_work import SpotWorkCreate
    service = SpotWorkService(db)
    work = service.create(SpotWorkCreate(**dto))
    return ApiResponse(
        code=200,
        message="Created successfully",
        data=work.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_spot_work(
    id: int,
    dto: dict,
    db: Session = Depends(get_db)
):
    from app.services.spot_work import SpotWorkUpdate
    service = SpotWorkService(db)
    work = service.update(id, SpotWorkUpdate(**dto))
    return ApiResponse(
        code=200,
        message="Updated successfully",
        data=work.to_dict()
    )


@router.delete("/{id}", response_model=ApiResponse)
def delete_spot_work(
    id: int,
    db: Session = Depends(get_db)
):
    service = SpotWorkService(db)
    service.delete(id)
    return ApiResponse(
        code=200,
        message="Deleted successfully",
        data=None
    )
