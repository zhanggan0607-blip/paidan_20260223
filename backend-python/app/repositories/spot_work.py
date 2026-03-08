"""
零星用工Repository
提供零星用工数据访问方法
"""
import logging
from datetime import date
from typing import Any

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.spot_work import SpotWork
from app.models.spot_work_worker import SpotWorkWorker
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


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
        client_name: str | None = None
    ) -> tuple[list[SpotWork], int]:
        """
        分页查询零星用工列表

        Args:
            page: 页码
            size: 每页数量
            project_name: 项目名称（模糊查询）
            work_id: 工单编号（模糊查询）
            status: 状态
            maintenance_personnel: 运维人员
            client_name: 客户名称（模糊查询）

        Returns:
            (工单列表, 总数)
        """
        try:
            query = self.db.query(SpotWork).options(joinedload(SpotWork.project)).filter(
                SpotWork.is_deleted == False
            )

            if project_name:
                query = query.filter(SpotWork.project_name.like(f'%{project_name}%'))

            if work_id:
                query = query.filter(SpotWork.work_id.like(f'%{work_id}%'))

            if status:
                query = query.filter(SpotWork.status == status)

            if maintenance_personnel:
                query = query.filter(SpotWork.maintenance_personnel == maintenance_personnel)

            if client_name:
                query = query.filter(SpotWork.client_name.like(f'%{client_name}%'))

            total = query.count()
            items = query.order_by(SpotWork.created_at.desc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询零星用工列表失败: {str(e)}")
            raise

    def find_by_work_id(self, work_id: str) -> SpotWork | None:
        """
        根据工单编号查询

        Args:
            work_id: 工单编号

        Returns:
            工单对象，未找到返回None
        """
        try:
            return self.db.query(SpotWork).options(joinedload(SpotWork.project)).filter(
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

    def soft_delete(self, work: SpotWork, user_id: int = None) -> None:
        """
        软删除零星用工单

        Args:
            work: 要删除的工单对象
            user_id: 执行删除的用户ID
        """
        try:
            work.soft_delete(user_id)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"软删除零星用工失败: {str(e)}")
            raise

    def find_all_unpaginated(self) -> list[SpotWork]:
        """
        查询所有零星用工（不分页）

        Returns:
            工单列表
        """
        try:
            return self.db.query(SpotWork).options(joinedload(SpotWork.project)).filter(
                SpotWork.is_deleted == False
            ).all()
        except Exception as e:
            logger.error(f"查询所有零星用工失败: {str(e)}")
            raise

    def find_workers_by_project_and_date(
        self,
        project_id: str,
        start_date: str | None = None,
        end_date: str | None = None
    ) -> list[SpotWorkWorker]:
        """
        根据项目ID和日期范围获取工人列表

        Args:
            project_id: 项目编号
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            工人列表
        """
        try:
            query = self.db.query(SpotWorkWorker).filter(
                SpotWorkWorker.project_id == project_id
            )

            if start_date:
                query = query.filter(func.date(SpotWorkWorker.start_date) == start_date)
            if end_date:
                query = query.filter(func.date(SpotWorkWorker.end_date) == end_date)

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
            self.db.commit()
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
            self.db.commit()
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
