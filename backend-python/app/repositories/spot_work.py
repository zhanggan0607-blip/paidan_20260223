from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.spot_work import SpotWork


class SpotWorkRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[SpotWork], int]:
        query = self.db.query(SpotWork)
        
        if project_name:
            query = query.filter(SpotWork.project_name.like(f'%{project_name}%'))
        
        if client_name:
            query = query.filter(SpotWork.client_name.like(f'%{client_name}%'))
        
        if status:
            query = query.filter(SpotWork.status == status)
        
        total = query.count()
        items = query.offset(page * size).limit(size).all()
        
        return items, total
    
    def find_by_id(self, id: int) -> Optional[SpotWork]:
        return self.db.query(SpotWork).filter(SpotWork.id == id).first()
    
    def find_by_work_id(self, work_id: str) -> Optional[SpotWork]:
        return self.db.query(SpotWork).filter(SpotWork.work_id == work_id).first()
    
    def exists_by_work_id(self, work_id: str) -> bool:
        return self.db.query(SpotWork).filter(SpotWork.work_id == work_id).first() is not None
    
    def create(self, work: SpotWork) -> SpotWork:
        self.db.add(work)
        self.db.commit()
        self.db.refresh(work)
        return work
    
    def update(self, work: SpotWork) -> SpotWork:
        self.db.commit()
        self.db.refresh(work)
        return work
    
    def delete(self, work: SpotWork) -> None:
        self.db.delete(work)
        self.db.commit()
    
    def find_all_unpaginated(self) -> List[SpotWork]:
        return self.db.query(SpotWork).all()
