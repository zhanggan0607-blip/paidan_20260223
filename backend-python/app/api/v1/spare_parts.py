"""
备品备件管理API接口
包含备品备件领用、归还等功能
"""
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_current_user_info, get_material_manager_user
from app.models.project_info import ProjectInfo
from app.models.spare_parts_stock import SparePartsStock
from app.models.spare_parts_usage import SparePartsUsage
from app.schemas.common import ApiResponse
from app.services.spare_parts_usage import SparePartsUsageService

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/spare-parts", tags=["Spare Parts Management"])


class SparePartsUsageCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    brand: str | None = Field(None, max_length=100, description="品牌")
    model: str | None = Field(None, max_length=100, description="产品型号")
    quantity: int = Field(..., gt=0, description="领用数量")
    user_name: str = Field(..., min_length=1, max_length=100, description="运维人员")
    issue_time: str | datetime = Field(..., description="领用时间")
    unit: str = Field("件", max_length=20, description="单位")
    project_id: str | None = Field(None, max_length=50, description="项目编号")
    project_name: str | None = Field(None, max_length=200, description="项目名称")
    remark: str | None = Field(None, max_length=500, description="备注")


class SparePartsReturn(BaseModel):
    return_quantity: int = Field(..., gt=0, description="归还数量")
    remark: str | None = Field(None, max_length=500, description="备注")


class SparePartsStockCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    brand: str | None = Field(None, max_length=100, description="品牌")
    model: str | None = Field(None, max_length=100, description="产品型号")
    quantity: int = Field(..., ge=0, description="库存数量")
    unit: str = Field("件", max_length=20, description="单位")
    remark: str | None = Field(None, max_length=500, description="备注")


def _parse_issue_time(issue_time: str | datetime) -> datetime:
    """
    解析领用时间

    Args:
        issue_time: 时间字符串或datetime对象

    Returns:
        datetime对象
    """
    if isinstance(issue_time, datetime):
        return issue_time

    try:
        return datetime.fromisoformat(issue_time.replace('Z', '+00:00'))
    except ValueError:
        try:
            return datetime.strptime(issue_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.strptime(issue_time, '%Y-%m-%d')


@router.post("/usage", response_model=ApiResponse)
def create_spare_parts_usage(
    request: Request,
    data: SparePartsUsageCreate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user_info)
):
    """
    创建备品备件领用记录

    - 必须先有库存记录才能领用
    - 领用时会自动扣减库存

    需要登录认证
    """
    if not current_user.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已过期"
        )
    logger.info(f"用户 {current_user.name} 创建备品备件领用记录: {data}")

    try:
        issue_time = _parse_issue_time(data.issue_time)

        stock = db.query(SparePartsStock).filter(
            SparePartsStock.product_name == data.product_name,
            SparePartsStock.brand == (data.brand or ''),
            SparePartsStock.model == (data.model or '')
        ).first()

        if not stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"库存中不存在该备件【{data.product_name}】，请先入库后再领用"
            )

        if stock.stock <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"库存不足，当前库存: {stock.stock} {stock.unit}，请先补充库存"
            )

        if stock.stock < data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"库存不足，当前库存: {stock.stock} {stock.unit}，请先补充库存"
            )

        stock.stock -= data.quantity
        stock_id = stock.id
        logger.info(f"扣减库存: stock_id={stock_id}, 剩余数量={stock.stock}")

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
                'stock_id': stock_id,
                'has_stock': True
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 创建备品备件领用记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"领用失败，错误ID: {error_id}，请联系管理员"
        ) from None


