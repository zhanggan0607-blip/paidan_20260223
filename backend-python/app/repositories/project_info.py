from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.project_info import ProjectInfo


class ProjectInfoRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, id: int) -> Optional[ProjectInfo]:
        return self.db.query(ProjectInfo).filter(ProjectInfo.id == id).first()
    
    def find_by_project_id(self, project_id: str) -> Optional[ProjectInfo]:
        return self.db.query(ProjectInfo).filter(ProjectInfo.project_id == project_id).first()
    
    def exists_by_project_id(self, project_id: str) -> bool:
        return self.db.query(ProjectInfo).filter(ProjectInfo.project_id == project_id).first() is not None
    
    def find_all(
        self, 
        page: int = 0, 
        size: int = 10, 
        project_name: Optional[str] = None, 
        client_name: Optional[str] = None
    ) -> tuple[List[ProjectInfo], int]:
        query = self.db.query(ProjectInfo)
        
        if project_name:
            query = query.filter(ProjectInfo.project_name.like(f"%{project_name}%"))
        
        if client_name:
            query = query.filter(ProjectInfo.client_name.like(f"%{client_name}%"))
        
        total = query.count()
        items = query.order_by(ProjectInfo.created_at.desc()).offset(page * size).limit(size).all()
        
        return items, total
    
    def find_all_unpaginated(self) -> List[ProjectInfo]:
        return self.db.query(ProjectInfo).order_by(ProjectInfo.created_at.desc()).all()
    
    def create(self, project_info: ProjectInfo) -> ProjectInfo:
        print(f"📥 [Repository] 准备插入数据: id={project_info.id}, project_id={project_info.project_id}")
        
        try:
            self.db.add(project_info)
            self.db.commit()
            self.db.refresh(project_info)
            print(f"✅ [Repository] 数据库插入成功: id={project_info.id}, project_id={project_info.project_id}")
            return project_info
        except Exception as e:
            print(f"❌ [Repository] 数据库插入失败: {str(e)}")
            self.db.rollback()
            raise e
    
    def update(self, project_info: ProjectInfo) -> ProjectInfo:
        self.db.commit()
        self.db.refresh(project_info)
        return project_info
    
    def delete(self, project_info: ProjectInfo) -> None:
        self.db.delete(project_info)
        self.db.commit()
