from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.personnel import Personnel
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
        @param id: 人员ID
        @param dto: 人员更新数据传输对象
        @return: 更新后的人员对象
        """
        existing_personnel = self.get_by_id(id)
        
        existing_personnel.name = dto.name
        existing_personnel.gender = dto.gender
        existing_personnel.phone = dto.phone
        existing_personnel.department = dto.department
        existing_personnel.role = dto.role
        existing_personnel.address = dto.address
        existing_personnel.remarks = dto.remarks
        
        return self.repository.update(existing_personnel)
    
    def delete(self, id: int) -> None:
        """
        删除人员
        @param id: 人员ID
        """
        # TODO: 删除前应该检查该人员是否有未完成的工单
        personnel = self.get_by_id(id)
        self.repository.delete(personnel)
    
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
