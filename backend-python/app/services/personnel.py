from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.personnel import Personnel
from app.models.online_user import OnlineUser
from app.models.project_info import ProjectInfo
from app.models.maintenance_plan import MaintenancePlan
from app.models.work_plan import WorkPlan
from app.models.periodic_inspection import PeriodicInspection
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork
from app.repositories.personnel import PersonnelRepository
from app.schemas.personnel import PersonnelCreate, PersonnelUpdate


# TODO: 后续考虑加入人员权限校验
# FIXME: 删除人员时应该检查是否有关联的工单
class PersonnelService:
    """
    人员管理服务类
    提供人员的增删改查等业务逻辑处理
    """
    
    def __init__(self, db: Session):
        """
        初始化人员服务
        @param db: 数据库会话对象
        """
        self.repository = PersonnelRepository(db)
    
    def get_all(
        self, 
        page: int = 0, 
        size: int = 10, 
        name: Optional[str] = None,
        department: Optional[str] = None,
        current_user_role: Optional[str] = None,
        current_user_department: Optional[str] = None
    ) -> tuple[List[Personnel], int]:
        """
        分页获取人员列表
        @param page: 页码，从0开始
        @param size: 每页大小
        @param name: 姓名模糊查询条件
        @param department: 部门筛选条件
        @param current_user_role: 当前用户角色，用于权限控制
        @param current_user_department: 当前用户部门，用于权限控制
        @return: (人员列表, 总数) 元组
        """
        return self.repository.find_all(
            page, size, name, department, 
            current_user_role, current_user_department
        )
    
    def get_by_id(self, id: int) -> Personnel:
        """
        根据ID获取人员信息
        @param id: 人员ID
        @return: 人员对象
        @raises HTTPException: 人员不存在时抛出404异常
        """
        personnel = self.repository.find_by_id(id)
        if not personnel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="人员不存在"
            )
        return personnel
    
    def create(self, dto: PersonnelCreate) -> Personnel:
        """
        创建新人员
        @param dto: 人员创建数据传输对象
        @return: 创建成功的人员对象
        """
        personnel = Personnel(
            name=dto.name,
            gender=dto.gender,
            phone=dto.phone,
            department=dto.department,
            role=dto.role,
            address=dto.address,
            remarks=dto.remarks
        )
        
        return self.repository.create(personnel)
    
    def update(self, id: int, dto: PersonnelUpdate) -> Personnel:
        """
        更新人员信息
        同时同步更新在线用户表和所有关联表中的相关信息
        @param id: 人员ID
        @param dto: 人员更新数据传输对象
        @return: 更新后的人员对象
        """
        existing_personnel = self.get_by_id(id)
        old_name = existing_personnel.name
        new_name = dto.name
        
        existing_personnel.name = dto.name
        existing_personnel.gender = dto.gender
        existing_personnel.phone = dto.phone
        existing_personnel.department = dto.department
        existing_personnel.role = dto.role
        existing_personnel.address = dto.address
        existing_personnel.remarks = dto.remarks
        
        result = self.repository.update(existing_personnel)
        
        self._sync_online_user_info(id, dto.name, dto.department, dto.role)
        
        if old_name != new_name:
            self._sync_personnel_name_to_all_tables(old_name, new_name)
        
        return result
    
    def _sync_personnel_name_to_all_tables(self, old_name: str, new_name: str) -> None:
        """
        同步更新所有关联表中的人员姓名
        @param old_name: 原姓名
        @param new_name: 新姓名
        """
        db = self.repository.db
        updated_count = 0
        
        project_infos = db.query(ProjectInfo).filter(
            ProjectInfo.project_manager == old_name
        ).all()
        for project in project_infos:
            project.project_manager = new_name
            updated_count += 1
        
        maintenance_plans = db.query(MaintenancePlan).filter(
            MaintenancePlan.maintenance_personnel == old_name
        ).all()
        for plan in maintenance_plans:
            plan.maintenance_personnel = new_name
            updated_count += 1
        
        work_plans = db.query(WorkPlan).filter(
            WorkPlan.maintenance_personnel == old_name
        ).all()
        for plan in work_plans:
            plan.maintenance_personnel = new_name
            updated_count += 1
        
        periodic_inspections = db.query(PeriodicInspection).filter(
            PeriodicInspection.maintenance_personnel == old_name
        ).all()
        for inspection in periodic_inspections:
            inspection.maintenance_personnel = new_name
            updated_count += 1
        
        temporary_repairs = db.query(TemporaryRepair).filter(
            TemporaryRepair.maintenance_personnel == old_name
        ).all()
        for repair in temporary_repairs:
            repair.maintenance_personnel = new_name
            updated_count += 1
        
        spot_works = db.query(SpotWork).filter(
            SpotWork.maintenance_personnel == old_name
        ).all()
        for work in spot_works:
            work.maintenance_personnel = new_name
            updated_count += 1
        
        if updated_count > 0:
            db.commit()
            print(f"[PersonnelService] 同步更新人员姓名: '{old_name}' -> '{new_name}', 共更新 {updated_count} 条记录")
    
    def _sync_online_user_info(self, user_id: int, name: str, department: str, role: str) -> None:
        """
        同步更新在线用户表中的用户信息
        @param user_id: 用户ID
        @param name: 用户姓名
        @param department: 部门
        @param role: 角色
        """
        online_users = self.repository.db.query(OnlineUser).filter(
            OnlineUser.user_id == user_id,
            OnlineUser.is_active == True
        ).all()
        
        for online_user in online_users:
            online_user.user_name = name
            online_user.department = department
            online_user.role = role
        
        if online_users:
            self.repository.db.commit()
    
    def delete(self, id: int) -> None:
        """
        删除人员
        同时将在线用户表中的该用户标记为离线
        @param id: 人员ID
        """
        personnel = self.get_by_id(id)
        
        self._set_online_user_offline(id)
        
        self.repository.delete(personnel)
    
    def _set_online_user_offline(self, user_id: int) -> None:
        """
        将在线用户表中的用户标记为离线
        @param user_id: 用户ID
        """
        online_users = self.repository.db.query(OnlineUser).filter(
            OnlineUser.user_id == user_id,
            OnlineUser.is_active == True
        ).all()
        
        for online_user in online_users:
            online_user.is_active = False
        
        if online_users:
            self.repository.db.commit()
    
    def get_all_unpaginated(self) -> List[Personnel]:
        """
        获取所有人员（不分页）
        @return: 所有人员列表
        """
        return self.repository.find_all_unpaginated()
    
    def validate_personnel_exists(self, name: str) -> bool:
        """
        验证人员姓名是否存在于personnel表中
        @param name: 人员姓名
        @return: 存在返回True，否则返回False
        """
        return self.repository.find_by_name(name) is not None
    
    def get_all_names(self) -> List[str]:
        """
        获取所有人员姓名列表
        @return: 人员姓名列表
        """
        personnel_list = self.repository.find_all_unpaginated()
        return [p.name for p in personnel_list]
