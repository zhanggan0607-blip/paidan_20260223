import os
import time
import uuid
from datetime import datetime

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1 import (
    auth,
    customer,
    dictionary,
    dingtalk_auth,
    expiring_soon,
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
    work_order,
    work_order_operation_log,
    work_plan,
)
from app.config import get_settings
from app.database import Base, engine
from app.dependencies import UserInfo, get_admin_user
from app.exceptions import BusinessException
from app.middleware.rate_limit import RateLimitMiddleware
from app.utils.logging_config import get_logger, setup_logging

setup_logging(level="DEBUG" if get_settings().debug else "INFO")

logger = get_logger(__name__)
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
)

Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
async def startup_event():
    """应用启动时创建数据库表和序列"""
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=120,
    requests_per_hour=2000,
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
app.include_router(work_order.router, prefix=settings.api_prefix)
app.include_router(maintenance_log.router, prefix=settings.api_prefix)
app.include_router(weekly_report.router, prefix=settings.api_prefix)
app.include_router(work_order_operation_log.router, prefix=settings.api_prefix)
app.include_router(operation_type.router, prefix=settings.api_prefix)
app.include_router(ocr.router, prefix=settings.api_prefix)
app.include_router(migration.router, prefix=settings.api_prefix)
app.include_router(dingtalk_auth.router, prefix=settings.api_prefix)
app.include_router(online_user.router, prefix=settings.api_prefix)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def read_root():
    return {
        "message": "SSTCP Maintenance System API",
        "version": settings.app_version,
        "docs": settings.docs_url,
        "supported_versions": ["/api/v1"],
    }


@app.get("/health")
def health_check():
    """
    健康检查端点
    用于监控服务状态和数据库连接
    """
    db_status = "healthy"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        logger.error(f"健康检查数据库连接失败: {e}")

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "database": db_status
    }


