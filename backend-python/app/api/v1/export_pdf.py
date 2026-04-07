"""
工单PDF导出API
提供定期巡检、临时维修、零星用工三种工单的PDF导出功能
"""
import io
import logging
from datetime import datetime
from typing import Any
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_current_user_info
from app.models.periodic_inspection import PeriodicInspection
from app.models.spot_work import SpotWork
from app.models.temporary_repair import TemporaryRepair
from app.repositories.periodic_inspection import PeriodicInspectionRepository
from app.repositories.spot_work import SpotWorkRepository
from app.repositories.temporary_repair import TemporaryRepairRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/export", tags=["PDF Export"])


def get_weasyprint():
    """
    延迟导入weasyprint，避免启动时加载失败
    """
    try:
        from weasyprint import HTML
        return HTML
    except ImportError as e:
        logger.error(f"Failed to import weasyprint: {e}")
        raise HTTPException(
            status_code=500,
            detail="PDF导出功能暂不可用，请联系管理员配置环境"
        )


def get_base_css() -> str:
    """
    获取PDF基础样式
    """
    return """
    <style>
    @page {
        size: A4;
        margin: 15mm;
    }
    body {
        font-family: "SimSun", "Microsoft YaHei", sans-serif;
        font-size: 12px;
        line-height: 1.6;
        color: #333;
    }
    .header {
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #333;
    }
    .info-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }
    .info-table td {
        border: 1px solid #333;
        padding: 8px 12px;
        vertical-align: top;
    }
    .info-table .label {
        background-color: #f5f5f5;
        font-weight: bold;
        width: 120px;
    }
    .info-table .value {
        min-width: 150px;
    }
    .section-title {
        font-size: 14px;
        font-weight: bold;
        margin: 15px 0 10px 0;
        padding-left: 10px;
        border-left: 3px solid #1976d2;
    }
    .content-box {
        border: 1px solid #333;
        padding: 10px;
        min-height: 60px;
        margin-bottom: 15px;
    }
    .signature-box {
        text-align: center;
        margin-top: 30px;
        padding-top: 20px;
    }
    .signature-img {
        max-width: 200px;
        max-height: 80px;
    }
    .photo-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    .photo-item {
        width: 120px;
        height: 120px;
        border: 1px solid #ddd;
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        padding-top: 10px;
        border-top: 1px solid #ddd;
        font-size: 10px;
        color: #666;
    }
    </style>
    """


def format_date(date_value: Any) -> str:
    """
    格式化日期
    """
    if not date_value:
        return "-"
    if isinstance(date_value, datetime):
        return date_value.strftime("%Y-%m-%d")
    if isinstance(date_value, str):
        if "T" in date_value:
            return date_value.split("T")[0]
        return date_value
    return str(date_value)


def format_datetime(datetime_value: Any) -> str:
    """
    格式化日期时间
    """
    if not datetime_value:
        return "-"
    if isinstance(datetime_value, datetime):
        return datetime_value.strftime("%Y-%m-%d %H:%M")
    if isinstance(datetime_value, str):
        return datetime_value.replace("T", " ")[:16]
    return str(datetime_value)


def get_encoded_filename(filename: str) -> str:
    """
    获取URL编码的文件名，支持中文
    """
    encoded = quote(filename)
    return f"attachment; filename*=UTF-8''{encoded}"


@router.get("/periodic-inspection/{inspection_id}")
def export_periodic_inspection_pdf(
    inspection_id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
) -> StreamingResponse:
    """
    导出定期巡检单为PDF
    """
    repo = PeriodicInspectionRepository(db)
    inspection = repo.find_by_id(inspection_id)

    if not inspection:
        raise HTTPException(status_code=404, detail="巡检单不存在")

    if inspection.status != "已完成":
        raise HTTPException(status_code=400, detail="只能导出已完成的工单")

    html_content = generate_periodic_inspection_html(inspection, db)

    HTML = get_weasyprint()
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)

    filename = f"定期巡检单_{inspection.inspection_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": get_encoded_filename(filename)}
    )


@router.get("/temporary-repair/{repair_id}")
def export_temporary_repair_pdf(
    repair_id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
) -> StreamingResponse:
    """
    导出临时维修单为PDF
    """
    repo = TemporaryRepairRepository(db)
    repair = repo.find_by_id(repair_id)

    if not repair:
        raise HTTPException(status_code=404, detail="维修单不存在")

    if repair.status != "已完成":
        raise HTTPException(status_code=400, detail="只能导出已完成的工单")

    html_content = generate_temporary_repair_html(repair)

    HTML = get_weasyprint()
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)

    filename = f"临时维修单_{repair.repair_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": get_encoded_filename(filename)}
    )


