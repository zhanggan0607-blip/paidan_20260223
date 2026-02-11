from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config import get_settings
from app.api.v1 import project_info, maintenance_plan, personnel, periodic_inspection, inspection_item, overdue_alert, temporary_repair, spot_work, spare_parts, spare_parts_stock, statistics
from app.database import Base, engine
from app.exceptions import BusinessException
import logging
import time
import uuid

logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
)

@app.on_event("startup")
async def startup_event():
    """应用启动时创建数据库表"""
    logger.info("正在创建数据库表...")
    try:
        Base.metadata.create_all(bind=engine, checkfirst=False)
        logger.info("数据库表创建成功")
    except Exception as e:
        if "already exists" not in str(e).lower():
            logger.error(f"创建数据库表失败: {str(e)}", exc_info=True)
        else:
            logger.info(f"数据库表或索引已存在，跳过创建")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志中间件"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    request.state.request_id = request_id
    request.state.start_time = start_time
    
    logger.info(f"[{request_id}] {request.method} {request.url.path} - 开始")
    
    try:
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        status_code = response.status_code
        
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"状态码: {status_code}, "
            f"处理时间: {process_time:.2f}ms"
        )
        
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"异常: {str(e)}, "
            f"处理时间: {process_time:.2f}ms"
        )
        raise

app.include_router(project_info.router, prefix=settings.api_prefix)
app.include_router(maintenance_plan.router, prefix=settings.api_prefix)
app.include_router(personnel.router, prefix=settings.api_prefix)
app.include_router(periodic_inspection.router, prefix=settings.api_prefix)
app.include_router(inspection_item.router, prefix=settings.api_prefix)
app.include_router(overdue_alert.router, prefix=settings.api_prefix)
app.include_router(temporary_repair.router, prefix=settings.api_prefix)
app.include_router(spot_work.router, prefix=settings.api_prefix)
app.include_router(spare_parts.router, prefix=settings.api_prefix)
app.include_router(spare_parts_stock.router, prefix=settings.api_prefix)
app.include_router(statistics.router, prefix=settings.api_prefix)
app.include_router(statistics.router, prefix=settings.api_prefix)


@app.get("/")
def read_root():
    return {
        "message": "SSTCP Maintenance System API",
        "version": settings.app_version,
        "docs": settings.docs_url,
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """处理业务异常"""
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail, "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": "参数验证失败", "data": {"errors": errors}},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "Internal server error", "data": None},
    )