@router.post("/stock", response_model=ApiResponse)
def create_spare_parts_stock(
    request: Request,
    data: SparePartsStockCreate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_material_manager_user)
):
    """
    创建或更新备品备件库存

    如果库存中已存在相同品名、品牌、型号的备件，则更新库存数量
    否则创建新的库存记录

    需要管理员、部门经理或材料员权限
    """
    logger.info(f"用户 {current_user.name} 创建/更新备品备件库存: {data}")

    try:
        stock = db.query(SparePartsStock).filter(
            SparePartsStock.product_name == data.product_name,
            SparePartsStock.brand == (data.brand or ''),
            SparePartsStock.model == (data.model or '')
        ).first()

        if stock:
            stock.stock = data.quantity
            stock.unit = data.unit
            if data.remark:
                stock.remark = data.remark
            stock.updated_at = datetime.now()
            logger.info(f"更新库存: id={stock.id}, 数量={data.quantity}")
        else:
            stock = SparePartsStock(
                product_name=data.product_name,
                brand=data.brand or '',
                model=data.model or '',
                stock=data.quantity,
                unit=data.unit,
                remark=data.remark
            )
            db.add(stock)
            logger.info(f"创建库存: {data.product_name}")

        db.commit()
        db.refresh(stock)

        return ApiResponse(
            code=200,
            message="库存创建/更新成功",
            data={
                'id': stock.id,
                'product_name': stock.product_name,
                'brand': stock.brand,
                'model': stock.model,
                'quantity': stock.stock,
                'unit': stock.unit
            }
        )
    except Exception as e:
        db.rollback()
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 创建/更新备品备件库存失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"操作失败，错误ID: {error_id}，请联系管理员"
        ) from None


@router.get("/usage", response_model=ApiResponse)
def get_spare_parts_usage(
    request: Request,
    user: str | None = Query(None, description="运维人员"),
    product: str | None = Query(None, description="产品名称"),
    project: str | None = Query(None, description="项目名称"),
    status_filter: str | None = Query(None, alias="status", description="状态"),
    page: int = Query(0, ge=0, description="页码，从0开始"),
    pageSize: int = Query(10, ge=1, le=1000, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user_info)
):
    """
    查询备品备件领用记录

    - 管理员可以查看所有记录
    - 普通用户只能查看自己的记录

    需要登录认证
    """
    if not current_user.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已过期"
        )

    logger.info(f"查询备品备件领用记录: user={user}, product={product}, project={project}, status={status_filter}")

    query_user = user
    if not current_user.is_manager:
        query_user = current_user.name

    service = SparePartsUsageService(db)
    items, total = service.get_all(
        page=page,
        size=pageSize,
        user=query_user,
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
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user_info)
):
    """
    获取领用记录详情

    需要登录认证
    """
    if not current_user.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已过期"
        )

    usage = db.query(SparePartsUsage).filter(SparePartsUsage.id == usage_id).first()
    if not usage:
        raise HTTPException(status_code=404, detail="领用记录不存在")

    if not current_user.is_manager and usage.user_name != current_user.name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此记录"
        )

    return ApiResponse(code=200, data=usage.to_dict())


@router.put("/usage/{usage_id}/return", response_model=ApiResponse)
def return_spare_parts(
    usage_id: int,
    data: SparePartsReturn,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user_info)
):
    """
    备品备件归还

    - 如果领用时有库存记录（stock_id不为空），归还时会自动回补库存
    - 如果领用时没有库存记录（stock_id为空），归还时不会回补库存

    需要登录认证
    """
    if not current_user.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已过期"
        )

    logger.info(f"用户 {current_user.name} 备品备件归还: usage_id={usage_id}, data={data}")

    usage = db.query(SparePartsUsage).filter(SparePartsUsage.id == usage_id).first()
    if not usage:
        raise HTTPException(status_code=404, detail="领用记录不存在")

    if not current_user.is_manager and usage.user_name != current_user.name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此记录"
        )

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
                stock.stock += data.return_quantity
                logger.info(f"回补库存: stock_id={stock.id}, 增加数量={data.return_quantity}, 当前库存={stock.stock}")
            else:
                logger.warning(f"领用记录 {usage_id} 关联的库存记录(stock_id={usage.stock_id})不存在，无法回补库存")
        else:
            logger.warning(f"领用记录 {usage_id} 没有关联库存记录，无法回补库存")

        db.commit()
        db.refresh(usage)

        logger.info(f"备品备件归还成功: id={usage.id}, return_quantity={data.return_quantity}")

        return ApiResponse(code=200, data=usage.to_dict(), message="归还成功")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 备品备件归还失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"归还失败，错误ID: {error_id}，请联系管理员") from None
