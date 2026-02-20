from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.customer import CustomerService
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
from app.schemas.common import ApiResponse
from app.auth import get_current_user

router = APIRouter(prefix="/customer", tags=["customer"])

@router.get("", response_model=ApiResponse[CustomerListResponse])
def get_customers(
    page: int = Query(0, ge=0, description="页码"),
    size: int = Query(10, ge=1, le=2000, description="每页数量"),
    name: Optional[str] = Query(None, description="客户名称"),
    contact_person: Optional[str] = Query(None, description="联系人"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    service = CustomerService(db)
    
    user_name = None
    is_manager = False
    client_names = None
    
    if current_user:
        user_name = current_user.get('sub') or current_user.get('name')
        role = current_user.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
        
        if not is_manager and user_name:
            client_names = service.get_user_client_names(user_name)
    
    result = service.get_list(page=page, size=size, name=name, contact_person=contact_person, client_names=client_names)
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
    db: Session = Depends(get_db)
):
    service = CustomerService(db)
    result = service.delete(customer_id)
    return ApiResponse(code=200, message="删除成功", data=None)
