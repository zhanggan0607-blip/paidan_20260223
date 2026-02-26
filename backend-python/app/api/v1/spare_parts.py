from typing import List, Optional, Union
from fastapi import APIRouter, Depends, Query, status, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime
from app.database import get_db
from app.schemas.common import ApiResponse
from app.models.spare_parts_usage import SparePartsUsage
from app.models.spare_parts_stock import SparePartsStock
from app.models.project_info import ProjectInfo
from app.services.spare_parts_usage import SparePartsUsageService
from app.auth import get_current_user, get_current_user_from_headers
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/spare-parts", tags=["Spare Parts Management"])


class SparePartsUsageCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    model: Optional[str] = Field(None, max_length=100, description="产品型号")
    quantity: int = Field(..., gt=0, description="领用数量")
    user_name: str = Field(..., min_length=1, max_length=100, description="运维人员员")
    issue_time: Union[str, datetime] = Field(..., description="领用时间")
    unit: str = Field("件", max_length=20, description="单位")
    project_id: Optional[str] = Field(None, max_length=50, description="项目编号")
    project_name: Optional[str] = Field(None, max_length=200, description="项目名称")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class SparePartsReturn(BaseModel):
    return_quantity: int = Field(..., gt=0, description="归还数量")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


@router.post("/usage", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_spare_parts_usage(
    data: SparePartsUsageCreate,
    db: Session = Depends(get_db)
):
    """创建备品备件领用记录"""
    logger.info(f"创建备品备件领用记录: {data}")
    
    try:
        issue_time = data.issue_time
        if isinstance(issue_time, str):
            try:
                issue_time = datetime.fromisoformat(issue_time.replace('Z', '+00:00'))
            except ValueError:
                try:
                    issue_time = datetime.strptime(issue_time, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    issue_time = datetime.strptime(issue_time, '%Y-%m-%d')
        
        stock = db.query(SparePartsStock).filter(
            SparePartsStock.product_name == data.product_name,
            SparePartsStock.brand == (data.brand or ''),
            SparePartsStock.model == (data.model or '')
        ).first()
        
        stock_id = None
        if stock:
            if stock.quantity < data.quantity:
                return ApiResponse(code=400, message=f"库存不足，当前库存: {stock.quantity}", data=None)
            stock.quantity -= data.quantity
            stock_id = stock.id
        
        project_name = data.project_name
        if data.project_id and not project_name:
            project = db.query(ProjectInfo).filter(ProjectInfo.project_id == data.project_id).first()
            if project:
                project_name = project.project_name
        
        usage = SparePartsUsage(
            product_name=data.product_name,
            brand=data.brand or '',
            model=data.model or '',
            quantity=data.quantity,
            return_quantity=0,
            user_name=data.user_name,
            issue_time=issue_time,
            unit=data.unit,
            project_id=data.project_id,
            project_name=project_name,
            stock_id=stock_id,
            status="待归还",
            remark=data.remark
        )
        
        db.add(usage)
        db.commit()
        db.refresh(usage)
        
        logger.info(f"备品备件领用记录创建成功: id={usage.id}, stock_id={stock_id}")
        
        return ApiResponse(
            code=200,
            message="领用成功",
            data={
                'id': usage.id,
                'product_name': usage.product_name,
                'quantity': usage.quantity,
                'user_name': usage.user_name,
                'stock_id': stock_id
            }
        )
    except Exception as e:
        db.rollback()
        logger.error(f"创建备品备件领用记录失败: {str(e)}")
        return ApiResponse(code=500, message=f"领用失败: {str(e)}", data=None)


@router.get("/usage", response_model=ApiResponse)
def get_spare_parts_usage(
    request: Request,
    user: Optional[str] = Query(None, description="运维人员员"),
    product: Optional[str] = Query(None, description="产品名称"),
    project: Optional[str] = Query(None, description="项目名称"),
    status_filter: Optional[str] = Query(None, alias="status", description="状态"),
    page: int = Query(0, ge=0, description="页码，从0开始"),
    pageSize: int = Query(10, ge=1, le=2000, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """查询备品备件领用记录"""
    logger.info(f"查询备品备件领用记录: user={user}, product={product}, project={project}, status={status_filter}, page={page}, pageSize={pageSize}")
    
    user_info = current_user or get_current_user_from_headers(request)
    user_name = None
    is_manager = False
    if user_info:
        user_name = user_info.get('sub') or user_info.get('name')
        role = user_info.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管', '物料管理员', '材料员']
    
    if not is_manager and user_name:
        user = user_name
    
    service = SparePartsUsageService(db)
    items, total = service.get_all(
        page=page, 
        size=pageSize, 
        user=user, 
        product=product, 
        project=project,
        status_filter=status_filter
    )
    
    result_items = []
    for item in items:
        result_items.append({
            'id': item.id,
            'project_id': item.project_id or '',
            'projectName': item.project_name or '',
            'productName': item.product_name,
            'brand': item.brand or '',
            'model': item.model or '',
            'quantity': item.quantity,
            'return_quantity': item.return_quantity or 0,
            'userName': item.user_name,
            'issueTime': item.issue_time,
            'returnTime': item.return_time,
            'unit': item.unit,
            'status': item.status,
            'stock_id': item.stock_id
        })

    logger.info(f"查询成功: 返回{len(result_items)}条记录，总计{total}条")
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            'items': result_items,
            'total': total
        }
    )


@router.get("/usage/{usage_id}", response_model=ApiResponse)
def get_spare_parts_usage_detail(
    usage_id: int,
    db: Session = Depends(get_db)
):
    """获取领用记录详情"""
    usage = db.query(SparePartsUsage).filter(SparePartsUsage.id == usage_id).first()
    if not usage:
        raise HTTPException(status_code=404, detail="领用记录不存在")
    
    return ApiResponse(code=200, data=usage.to_dict())


@router.put("/usage/{usage_id}/return", response_model=ApiResponse)
def return_spare_parts(
    usage_id: int,
    data: SparePartsReturn,
    db: Session = Depends(get_db)
):
    """备品备件归还"""
    logger.info(f"备品备件归还: usage_id={usage_id}, data={data}")
    
    usage = db.query(SparePartsUsage).filter(SparePartsUsage.id == usage_id).first()
    if not usage:
        raise HTTPException(status_code=404, detail="领用记录不存在")
    
    if usage.status == "已归还":
        raise HTTPException(status_code=400, detail="该备品备件已归还")
    
    if data.return_quantity > usage.quantity - (usage.return_quantity or 0):
        raise HTTPException(status_code=400, detail="归还数量超过领用数量")
    
    try:
        usage.return_quantity = (usage.return_quantity or 0) + data.return_quantity
        usage.return_time = datetime.now()
        
        if usage.return_quantity >= usage.quantity:
            usage.status = "已归还"
        
        if data.remark:
            usage.remark = data.remark
        
        if usage.stock_id:
            stock = db.query(SparePartsStock).filter(SparePartsStock.id == usage.stock_id).first()
            if stock:
                stock.quantity += data.return_quantity
        
        db.commit()
        db.refresh(usage)
        
        logger.info(f"备品备件归还成功: id={usage.id}, return_quantity={data.return_quantity}")
        
        return ApiResponse(code=200, data=usage.to_dict(), message="归还成功")
    except Exception as e:
        db.rollback()
        logger.error(f"备品备件归还失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"归还失败: {str(e)}")
