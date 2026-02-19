from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.repair_tools import RepairToolsStock, RepairToolsIssue
from app.models.project_info import ProjectInfo
from app.models.personnel import Personnel
from app.models.work_plan import WorkPlan
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
from app.auth import get_current_user, get_current_user_from_headers

router = APIRouter(prefix="/repair-tools", tags=["维修工具管理"])


@router.get("/personnel-projects", summary="获取人员与项目的关联关系")
async def get_personnel_projects(
    personnel_id: Optional[int] = Query(None, description="人员ID"),
    project_id: Optional[str] = Query(None, description="项目编号"),
    db: Session = Depends(get_db)
):
    result = []
    
    if personnel_id:
        person = db.query(Personnel).filter(Personnel.id == personnel_id).first()
        if person:
            work_plans = db.query(WorkPlan).filter(
                WorkPlan.maintenance_personnel == person.name
            ).all()
            
            for plan in work_plans:
                project = db.query(ProjectInfo).filter(
                    ProjectInfo.project_id == plan.project_id
                ).first()
                if project:
                    result.append({
                        'project_id': project.project_id,
                        'project_name': project.project_name
                    })
    
    elif project_id:
        work_plans = db.query(WorkPlan).filter(
            WorkPlan.project_id == project_id
        ).all()
        
        for plan in work_plans:
            if plan.maintenance_personnel:
                person = db.query(Personnel).filter(
                    Personnel.name == plan.maintenance_personnel,
                    Personnel.role == '运维人员'
                ).first()
                if person:
                    if not any(p['id'] == person.id for p in result):
                        result.append({
                            'id': person.id,
                            'name': person.name
                        })
    
    else:
        work_plans = db.query(WorkPlan).all()
        personnel_projects = {}
        
        for plan in work_plans:
            if plan.maintenance_personnel and plan.project_id:
                person = db.query(Personnel).filter(
                    Personnel.name == plan.maintenance_personnel,
                    Personnel.role == '运维人员'
                ).first()
                
                if person:
                    if person.id not in personnel_projects:
                        personnel_projects[person.id] = {
                            'personnel_id': person.id,
                            'personnel_name': person.name,
                            'projects': []
                        }
                    
                    project = db.query(ProjectInfo).filter(
                        ProjectInfo.project_id == plan.project_id
                    ).first()
                    
                    if project:
                        if not any(p['project_id'] == project.project_id for p in personnel_projects[person.id]['projects']):
                            personnel_projects[person.id]['projects'].append({
                                'project_id': project.project_id,
                                'project_name': project.project_name
                            })
        
        result = list(personnel_projects.values())
    
    return ApiResponse(code=200, message="success", data=result)


@router.get("/tools/search", summary="模糊搜索工具")
async def search_tools(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(0, ge=0, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    query = db.query(RepairToolsStock).filter(RepairToolsStock.stock > 0)
    
    if keyword:
        query = query.filter(
            or_(
                RepairToolsStock.tool_name.ilike(f"%{keyword}%"),
                RepairToolsStock.tool_id.ilike(f"%{keyword}%"),
                RepairToolsStock.specification.ilike(f"%{keyword}%"),
                RepairToolsStock.category.ilike(f"%{keyword}%")
            )
        )
    
    total = query.count()
    items = query.order_by(RepairToolsStock.tool_name).offset(page * size).limit(size).all()
    
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


@router.get("/stock", summary="获取维修工具库存列表")
async def get_stock_list(
    page: int = Query(0, ge=0, description="页码"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
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
    
    return ApiResponse(code=200, data=stock.to_dict(), message="新增成功")


@router.get("/stock/{stock_id}", summary="获取维修工具详情")
async def get_stock_detail(
    stock_id: int,
    db: Session = Depends(get_db)
):
    stock = db.query(RepairToolsStock).filter(RepairToolsStock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="工具不存在")
    
    return ApiResponse(code=200, data=stock.to_dict())


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
    
    return ApiResponse(code=200, data=stock.to_dict(), message="更新成功")


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
    
    return ApiResponse(code=200, data=stock.to_dict(), message="入库成功")


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
    
    return ApiResponse(code=200, message="删除成功")


@router.get("/issue", summary="获取维修工具领用记录列表")
async def get_issue_list(
    request: Request,
    page: int = Query(0, ge=0, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    tool_name: Optional[str] = Query(None, description="工具名称"),
    user_name: Optional[str] = Query(None, description="运维人员"),
    status: Optional[str] = Query(None, description="状态"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    user_info = current_user or get_current_user_from_headers(request)
    current_user_name = None
    is_manager = False
    if user_info:
        current_user_name = user_info.get('sub') or user_info.get('name')
        role = user_info.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管', '物料管理员', '材料员']
    
    query = db.query(RepairToolsIssue)
    
    if tool_name:
        query = query.filter(RepairToolsIssue.tool_name.ilike(f"%{tool_name}%"))
    
    if not is_manager and current_user_name:
        query = query.filter(RepairToolsIssue.user_name == current_user_name)
    elif user_name:
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
    tool_name = data.tool_name
    specification = data.specification
    
    if data.tool_id:
        if data.tool_id.isdigit():
            stock = db.query(RepairToolsStock).filter(RepairToolsStock.id == int(data.tool_id)).first()
        else:
            stock = db.query(RepairToolsStock).filter(RepairToolsStock.tool_id == data.tool_id).first()
        
        if stock:
            if stock.stock < data.quantity:
                raise HTTPException(status_code=400, detail="库存不足")
            stock.stock -= data.quantity
            if not tool_name:
                tool_name = stock.tool_name
            if not specification:
                specification = stock.specification
    
    user_name = data.user_name
    if data.user_id and not user_name:
        user = db.query(Personnel).filter(Personnel.id == data.user_id).first()
        if user:
            user_name = user.name
    
    project_name = data.project_name
    if data.project_id and not project_name:
        project = db.query(ProjectInfo).filter(ProjectInfo.project_id == data.project_id).first()
        if project:
            project_name = project.project_name
    
    if not tool_name:
        raise HTTPException(status_code=400, detail="请选择工具")
    if not user_name:
        raise HTTPException(status_code=400, detail="请选择运维人员")
    
    issue = RepairToolsIssue(
        tool_id=data.tool_id,
        tool_name=tool_name,
        specification=specification or '',
        quantity=data.quantity,
        return_quantity=0,
        user_id=data.user_id,
        user_name=user_name,
        issue_time=datetime.now(),
        project_id=data.project_id,
        project_name=project_name,
        status="待归还",
        remark=data.remark,
        stock_id=stock.id if stock else None
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    
    return ApiResponse(code=200, data=issue.to_dict(), message="领用成功")


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
    
    return ApiResponse(code=200, data=issue.to_dict(), message="归还成功")


@router.get("/issue/{issue_id}", summary="获取领用记录详情")
async def get_issue_detail(
    issue_id: int,
    db: Session = Depends(get_db)
):
    issue = db.query(RepairToolsIssue).filter(RepairToolsIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="领用记录不存在")
    
    return ApiResponse(code=200, data=issue.to_dict())