@router.get("/spot-work/{work_id}")
def export_spot_work_pdf(
    work_id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
) -> StreamingResponse:
    """
    导出零星用工单为PDF
    """
    repo = SpotWorkRepository(db)
    work = repo.find_by_id(work_id)

    if not work:
        raise HTTPException(status_code=404, detail="用工单不存在")

    if work.status != "已完成":
        raise HTTPException(status_code=400, detail="只能导出已完成的工单")

    html_content = generate_spot_work_html(work, db)

    HTML = get_weasyprint()
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)

    filename = f"零星用工单_{work.work_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": get_encoded_filename(filename)}
    )


def generate_periodic_inspection_html(inspection: PeriodicInspection, db: Session) -> str:
    """
    生成定期巡检单HTML内容
    """
    from app.repositories.periodic_inspection_record import PeriodicInspectionRecordRepository
    from app.repositories.work_order_operation_log import WorkOrderOperationLogRepository

    record_repo = PeriodicInspectionRecordRepository(db)
    records = record_repo.find_by_inspection_id(inspection.inspection_id)

    log_repo = WorkOrderOperationLogRepository(db)
    logs = log_repo.find_by_work_order_no("periodic_inspection", inspection.inspection_id)

    client_contact = ''
    client_contact_info = ''
    address = ''
    if inspection.project:
        client_contact = inspection.project.client_contact or ''
        client_contact_info = inspection.project.client_contact_info or ''
        address = inspection.project.address or ''

    photos_html = ""
    if records:
        for record in records:
            if record.photos:
                for photo in record.photos:
                    photos_html += f'<img src="{photo}" class="photo-item" />'

    logs_html = ""
    if logs:
        for log in logs:
            logs_html += f"""
            <tr>
                <td>{format_datetime(log.created_at)}</td>
                <td>{log.operator_name}</td>
                <td>{log.operation_type_name}</td>
                <td>{log.operation_remark or '-'}</td>
            </tr>
            """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>定期巡检单</title>
        {get_base_css()}
    </head>
    <body>
        <div class="header">定期巡检单</div>

        <table class="info-table">
            <tr>
                <td class="label">巡检单编号</td>
                <td class="value">{inspection.inspection_id}</td>
                <td class="label">项目编号</td>
                <td class="value">{inspection.project_id}</td>
            </tr>
            <tr>
                <td class="label">项目名称</td>
                <td class="value" colspan="3">{inspection.project_name}</td>
            </tr>
            <tr>
                <td class="label">客户单位</td>
                <td class="value">{inspection.client_name or '-'}</td>
                <td class="label">客户联系人</td>
                <td class="value">{client_contact or '-'}</td>
            </tr>
            <tr>
                <td class="label">客户地址</td>
                <td class="value" colspan="3">{address or '-'}</td>
            </tr>
            <tr>
                <td class="label">计划开始日期</td>
                <td class="value">{format_date(inspection.plan_start_date)}</td>
                <td class="label">计划结束日期</td>
                <td class="value">{format_date(inspection.plan_end_date)}</td>
            </tr>
            <tr>
                <td class="label">运维人员</td>
                <td class="value">{inspection.maintenance_personnel or '-'}</td>
                <td class="label">状态</td>
                <td class="value">{inspection.status}</td>
            </tr>
        </table>

        <div class="section-title">发现问题</div>
        <div class="content-box">{inspection.execution_result or '无'}</div>

        <div class="section-title">处理结果</div>
        <div class="content-box">{inspection.remarks or '无'}</div>

        <div class="section-title">现场照片</div>
        <div class="photo-grid">
            {photos_html if photos_html else '<p>暂无照片</p>'}
        </div>

        <div class="section-title">用户签字</div>
        <div class="signature-box">
            {'<img src="' + inspection.signature + '" class="signature-img" />' if inspection.signature else '<p>暂无签字</p>'}
        </div>

        <div class="section-title">操作记录</div>
        <table class="info-table">
            <tr>
                <td class="label">操作时间</td>
                <td class="label">操作人</td>
                <td class="label">操作类型</td>
                <td class="label">备注</td>
            </tr>
            {logs_html if logs_html else '<tr><td colspan="4" style="text-align:center;">暂无操作记录</td></tr>'}
        </table>

        <div class="footer">
            <p>打印时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """


def generate_temporary_repair_html(repair: TemporaryRepair) -> str:
    """
    生成临时维修单HTML内容
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>临时维修单</title>
        {get_base_css()}
    </head>
    <body>
        <div class="header">临时维修单</div>

        <table class="info-table">
            <tr>
                <td class="label">维修单编号</td>
                <td class="value">{repair.repair_id}</td>
                <td class="label">项目编号</td>
                <td class="value">{repair.project_id}</td>
            </tr>
            <tr>
                <td class="label">项目名称</td>
                <td class="value" colspan="3">{repair.project_name}</td>
            </tr>
            <tr>
                <td class="label">客户单位</td>
                <td class="value">{repair.client_name or '-'}</td>
                <td class="label">运维人员</td>
                <td class="value">{repair.maintenance_personnel or '-'}</td>
            </tr>
            <tr>
                <td class="label">计划开始日期</td>
                <td class="value">{format_date(repair.plan_start_date)}</td>
                <td class="label">计划结束日期</td>
                <td class="value">{format_date(repair.plan_end_date)}</td>
            </tr>
            <tr>
                <td class="label">状态</td>
                <td class="value" colspan="3">{repair.status}</td>
            </tr>
        </table>

        <div class="section-title">报修内容</div>
        <div class="content-box">{repair.remarks or '无'}</div>

        <div class="section-title">处理结果</div>
        <div class="content-box">{repair.execution_result or '无'}</div>

        <div class="footer">
            <p>打印时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """


def generate_spot_work_html(work: SpotWork, db: Session) -> str:
    """
    生成零星用工单HTML内容
    """
    from app.repositories.spot_work import SpotWorkRepository

    repo = SpotWorkRepository(db)
    workers = repo.find_workers_for_spot_work(
        work.project_id,
        work.plan_start_date,
        work.plan_end_date
    )

    workers_html = ""
    if workers:
        for i, worker in enumerate(workers, 1):
            workers_html += f"""
            <tr>
                <td>{i}</td>
                <td>{worker.name}</td>
                <td>{worker.gender or '-'}</td>
                <td>{worker.id_card_number[:6] + '****' + worker.id_card_number[-4:] if worker.id_card_number else '-'}</td>
            </tr>
            """

    photos = []
    if work.photos:
        if isinstance(work.photos, str):
            photos = [p.strip() for p in work.photos.split(",") if p.strip()]
        elif isinstance(work.photos, list):
            photos = work.photos

    photos_html = ""
    for photo in photos:
        photos_html += f'<img src="{photo}" class="photo-item" />'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>零星用工单</title>
        {get_base_css()}
    </head>
    <body>
        <div class="header">零星用工单</div>

        <table class="info-table">
            <tr>
                <td class="label">用工单编号</td>
                <td class="value">{work.work_id}</td>
                <td class="label">项目编号</td>
                <td class="value">{work.project_id}</td>
            </tr>
            <tr>
                <td class="label">项目名称</td>
                <td class="value" colspan="3">{work.project_name}</td>
            </tr>
            <tr>
                <td class="label">客户单位</td>
                <td class="value">{work.client_name or '-'}</td>
                <td class="label">运维人员</td>
                <td class="value">{work.maintenance_personnel or '-'}</td>
            </tr>
            <tr>
                <td class="label">用工开始日期</td>
                <td class="value">{format_date(work.plan_start_date)}</td>
                <td class="label">用工结束日期</td>
                <td class="value">{format_date(work.plan_end_date)}</td>
            </tr>
            <tr>
                <td class="label">用工天数</td>
                <td class="value">{work.work_days or '-'} 天</td>
                <td class="label">施工人数</td>
                <td class="value">{work.worker_count or len(workers)} 人</td>
            </tr>
            <tr>
                <td class="label">状态</td>
                <td class="value" colspan="3">{work.status}</td>
            </tr>
        </table>

        <div class="section-title">工作内容</div>
        <div class="content-box">{work.work_content or work.remarks or '无'}</div>

        <div class="section-title">施工人员名单</div>
        <table class="info-table">
            <tr>
                <td class="label">序号</td>
                <td class="label">姓名</td>
                <td class="label">性别</td>
                <td class="label">身份证号</td>
            </tr>
            {workers_html if workers_html else '<tr><td colspan="4" style="text-align:center;">暂无施工人员</td></tr>'}
        </table>

        <div class="section-title">现场照片</div>
        <div class="photo-grid">
            {photos_html if photos_html else '<p>暂无照片</p>'}
        </div>

        <div class="section-title">班组签字</div>
        <div class="signature-box">
            {'<img src="' + work.signature + '" class="signature-img" />' if work.signature else '<p>暂无签字</p>'}
        </div>

        <div class="footer">
            <p>打印时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """
