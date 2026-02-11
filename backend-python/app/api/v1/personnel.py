from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.personnel import PersonnelService
from app.schemas.personnel import (
    PersonnelCreate,
    PersonnelUpdate,
    PersonnelResponse,
    PaginatedResponse,
    ApiResponse
)

router = APIRouter(prefix="/personnel", tags=["Personnel Management"])


@router.get("/all/list", response_model=ApiResponse)
def get_all_personnel(
    db: Session = Depends(get_db)
):
    service = PersonnelService(db)
    items = service.get_all_unpaginated()
    return ApiResponse.success([item.to_dict() for item in items])


@router.get("", response_model=PaginatedResponse)
def get_personnel_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    name: Optional[str] = Query(None, description="Name (fuzzy search)"),
    department: Optional[str] = Query(None, description="Department (fuzzy search)"),
    current_user_role: Optional[str] = Query(None, description="Current user role"),
    current_user_department: Optional[str] = Query(None, description="Current user department"),
    db: Session = Depends(get_db)
):
    service = PersonnelService(db)
    items, total = service.get_all(
        page=page, size=size, name=name, department=department,
        current_user_role=current_user_role, current_user_department=current_user_department
    )
    items_dict = [item.to_dict() for item in items]
    return PaginatedResponse.success(items_dict, total, page, size)


@router.get("/{id}", response_model=ApiResponse)
def get_personnel_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    service = PersonnelService(db)
    personnel = service.get_by_id(id)
    return ApiResponse.success(personnel.to_dict())


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_personnel(
    dto: PersonnelCreate,
    db: Session = Depends(get_db)
):
    service = PersonnelService(db)
    personnel = service.create(dto)
    return ApiResponse.success(personnel.to_dict(), "Created successfully")


@router.put("/{id}", response_model=ApiResponse)
def update_personnel(
    id: int,
    dto: PersonnelUpdate,
    db: Session = Depends(get_db)
):
    service = PersonnelService(db)
    personnel = service.update(id, dto)
    return ApiResponse.success(personnel.to_dict(), "Updated successfully")


@router.delete("/{id}", response_model=ApiResponse)
def delete_personnel(
    id: int,
    db: Session = Depends(get_db)
):
    service = PersonnelService(db)
    service.delete(id)
    return ApiResponse.success(None, "Deleted successfully")
