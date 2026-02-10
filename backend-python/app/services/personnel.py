from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.personnel import Personnel
from app.repositories.personnel import PersonnelRepository
from app.schemas.personnel import PersonnelCreate, PersonnelUpdate


class PersonnelService:
    def __init__(self, db: Session):
        self.repository = PersonnelRepository(db)
    
    def get_all(
        self, 
        page: int = 0, 
        size: int = 10, 
        name: Optional[str] = None,
        department: Optional[str] = None,
        current_user_role: Optional[str] = None,
        current_user_department: Optional[str] = None
    ) -> tuple[List[Personnel], int]:
        return self.repository.find_all(
            page, size, name, department, 
            current_user_role, current_user_department
        )
    
    def get_by_id(self, id: int) -> Personnel:
        personnel = self.repository.find_by_id(id)
        if not personnel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="人员不存在"
            )
        return personnel
    
    def create(self, dto: PersonnelCreate) -> Personnel:
        personnel = Personnel(
            name=dto.name,
            gender=dto.gender,
            phone=dto.phone,
            department=dto.department,
            role=dto.role,
            address=dto.address,
            remarks=dto.remarks
        )
        
        return self.repository.create(personnel)
    
    def update(self, id: int, dto: PersonnelUpdate) -> Personnel:
        existing_personnel = self.get_by_id(id)
        
        existing_personnel.name = dto.name
        existing_personnel.gender = dto.gender
        existing_personnel.phone = dto.phone
        existing_personnel.department = dto.department
        existing_personnel.role = dto.role
        existing_personnel.address = dto.address
        existing_personnel.remarks = dto.remarks
        
        return self.repository.update(existing_personnel)
    
    def delete(self, id: int) -> None:
        personnel = self.get_by_id(id)
        self.repository.delete(personnel)
    
    def get_all_unpaginated(self) -> List[Personnel]:
        return self.repository.find_all_unpaginated()
