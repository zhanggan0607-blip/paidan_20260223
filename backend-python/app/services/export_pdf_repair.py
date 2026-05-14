import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from sqlalchemy.orm import Session

from app.models.temporary_repair import TemporaryRepair
from app.services.export_pdf_base import (
    NumberedCanvas, get_styles, build_info_table, render_section,
    _get_project_info, LAYOUT_CONFIG, NO_DATA_TEXT,
)
from app.utils.logging_config import get_logger, log_performance

logger = get_logger(__name__)


@log_performance(2000)
def generate_temporary_repair_pdf(repair: TemporaryRepair, db: Session) -> bytes:
    from app.repositories.work_order_operation_log import WorkOrderOperationLogRepository

    log_repo = WorkOrderOperationLogRepository(db)
    logs = log_repo.find_by_work_order_no("temporary_repair", repair.repair_id)
    project, _, _, _, _ = _get_project_info(repair)

    config = LAYOUT_CONFIG["temporary_repair"]
    styles = get_styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
    )

    elements = []
    elements.append(Paragraph(config["title"], styles['ChineseTitle']))
    elements.append(Spacer(1, 10))

    info_table = build_info_table("temporary_repair", repair, project)
    elements.append(info_table)
    elements.append(Spacer(1, 15))

    for section_def in config["sections"]:
        render_section(section_def, repair, project, styles, elements, logs=logs, db=db)

    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"打印时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['ChineseFooter']))

    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
