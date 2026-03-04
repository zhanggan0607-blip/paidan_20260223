"""
项目信息服务
提供项目信息业务逻辑处理
"""
from typing import List, Optional
import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.project_info import ProjectInfo
from app.repositories.project_info import ProjectInfoRepository
from app.schemas.project_info import ProjectInfoCreate, ProjectInfoUpdate
from app.exceptions import NotFoundException, DuplicateException, ValidationException

logger = logging.getLogger(__name__)


class ProjectInfoService:
    """
    项目信息服务
    提供项目信息的增删改查等业务逻辑
    """
    
    def __init__(self, db: Session):
        self.repository = ProjectInfoRepository(db)
        self._db = db
    
    def _sync_customer_data(self, client_name: str, client_contact: Optional[str], client_contact_info: Optional[str], address: Optional[str], client_contact_position: Optional[str]):
        """
        同步客户数据到customer表
        如果客户不存在则创建，存在则更新
        """
        from app.models.customer import Customer
        
        if not client_name:
            return
        
        try:
            existing_customer = self._db.query(Customer).filter(Customer.name == client_name).first()
            
            if existing_customer:
                if client_contact and client_contact != existing_customer.contact_person:
                    existing_customer.contact_person = client_contact
                if client_contact_info and client_contact_info != existing_customer.phone:
                    existing_customer.phone = client_contact_info
                if address and address != existing_customer.address:
                    existing_customer.address = address
                if client_contact_position and client_contact_position != existing_customer.contact_position:
                    existing_customer.contact_position = client_contact_position
                self._db.commit()
                logger.info(f"同步更新客户信息: {client_name}")
            else:
                new_customer = Customer(
                    name=client_name,
                    contact_person=client_contact or '',
                    phone=client_contact_info or '',
                    address=address or '',
                    contact_position=client_contact_position or ''
                )
                self._db.add(new_customer)
                self._db.commit()
                logger.info(f"自动创建客户: {client_name}")
        except Exception as e:
            self._db.rollback()
            logger.error(f"同步客户数据失败: {str(e)}")
    
    def _create_operation_log(
        self,
        work_order_type: str,
        work_order_id: int,
        work_order_no: str,
        operator_name: str,
        operator_id: Optional[int],
        operation_type: str,
        operation_type_name: str,
        remark: str
    ) -> None:
        """
        创建操作日志
        
        Args:
            work_order_type: 工单类型
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
            work_order_type=work_order_type,
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
    
    def get_all(
        self, 
        page: int = 0, 
        size: int = 10, 
        project_name: Optional[str] = None, 
        client_name: Optional[str] = None,
        project_ids: Optional[List[str]] = None
    ) -> tuple[List[ProjectInfo], int]:
        """
        分页获取项目信息列表
        
        Args:
            page: 页码
            size: 每页数量
            project_name: 项目名称
            client_name: 客户名称
            project_ids: 项目ID列表（权限过滤）
            
        Returns:
            (项目信息列表, 总数)
        """
        return self.repository.find_all(page, size, project_name, client_name, project_ids)
    
    def get_by_id(self, id: int) -> ProjectInfo:
        """
        根据ID获取项目信息
        
        Args:
            id: 项目信息ID
            
        Returns:
            项目信息对象
            
        Raises:
            NotFoundException: 项目信息不存在
        """
        project_info = self.repository.find_by_id(id)
        if not project_info:
            raise NotFoundException("项目信息不存在")
        return project_info
    
    def get_by_project_id(self, project_id: str) -> ProjectInfo:
        """
        根据项目编号获取项目信息
        
        Args:
            project_id: 项目编号
            
        Returns:
            项目信息对象
            
        Raises:
            NotFoundException: 项目信息不存在
        """
        project_info = self.repository.find_by_project_id(project_id)
        if not project_info:
            raise NotFoundException("项目信息不存在")
        return project_info
    
    def create(
        self, 
        dto: ProjectInfoCreate, 
        operator_id: Optional[int] = None, 
        operator_name: Optional[str] = None
    ) -> ProjectInfo:
        """
        创建项目信息
        
        Args:
            dto: 创建数据传输对象
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            创建的项目信息对象
            
        Raises:
            DuplicateException: 项目编号已存在
        """
        logger.info(f"📥 [Service] 开始创建项目: project_id={dto.project_id}, project_name={dto.project_name}")

        if self.repository.exists_by_project_id(dto.project_id):
            logger.error(f"❌ [Service] 项目编号已存在: {dto.project_id}")
            raise DuplicateException("项目编号已存在")

        project_info = ProjectInfo(
            project_id=dto.project_id,
            project_name=dto.project_name,
            completion_date=dto.completion_date,
            maintenance_end_date=dto.maintenance_end_date,
            maintenance_period=dto.maintenance_period,
            client_name=dto.client_name,
            address=dto.address,
            project_abbr=dto.project_abbr,
            project_manager=dto.project_manager,
            client_contact=dto.client_contact,
            client_contact_position=dto.client_contact_position,
            client_contact_info=dto.client_contact_info
        )

        logger.info(f"📥 [Service] 准备保存到数据库: project_id={project_info.project_id}, project_name={project_info.project_name}")
        result = self.repository.create(project_info)
        
        self._sync_customer_data(
            dto.client_name,
            dto.client_contact,
            dto.client_contact_info,
            dto.address,
            dto.client_contact_position
        )
        
        if operator_name and result.id:
            self._create_operation_log(
                work_order_type='project_info',
                work_order_id=result.id,
                work_order_no=result.project_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='create',
                operation_type_name='创建',
                remark='创建项目信息'
            )
        
        logger.info(f"✅ [Service] 数据库保存成功: id={result.id}, project_id={result.project_id}")
        return result
    
    def update(
        self, 
        id: int, 
        dto: ProjectInfoUpdate, 
        operator_id: Optional[int] = None, 
        operator_name: Optional[str] = None
    ) -> ProjectInfo:
        """
        更新项目信息
        
        Args:
            id: 项目信息ID
            dto: 更新数据传输对象
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            更新后的项目信息对象
            
        Raises:
            NotFoundException: 项目信息不存在
            ValidationException: 项目编号不允许修改
        """
        existing_project = self.get_by_id(id)
        
        if existing_project.project_id != dto.project_id:
            raise ValidationException("项目编号不允许修改")
        
        old_project_name = existing_project.project_name
        old_client_name = existing_project.client_name
        old_project_manager = existing_project.project_manager
        
        project_name_changed = old_project_name != dto.project_name
        client_name_changed = old_client_name != dto.client_name
        project_manager_changed = old_project_manager != dto.project_manager
        
        existing_project.project_name = dto.project_name
        existing_project.completion_date = dto.completion_date
        existing_project.maintenance_end_date = dto.maintenance_end_date
        existing_project.maintenance_period = dto.maintenance_period
        existing_project.client_name = dto.client_name
        existing_project.address = dto.address
        existing_project.project_abbr = dto.project_abbr
        existing_project.project_manager = dto.project_manager
        existing_project.client_contact = dto.client_contact
        existing_project.client_contact_position = dto.client_contact_position
        existing_project.client_contact_info = dto.client_contact_info
        
        result = self.repository.update(existing_project)
        
        self._sync_customer_data(
            dto.client_name,
            dto.client_contact,
            dto.client_contact_info,
            dto.address,
            dto.client_contact_position
        )
        
        if project_name_changed or client_name_changed:
            self._sync_related_tables(
                existing_project.project_id,
                existing_project.id,
                dto.project_name if project_name_changed else None,
                dto.client_name if client_name_changed else None
            )
        
        if project_manager_changed and dto.project_manager:
            self._sync_maintenance_plan_responsible_person(
                existing_project.project_id,
                dto.project_manager
            )
            self._sync_work_orders_maintenance_personnel(
                existing_project.project_id,
                old_project_manager,
                dto.project_manager
            )
        
        if operator_name and result.id:
            self._create_operation_log(
                work_order_type='project_info',
                work_order_id=result.id,
                work_order_no=result.project_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='update',
                operation_type_name='更新',
                remark='更新项目信息'
            )
        
        return result
    
    def _sync_related_tables(
        self, 
        project_id: str,
        project_pk: int,
        new_project_name: Optional[str] = None, 
        new_client_name: Optional[str] = None
    ):
        """
        同步更新关联表数据
        """
        from app.models.work_plan import WorkPlan
        from app.models.periodic_inspection import PeriodicInspection
        from app.models.temporary_repair import TemporaryRepair
        from app.models.spot_work import SpotWork
        from app.models.spare_parts_usage import SparePartsUsage
        from app.models.repair_tools import RepairToolsIssue
        from app.models.maintenance_plan import MaintenancePlan
        
        sync_count = 0
        
        if new_project_name:
            work_plan_updated = self._db.query(WorkPlan).filter(
                WorkPlan.project_id == project_id
            ).update({"project_name": new_project_name}, synchronize_session=False)
            sync_count += work_plan_updated
            
            periodic_updated = self._db.query(PeriodicInspection).filter(
                PeriodicInspection.project_id == project_id
            ).update({"project_name": new_project_name}, synchronize_session=False)
            sync_count += periodic_updated
            
            repair_updated = self._db.query(TemporaryRepair).filter(
                TemporaryRepair.project_id == project_id
            ).update({"project_name": new_project_name}, synchronize_session=False)
            sync_count += repair_updated
            
            spot_work_updated = self._db.query(SpotWork).filter(
                SpotWork.project_id == project_id
            ).update({"project_name": new_project_name}, synchronize_session=False)
            sync_count += spot_work_updated
            
            spare_parts_updated = self._db.query(SparePartsUsage).filter(
                SparePartsUsage.project_id == project_id
            ).update({"project_name": new_project_name}, synchronize_session=False)
            sync_count += spare_parts_updated
            
            tools_issue_updated = self._db.query(RepairToolsIssue).filter(
                RepairToolsIssue.project_id == project_id
            ).update({"project_name": new_project_name}, synchronize_session=False)
            sync_count += tools_issue_updated
            
            maintenance_plan_updated = self._db.query(MaintenancePlan).filter(
                MaintenancePlan.project_id == project_id
            ).update({"project_name": new_project_name}, synchronize_session=False)
            sync_count += maintenance_plan_updated
        
        if new_client_name:
            work_plan_updated = self._db.query(WorkPlan).filter(
                WorkPlan.project_id == project_id
            ).update({"client_name": new_client_name}, synchronize_session=False)
            sync_count += work_plan_updated
            
            periodic_updated = self._db.query(PeriodicInspection).filter(
                PeriodicInspection.project_id == project_id
            ).update({"client_name": new_client_name}, synchronize_session=False)
            sync_count += periodic_updated
            
            repair_updated = self._db.query(TemporaryRepair).filter(
                TemporaryRepair.project_id == project_id
            ).update({"client_name": new_client_name}, synchronize_session=False)
            sync_count += repair_updated
            
            spot_work_updated = self._db.query(SpotWork).filter(
                SpotWork.project_id == project_id
            ).update({"client_name": new_client_name}, synchronize_session=False)
            sync_count += spot_work_updated
        
        if sync_count > 0:
            self._db.commit()
            logger.info(f"✅ [Service] 同步更新关联表数据: project_id={project_id}, 更新记录数={sync_count}")
    
    def _sync_maintenance_plan_responsible_person(self, project_id: str, new_responsible_person: str):
        """
        同步更新维保计划的负责人
        """
        from app.models.maintenance_plan import MaintenancePlan
        
        try:
            updated_count = self._db.query(MaintenancePlan).filter(
                MaintenancePlan.project_id == project_id
            ).update({"maintenance_personnel": new_responsible_person}, synchronize_session=False)
            
            if updated_count > 0:
                self._db.commit()
                logger.info(f"✅ [Service] 同步更新维保计划负责人: project_id={project_id}, 新负责人={new_responsible_person}, 更新记录数={updated_count}")
        except Exception as e:
            self._db.rollback()
            logger.error(f"❌ [Service] 同步更新维保计划负责人失败: {str(e)}")
    
    def _sync_work_orders_maintenance_personnel(self, project_id: str, old_personnel: str, new_personnel: str):
        """
        同步更新工单的运维人员
        """
        from app.models.periodic_inspection import PeriodicInspection
        from app.models.temporary_repair import TemporaryRepair
        from app.models.spot_work import SpotWork
        
        total_updated = 0
        
        try:
            periodic_updated = self._db.query(PeriodicInspection).filter(
                PeriodicInspection.project_id == project_id,
                PeriodicInspection.maintenance_personnel == old_personnel
            ).update({"maintenance_personnel": new_personnel}, synchronize_session=False)
            total_updated += periodic_updated
            logger.info(f"📝 [Service] 更新定期巡检工单运维人员: {periodic_updated} 条")
            
            repair_updated = self._db.query(TemporaryRepair).filter(
                TemporaryRepair.project_id == project_id,
                TemporaryRepair.maintenance_personnel == old_personnel
            ).update({"maintenance_personnel": new_personnel}, synchronize_session=False)
            total_updated += repair_updated
            logger.info(f"📝 [Service] 更新临时维修工单运维人员: {repair_updated} 条")
            
            spot_work_updated = self._db.query(SpotWork).filter(
                SpotWork.project_id == project_id,
                SpotWork.maintenance_personnel == old_personnel
            ).update({"maintenance_personnel": new_personnel}, synchronize_session=False)
            total_updated += spot_work_updated
            logger.info(f"📝 [Service] 更新零星用工工单运维人员: {spot_work_updated} 条")
            
            if total_updated > 0:
                self._db.commit()
                logger.info(f"✅ [Service] 同步更新工单运维人员完成: project_id={project_id}, {old_personnel} -> {new_personnel}, 共更新 {total_updated} 条记录")
            else:
                logger.info(f"ℹ️ [Service] 无需更新工单运维人员: project_id={project_id}, 未找到原运维人员 {old_personnel} 的工单")
                
        except Exception as e:
            self._db.rollback()
            logger.error(f"❌ [Service] 同步更新工单运维人员失败: {str(e)}")
    
    def delete(self, id: int, cascade: bool = False, user_id: int = None, operator_name: str = None) -> dict:
        """
        删除项目信息
        
        Args:
            id: 项目信息ID
            cascade: 是否级联删除
            user_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            删除结果
            
        Raises:
            NotFoundException: 项目信息不存在
            ValidationException: 存在关联数据且未指定级联删除
        """
        project_info = self.get_by_id(id)
        
        from app.models.work_plan import WorkPlan
        from app.models.periodic_inspection import PeriodicInspection
        from app.models.temporary_repair import TemporaryRepair
        from app.models.spot_work import SpotWork
        from app.models.maintenance_plan import MaintenancePlan
        
        project_id = project_info.project_id
        
        work_plan_count = self._db.query(WorkPlan).filter(WorkPlan.project_id == project_id).count()
        periodic_count = self._db.query(PeriodicInspection).filter(PeriodicInspection.project_id == project_id).count()
        repair_count = self._db.query(TemporaryRepair).filter(TemporaryRepair.project_id == project_id).count()
        spot_count = self._db.query(SpotWork).filter(SpotWork.project_id == project_id).count()
        maintenance_count = self._db.query(MaintenancePlan).filter(MaintenancePlan.project_id == project_id).count()
        
        total_related = work_plan_count + periodic_count + repair_count + spot_count + maintenance_count
        
        if total_related > 0 and not cascade:
            details = []
            if work_plan_count > 0:
                details.append(f"{work_plan_count} 条工作计划")
            if periodic_count > 0:
                details.append(f"{periodic_count} 条定期巡检")
            if repair_count > 0:
                details.append(f"{repair_count} 条临时维修")
            if spot_count > 0:
                details.append(f"{spot_count} 条零星用工")
            if maintenance_count > 0:
                details.append(f"{maintenance_count} 条维保计划")
            
            raise ValidationException(f"该项目下有 {', '.join(details)}，请确认是否级联删除")
        
        deleted_counts = {}
        
        if cascade:
            if work_plan_count > 0:
                self._db.query(WorkPlan).filter(WorkPlan.project_id == project_id).delete(synchronize_session=False)
                deleted_counts['work_plan'] = work_plan_count
            
            if periodic_count > 0:
                self._db.query(PeriodicInspection).filter(PeriodicInspection.project_id == project_id).delete(synchronize_session=False)
                deleted_counts['periodic_inspection'] = periodic_count
            
            if repair_count > 0:
                self._db.query(TemporaryRepair).filter(TemporaryRepair.project_id == project_id).delete(synchronize_session=False)
                deleted_counts['temporary_repair'] = repair_count
            
            if spot_count > 0:
                self._db.query(SpotWork).filter(SpotWork.project_id == project_id).delete(synchronize_session=False)
                deleted_counts['spot_work'] = spot_count
            
            if maintenance_count > 0:
                self._db.query(MaintenancePlan).filter(MaintenancePlan.project_id == project_id).delete(synchronize_session=False)
                deleted_counts['maintenance_plan'] = maintenance_count
            
            self._db.commit()
        
        if operator_name and project_info.id:
            self._create_operation_log(
                work_order_type='project_info',
                work_order_id=project_info.id,
                work_order_no=project_info.project_id,
                operator_name=operator_name,
                operator_id=user_id,
                operation_type='delete',
                operation_type_name='删除',
                remark=f'删除项目信息 {project_info.project_name}'
            )
        
        self.repository.delete(project_info)
        
        return {
            'project_name': project_info.project_name,
            'deleted_related': deleted_counts
        }
    
    def get_all_unpaginated(self, project_ids: Optional[List[str]] = None) -> List[ProjectInfo]:
        """
        获取所有项目信息（不分页）
        
        Args:
            project_ids: 项目ID列表（权限过滤）
            
        Returns:
            项目信息列表
        """
        return self.repository.find_all_unpaginated(project_ids)
    
    def get_user_project_ids(self, user_name: str) -> List[str]:
        """
        获取用户关联的项目ID列表（通过项目运维人员字段关联）
        
        Args:
            user_name: 用户名
            
        Returns:
            项目ID列表
        """
        projects = self._db.query(ProjectInfo.project_id).filter(
            ProjectInfo.project_manager == user_name
        ).all()
        project_ids = [p[0] for p in projects if p[0]]
        return project_ids if project_ids else []
