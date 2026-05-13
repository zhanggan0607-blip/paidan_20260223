"""
维修工具Repository
提供维修工具库存和领用相关的数据库操作
"""
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.repair_tools import RepairToolsIssue, RepairToolsStock
from app.models.repair_tools_inbound import RepairToolsInbound
from app.repositories.base import BaseRepository


class RepairToolsStockRepository(BaseRepository[RepairToolsStock]):
    def __init__(self, db: Session):
        super().__init__(db, RepairToolsStock)

    def find_by_name(self, tool_name: str) -> RepairToolsStock | None:
        return self.db.query(RepairToolsStock).filter(
            RepairToolsStock.tool_name == tool_name
        ).first()

    def search_stock(self, tool_name: str | None = None) -> list[RepairToolsStock]:
        query = self.db.query(RepairToolsStock)
        if tool_name:
            query = query.filter(RepairToolsStock.tool_name.like(f'%{tool_name}%'))
        return query.order_by(RepairToolsStock.tool_name.asc()).all()


class RepairToolsIssueRepository(BaseRepository[RepairToolsIssue]):
    def __init__(self, db: Session):
        super().__init__(db, RepairToolsIssue)

    def search_issues(self, tool_name: str | None = None, status: str | None = None,
                      page: int = 0, page_size: int = 10) -> tuple[list[RepairToolsIssue], int]:
        query = self.db.query(RepairToolsIssue)
        if tool_name:
            query = query.filter(RepairToolsIssue.tool_name.like(f'%{tool_name}%'))
        if status:
            query = query.filter(RepairToolsIssue.status == status)
        total = query.count()
        items = query.order_by(RepairToolsIssue.created_at.desc()).offset(page * page_size).limit(page_size).all()
        return items, total


class RepairToolsInboundRepository(BaseRepository[RepairToolsInbound]):
    def __init__(self, db: Session):
        super().__init__(db, RepairToolsInbound)
