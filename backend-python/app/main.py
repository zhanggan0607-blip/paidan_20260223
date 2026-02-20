from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config import get_settings
from app.api.v1 import project_info, maintenance_plan, personnel, periodic_inspection, periodic_inspection_record, inspection_item, overdue_alert, expiring_soon, temporary_repair, spot_work, spare_parts, spare_parts_stock, statistics, dictionary, user_dashboard_config, work_plan, customer, repair_tools, upload, auth, work_order, maintenance_log, weekly_report, work_order_operation_log, operation_type, ocr
from app.database import Base, engine
from app.exceptions import BusinessException
from app.middleware.rate_limit import RateLimitMiddleware
import logging
import time
import uuid
import os

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
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("数据库表创建成功")
    except Exception as e:
        if "already exists" not in str(e).lower() and "duplicate" not in str(e).lower():
            logger.error(f"创建数据库表失败: {str(e)}", exc_info=True)
        else:
            logger.info(f"数据库表或索引已存在，跳过创建")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-User-Name", "X-User-Role"],
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
app.include_router(user_dashboard_config.router, prefix=settings.api_prefix)
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
    return {"status": "healthy"}


@app.post("/migrate/add-total-count")
def migrate_add_total_count():
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
        return {"success": False, "message": str(e)}


@app.post("/migrate/add-plan-id-to-work-orders")
def migrate_add_plan_id():
    """
    为工单表添加plan_id字段，关联维保计划
    """
    from sqlalchemy import text
    results = {}
    
    tables = [
        ('periodic_inspection', 'inspection_id'),
        ('temporary_repair', 'repair_id'),
        ('spot_work', 'work_id')
    ]
    
    try:
        with engine.connect() as conn:
            for table_name, id_field in tables:
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
        return {"success": False, "message": str(e), "details": results}


@app.post("/migrate/add-signature-field")
def migrate_add_signature_field():
    """
    为工单表添加signature字段
    """
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
        return {"success": False, "message": str(e), "details": results}


@app.post("/migrate/fix-maintenance-plan-columns")
def migrate_fix_maintenance_plan_columns():
    """
    修复maintenance_plan表缺失的字段
    """
    from sqlalchemy import text
    results = {}
    
    columns_to_add = [
        ('maintenance_personnel', 'VARCHAR(100)', '运维人员'),
        ('responsible_department', 'VARCHAR(100)', '负责部门'),
        ('contact_info', 'VARCHAR(50)', '联系方式'),
        ('maintenance_requirements', 'TEXT', '维保要求'),
        ('maintenance_standard', 'TEXT', '维保标准'),
        ('plan_status', 'VARCHAR(20)', '计划状态'),
        ('status', 'VARCHAR(20) DEFAULT \'未进行\'', '执行状态'),
        ('completion_rate', 'INTEGER DEFAULT 0', '完成率'),
        ('filled_count', 'INTEGER DEFAULT 0', '已填写检查项数量'),
        ('total_count', 'INTEGER DEFAULT 5', '检查项总数量'),
        ('inspection_items', 'TEXT', '巡查项数据'),
    ]
    
    try:
        with engine.connect() as conn:
            for col_name, col_type, col_comment in columns_to_add:
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
        return {"success": False, "message": str(e), "details": results}


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
