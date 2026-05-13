import io
import json
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from sqlalchemy.orm import Session

from app.models.periodic_inspection import PeriodicInspection
from app.services.export_pdf_base import (
    NumberedCanvas, get_styles, get_chinese_font_name, _escape_xml,
    _get_table_styles, resolve_field_value, render_section, calculate_remaining_time,
    _get_project_info, LAYOUT_CONFIG, INFO_TABLE_COL_WIDTHS, NO_DATA_TEXT,
)
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def generate_periodic_inspection_pdf(inspection: PeriodicInspection, db: Session) -> bytes:
    from app.repositories.periodic_inspection_record import PeriodicInspectionRecordRepository
    from app.repositories.work_order_operation_log import WorkOrderOperationLogRepository

    try:
        record_repo = PeriodicInspectionRecordRepository(db)
        records = record_repo.find_by_inspection_id(inspection.inspection_id)
        log_repo = WorkOrderOperationLogRepository(db)
        logs = log_repo.find_by_work_order_no("periodic_inspection", inspection.inspection_id)
        project, _, _, _, _ = _get_project_info(inspection)

        inspection_items_data = []
        if records:
            inspection_items_data = [
                {
                    "inspection_item": r.inspection_item or "",
                    "inspection_content": r.inspection_content or "",
                    "check_requirements": r.check_content or "",
                    "brief_description": r.brief_description or "",
                }
                for r in records
            ]
        if not inspection_items_data and inspection.plan_id:
            from app.models.maintenance_plan import MaintenancePlan
            plan = db.query(MaintenancePlan).filter(MaintenancePlan.plan_id == inspection.plan_id).first()
            if plan and plan.inspection_items:
                try:
                    inspection_items_data = json.loads(plan.inspection_items)
                except (json.JSONDecodeError, TypeError):
                    inspection_items_data = []

        config = LAYOUT_CONFIG["periodic_inspection"]
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
            name='InfoLabelPI', fontName=font_name, fontSize=10,
            leading=14, wordWrap='CJK', alignment=0,
        )
        value_style = ParagraphStyle(
            name='InfoValuePI', fontName=font_name, fontSize=10,
            leading=14, wordWrap='CJK', alignment=0,
        )
        for row in config["info_rows"]:
            left = row[0]
            right = row[1] if len(row) > 1 else None
            left_value = resolve_field_value(inspection, left, project)
            if left.get("computed") and left.get("field") == "remaining_time":
                remaining_time = calculate_remaining_time(project.maintenance_end_date) if project else NO_DATA_TEXT
                left_value = remaining_time
            if right:
                right_value = resolve_field_value(inspection, right, project)
                if right.get("computed") and right.get("field") == "remaining_time":
                    remaining_time = calculate_remaining_time(project.maintenance_end_date) if project else NO_DATA_TEXT
                    right_value = remaining_time
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
            render_section(section_def, inspection, project, styles, elements,
                           logs=logs, records=records, inspection_items=inspection_items_data, db=db)

        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"打印时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['ChineseFooter']))

        doc.build(elements, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"生成PDF时发生错误: {str(e)}", exc_info=True)
        raise
