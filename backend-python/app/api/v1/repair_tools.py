from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.repair_tools import RepairToolsStock, RepairToolsIssue
from app.schemas.repair_tools import (
    RepairToolsStockCreate,
    RepairToolsStockUpdate,
    RepairToolsRestock,
    RepairToolsIssueCreate,
    RepairToolsReturn,
    RepairToolsStockResponse,
    RepairToolsIssueResponse
)
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/repair-tools", tags=["维修工具管理"])


@router.get("/stock", summary="获取维修工具库存列表")
async def get_stock_list(
    page: int = Query(0, ge=0, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    tool_name: Optional[str] = Query(None, description="工具名称"),
    category: Optional[str] = Query(None, description="工具分类"),
    db: Session = Depends(get_db)
):
    query = db.query(RepairToolsStock)
    
    if tool_name:
        query = query.filter(RepairToolsStock.tool_name.ilike(f"%{tool_name}%"))
    if category:
        query = query.filter(RepairToolsStock.category == category)
    
    total = query.count()
    items = query.order_by(RepairToolsStock.updated_at.desc()).offset(page * size).limit(size).all()
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            'items': [item.to_dict() for item in items],
            'total': total,
            'page': page,
            'size': size
        }
    )


@router.post("/stock", summary="新增维修工具入库")
async def create_stock(
    data: RepairToolsStockCreate,
    db: Session = Depends(get_db)
):
    stock = RepairToolsStock(
        tool_name=data.tool_name,
        category=data.category,
        specification=data.specification,
        unit=data.unit,
        stock=data.stock,
        min_stock=data.min_stock,
        location=data.location,
        remark=data.remark
    )
    db.add(stock)
    db.commit()
    db.refresh(stock)
    
    return ApiResponse(data=stock.to_dict(), message="新增成功")


@router.get("/stock/{stock_id}", summary="获取维修工具详情")
async def get_stock_detail(
    stock_id: int,
    db: Session = Depends(get_db)
):
    stock = db.query(RepairToolsStock).filter(RepairToolsStock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="工具不存在")
    
    return ApiResponse(data=stock.to_dict())


@router.put("/stock/{stock_id}", summary="更新维修工具信息")
async def update_stock(
    stock_id: int,
    data: RepairToolsStockUpdate,
    db: Session = Depends(get_db)
):
    stock = db.query(RepairToolsStock).filter(RepairToolsStock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="工具不存在")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(stock, key, value)
    
    db.commit()
    db.refresh(stock)
    
    return ApiResponse(data=stock.to_dict(), message="更新成功")


@router.post("/stock/{stock_id}/restock", summary="工具入库（增加库存）")
async def restock_tool(
    stock_id: int,
    data: RepairToolsRestock,
    db: Session = Depends(get_db)
):
    stock = db.query(RepairToolsStock).filter(RepairToolsStock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="工具不存在")
    
    stock.stock += data.quantity
    db.commit()
    db.refresh(stock)
    
    return ApiResponse(data=stock.to_dict(), message="入库成功")


@router.delete("/stock/{stock_id}", summary="删除维修工具")
async def delete_stock(
    stock_id: int,
    db: Session = Depends(get_db)
):
    stock = db.query(RepairToolsStock).filter(RepairToolsStock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="工具不存在")
    
    db.delete(stock)
    db.commit()
    
    return ApiResponse(message="删除成功")


@router.get("/issue", summary="获取维修工具领用记录列表")
async def get_issue_list(
    page: int = Query(0, ge=0, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    tool_name: Optional[str] = Query(None, description="工具名称"),
    user_name: Optional[str] = Query(None, description="领用人"),
    status: Optional[str] = Query(None, description="状态"),
    db: Session = Depends(get_db)
):
    query = db.query(RepairToolsIssue)
    
    if tool_name:
        query = query.filter(RepairToolsIssue.tool_name.ilike(f"%{tool_name}%"))
    if user_name:
        query = query.filter(RepairToolsIssue.user_name.ilike(f"%{user_name}%"))
    if status:
        query = query.filter(RepairToolsIssue.status == status)
    
    total = query.count()
    items = query.order_by(RepairToolsIssue.issue_time.desc()).offset(page * size).limit(size).all()
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            'items': [item.to_dict() for item in items],
            'total': total,
            'page': page,
            'size': size
        }
    )


@router.post("/issue", summary="新增工具领用")
async def create_issue(
    data: RepairToolsIssueCreate,
    db: Session = Depends(get_db)
):
    stock = None
    if data.tool_id and data.tool_id.isdigit():
        stock = db.query(RepairToolsStock).filter(RepairToolsStock.id == int(data.tool_id)).first()
    
    if stock:
        if stock.stock < data.quantity:
            raise HTTPException(status_code=400, detail="库存不足")
        stock.stock -= data.quantity
    
    issue = RepairToolsIssue(
        tool_id=data.tool_id,
        tool_name=data.tool_name,
        specification=data.specification or (stock.specification if stock else ''),
        quantity=data.quantity,
        return_quantity=0,
        user_id=data.user_id,
        user_name=data.user_name,
        issue_time=datetime.now(),
        project_id=data.project_id,
        project_name=data.project_name,
        status="待归还",
        remark=data.remark,
        stock_id=stock.id if stock else None
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    
    return ApiResponse(data=issue.to_dict(), message="领用成功")


@router.put("/issue/{issue_id}/return", summary="工具归还")
async def return_tool(
    issue_id: int,
    data: RepairToolsReturn,
    db: Session = Depends(get_db)
):
    issue = db.query(RepairToolsIssue).filter(RepairToolsIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="领用记录不存在")
    
    if issue.status == "已归还":
        raise HTTPException(status_code=400, detail="该工具已归还")
    
    if data.return_quantity > issue.quantity - (issue.return_quantity or 0):
        raise HTTPException(status_code=400, detail="归还数量超过领用数量")
    
    issue.return_quantity = (issue.return_quantity or 0) + data.return_quantity
    issue.return_time = datetime.now()
    
    if issue.return_quantity >= issue.quantity:
        issue.status = "已归还"
    
    if issue.stock_id:
        stock = db.query(RepairToolsStock).filter(RepairToolsStock.id == issue.stock_id).first()
        if stock:
            stock.stock += data.return_quantity
    
    db.commit()
    db.refresh(issue)
    
    return ApiResponse(data=issue.to_dict(), message="归还成功")


@router.get("/issue/{issue_id}", summary="获取领用记录详情")
async def get_issue_detail(
    issue_id: int,
    db: Session = Depends(get_db)
):
    issue = db.query(RepairToolsIssue).filter(RepairToolsIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="领用记录不存在")
    
    return ApiResponse(data=issue.to_dict())
