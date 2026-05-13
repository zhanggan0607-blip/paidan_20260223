"""
零星用工Repository
提供零星用工数据访问方法
"""
from app.utils.logging_config import get_logger
from datetime import date
from typing import Any

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from app.models.spot_work import SpotWork
from app.models.spot_work_worker import SpotWorkWorker
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class SpotWorkRepository(BaseRepository[SpotWork]):
    """
    零星用工Repository
    继承BaseRepository，复用通用CRUD方法
    """

    def __init__(self, db: Session):
        super().__init__(db, SpotWork)

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        project_name: str | None = None,
        work_id: str | None = None,
        status: str | None = None,
        maintenance_personnel: str | None = None,
        client_name: str | None = None,
        statuses: list[str] | None = None
    ) -> tuple[list[SpotWork], int]:
        try:
            query = self.db.query(SpotWork).filter(SpotWork.is_deleted == False)

            if project_name:
                query = query.filter(SpotWork.project_name.like(f'%{self.escape_like(project_name)}%', escape='\\'))

            if work_id:
                query = query.filter(SpotWork.work_id.like(f'%{self.escape_like(work_id)}%', escape='\\'))

            if status:
                query = query.filter(SpotWork.status == status)

            if statuses:
                query = query.filter(SpotWork.status.in_(statuses))

            if maintenance_personnel:
                query = query.filter(SpotWork.maintenance_personnel == maintenance_personnel)

            if client_name:
                query = query.filter(SpotWork.client_name.like(f'%{self.escape_like(client_name)}%', escape='\\'))

            total = query.count()
            items = query.order_by(SpotWork.created_at.desc(), SpotWork.id.desc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询零星用工列表失败: {str(e)}")
            raise

    def find_by_work_id(self, work_id: str) -> SpotWork | None:
        try:
            return self.db.query(SpotWork).options(selectinload(SpotWork.project)).filter(
                SpotWork.work_id == work_id,
                SpotWork.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"查询零星用工失败 (work_id={work_id}): {str(e)}")
            raise

    def exists_by_work_id(self, work_id: str) -> bool:
        """
        检查工单编号是否存在

        Args:
            work_id: 工单编号

        Returns:
            是否存在
        """
        try:
            return self.db.query(SpotWork).filter(
                SpotWork.work_id == work_id,
                SpotWork.is_deleted == False
            ).first() is not None
        except Exception as e:
            logger.error(f"检查零星用工是否存在失败 (work_id={work_id}): {str(e)}")
            raise

    def count_by_work_id_prefix(self, prefix: str) -> int:
        """
        根据工单编号前缀统计数量

        Args:
            prefix: 工单编号前缀

        Returns:
            数量
        """
        try:
            return self.db.query(SpotWork).filter(
                SpotWork.work_id.like(f"{prefix}%"),
                SpotWork.is_deleted == False
            ).count()
        except Exception as e:
            logger.error(f"统计工单编号前缀数量失败 (prefix={prefix}): {str(e)}")
            raise

    def find_all_unpaginated(self) -> list[SpotWork]:
        try:
            return list(
                self.db.query(SpotWork).options(selectinload(SpotWork.project)).filter(
                    SpotWork.is_deleted == False
                ).order_by(SpotWork.created_at.desc(), SpotWork.id.desc())
                .yield_per(200)
            )
        except Exception as e:
            logger.error(f"查询所有零星用工失败: {str(e)}")
            raise

    def find_workers_by_project_and_date(
        self,
        project_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
        unlinked_only: bool = False
    ) -> list[SpotWorkWorker]:
        try:
            query = self.db.query(SpotWorkWorker).filter(
                SpotWorkWorker.project_id == project_id
            )

            if start_date:
                query = query.filter(func.date(SpotWorkWorker.start_date) == start_date)
            if end_date:
                query = query.filter(func.date(SpotWorkWorker.end_date) == end_date)

            if unlinked_only:
                query = query.filter(SpotWorkWorker.spot_work_id.is_(None))

            return query.all()
        except Exception as e:
            logger.error(f"查询工人列表失败: {str(e)}")
            raise

    def find_workers_by_conditions(
        self,
        project_ids: list[str],
        date_filters: list[Any]
    ) -> list[SpotWorkWorker]:
        """
        根据多个条件批量查询工人

        Args:
            project_ids: 项目ID列表
            date_filters: 日期过滤条件列表

        Returns:
            工人列表
        """
        try:
            if not date_filters:
                return []

            return self.db.query(SpotWorkWorker).filter(
                SpotWorkWorker.project_id.in_(project_ids),
                or_(*date_filters)
            ).all()
        except Exception as e:
            logger.error(f"批量查询工人失败: {str(e)}")
            raise

    def find_worker_by_unique_key(
        self,
        project_id: str,
        id_card_number: str,
        start_date: date | None,
        end_date: date | None
    ) -> SpotWorkWorker | None:
        """
        根据唯一键查询工人（用于判断是否已存在）

        Args:
            project_id: 项目编号
            id_card_number: 身份证号码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            工人对象，未找到返回None
        """
        try:
            query = self.db.query(SpotWorkWorker).filter(
                SpotWorkWorker.project_id == project_id,
                SpotWorkWorker.id_card_number == id_card_number
            )

            if start_date:
                query = query.filter(SpotWorkWorker.start_date == start_date)
            if end_date:
                query = query.filter(SpotWorkWorker.end_date == end_date)

            return query.first()
        except Exception as e:
            logger.error(f"查询工人失败: {str(e)}")
            raise

    def find_worker_in_same_work(
        self,
        project_id: str,
        id_card_number: str,
        start_date: date | None = None,
        end_date: date | None = None,
        include_unlinked: bool = False
    ) -> SpotWorkWorker | None:
        """
        根据项目ID+日期范围+身份证号码查询工人（用于同一工单内身份证去重）

        Args:
            project_id: 项目编号
            id_card_number: 身份证号码
            start_date: 开始日期
            end_date: 结束日期
            include_unlinked: 是否包含未关联工单的工人

        Returns:
            工人对象，未找到返回None
        """
        try:
            query = self.db.query(SpotWorkWorker).filter(
                SpotWorkWorker.project_id == project_id,
                SpotWorkWorker.id_card_number == id_card_number
            )

            if not include_unlinked:
                query = query.filter(SpotWorkWorker.spot_work_id.isnot(None))

            if start_date:
                query = query.filter(func.date(SpotWorkWorker.start_date) == start_date)
            if end_date:
                query = query.filter(func.date(SpotWorkWorker.end_date) == end_date)

            return query.first()
        except Exception as e:
            logger.error(f"查询同工单内工人失败: {str(e)}")
            raise

    def find_worker_by_id_card_number(self, id_card_number: str) -> SpotWorkWorker | None:
        """
        根据身份证号码查询工人（全局检查，用于判断身份证是否已录入）

        Args:
            id_card_number: 身份证号码

        Returns:
            工人对象，未找到返回None
        """
        try:
            return self.db.query(SpotWorkWorker).filter(
                SpotWorkWorker.id_card_number == id_card_number
            ).first()
        except Exception as e:
            logger.error(f"根据身份证号码查询工人失败: {str(e)}")
            raise

    def check_worker_can_be_reused(self, id_card_number: str) -> dict[str, Any]:
        """
        检查施工人员是否可以被复用（关联的工单是否已完成）

        Args:
            id_card_number: 身份证号码

        Returns:
            字典包含：can_reuse（是否可复用）、worker_info（工人信息）、work_status（工单状态）
        """
        try:
            worker = self.db.query(SpotWorkWorker).filter(
                SpotWorkWorker.id_card_number == id_card_number
            ).first()

            if not worker:
                return {
                    'exists': False,
                    'can_reuse': True,
                    'worker_info': None,
                    'work_status': None
                }

            work = self.db.query(SpotWork).filter(
                SpotWork.project_id == worker.project_id,
                SpotWork.plan_start_date == worker.start_date,
                SpotWork.plan_end_date == worker.end_date,
                SpotWork.is_deleted == False
            ).first()

            work_status = work.status if work else None
            can_reuse = work_status == '已完成' if work else True

            return {
                'exists': True,
                'can_reuse': can_reuse,
                'worker_info': {
                    'name': worker.name,
                    'project_id': worker.project_id,
                    'project_name': worker.project_name,
                    'id_card_number': worker.id_card_number
                },
                'work_status': work_status,
                'work_id': work.work_id if work else None
            }
        except Exception as e:
            logger.error(f"检查施工人员是否可复用失败: {str(e)}")
            raise

    def create_worker(self, worker: SpotWorkWorker) -> SpotWorkWorker:
        """
        创建工人记录

        Args:
            worker: 工人对象

        Returns:
            创建后的工人对象
        """
        try:
            self.db.add(worker)
            self.db.flush()
            self.db.refresh(worker)
            return worker
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建工人失败: {str(e)}")
            raise

    def create_workers_batch(self, workers: list[SpotWorkWorker]) -> int:
        """
        批量创建工人记录

        Args:
            workers: 工人对象列表

        Returns:
            创建数量
        """
        try:
            self.db.add_all(workers)
            self.db.flush()
            return len(workers)
        except Exception as e:
            self.db.rollback()
            logger.error(f"批量创建工人失败: {str(e)}")
            raise

    def find_workers_for_spot_work(
        self,
        project_id: str,
        plan_start_date: date | None,
        plan_end_date: date | None
    ) -> list[SpotWorkWorker]:
        """
        根据工单信息查询关联的工人

        Args:
            project_id: 项目编号
            plan_start_date: 计划开始日期
            plan_end_date: 计划结束日期

        Returns:
            工人列表
        """
        try:
            query = self.db.query(SpotWorkWorker).filter(
                SpotWorkWorker.project_id == project_id
            )

            if plan_start_date:
                query = query.filter(
                    func.date(SpotWorkWorker.start_date) == plan_start_date
                )
            if plan_end_date:
                query = query.filter(
                    func.date(SpotWorkWorker.end_date) == plan_end_date
                )

            return query.all()
        except Exception as e:
            logger.error(f"查询工单关联工人失败: {str(e)}")
            raise

    def delete_worker(self, worker_id: int) -> bool:
        try:
            worker = self.db.query(SpotWorkWorker).filter(
                SpotWorkWorker.id == worker_id
            ).first()
            if not worker:
                return False
            self.db.delete(worker)
            self.db.flush()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除工人失败: {str(e)}")
            raise
