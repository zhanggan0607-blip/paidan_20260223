from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.periodic_inspection import PeriodicInspection


class PeriodicInspectionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, id: int) -> Optional[PeriodicInspection]:
        return self.db.query(PeriodicInspection).filter(PeriodicInspection.id == id).first()
    
    def find_by_inspection_id(self, inspection_id: str) -> Optional[PeriodicInspection]:
        return self.db.query(PeriodicInspection).filter(PeriodicInspection.inspection_id == inspection_id).first()
    
    def exists_by_inspection_id(self, inspection_id: str) -> bool:
        return self.db.query(PeriodicInspection).filter(PeriodicInspection.inspection_id == inspection_id).first() is not None
    
    def find_all(
        self, 
        page: int = 0, 
        size: int = 10, 
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[PeriodicInspection], int]:
        query = self.db.query(PeriodicInspection)
        
        if project_name:
            query = query.filter(PeriodicInspection.project_name.like(f"%{project_name}%"))
        
        if client_name:
            query = query.filter(PeriodicInspection.client_name.like(f"%{client_name}%"))
        
        if status:
            query = query.filter(PeriodicInspection.status == status)
        
        total = query.count()
        items = query.order_by(PeriodicInspection.created_at.desc()).offset(page * size).limit(size).all()
        
        return items, total
    
    def find_all_unpaginated(self) -> List[PeriodicInspection]:
        return self.db.query(PeriodicInspection).order_by(PeriodicInspection.created_at.desc()).all()
    
    def create(self, inspection: PeriodicInspection) -> PeriodicInspection:
        try:
            self.db.add(inspection)
            self.db.commit()
            self.db.refresh(inspection)
            return inspection
        except Exception as e:
            self.db.rollback()
            raise e
    
    def update(self, inspection: PeriodicInspection) -> PeriodicInspection:
        self.db.commit()
        self.db.refresh(inspection)
        return inspection
    
    def delete(self, inspection: PeriodicInspection) -> None:
        self.db.delete(inspection)
        self.db.commit()
