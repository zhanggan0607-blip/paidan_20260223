from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.customer import CustomerService
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/customer", tags=["customer"])

@router.get("", response_model=ApiResponse[CustomerListResponse])
def get_customers(
    page: int = Query(0, ge=0, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: Optional[str] = Query(None, description="客户名称"),
    contact_person: Optional[str] = Query(None, description="联系人"),
    db: Session = Depends(get_db)
):
    service = CustomerService(db)
    result = service.get_list(page=page, size=size, name=name, contact_person=contact_person)
    return ApiResponse(code=200, message="success", data=result)

@router.get("/{customer_id}", response_model=ApiResponse[CustomerResponse])
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    service = CustomerService(db)
    result = service.get_by_id(customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="客户不存在")
    return ApiResponse(code=200, message="success", data=result)

@router.post("", response_model=ApiResponse[CustomerResponse])
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    service = CustomerService(db)
    result = service.create(customer)
    return ApiResponse(code=200, message="创建成功", data=result)

@router.put("/{customer_id}", response_model=ApiResponse[CustomerResponse])
def update_customer(customer_id: int, customer: CustomerUpdate, db: Session = Depends(get_db)):
    service = CustomerService(db)
    result = service.update(customer_id, customer)
    if not result:
        raise HTTPException(status_code=404, detail="客户不存在")
    return ApiResponse(code=200, message="更新成功", data=result)

@router.delete("/{customer_id}", response_model=ApiResponse[None])
def delete_customer(
    customer_id: int,
    cascade: bool = Query(False, description="是否级联删除关联数据"),
    db: Session = Depends(get_db)
):
    service = CustomerService(db)
    result = service.delete(customer_id, cascade=cascade)
    
    if result.get('deleted_related'):
        deleted_info = []
        for key, count in result['deleted_related'].items():
            name_map = {
                'project': '项目',
                'work_plan': '工作计划',
                'periodic_inspection': '定期巡检',
                'temporary_repair': '临时维修',
                'spot_work': '零星用工',
                'maintenance_plan': '维保计划'
            }
            deleted_info.append(f"{count} 条{name_map.get(key, key)}")
        message = f"已删除客户【{result['customer_name']}】及其关联的 {', '.join(deleted_info)}"
    else:
        message = "删除成功"
    
    return ApiResponse(code=200, message=message, data=None)
