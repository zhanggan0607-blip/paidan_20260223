"""
SSTCP维保系统 - FastAPI后端主入口
"""
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1 import (
    admin_edit,
    auth,
    customer,
    dictionary,
    dingtalk_auth,
    expiring_soon,
    export_pdf,
    files,
    inspection_item,
    maintenance_log,
    maintenance_plan,
    migration,
    ocr,
    online_user,
    operation_type,
    overdue_alert,
    periodic_inspection,
    periodic_inspection_record,
    personnel,
    project_info,
    repair_tools,
    spare_parts,
    spare_parts_stock,
    spot_work,
    statistics,
    temporary_repair,
    upload,
    weekly_report,
    websocket as websocket_api,
    work_order,
    work_order_operation_log,
    work_plan,
)
from app.config import get_settings
from app.database import Base, engine, async_engine
from app.dependencies import UserInfo, get_admin_user
from app.exceptions import BusinessException
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.csp import CSPMiddleware
from app.middleware.csrf import CSRFMiddleware
from app.utils.logging_config import get_logger, setup_logging


setup_logging(debug=get_settings().debug)

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("正在创建数据库表...")
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("数据库表创建成功")
    except Exception as e:
        if "already exists" not in str(e).lower() and "duplicate" not in str(e).lower():
            logger.error(f"创建数据库表失败: {str(e)}", exc_info=True)
        else:
            logger.info("数据库表或索引已存在，跳过创建")

    logger.info("正在创建工单编号序列...")
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE SEQUENCE IF NOT EXISTS work_order_seq START 1"))
            conn.commit()
        logger.info("工单编号序列创建成功")
    except Exception as e:
        logger.warning(f"创建工单编号序列失败（可能已存在）: {str(e)}")

    yield

    logger.info("正在关闭数据库连接...")
    if async_engine:
        await async_engine.dispose()
    engine.dispose()
    logger.info("数据库连接已关闭")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=settings.docs_url if settings.debug else None,
    redoc_url=settings.redoc_url if settings.debug else None,
    openapi_url=settings.openapi_url if settings.debug else None,
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "X-Requested-With",
        "X-Request-ID",
    ],
    expose_headers=["X-Request-ID"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(CSPMiddleware)

app.add_middleware(CSRFMiddleware)

app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.rate_limit_per_minute,
    requests_per_hour=settings.rate_limit_per_hour,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())

    request.state.request_id = request_id
    request.state.start_time = start_time

    logger.info(f"[{request_id}] {request.method} {request.url.path} - 开始")

    try:
        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        status_code = response.status_code

        if request.url.path.startswith('/uploads/') or request.url.path.startswith('/api/v1/files/'):
            response.headers['Cache-Control'] = 'public, max-age=31536000'
        elif request.url.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'public, max-age=60'

        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), payment=()'
        if request.url.scheme == 'https':
            response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains'

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

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(project_info.router, prefix=settings.api_prefix)
app.include_router(maintenance_plan.router, prefix=settings.api_prefix)
app.include_router(personnel.router, prefix=settings.api_prefix)
app.include_router(periodic_inspection.router, prefix=settings.api_prefix)
app.include_router(periodic_inspection_record.router, prefix=settings.api_prefix)
app.include_router(inspection_item.router, prefix=settings.api_prefix)
app.include_router(overdue_alert.router, prefix=settings.api_prefix)
app.include_router(expiring_soon.router, prefix=settings.api_prefix)
app.include_router(temporary_repair.router, prefix=settings.api_prefix)
app.include_router(spot_work.router, prefix=settings.api_prefix)
app.include_router(spare_parts.router, prefix=settings.api_prefix)
app.include_router(spare_parts_stock.router, prefix=settings.api_prefix)
app.include_router(statistics.router, prefix=settings.api_prefix)
app.include_router(dictionary.router, prefix=settings.api_prefix)
app.include_router(work_plan.router, prefix=settings.api_prefix)
app.include_router(customer.router, prefix=settings.api_prefix)
app.include_router(repair_tools.router, prefix=settings.api_prefix)
app.include_router(upload.router, prefix=settings.api_prefix)
app.include_router(files.router, prefix=settings.api_prefix)
app.include_router(work_order.router, prefix=settings.api_prefix)
app.include_router(maintenance_log.router, prefix=settings.api_prefix)
app.include_router(weekly_report.router, prefix=settings.api_prefix)
app.include_router(work_order_operation_log.router, prefix=settings.api_prefix)
app.include_router(operation_type.router, prefix=settings.api_prefix)
app.include_router(ocr.router, prefix=settings.api_prefix)
app.include_router(migration.router, prefix=settings.api_prefix)
app.include_router(dingtalk_auth.router, prefix=settings.api_prefix)
app.include_router(online_user.router, prefix=settings.api_prefix)
app.include_router(websocket_api.router, prefix=settings.api_prefix)
app.include_router(export_pdf.router, prefix=settings.api_prefix)
app.include_router(admin_edit.router, prefix=settings.api_prefix)


@app.get("/")
def read_root():
    return {
        "message": "SSTCP Maintenance System API",
        "version": settings.app_version,
        "docs": settings.docs_url,
        "supported_versions": ["/api/v1"],
    }


@app.get("/api/v1/health")
async def health_check():
    db_status = "healthy"
    try:
        if async_engine:
            async with async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        else:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        logger.error(f"健康检查数据库连接失败: {e}")

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "database": db_status,
        "async_db": async_engine is not None,
    }


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    logger.warning(f"业务异常 [{request.method} {request.url.path}]: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP异常 [{request.method} {request.url.path}]: {exc.status_code} - {exc.detail}")
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
    logger.warning(f"参数验证失败 [{request.method} {request.url.path}]: {errors}")
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": "参数验证失败", "data": {"errors": errors}},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    import traceback
    error_id = str(uuid.uuid4())[:8]
    error_trace = traceback.format_exc()
    logger.error(f"[{error_id}] 未处理异常 [{request.method} {request.url.path}]: {str(exc)}\n{error_trace}")

    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": f"服务器内部错误，错误ID: {error_id}，请联系管理员",
            "data": None
        },
    )
