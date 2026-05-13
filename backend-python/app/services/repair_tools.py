"""
维修工具Service
提供维修工具库存和领用管理的业务逻辑
"""
import uuid

from sqlalchemy.orm import Session

from app.exceptions import BusinessException
from app.repositories.repair_tools import RepairToolsStockRepository, RepairToolsIssueRepository
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class RepairToolsService:
    def __init__(self, db: Session):
        self._db = db
        self._stock_repo = RepairToolsStockRepository(db)
        self._issue_repo = RepairToolsIssueRepository(db)

    def get_stock_list(self, tool_name: str | None = None) -> list:
        return self._stock_repo.search_stock(tool_name)

    def get_issue_list(self, tool_name: str | None = None, status: str | None = None,
                       page: int = 0, page_size: int = 10) -> tuple[list, int]:
        return self._issue_repo.search_issues(tool_name, status, page, page_size)
