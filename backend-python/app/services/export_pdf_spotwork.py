import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from sqlalchemy.orm import Session

from app.models.spot_work import SpotWork
from app.services.export_pdf_base import (
    NumberedCanvas, get_styles, get_chinese_font_name, _escape_xml,
    _get_table_styles, resolve_field_value, render_section,
    _get_project_info, LAYOUT_CONFIG, INFO_TABLE_COL_WIDTHS, NO_DATA_TEXT,
)
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def generate_spot_work_pdf(work: SpotWork, db: Session) -> bytes:
    from app.repositories.spot_work import SpotWorkRepository
    from app.repositories.work_order_operation_log import WorkOrderOperationLogRepository

    repo = SpotWorkRepository(db)
    workers = repo.find_workers_for_spot_work(
        work.project_id,
        work.plan_start_date,
        work.plan_end_date,
    )
    log_repo = WorkOrderOperationLogRepository(db)
    logs = log_repo.find_by_work_order_no("spot_work", work.work_id)
    project, _, _, _, _ = _get_project_info(work)

    config = LAYOUT_CONFIG["spot_work"]
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

    info_data = []
    font_name = get_chinese_font_name()
    label_style = ParagraphStyle(
        name='InfoLabelSW', fontName=font_name, fontSize=10,
        leading=14, wordWrap='CJK', alignment=0,
    )
    value_style = ParagraphStyle(
        name='InfoValueSW', fontName=font_name, fontSize=10,
        leading=14, wordWrap='CJK', alignment=0,
    )
    for row in config["info_rows"]:
        left = row[0]
        right = row[1] if len(row) > 1 else None
        left_value = resolve_field_value(work, left, project)
        if left.get("computed") and left.get("field") == "work_days":
            if work.plan_start_date and work.plan_end_date:
                left_value = f"{(work.plan_end_date - work.plan_start_date).days + 1}工天"
            else:
                left_value = NO_DATA_TEXT
        if right:
            right_value = resolve_field_value(work, right, project)
            if right.get("computed") and right.get("field") == "work_days":
                if work.plan_start_date and work.plan_end_date:
                    right_value = f"{(work.plan_end_date - work.plan_start_date).days + 1}工天"
                else:
                    right_value = NO_DATA_TEXT
            info_data.append([
                Paragraph(_escape_xml(left.get("label", "")), label_style),
                Paragraph(_escape_xml(left_value), value_style),
                Paragraph(_escape_xml(right.get("label", "")), label_style),
                Paragraph(_escape_xml(right_value), value_style),
            ])
        else:
            info_data.append([
                Paragraph(_escape_xml(left.get("label", "")), label_style),
                Paragraph(_escape_xml(left_value), value_style),
                "", "",
            ])

    table = Table(info_data, colWidths=INFO_TABLE_COL_WIDTHS)
    info_style, _ = _get_table_styles()
    table.setStyle(info_style)
    elements.append(table)
    elements.append(Spacer(1, 15))

    for section_def in config["sections"]:
        render_section(section_def, work, project, styles, elements, logs=logs, workers=workers, db=db)

    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"打印时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['ChineseFooter']))

    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
