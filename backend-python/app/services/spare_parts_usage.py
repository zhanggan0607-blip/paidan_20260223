from typing import List, Optional, Union
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.spare_parts_usage import SparePartsUsage
from app.repositories.spare_parts_usage import SparePartsUsageRepository
from pydantic import BaseModel


class SparePartsUsageCreate(BaseModel):
    product_name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    quantity: int
    user_name: str
    issue_time: Union[str, datetime]
    unit: str = "件"
    project_id: Optional[str] = None
    project_name: Optional[str] = None


class SparePartsUsageUpdate(BaseModel):
    product_name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    quantity: Optional[int] = None
    user_name: Optional[str] = None
    issue_time: Optional[Union[str, datetime]] = None
    unit: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None


class SparePartsUsageService:
    def __init__(self, db: Session):
        self.repository = SparePartsUsageRepository(db)
    
    def _parse_date(self, date_value: Union[str, datetime, None]) -> Optional[datetime]:
        if date_value is None:
            return None
        if isinstance(date_value, datetime):
            return date_value
        if isinstance(date_value, str):
            try:
                return datetime.fromisoformat(date_value)
            except ValueError:
                try:
                    return datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    raise ValueError(f'日期格式无效: {date_value}')
        return None
    
    def get_all(
        self, 
        page: int = 0, 
        size: int = 10, 
        user: Optional[str] = None,
        product: Optional[str] = None,
        project: Optional[str] = None
    ) -> tuple[List[SparePartsUsage], int]:
        return self.repository.find_all(
            page, size, user, product, project
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