from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.temporary_repair import TemporaryRepair


class TemporaryRepairRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[TemporaryRepair], int]:
        query = self.db.query(TemporaryRepair)
        
        if project_name:
            query = query.filter(TemporaryRepair.project_name.like(f'%{project_name}%'))
        
        if client_name:
            query = query.filter(TemporaryRepair.client_name.like(f'%{client_name}%'))
        
        if status:
            query = query.filter(TemporaryRepair.status == status)
        
        total = query.count()
        items = query.offset(page * size).limit(size).all()
        
        return items, total
    
    def find_by_id(self, id: int) -> Optional[TemporaryRepair]:
        return self.db.query(TemporaryRepair).filter(TemporaryRepair.id == id).first()
    
    def find_by_repair_id(self, repair_id: str) -> Optional[TemporaryRepair]:
        return self.db.query(TemporaryRepair).filter(TemporaryRepair.repair_id == repair_id).first()
    
    def exists_by_repair_id(self, repair_id: str) -> bool:
        return self.db.query(TemporaryRepair).filter(TemporaryRepair.repair_id == repair_id).first() is not None
    
    def create(self, repair: TemporaryRepair) -> TemporaryRepair:
        self.db.add(repair)
        self.db.commit()
        self.db.refresh(repair)
        return repair
    
    def update(self, repair: TemporaryRepair) -> TemporaryRepair:
        self.db.commit()
        self.db.refresh(repair)
        return repair
    
    def delete(self, repair: TemporaryRepair) -> None:
        self.db.delete(repair)
        self.db.commit()
    
    def find_all_unpaginated(self) -> List[TemporaryRepair]:
        return self.db.query(TemporaryRepair).all()
