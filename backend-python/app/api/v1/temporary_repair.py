from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.temporary_repair import TemporaryRepairService
from app.schemas.common import ApiResponse, PaginatedResponse


router = APIRouter(prefix="/temporary-repair", tags=["Temporary Repair Management"])


@router.get("/all/list", response_model=ApiResponse)
def get_all_temporary_repairs(
    db: Session = Depends(get_db)
):
    service = TemporaryRepairService(db)
    items = service.get_all_unpaginated()
    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_dict() for item in items]
    )


@router.get("", response_model=ApiResponse)
def get_temporary_repairs_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    project_name: Optional[str] = Query(None, description="Project name (fuzzy search)"),
    client_name: Optional[str] = Query(None, description="Client name (fuzzy search)"),
    status: Optional[str] = Query(None, description="Status"),
    db: Session = Depends(get_db)
):
    service = TemporaryRepairService(db)
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
def get_temporary_repair_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    service = TemporaryRepairService(db)
    repair = service.get_by_id(id)
    return ApiResponse(
        code=200,
        message="success",
        data=repair.to_dict()
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_temporary_repair(
    dto: dict,
    db: Session = Depends(get_db)
):
    from app.services.temporary_repair import TemporaryRepairCreate
    service = TemporaryRepairService(db)
    repair = service.create(TemporaryRepairCreate(**dto))
    return ApiResponse(
        code=200,
        message="Created successfully",
        data=repair.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_temporary_repair(
    id: int,
    dto: dict,
    db: Session = Depends(get_db)
):
    from app.services.temporary_repair import TemporaryRepairUpdate
    service = TemporaryRepairService(db)
    repair = service.update(id, TemporaryRepairUpdate(**dto))
    return ApiResponse(
        code=200,
        message="Updated successfully",
        data=repair.to_dict()
    )


@router.delete("/{id}", response_model=ApiResponse)
def delete_temporary_repair(
    id: int,
    db: Session = Depends(get_db)
):
    service = TemporaryRepairService(db)
    service.delete(id)
    return ApiResponse(
        code=200,
        message="Deleted successfully",
        data=None
    )
