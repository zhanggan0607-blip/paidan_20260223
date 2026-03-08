"""
零星用工服务
提供零星用工业务逻辑处理
"""
import json
import logging
from datetime import datetime
from typing import Any

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.exceptions import DuplicateException, NotFoundException, ValidationException
from app.models.spot_work import SpotWork
from app.models.spot_work_worker import SpotWorkWorker
from app.repositories.spot_work import SpotWorkRepository
from app.schemas.spot_work import SpotWorkCreate, SpotWorkUpdate
from app.services.sync_service import PLAN_TYPE_SPOTWORK, SyncService
from app.utils.date_utils import parse_datetime
from app.utils.dictionary_helper import get_default_spot_work_status
from app.utils.work_order_id_generator import generate_spot_work_id

logger = logging.getLogger(__name__)


class SpotWorkService:
    """
    零星用工服务
    提供零星用工的增删改查等业务逻辑
    """

    def __init__(self, db: Session):
        self.repository = SpotWorkRepository(db)
        self.sync_service = SyncService(db)
        self._db = db

    def _parse_date(self, date_value: str | datetime | None) -> datetime | None:
        """解析日期"""
        return parse_datetime(date_value)

    def get_all(
        self,
        page: int = 0,
        size: int = 10,
        project_name: str | None = None,
        work_id: str | None = None,
        status: str | None = None,
        maintenance_personnel: str | None = None
    ) -> tuple[list[SpotWork], int]:
        """
        分页获取零星用工列表

        Args:
            page: 页码
            size: 每页数量
            project_name: 项目名称
            work_id: 工单编号
            status: 状态
            maintenance_personnel: 运维人员

        Returns:
            (工单列表, 总数)
        """
        return self.repository.find_all(
            page, size, project_name, work_id, status, maintenance_personnel
        )

    def get_by_id(self, id: int) -> SpotWork:
        """
        根据ID获取零星用工

        Args:
            id: 工单ID

        Returns:
            工单对象

        Raises:
            NotFoundException: 工单不存在
        """
        work = self.repository.find_by_id(id)
        if not work:
            raise NotFoundException("用工单不存在")
        return work

    def get_by_work_id(self, work_id: str) -> SpotWork:
        """
        根据工单编号获取零星用工

        Args:
            work_id: 工单编号

        Returns:
            工单对象

        Raises:
            NotFoundException: 工单不存在
        """
        work = self.repository.find_by_work_id(work_id)
        if not work:
            raise NotFoundException("用工单不存在")
        return work

    def generate_work_id(self, project_id: str) -> str:
        """
        生成工单编号（使用数据库序列保证并发安全）

        Args:
            project_id: 项目编号

        Returns:
            工单编号
        """
        return generate_spot_work_id(self._db, project_id)

    def create(self, dto: SpotWorkCreate, operator_id: int | None = None, operator_name: str | None = None) -> SpotWork:
        """
        创建零星用工

        Args:
            dto: 创建数据传输对象
            operator_id: 操作者ID
            operator_name: 操作者名称

        Returns:
            创建的工单对象

        Raises:
            DuplicateException: 工单编号已存在
        """
        work_id = dto.work_id
        if work_id and self.repository.exists_by_work_id(work_id):
            raise DuplicateException("用工单编号已存在")

        if not work_id:
            work_id = self.generate_work_id(dto.project_id)

        default_status = get_default_spot_work_status(self._db)

        photos_json = json.dumps(dto.photos, ensure_ascii=False) if dto.photos else None

        work = SpotWork(
            work_id=work_id,
            project_id=dto.project_id,
            project_name=dto.project_name,
            plan_start_date=self._parse_date(dto.plan_start_date),
            plan_end_date=self._parse_date(dto.plan_end_date),
            client_name=dto.client_name,
            client_contact=dto.client_contact,
            client_contact_info=dto.client_contact_info,
            maintenance_personnel=dto.maintenance_personnel,
            work_content=dto.work_content,
            photos=photos_json,
            signature=dto.signature,
            status=dto.status or default_status,
            remarks=dto.remarks
        )

        result = self.repository.create(work)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_SPOTWORK, result)

        if operator_name and result.id:
            self._create_operation_log(
                work_order_id=result.id,
                work_order_no=result.work_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='create',
                operation_type_name='创建',
                remark='创建零星用工工单'
            )

        return result

    def update(self, id: int, dto: SpotWorkUpdate) -> SpotWork:
        """
        更新零星用工

        Args:
            id: 工单ID
            dto: 更新数据传输对象

        Returns:
            更新后的工单对象

        Raises:
            NotFoundException: 工单不存在
            DuplicateException: 工单编号已存在
        """
        existing_work = self.get_by_id(id)

        if existing_work.work_id != dto.work_id and self.repository.exists_by_work_id(dto.work_id):
            raise DuplicateException("用工单编号已存在")

        photos_json = json.dumps(dto.photos, ensure_ascii=False) if dto.photos else None

        existing_work.work_id = dto.work_id
        existing_work.project_id = dto.project_id
        existing_work.project_name = dto.project_name
        existing_work.plan_start_date = self._parse_date(dto.plan_start_date)
        existing_work.plan_end_date = self._parse_date(dto.plan_end_date)
        existing_work.client_name = dto.client_name
        existing_work.client_contact = dto.client_contact
        existing_work.client_contact_info = dto.client_contact_info
        existing_work.maintenance_personnel = dto.maintenance_personnel
        existing_work.work_content = dto.work_content
        existing_work.photos = photos_json
        existing_work.signature = dto.signature
        existing_work.status = dto.status
        existing_work.remarks = dto.remarks

        result = self.repository.update(existing_work)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_SPOTWORK, result)
        self._db.commit()
        return result

    def partial_update(self, id: int, dto) -> SpotWork:
        """
        部分更新零星用工

        Args:
            id: 工单ID
            dto: 部分更新数据传输对象

        Returns:
            更新后的工单对象

        Raises:
            NotFoundException: 工单不存在
            DuplicateException: 工单编号已存在
        """
        existing_work = self.get_by_id(id)

        if dto.work_id is not None:
            if existing_work.work_id != dto.work_id and self.repository.exists_by_work_id(dto.work_id):
                raise DuplicateException("用工单编号已存在")
            existing_work.work_id = dto.work_id
        if dto.project_id is not None:
            existing_work.project_id = dto.project_id
        if dto.project_name is not None:
            existing_work.project_name = dto.project_name
        if dto.plan_start_date is not None:
            existing_work.plan_start_date = self._parse_date(dto.plan_start_date)
        if dto.plan_end_date is not None:
            existing_work.plan_end_date = self._parse_date(dto.plan_end_date)
        if dto.client_name is not None:
            existing_work.client_name = dto.client_name
        if dto.client_contact is not None:
            existing_work.client_contact = dto.client_contact
        if dto.client_contact_info is not None:
            existing_work.client_contact_info = dto.client_contact_info
        if dto.maintenance_personnel is not None:
            existing_work.maintenance_personnel = dto.maintenance_personnel
        if dto.work_content is not None:
            existing_work.work_content = dto.work_content
        if dto.photos is not None:
            existing_work.photos = json.dumps(dto.photos, ensure_ascii=False)
        if dto.signature is not None:
            existing_work.signature = dto.signature
        if dto.status is not None:
            existing_work.status = dto.status
            if dto.status == '已完成' and not existing_work.actual_completion_date:
                existing_work.actual_completion_date = datetime.now()
        if dto.remarks is not None:
            existing_work.remarks = dto.remarks

        result = self.repository.update(existing_work)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_SPOTWORK, result)
        self._db.commit()
        return result

    def delete(self, id: int, user_id: int = None, operator_name: str = None) -> None:
        """
        软删除零星用工单

        Args:
            id: 工单ID
            user_id: 执行删除的用户ID
            operator_name: 操作者名称

        Raises:
            NotFoundException: 工单不存在
        """
        work = self.get_by_id(id)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_SPOTWORK, work, is_delete=True, user_id=user_id)

        if operator_name and work.id:
            self._create_operation_log(
                work_order_id=work.id,
                work_order_no=work.work_id,
                operator_name=operator_name,
                operator_id=user_id,
                operation_type='delete',
                operation_type_name='删除',
                remark=f'删除零星用工单 {work.work_id}'
            )

        self.repository.soft_delete(work, user_id)

    def get_all_unpaginated(self) -> list[SpotWork]:
        """
        获取所有零星用工（不分页）

        Returns:
            工单列表
        """
        return self.repository.find_all_unpaginated()

    def get_all_with_workers(
        self,
        page: int = 0,
        size: int = 10,
        project_name: str | None = None,
        work_id: str | None = None,
        status: str | None = None,
        maintenance_personnel: str | None = None
    ) -> tuple[list[dict[str, Any]], int]:
        """
        分页获取零星用工列表（包含工人信息）

        Args:
            page: 页码
            size: 每页数量
            project_name: 项目名称
            work_id: 工单编号
            status: 状态
            maintenance_personnel: 运维人员

        Returns:
            (工单字典列表, 总数)
        """
        items, total = self.repository.find_all(
            page, size, project_name, work_id, status, maintenance_personnel
        )

        if not items:
            return [], total

        project_ids = [item.project_id for item in items]

        date_filters = []
        for item in items:
            if item.plan_start_date and item.plan_end_date:
                date_filters.append(
                    and_(
                        SpotWorkWorker.project_id == item.project_id,
                        func.date(SpotWorkWorker.start_date) == item.plan_start_date.date(),
                        func.date(SpotWorkWorker.end_date) == item.plan_end_date.date()
                    )
                )
            elif item.plan_start_date:
                date_filters.append(
                    and_(
                        SpotWorkWorker.project_id == item.project_id,
                        func.date(SpotWorkWorker.start_date) == item.plan_start_date.date()
                    )
                )

        all_workers = self.repository.find_workers_by_conditions(project_ids, date_filters)

        worker_map = {}
        for worker in all_workers:
            key = (
                worker.project_id,
                worker.start_date.date() if worker.start_date else None,
                worker.end_date.date() if worker.end_date else None
            )
            if key not in worker_map:
                worker_map[key] = []
            worker_map[key].append(worker)

        items_dict = []
        for item in items:
            item_dict = item.to_dict()

            key = (
                item.project_id,
                item.plan_start_date.date() if item.plan_start_date else None,
                item.plan_end_date.date() if item.plan_end_date else None
            )
            workers = worker_map.get(key, [])
            worker_count = len(workers)

            days = 0
            if item.plan_start_date and item.plan_end_date:
                delta = (item.plan_end_date - item.plan_start_date).days + 1
                days = max(0, delta)

            item_dict['worker_count'] = worker_count
            item_dict['work_days'] = days * worker_count
            items_dict.append(item_dict)

        return items_dict, total

    def get_by_id_with_workers(self, id: int) -> dict[str, Any]:
        """
        根据ID获取零星用工（包含工人信息）

        Args:
            id: 工单ID

        Returns:
            工单字典

        Raises:
            NotFoundException: 工单不存在
        """
        work = self.get_by_id(id)
        work_dict = work.to_dict()

        plan_start = work.plan_start_date.date() if work.plan_start_date else None
        plan_end = work.plan_end_date.date() if work.plan_end_date else None

        workers = self.repository.find_workers_for_spot_work(
            work.project_id, plan_start, plan_end
        )

        worker_count = len(workers)

        days = 0
        if work.plan_start_date and work.plan_end_date:
            delta = (work.plan_end_date - work.plan_start_date).days + 1
            days = max(0, delta)

        work_dict['worker_count'] = worker_count
        work_dict['work_days'] = days * worker_count
        work_dict['workers'] = [w.to_dict() for w in workers]

        return work_dict

    def get_workers_by_project_and_date(
        self,
        project_id: str,
        start_date: str,
        end_date: str
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
        return self.repository.find_workers_by_project_and_date(project_id, start_date, end_date)

    def save_workers(
        self,
        project_id: str,
        project_name: str,
        start_date: str | None,
        end_date: str | None,
        workers_data: list[dict[str, Any]]
    ) -> tuple[int, int]:
        """
        保存施工人员信息

        Args:
            project_id: 项目编号
            project_name: 项目名称
            start_date: 开始日期
            end_date: 结束日期
            workers_data: 工人数据列表

        Returns:
            (保存数量, 跳过数量)

        Raises:
            ValidationException: 身份证验证失败
        """
        from app.utils.id_card_validator import validate_id_card

        try:
            start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        except Exception as e:
            logger.error(f"日期解析错误: {e}")
            start = None
            end = None

        saved_count = 0
        skipped_count = 0
        workers_to_create = []

        for worker_data in workers_data:
            is_valid, id_card_msg, birth_date_from_id, gender_from_id = validate_id_card(
                worker_data.get('idCardNumber', '')
            )
            if not is_valid:
                raise ValidationException(
                    f"施工人员'{worker_data.get('name')}'的身份证号码无效: {id_card_msg}"
                )

            birth_date = worker_data.get('birthDate')
            if birth_date_from_id and birth_date and birth_date != birth_date_from_id:
                raise ValidationException(
                    f"施工人员'{worker_data.get('name')}'的身份证号码与出生日期不匹配，根据身份证应为{birth_date_from_id}"
                )

            gender = worker_data.get('gender')
            if gender_from_id and gender and gender != gender_from_id:
                raise ValidationException(
                    f"施工人员'{worker_data.get('name')}'的身份证号码与性别不匹配，根据身份证应为{gender_from_id}"
                )

            existing = self.repository.find_worker_by_unique_key(
                project_id,
                worker_data.get('idCardNumber'),
                start.date() if start else None,
                end.date() if end else None
            )

            if existing:
                logger.info(f"施工人员已存在，跳过: name={worker_data.get('name')}")
                skipped_count += 1
                continue

            logger.info(f"准备保存施工人员: name={worker_data.get('name')}")
            worker = SpotWorkWorker(
                project_id=project_id,
                project_name=project_name,
                start_date=start,
                end_date=end,
                name=worker_data.get('name'),
                gender=worker_data.get('gender'),
                birth_date=worker_data.get('birthDate'),
                address=worker_data.get('address'),
                id_card_number=worker_data.get('idCardNumber'),
                issuing_authority=worker_data.get('issuingAuthority'),
                valid_period=worker_data.get('validPeriod'),
                id_card_front=worker_data.get('idCardFront'),
                id_card_back=worker_data.get('idCardBack')
            )
            workers_to_create.append(worker)
            saved_count += 1

        if workers_to_create:
            self.repository.create_workers_batch(workers_to_create)

        logger.info(f"施工人员保存成功，新增 {saved_count} 条，跳过 {skipped_count} 条重复数据")
        return saved_count, skipped_count

    def quick_fill(
        self,
        project_id: str,
        project_name: str,
        plan_start_date: str,
        plan_end_date: str,
        work_content: str | None = None,
        remark: str | None = None,
        client_contact: str | None = None,
        client_contact_info: str | None = None,
        photos: str | None = None,
        signature: str | None = None,
        maintenance_personnel: str | None = None,
        operator_id: int | None = None,
        operator_name: str | None = None
    ) -> SpotWork:
        """
        快速填报零星用工

        Args:
            project_id: 项目编号
            project_name: 项目名称
            plan_start_date: 计划开始日期
            plan_end_date: 计划结束日期
            work_content: 工作内容
            remark: 备注
            client_contact: 客户联系人
            client_contact_info: 客户联系电话
            photos: 现场图片
            signature: 签字图片
            maintenance_personnel: 运维人员
            operator_id: 操作者ID
            operator_name: 操作者名称

        Returns:
            创建的工单对象
        """
        work_id = self.generate_work_id(project_id)

        photos_list = None
        if photos:
            try:
                photos_list = json.loads(photos) if isinstance(photos, str) else photos
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Failed to parse photos JSON: {e}")
                photos_list = None

        create_dto = SpotWorkCreate(
            work_id=work_id,
            project_id=project_id,
            project_name=project_name,
            plan_start_date=plan_start_date,
            plan_end_date=plan_end_date,
            client_name='',
            client_contact=client_contact,
            client_contact_info=client_contact_info,
            maintenance_personnel=maintenance_personnel,
            work_content=work_content,
            photos=photos_list,
            signature=signature,
            status='待确认',
            remarks=remark
        )

        work = self.create(create_dto, operator_id, operator_name)

        if operator_name and work.id:
            self._create_operation_log(
                work_order_id=work.id,
                work_order_no=work.work_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='submit',
                operation_type_name='提交',
                remark='员工提交工单'
            )

        return work

    def _create_operation_log(
        self,
        work_order_id: int,
        work_order_no: str,
        operator_name: str,
        operator_id: int | None,
        operation_type: str,
        operation_type_name: str,
        remark: str
    ) -> None:
        """
        创建操作日志

        Args:
            work_order_id: 工单ID
            work_order_no: 工单编号
            operator_name: 操作者名称
            operator_id: 操作者ID
            operation_type: 操作类型代码
            operation_type_name: 操作类型名称
            remark: 备注
        """
        from app.models.work_order_operation_log import WorkOrderOperationLog

        log = WorkOrderOperationLog(
            work_order_type='spot_work',
            work_order_id=work_order_id,
            work_order_no=work_order_no,
            operator_name=operator_name,
            operator_id=operator_id,
            operation_type=operation_type,
            operation_type_code=operation_type,
            operation_type_name=operation_type_name,
            operation_remark=remark
        )
        self._db.add(log)
        self._db.commit()