@app.post("/migrate/add-total-count")
def migrate_add_total_count(admin_user: UserInfo = Depends(get_admin_user)):
    """
    数据库迁移：添加total_count字段
    需要超级管理员权限
    """
    logger.info(f"迁移操作由管理员 {admin_user.name} 执行")
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'periodic_inspection' AND column_name = 'total_count'
            """))

            if result.fetchone() is None:
                conn.execute(text("ALTER TABLE periodic_inspection ADD COLUMN total_count INTEGER DEFAULT 5"))
                conn.commit()
                return {"success": True, "message": "Successfully added total_count column"}
            else:
                return {"success": True, "message": "Column total_count already exists"}
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 迁移失败: {str(e)}")
        return {"success": False, "message": f"迁移失败，错误ID: {error_id}，请联系管理员"}


@app.post("/migrate/add-plan-id-to-work-orders")
def migrate_add_plan_id(admin_user: UserInfo = Depends(get_admin_user)):
    """
    为工单表添加plan_id字段，关联维保计划
    需要超级管理员权限
    """
    logger.info(f"迁移操作由管理员 {admin_user.name} 执行")
    from sqlalchemy import text
    results = {}

    tables = [
        ('periodic_inspection', 'inspection_id'),
        ('temporary_repair', 'repair_id'),
        ('spot_work', 'work_id')
    ]

    try:
        with engine.connect() as conn:
            for table_name, _id_field in tables:
                result = conn.execute(text(f"""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}' AND column_name = 'plan_id'
                """))

                if result.fetchone() is None:
                    conn.execute(text(f"""
                        ALTER TABLE {table_name}
                        ADD COLUMN plan_id VARCHAR(50) NULL
                    """))
                    conn.execute(text(f"""
                        CREATE INDEX IF NOT EXISTS idx_{table_name}_plan_id
                        ON {table_name}(plan_id)
                    """))
                    conn.commit()
                    results[table_name] = "Added plan_id column"
                else:
                    results[table_name] = "Column plan_id already exists"

            return {"success": True, "message": "Migration completed", "details": results}
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 迁移失败: {str(e)}")
        return {"success": False, "message": f"迁移失败，错误ID: {error_id}，请联系管理员", "details": results}


@app.post("/migrate/add-signature-field")
def migrate_add_signature_field(admin_user: UserInfo = Depends(get_admin_user)):
    """
    为工单表添加signature字段
    需要超级管理员权限
    """
    logger.info(f"迁移操作由管理员 {admin_user.name} 执行")
    from sqlalchemy import text
    results = {}

    tables = ['periodic_inspection', 'temporary_repair', 'spot_work']

    try:
        with engine.connect() as conn:
            for table_name in tables:
                result = conn.execute(text(f"""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}' AND column_name = 'signature'
                """))

                if result.fetchone() is None:
                    conn.execute(text(f"""
                        ALTER TABLE {table_name}
                        ADD COLUMN signature TEXT NULL
                    """))
                    conn.commit()
                    results[table_name] = "Added signature column"
                else:
                    results[table_name] = "Column signature already exists"

            return {"success": True, "message": "Migration completed", "details": results}
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 迁移失败: {str(e)}")
        return {"success": False, "message": f"迁移失败，错误ID: {error_id}，请联系管理员", "details": results}


@app.post("/migrate/fix-maintenance-plan-columns")
def migrate_fix_maintenance_plan_columns(admin_user: UserInfo = Depends(get_admin_user)):
    """
    修复maintenance_plan表缺失的字段
    需要超级管理员权限
    """
    logger.info(f"迁移操作由管理员 {admin_user.name} 执行")
    from sqlalchemy import text
    results = {}

    columns_to_add = [
        ('maintenance_personnel', 'VARCHAR(100)', '运维人员'),
        ('responsible_department', 'VARCHAR(100)', '负责部门'),
        ('contact_info', 'VARCHAR(50)', '联系方式'),
        ('maintenance_requirements', 'TEXT', '维保要求'),
        ('maintenance_standard', 'TEXT', '维保标准'),
        ('plan_status', 'VARCHAR(20)', '计划状态'),
        ('status', 'VARCHAR(20) DEFAULT \'执行中\'', '执行状态'),
        ('completion_rate', 'INTEGER DEFAULT 0', '完成率'),
        ('filled_count', 'INTEGER DEFAULT 0', '已填写检查项数量'),
        ('total_count', 'INTEGER DEFAULT 5', '检查项总数量'),
        ('inspection_items', 'TEXT', '巡查项数据'),
    ]

    try:
        with engine.connect() as conn:
            for col_name, col_type, _col_comment in columns_to_add:
                result = conn.execute(text(f"""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'maintenance_plan' AND column_name = '{col_name}'
                """))

                if result.fetchone() is None:
                    conn.execute(text(f"""
                        ALTER TABLE maintenance_plan
                        ADD COLUMN {col_name} {col_type} NULL
                    """))
                    conn.commit()
                    results[col_name] = f"Added column {col_name}"
                else:
                    results[col_name] = f"Column {col_name} already exists"

            return {"success": True, "message": "Migration completed", "details": results}
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 迁移失败: {str(e)}")
        return {"success": False, "message": f"迁移失败，错误ID: {error_id}，请联系管理员", "details": results}


@app.post("/migrate/unify-status")
def migrate_unify_status(admin_user: UserInfo = Depends(get_admin_user)):
    """
    统一工单状态为4种：执行中、待确认、已完成、已退回
    需要超级管理员权限
    """
    logger.info(f"迁移操作由管理员 {admin_user.name} 执行")
    from sqlalchemy import text
    results = {}

    try:
        with engine.connect() as conn:
            tables = ['periodic_inspection', 'temporary_repair', 'spot_work', 'maintenance_plan', 'work_plan']
            old_statuses = ['未下发', '待执行', '未进行']

            for table in tables:
                try:
                    for status in old_statuses:
                        result = conn.execute(text(f"""
                            UPDATE {table}
                            SET status = '执行中'
                            WHERE status = :status
                        """), {"status": status})
                        if result.rowcount > 0:
                            results[f"{table}_{status}"] = f"Updated {result.rowcount} rows"
                    conn.commit()
                except Exception as e:
                    results[table] = f"Error: {str(e)}"

            try:
                conn.execute(text("""
                    UPDATE dictionary
                    SET dict_value = '执行中'
                    WHERE dict_value IN ('未下发', '待执行', '未进行')
                    AND dict_type LIKE '%status%'
                """))
                conn.commit()
                results['dictionary'] = "Updated dictionary entries"
            except Exception as e:
                results['dictionary'] = f"Error: {str(e)}"

            return {"success": True, "message": "状态统一迁移完成", "details": results}
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 迁移失败: {str(e)}")
        return {"success": False, "message": f"迁移失败，错误ID: {error_id}，请联系管理员", "details": results}


@app.post("/migrate/add-indexes")
def migrate_add_indexes(admin_user: UserInfo = Depends(get_admin_user)):
    """
    添加缺失索引
    需要超级管理员权限
    """
    logger.info(f"迁移操作由管理员 {admin_user.name} 执行")
    from sqlalchemy import text
    results = {}

    indexes = [
        ('idx_project_info_project_manager', 'project_info', 'project_manager'),
        ('idx_spot_work_worker_id_card', 'spot_work_worker', 'id_card_number'),
        ('idx_spot_work_worker_name', 'spot_work_worker', 'name'),
        ('idx_weekly_report_is_deleted', 'weekly_report', 'is_deleted'),
        ('idx_maintenance_log_is_deleted', 'maintenance_log', 'is_deleted'),
    ]

    try:
        with engine.connect() as conn:
            for idx_name, table, column in indexes:
                try:
                    conn.execute(text(f"""
                        CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})
                    """))
                    conn.commit()
                    results[idx_name] = f"Created index on {table}.{column}"
                except Exception as e:
                    results[idx_name] = f"Error: {str(e)}"

            return {"success": True, "message": "索引添加完成", "details": results}
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 迁移失败: {str(e)}")
        return {"success": False, "message": f"迁移失败，错误ID: {error_id}，请联系管理员", "details": results}


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """
    处理业务异常
    业务异常是预期的错误，可以安全地返回给客户端
    """
    logger.warning(f"业务异常 [{request.method} {request.url.path}]: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    处理HTTP异常
    """
    logger.warning(f"HTTP异常 [{request.method} {request.url.path}]: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail, "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求参数验证异常
    """
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
    """
    处理未捕获异常
    不暴露内部错误信息，只返回错误ID用于追踪
    """
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
