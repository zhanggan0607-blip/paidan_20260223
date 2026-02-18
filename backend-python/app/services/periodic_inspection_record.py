import json
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.periodic_inspection_record import PeriodicInspectionRecord
from app.schemas.periodic_inspection_record import (
    PeriodicInspectionRecordCreate,
    PeriodicInspectionRecordUpdate,
    BatchRecordSave
)


class PeriodicInspectionRecordService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_inspection_id(self, inspection_id: str) -> List[PeriodicInspectionRecord]:
        records = self.db.query(PeriodicInspectionRecord).filter(
            PeriodicInspectionRecord.inspection_id == inspection_id
        ).all()
        return records

    def get_by_id(self, record_id: int) -> Optional[PeriodicInspectionRecord]:
        return self.db.query(PeriodicInspectionRecord).filter(
            PeriodicInspectionRecord.id == record_id
        ).first()

    def create(self, dto: PeriodicInspectionRecordCreate) -> PeriodicInspectionRecord:
        return self.upsert(dto)

    def update(self, record_id: int, dto: PeriodicInspectionRecordUpdate) -> PeriodicInspectionRecord:
        record = self.get_by_id(record_id)
        if not record:
            raise ValueError(f"Record with id {record_id} not found")
        
        if dto.inspected is not None:
            record.inspected = dto.inspected
        if dto.photos is not None:
            record.photos = json.dumps(dto.photos)
        if dto.inspection_result is not None:
            record.inspection_result = dto.inspection_result
        
        self.db.commit()
        self.db.refresh(record)
        return record

    def upsert(self, dto: PeriodicInspectionRecordCreate) -> PeriodicInspectionRecord:
        existing = self.db.query(PeriodicInspectionRecord).filter(
            PeriodicInspectionRecord.inspection_id == dto.inspection_id,
            PeriodicInspectionRecord.item_id == dto.item_id
        ).first()
        
        if existing:
            existing.item_name = dto.item_name
            existing.inspection_item = dto.inspection_item
            existing.inspection_content = dto.inspection_content
            existing.check_content = dto.check_content
            existing.brief_description = dto.brief_description
            existing.equipment_name = dto.equipment_name
            existing.equipment_location = dto.equipment_location
            existing.inspected = dto.inspected
            existing.photos = json.dumps(dto.photos) if dto.photos else '[]'
            existing.inspection_result = dto.inspection_result
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            return self.create(dto)

    def batch_save(self, dto: BatchRecordSave) -> List[PeriodicInspectionRecord]:
        results = []
        for record_dto in dto.records:
            record_dto.inspection_id = dto.inspection_id
            result = self.upsert(record_dto)
            results.append(result)
        return results

    def delete(self, record_id: int) -> None:
        record = self.get_by_id(record_id)
        if record:
            self.db.delete(record)
            self.db.commit()

    def delete_by_inspection_id(self, inspection_id: str) -> None:
        self.db.query(PeriodicInspectionRecord).filter(
            PeriodicInspectionRecord.inspection_id == inspection_id
        ).delete()
        self.db.commit()
