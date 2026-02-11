from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.periodic_inspection import PeriodicInspectionService
from app.schemas.periodic_inspection import (
    PeriodicInspectionCreate,
    PeriodicInspectionUpdate,
    PeriodicInspectionResponse,
    PaginatedResponse,
    ApiResponse
)

router = APIRouter(prefix="/periodic-inspection", tags=["Periodic Inspection Management"])


@router.get("/all/list", response_model=ApiResponse)
def get_all_periodic_inspection(
    db: Session = Depends(get_db)
):
    service = PeriodicInspectionService(db)
    items = service.get_all_unpaginated()
    return ApiResponse.success([item.to_dict() for item in items])


@router.get("", response_model=PaginatedResponse)
def get_periodic_inspection_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    project_name: Optional[str] = Query(None, description="Project name (fuzzy search)"),
    client_name: Optional[str] = Query(None, description="Client name (fuzzy search)"),
    status: Optional[str] = Query(None, description="Status"),
    db: Session = Depends(get_db)
):
    service = PeriodicInspectionService(db)
    items, total = service.get_all(
        page, size, project_name, client_name, status
    )
    items_dict = [item.to_dict() for item in items]
    return PaginatedResponse.success(items_dict, total, page, size)


@router.get("/{id}", response_model=ApiResponse)
def get_periodic_inspection_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    service = PeriodicInspectionService(db)
    inspection = service.get_by_id(id)
    return ApiResponse.success(inspection.to_dict())


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_periodic_inspection(
    dto: PeriodicInspectionCreate,
    db: Session = Depends(get_db)
):
    service = PeriodicInspectionService(db)
    inspection = service.create(dto)
    return ApiResponse.success(inspection.to_dict(), "Created successfully")


@router.put("/{id}", response_model=ApiResponse)
def update_periodic_inspection(
    id: int,
    dto: PeriodicInspectionUpdate,
    db: Session = Depends(get_db)
):
    service = PeriodicInspectionService(db)
    inspection = service.update(id, dto)
    return ApiResponse.success(inspection.to_dict(), "Updated successfully")


@router.delete("/{id}", response_model=ApiResponse)
def delete_periodic_inspection(
    id: int,
    db: Session = Depends(get_db)
):
    service = PeriodicInspectionService(db)
    service.delete(id)
    return ApiResponse.success(None, "Deleted successfully")
