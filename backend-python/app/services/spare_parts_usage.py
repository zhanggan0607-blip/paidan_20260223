from typing import List, Optional, Union
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.spare_parts_usage import SparePartsUsage
from app.repositories.spare_parts_usage import SparePartsUsageRepository
from app.schemas.spare_parts import SparePartsUsageCreate, SparePartsUsageUpdate
from app.utils.date_utils import parse_datetime


class SparePartsUsageService:
    def __init__(self, db: Session):
        self.repository = SparePartsUsageRepository(db)
    
    def _parse_date(self, date_value: Union[str, datetime, None]) -> Optional[datetime]:
        return parse_datetime(date_value)
    
    def get_all(
        self, 
        page: int = 0, 
        size: int = 10, 
        user: Optional[str] = None,
        product: Optional[str] = None,
        project: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> tuple[List[SparePartsUsage], int]:
        return self.repository.find_all(
            page, size, user, product, project, status_filter
        )
    
    def get_by_id(self, id: int) -> SparePartsUsage:
        usage = self.repository.find_by_id(id)
        if not usage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="领用记录不存在"
            )
        return usage
    
    def create(self, dto: SparePartsUsageCreate) -> SparePartsUsage:
        usage = SparePartsUsage(
            product_name=dto.product_name,
            brand=dto.brand,
            model=dto.model,
            quantity=dto.quantity,
            user_name=dto.user_name,
            issue_time=self._parse_date(dto.issue_time),
            unit=dto.unit,
            project_id=dto.project_id,
            project_name=dto.project_name
        )
        
        return self.repository.create(usage)
    
    def update(self, id: int, dto: SparePartsUsageUpdate) -> SparePartsUsage:
        existing_usage = self.get_by_id(id)
        
        if dto.product_name is not None:
            existing_usage.product_name = dto.product_name
        if dto.brand is not None:
            existing_usage.brand = dto.brand
        if dto.model is not None:
            existing_usage.model = dto.model
        if dto.quantity is not None:
            existing_usage.quantity = dto.quantity
        if dto.user_name is not None:
            existing_usage.user_name = dto.user_name
        if dto.issue_time is not None:
            existing_usage.issue_time = self._parse_date(dto.issue_time)
        if dto.unit is not None:
            existing_usage.unit = dto.unit
        if dto.project_id is not None:
            existing_usage.project_id = dto.project_id
        if dto.project_name is not None:
            existing_usage.project_name = dto.project_name
        
        return self.repository.update(existing_usage)
    
    def delete(self, id: int) -> None:
        usage = self.get_by_id(id)
        self.repository.delete(usage)