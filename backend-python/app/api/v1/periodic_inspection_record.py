from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.periodic_inspection_record import PeriodicInspectionRecordService
from app.schemas.periodic_inspection_record import (
    PeriodicInspectionRecordCreate,
    PeriodicInspectionRecordUpdate,
    PeriodicInspectionRecordResponse,
    BatchRecordSave
)
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/periodic-inspection-record", tags=["Periodic Inspection Record"])


@router.get("/inspection/{inspection_id}", response_model=ApiResponse)
def get_records_by_inspection_id(
    inspection_id: str,
    db: Session = Depends(get_db)
):
    service = PeriodicInspectionRecordService(db)
    records = service.get_by_inspection_id(inspection_id)
    return ApiResponse.success([record.to_dict() for record in records])


@router.get("/{id}", response_model=ApiResponse)
def get_record_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    service = PeriodicInspectionRecordService(db)
    record = service.get_by_id(id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return ApiResponse.success(record.to_dict())


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_record(
    dto: PeriodicInspectionRecordCreate,
    db: Session = Depends(get_db)
):
    service = PeriodicInspectionRecordService(db)
    record = service.create(dto)
    return ApiResponse.success(record.to_dict(), "Created successfully")


@router.post("/batch", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def batch_save_records(
    dto: BatchRecordSave,
    db: Session = Depends(get_db)
):
    service = PeriodicInspectionRecordService(db)
    records = service.batch_save(dto)
    return ApiResponse.success([record.to_dict() for record in records], "Saved successfully")


@router.put("/{id}", response_model=ApiResponse)
def update_record(
    id: int,
    dto: PeriodicInspectionRecordUpdate,
    db: Session = Depends(get_db)
):
    service = PeriodicInspectionRecordService(db)
    record = service.update(id, dto)
    return ApiResponse.success(record.to_dict(), "Updated successfully")


@router.delete("/{id}", response_model=ApiResponse)
def delete_record(
    id: int,
    db: Session = Depends(get_db)
):
    service = PeriodicInspectionRecordService(db)
    service.delete(id)
    return ApiResponse.success(None, "Deleted successfully")
