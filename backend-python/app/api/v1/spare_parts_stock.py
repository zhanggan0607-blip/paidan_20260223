from app.utils.logging_config import get_logger
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_current_user_required, get_material_manager_user
from app.exceptions import BusinessException, ValidationException
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.spare_parts_stock import SparePartsInboundCreate, SparePartsInboundUpdate
from app.services.spare_parts_stock import SparePartsStockService

logger = get_logger(__name__)

router = APIRouter(prefix="/spare-parts-stock", tags=["Spare Parts Stock Management"])


@router.post("/inbound", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_inbound(
    data: SparePartsInboundCreate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_material_manager_user)
):
    service = SparePartsStockService(db)
    try:
        result = service.create_inbound(data.model_dump(), user_info)
        return ApiResponse(code=200, message="入库单创建成功", data=result)
    except (ValidationException, BusinessException):
        raise
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 创建入库单失败: {str(e)}")
        raise BusinessException(f"入库操作失败，错误ID: {error_id}，请联系管理员") from None


@router.get("/inbound-records", response_model=ApiResponse)
def get_inbound_records(
    product: str | None = Query(None, description="产品名称"),
    user: str | None = Query(None, description="入库人"),
    page: int = Query(0, ge=0, description="页码，从0开始"),
    pageSize: int = Query(10, ge=1, le=1000, description="每页数量"),
    db: Session = Depends(get_db)
):
    service = SparePartsStockService(db)
    result = service.get_inbound_records(product, user, page, pageSize)
    return PaginatedResponse.success(result['items'], result['total'], page, pageSize)


@router.get("/stock", response_model=ApiResponse)
def get_stock(
    product_name: str | None = Query(None, description="产品名称"),
    db: Session = Depends(get_db)
):
    service = SparePartsStockService(db)
    result = service.get_stock(product_name)
    return PaginatedResponse.success(result['items'], result['total'], 0, len(result['items']) if result['items'] else 1)


@router.get("/products", response_model=ApiResponse)
def get_products(
    product_name: str | None = Query(None, description="产品名称"),
    db: Session = Depends(get_db)
):
    service = SparePartsStockService(db)
    result = service.get_products(product_name)
    return ApiResponse(code=200, message="success", data=result)


@router.put("/inbound/{inbound_id}", response_model=ApiResponse)
def update_inbound(
    inbound_id: int,
    data: SparePartsInboundUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_material_manager_user)
):
    service = SparePartsStockService(db)
    try:
        result = service.update_inbound(inbound_id, data.model_dump(exclude_none=True), user_info)
        return ApiResponse(code=200, message="入库记录更新成功", data={'inboundNo': result.get('inbound_no')})
    except (ValidationException, BusinessException):
        raise
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 更新入库记录失败: {str(e)}")
        raise BusinessException(f"更新操作失败，错误ID: {error_id}，请联系管理员") from None


@router.delete("/inbound/{inbound_id}", response_model=ApiResponse)
def delete_inbound(
    inbound_id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_material_manager_user)
):
    service = SparePartsStockService(db)
    try:
        service.delete_inbound(inbound_id, user_info)
        return ApiResponse(code=200, message="入库记录删除成功")
    except (ValidationException, BusinessException):
        raise
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 删除入库记录失败: {str(e)}")
        raise BusinessException(f"删除操作失败，错误ID: {error_id}，请联系管理员") from None
