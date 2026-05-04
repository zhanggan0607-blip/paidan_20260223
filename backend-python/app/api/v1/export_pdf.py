"""
工单PDF导出API
提供定期巡检、临时维修、零星用工三种工单的PDF导出功能

模板驱动设计：PDF布局由LAYOUT_CONFIG模板配置驱动，与前端Vue组件保持一致。
当前端查看页面变更时，只需更新对应的LAYOUT_CONFIG即可自动同步PDF格式。

TODO: 巡检单PDF缺少巡检项详情表格（inspection_items section）
FIXME: SparePartsStock/SparePartsInbound的to_dict()使用camelCase，其他Model都用snake_case
FIXME: KeepTogether导入但未使用，应移除或启用
"""
import io
import json
import logging
import os
import platform
from datetime import datetime
from typing import Any, Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.platypus.flowables import KeepTogether
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
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

_chinese_font_registered = False

NO_DATA_TEXT = "暂无数据"

INFO_TABLE_COL_WIDTHS = [80, 150, 80, 150]

PAGE_AVAILABLE_WIDTH = A4[0] - 30 * mm


class NumberedCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        font_name = get_chinese_font_name()
        for i, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            page_num = i + 1
            text = f"第{page_num}页-共{num_pages}页"
            self.setFont(font_name, 8)
            self.setFillColor(colors.grey)
            self.drawCentredString(A4[0] / 2, 8 * mm, text)
            Canvas.showPage(self)
        Canvas.save(self)


def _escape_xml(text: str) -> str:
    if not text:
        return ""
    text = str(text)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace("\n", "<br/>")
    return text


def _make_cell_paragraph(text: str, styles, cell_style_name: str = 'TableCell') -> Paragraph:
    font_name = get_chinese_font_name()
    if not text:
        text = NO_DATA_TEXT
    escaped = _escape_xml(text)
    cell_style = ParagraphStyle(
        name=cell_style_name,
        fontName=font_name,
        fontSize=9,
        leading=13,
        wordWrap='CJK',
        alignment=TA_LEFT,
    )
    return Paragraph(escaped, cell_style)


def _get_table_styles():
    font_name = get_chinese_font_name()
    info_style = TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f5f5f5')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d9d9d9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ])
    log_style = TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d9d9d9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ])
    return info_style, log_style

LAYOUT_CONFIG = {
    "temporary_repair": {
        "title": "临时维修工单详情",
        "frontend_ref": "src/views/TemporaryRepairDetail.vue",
        "info_rows": [
            [
                {"label": "项目名称", "field": "project_name"},
                {"label": "项目编号", "field": "project_id"},
            ],
            [
                {"label": "计划开始日期", "field": "plan_start_date", "format": "date"},
                {"label": "计划结束日期", "field": "plan_end_date", "format": "date"},
            ],
            [
                {"label": "运维人员", "field": "maintenance_personnel"},
                {"label": "工单编号", "field": "repair_id"},
            ],
            [
                {"label": "客户单位", "field": "client_name"},
                {"label": "客户地址", "field": "address", "source": "project"},
            ],
            [
                {"label": "客户联系人", "field": "client_contact", "source": "project"},
                {"label": "客户联系方式", "field": "client_contact_info", "source": "project"},
            ],
        ],
        "sections": [
            {"type": "divider", "text": "维修详情"},
            {"type": "text", "label": "报修内容", "field": "remarks"},
            {"type": "text", "label": "故障描述", "field": "fault_description"},
            {"type": "text", "label": "解决方案", "field": "solution"},
            {"type": "photos", "label": "现场图片", "field": "photos"},
            {"type": "signature", "label": "用户签字", "field": "signature"},
            {"type": "logs", "label": "内部确认区"},
        ],
    },
    "periodic_inspection": {
        "title": "查看巡检单",
        "frontend_ref": "src/views/PeriodicInspectionQuery.vue",
        "info_rows": [
            [
                {"label": "巡检单编号", "field": "inspection_id"},
                {"label": "计划开始日期", "field": "plan_start_date", "format": "date"},
            ],
            [
                {"label": "项目编号", "field": "project_id"},
                {"label": "计划结束日期", "field": "plan_end_date", "format": "date"},
            ],
            [
                {"label": "项目名称", "field": "project_name"},
                {"label": "运维人员", "field": "maintenance_personnel"},
            ],
            [
                {"label": "客户单位", "field": "client_name"},
                {"label": "客户联系方式", "field": "client_contact_info", "source": "project"},
            ],
            [
                {"label": "客户联系人", "field": "client_contact", "source": "project"},
                {"label": "客户地址", "field": "address", "source": "project"},
            ],
            [
                {"label": "联系人职位", "field": "client_contact_position", "source": "project"},
                {"label": "合同剩余时间", "field": "remaining_time", "computed": True},
            ],
            [
                {"label": "状态", "field": "status"},
                {"label": "创建时间", "field": "created_at", "format": "datetime"},
            ],
        ],
        "sections": [
            {"type": "inspection_items", "label": "巡检内容"},
            {"type": "field_handling", "label": "现场处理内容"},
            {"type": "text", "label": "发现问题", "field": "execution_result"},
            {"type": "text", "label": "处理结果", "field": "remarks"},
            {"type": "signature", "label": "用户签字", "field": "signature"},
            {"type": "inspection_photos", "label": "现场照片"},
            {"type": "logs", "label": "内部确认区"},
        ],
    },
    "spot_work": {
        "title": "零星用工工单详情",
        "frontend_ref": "src/views/SpotWorkDetail.vue",
        "info_rows": [
            [
                {"label": "项目名称", "field": "project_name"},
                {"label": "工单编号", "field": "work_id"},
            ],
            [
                {"label": "计划开始日期", "field": "plan_start_date", "format": "date"},
                {"label": "计划结束日期", "field": "plan_end_date", "format": "date"},
            ],
            [
                {"label": "客户单位", "field": "client_name"},
                {"label": "客户地址", "field": "address", "source": "project"},
            ],
            [
                {"label": "客户联系人", "field": "client_contact", "source": "project"},
                {"label": "客户联系方式", "field": "client_contact_info", "source": "project"},
            ],
            [
                {"label": "运维人员", "field": "maintenance_personnel"},
                {"label": "工天统计", "field": "work_days", "computed": True},
            ],
        ],
        "sections": [
            {"type": "text", "label": "工作内容", "field": "work_content"},
            {"type": "status", "label": "状态", "field": "status"},
            {"type": "photos", "label": "现场图片", "field": "photos"},
            {"type": "signature", "label": "班组签字", "field": "signature"},
            {"type": "workers", "label": "施工人员详情"},
            {"type": "logs", "label": "内部确认区"},
        ],
    },
}


def register_chinese_font():
    global _chinese_font_registered
    if _chinese_font_registered:
        return True

    system = platform.system()
    font_paths = []

    if system == "Windows":
        font_paths = [
            ("C:/Windows/Fonts/simhei.ttf", "SimHei"),
            ("C:/Windows/Fonts/msyh.ttc", "Microsoft YaHei"),
            ("C:/Windows/Fonts/simsun.ttc", "SimSun"),
            ("C:/Windows/Fonts/simkai.ttf", "KaiTi"),
        ]
    elif system == "Linux":
        font_paths = [
            ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", "WenQuanYi Zen Hei"),
            ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", "WenQuanYi Micro Hei"),
            ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "Noto Sans CJK"),
            ("/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc", "Noto Sans CJK"),
        ]
    elif system == "Darwin":
        font_paths = [
            ("/System/Library/Fonts/PingFang.ttc", "PingFang"),
            ("/System/Library/Fonts/STHeiti Light.ttc", "STHeiti"),
            ("/System/Library/Fonts/Hiragino Sans GB.ttc", "Hiragino Sans GB"),
        ]

    for font_path, font_name in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                logger.info(f"成功注册中文字体: {font_name} ({font_path})")
                _chinese_font_registered = True
                return True
            except Exception as e:
                logger.warning(f"注册字体失败 {font_path}: {e}")

    logger.warning("未找到可用的中文字体")
    return False


def get_chinese_font_name():
    system = platform.system()
    if system == "Windows":
        return "SimHei"
    elif system == "Linux":
        return "WenQuanYi Zen Hei"
    elif system == "Darwin":
        return "PingFang"
    return "Helvetica"


def get_styles():
    register_chinese_font()
    font_name = get_chinese_font_name()

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='ChineseTitle',
        fontName=font_name,
        fontSize=18,
        leading=24,
        alignment=1,
        spaceAfter=20,
        spaceBefore=10,
        wordWrap='CJK',
    ))

    styles.add(ParagraphStyle(
        name='ChineseNormal',
        fontName=font_name,
        fontSize=10,
        leading=16,
        wordWrap='CJK',
    ))

    styles.add(ParagraphStyle(
        name='ChineseSection',
        fontName=font_name,
        fontSize=12,
        leading=18,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#1976d2'),
        wordWrap='CJK',
    ))

    styles.add(ParagraphStyle(
        name='ChineseContent',
        fontName=font_name,
        fontSize=10,
        leading=16,
        borderPadding=5,
        wordWrap='CJK',
    ))

    styles.add(ParagraphStyle(
        name='ChineseFooter',
        fontName=font_name,
        fontSize=8,
        leading=12,
        alignment=1,
        textColor=colors.grey,
        wordWrap='CJK',
    ))

    styles.add(ParagraphStyle(
        name='ChineseDivider',
        fontName=font_name,
        fontSize=12,
        leading=18,
        alignment=1,
        spaceBefore=15,
        spaceAfter=15,
        textColor=colors.HexColor('#666666'),
        wordWrap='CJK',
    ))

    styles.add(ParagraphStyle(
        name='ChineseNoData',
        fontName=font_name,
        fontSize=10,
        leading=16,
        textColor=colors.HexColor('#999999'),
        wordWrap='CJK',
    ))

    return styles


def format_date(date_value: Any) -> str:
    if not date_value:
        return NO_DATA_TEXT
    if isinstance(date_value, datetime):
        return date_value.strftime("%Y-%m-%d")
    if isinstance(date_value, str):
        if "T" in date_value:
            return date_value.split("T")[0]
        return date_value
    return str(date_value)


def format_datetime(datetime_value: Any) -> str:
    if not datetime_value:
        return NO_DATA_TEXT
    if isinstance(datetime_value, datetime):
        return datetime_value.strftime("%Y-%m-%d %H:%M")
    if isinstance(datetime_value, str):
        return datetime_value.replace("T", " ")[:16]
    return str(datetime_value)


def get_encoded_filename(filename: str) -> str:
    encoded = quote(filename)
    return f"attachment; filename*=UTF-8''{encoded}"


def parse_photos(photos_value: Any) -> list:
    if not photos_value:
        return []
    if isinstance(photos_value, list):
        return photos_value
    if isinstance(photos_value, str):
        try:
            parsed = json.loads(photos_value)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
    return []


def get_image_url_or_path(relative_path: str, db: Session = None) -> str:
    if not relative_path:
        return ""
    if relative_path.startswith("data:image"):
        return relative_path
    if relative_path.startswith(("http://", "https://")):
        return relative_path
    from app.config import get_settings
    from app.utils.oss_service import get_oss_service
    settings = get_settings()
    if relative_path.startswith("/uploads/"):
        oss_key = relative_path[1:]
    elif relative_path.startswith("uploads/"):
        oss_key = relative_path
    else:
        return relative_path
    if db:
        from app.models.uploaded_file import UploadedFile
        from sqlalchemy.orm import load_only
        uploaded_file = db.query(UploadedFile).filter(
            UploadedFile.file_path == relative_path
        ).options(
            load_only(UploadedFile.storage_type, UploadedFile.oss_url, UploadedFile.file_path)
        ).first()
        if uploaded_file:
            if uploaded_file.storage_type == "database":
                return f"db://{relative_path}"
            if uploaded_file.storage_type == "oss" and uploaded_file.oss_url:
                return uploaded_file.oss_url
    if settings.aliyun_oss_enabled:
        oss_service = get_oss_service()
        if oss_service.is_available:
            return oss_service.get_file_url(oss_key)
    upload_dir = "/app/uploads"
    if relative_path.startswith("/"):
        local_path = upload_dir + relative_path.replace("/uploads", "")
    else:
        local_path = os.path.join(upload_dir, relative_path.replace("uploads/", ""))
    if os.path.exists(local_path):
        return local_path
    if settings.aliyun_oss_enabled:
        return f"https://{settings.aliyun_oss_bucket_name}.{settings.aliyun_oss_endpoint}/{oss_key}"
    return f"{settings.server_base_url}{relative_path}"


def _load_image_from_db(file_path: str, db: Session):
    from app.models.uploaded_file import UploadedFile
    from io import BytesIO as IOBytesIO
    uploaded_file = db.query(UploadedFile).filter(UploadedFile.file_path == file_path).first()
    if uploaded_file and uploaded_file.file_data:
        return IOBytesIO(uploaded_file.file_data)
    return None


def create_image_from_url(url_or_path: str, width: float, height: float, db: Session = None):
    import base64
    import requests
    from io import BytesIO as IOBytesIO

    if not url_or_path:
        return None
    try:
        if url_or_path.startswith("data:image"):
            if "base64," in url_or_path:
                base64_data = url_or_path.split("base64,")[1]
                img_data = base64.b64decode(base64_data)
                return Image(IOBytesIO(img_data), width=width, height=height)
            else:
                return None
        elif url_or_path.startswith("db://"):
            file_path = url_or_path[5:]
            if db:
                img_stream = _load_image_from_db(file_path, db)
                if img_stream:
                    return Image(img_stream, width=width, height=height)
            return None
        elif url_or_path.startswith(("http://", "https://")):
            from urllib.parse import urlparse
            from app.config import get_settings
            parsed = urlparse(url_or_path)
            allowed_domains = []
            settings = get_settings()
            if settings.aliyun_oss_endpoint:
                allowed_domains.append(settings.aliyun_oss_endpoint)
            if settings.aliyun_oss_cdn_domain:
                allowed_domains.append(settings.aliyun_oss_cdn_domain)
            if settings.server_base_url:
                server_parsed = urlparse(settings.server_base_url)
                if server_parsed.hostname:
                    allowed_domains.append(server_parsed.hostname)
            if allowed_domains and parsed.hostname not in allowed_domains:
                logger.warning(f"图片URL域名不在白名单中: {parsed.hostname}, 允许: {allowed_domains}")
                return None
            response = requests.get(url_or_path, timeout=10)
            if response.status_code == 200:
                img_data = IOBytesIO(response.content)
                return Image(img_data, width=width, height=height)
            else:
                logger.warning(f"无法下载图片 {url_or_path}: HTTP {response.status_code}")
                return None
        elif os.path.exists(url_or_path):
            return Image(url_or_path, width=width, height=height)
        else:
            logger.warning(f"图片文件不存在: {url_or_path}")
            return None
    except Exception as e:
        logger.warning(f"无法加载图片: {e}")
        return None


def create_section_title(title: str, styles):
    return Paragraph(title, styles['ChineseSection'])


def create_content_box(content: str, styles):
    if not content:
        content = NO_DATA_TEXT
    escaped = _escape_xml(str(content))
    return Paragraph(escaped, styles['ChineseContent'])


def create_divider(text: str, styles):
    elements = []
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#d9d9d9')))
    elements.append(Paragraph(text, styles['ChineseDivider']))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#d9d9d9')))
    elements.append(Spacer(1, 8))
    return elements


def resolve_field_value(obj, field_def: dict, project=None) -> str:
    field_name = field_def.get("field", "")
    fmt = field_def.get("format")
    source = field_def.get("source")
    computed = field_def.get("computed")

    if computed:
        return NO_DATA_TEXT

    if source == "project":
        if not project:
            return NO_DATA_TEXT
        value = getattr(project, field_name, None)
    else:
        value = getattr(obj, field_name, None)

    if value is None or value == "":
        return NO_DATA_TEXT

    if fmt == "date":
        return format_date(value)
    elif fmt == "datetime":
        return format_datetime(value)

    return str(value)


def build_info_table(config_key: str, obj, project=None, styles=None) -> Table:
    config = LAYOUT_CONFIG[config_key]
    info_data = []
    info_style, log_style = _get_table_styles()
    span_commands = list(info_style.getCommands())

    font_name = get_chinese_font_name()
    label_style = ParagraphStyle(
        name='InfoLabel',
        fontName=font_name,
        fontSize=10,
        leading=14,
        wordWrap='CJK',
        alignment=TA_LEFT,
    )
    value_style = ParagraphStyle(
        name='InfoValue',
        fontName=font_name,
        fontSize=10,
        leading=14,
        wordWrap='CJK',
        alignment=TA_LEFT,
    )

    for row_idx, row in enumerate(config["info_rows"]):
        left = row[0]
        right = row[1] if len(row) > 1 else None

        left_label = left.get("label", "")
        left_value = resolve_field_value(obj, left, project)

        left_label_p = Paragraph(_escape_xml(left_label), label_style)
        left_value_p = Paragraph(_escape_xml(left_value), value_style)

        if right:
            right_label = right.get("label", "")
            right_value = resolve_field_value(obj, right, project)
            right_label_p = Paragraph(_escape_xml(right_label), label_style)
            right_value_p = Paragraph(_escape_xml(right_value), value_style)
            info_data.append([left_label_p, left_value_p, right_label_p, right_value_p])
        else:
            info_data.append([left_label_p, left_value_p, "", ""])
            span_commands.append(('SPAN', (1, row_idx), (3, row_idx)))

    table = Table(info_data, colWidths=INFO_TABLE_COL_WIDTHS)
    style_commands = list(info_style.getCommands())
    style_commands.extend(span_commands)
    table.setStyle(TableStyle(style_commands))
    return table


def render_text_section(label: str, value, styles, elements: list):
    elements.append(create_section_title(label, styles))
    content = value if value else None
    if content:
        elements.append(create_content_box(str(content), styles))
    else:
        elements.append(Paragraph(NO_DATA_TEXT, styles['ChineseNoData']))
    elements.append(Spacer(1, 10))


def render_status_section(label: str, value, styles, elements: list):
    elements.append(create_section_title(label, styles))
    status_text = str(value) if value else NO_DATA_TEXT
    elements.append(Paragraph(status_text, styles['ChineseNormal']))
    elements.append(Spacer(1, 10))


def render_photos_section(label: str, photos_value, styles, elements: list, db: Session = None):
    elements.append(create_section_title(label, styles))
    photos = parse_photos(photos_value)
    if photos:
        img_width = 80 * mm
        img_height = 60 * mm
        col_width = (PAGE_AVAILABLE_WIDTH - 5 * mm) / 2
        images = []
        for photo in photos:
            img_url = get_image_url_or_path(photo, db=db)
            img = create_image_from_url(img_url, img_width, img_height, db=db)
            if img:
                images.append(img)
        if images:
            for i in range(0, len(images), 2):
                row = [images[i]]
                if i + 1 < len(images):
                    row.append(images[i + 1])
                else:
                    row.append("")
                photo_table = Table([row], colWidths=[col_width, col_width])
                photo_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                elements.append(photo_table)
        else:
            elements.append(Paragraph(NO_DATA_TEXT, styles['ChineseNoData']))
    else:
        elements.append(Paragraph(NO_DATA_TEXT, styles['ChineseNoData']))
    elements.append(Spacer(1, 10))


def render_signature_section(label: str, signature_value, styles, elements: list, db: Session = None):
    elements.append(create_section_title(label, styles))
    if signature_value:
        sig_url = get_image_url_or_path(signature_value, db=db)
        sig_img = create_image_from_url(sig_url, 50 * mm, 20 * mm, db=db)
        if sig_img:
            elements.append(sig_img)
        else:
            elements.append(Paragraph(NO_DATA_TEXT, styles['ChineseNoData']))
    else:
        elements.append(Paragraph(NO_DATA_TEXT, styles['ChineseNoData']))
    elements.append(Spacer(1, 10))


def render_logs_section(label: str, logs, styles, elements: list):
    elements.append(create_section_title(label, styles))
    if logs:
        font_name = get_chinese_font_name()
        header_style = ParagraphStyle(
            name='LogHeader',
            fontName=font_name,
            fontSize=9,
            leading=13,
            wordWrap='CJK',
            alignment=TA_CENTER,
        )
        log_data = [[
            Paragraph("操作时间", header_style),
            Paragraph("操作人", header_style),
            Paragraph("操作类型", header_style),
            Paragraph("备注", header_style),
        ]]
        for log in logs:
            log_data.append([
                _make_cell_paragraph(format_datetime(log.created_at), styles, 'LogTime'),
                _make_cell_paragraph(log.operator_name or NO_DATA_TEXT, styles, 'LogOperator'),
                _make_cell_paragraph(log.operation_type_name or NO_DATA_TEXT, styles, 'LogType'),
                _make_cell_paragraph(log.operation_remark or NO_DATA_TEXT, styles, 'LogRemark'),
            ])
        log_table = Table(log_data, colWidths=[100, 80, 80, 180])
        _, log_style = _get_table_styles()
        log_table.setStyle(log_style)
        elements.append(log_table)
    else:
        elements.append(Paragraph(NO_DATA_TEXT, styles['ChineseNoData']))
    elements.append(Spacer(1, 10))


def render_workers_section(label: str, workers, styles, elements: list):
    elements.append(create_section_title(label, styles))
    if workers:
        font_name = get_chinese_font_name()
        header_style = ParagraphStyle(
            name='WorkerHeader',
            fontName=font_name,
            fontSize=9,
            leading=13,
            wordWrap='CJK',
            alignment=TA_CENTER,
        )
        worker_data = [[
            Paragraph("序号", header_style),
            Paragraph("姓名", header_style),
            Paragraph("性别", header_style),
            Paragraph("身份证号码", header_style),
            Paragraph("住址", header_style),
        ]]
        for i, worker in enumerate(workers, 1):
            id_card = worker.id_card_number or NO_DATA_TEXT
            if id_card != NO_DATA_TEXT and len(id_card) >= 7:
                id_card = f"{id_card[:3]}****{id_card[-4:]}"
            worker_data.append([
                _make_cell_paragraph(str(i), styles, 'WorkerSeq'),
                _make_cell_paragraph(worker.name or NO_DATA_TEXT, styles, 'WorkerName'),
                _make_cell_paragraph(worker.gender or NO_DATA_TEXT, styles, 'WorkerGender'),
                _make_cell_paragraph(id_card, styles, 'WorkerIdCard'),
                _make_cell_paragraph(worker.address or NO_DATA_TEXT, styles, 'WorkerAddr'),
            ])
        worker_table = Table(worker_data, colWidths=[40, 80, 50, 130, 140])
        _, log_style = _get_table_styles()
        worker_table.setStyle(log_style)
        elements.append(worker_table)
    else:
        elements.append(Paragraph(NO_DATA_TEXT, styles['ChineseNoData']))
    elements.append(Spacer(1, 10))


def render_inspection_photos_section(label: str, records, styles, elements: list, db: Session = None):
    elements.append(create_section_title(label, styles))
    has_photos = False
    all_images = []
    if records:
        for record in records:
            photos = parse_photos(record.photos)
            for photo in photos:
                img_url = get_image_url_or_path(photo, db=db)
                img = create_image_from_url(img_url, 80 * mm, 60 * mm, db=db)
                if img:
                    has_photos = True
                    all_images.append(img)
    if has_photos:
        col_width = (PAGE_AVAILABLE_WIDTH - 5 * mm) / 2
        for i in range(0, len(all_images), 2):
            row = [all_images[i]]
            if i + 1 < len(all_images):
                row.append(all_images[i + 1])
            else:
                row.append("")
            photo_table = Table([row], colWidths=[col_width, col_width])
            photo_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            elements.append(photo_table)
    else:
        elements.append(Paragraph(NO_DATA_TEXT, styles['ChineseNoData']))
    elements.append(Spacer(1, 10))


def render_inspection_items_section(label: str, inspection_items_data, styles, elements: list):
    elements.append(create_section_title(label, styles))
    if inspection_items_data:
        font_name = get_chinese_font_name()
        header_style = ParagraphStyle(
            name='ItemHeader',
            fontName=font_name,
            fontSize=9,
            leading=13,
            wordWrap='CJK',
            alignment=TA_CENTER,
        )
        item_data = [[
            Paragraph("序号", header_style),
            Paragraph("巡查项", header_style),
            Paragraph("巡查内容", header_style),
            Paragraph("检查要求", header_style),
            Paragraph("简要说明", header_style),
        ]]
        for i, item in enumerate(inspection_items_data, 1):
            if isinstance(item, dict):
                check_req = item.get("check_requirements", "") or item.get("check_content", "")
            else:
                check_req = getattr(item, "check_content", "") or getattr(item, "check_requirements", "")
            item_data.append([
                _make_cell_paragraph(str(i), styles, 'ItemSeq'),
                _make_cell_paragraph(item.get("inspection_item", "") if isinstance(item, dict) else (getattr(item, "inspection_item", "") or ""), styles, 'ItemName'),
                _make_cell_paragraph(item.get("inspection_content", "") if isinstance(item, dict) else (getattr(item, "inspection_content", "") or ""), styles, 'ItemContent'),
                _make_cell_paragraph(check_req, styles, 'ItemReq'),
                _make_cell_paragraph(item.get("brief_description", "") if isinstance(item, dict) else (getattr(item, "brief_description", "") or ""), styles, 'ItemDesc'),
            ])
        item_table = Table(item_data, colWidths=[30, 70, 80, 150, 100])
        _, log_style = _get_table_styles()
        item_table.setStyle(log_style)
        elements.append(item_table)
    else:
        elements.append(Paragraph(NO_DATA_TEXT, styles['ChineseNoData']))
    elements.append(Spacer(1, 10))


def render_field_handling_section(label: str, records, styles, elements: list):
    elements.append(create_section_title(label, styles))
    if records:
        font_name = get_chinese_font_name()
        header_style = ParagraphStyle(
            name='HandlingHeader',
            fontName=font_name,
            fontSize=9,
            leading=13,
            wordWrap='CJK',
            alignment=TA_CENTER,
        )
        handling_data = [[
            Paragraph("实际现场故障情况", header_style),
            Paragraph("故障解决方案", header_style),
            Paragraph("是否解决", header_style),
        ]]
        for record in records:
            fault = record.inspection_result or NO_DATA_TEXT
            solution = record.brief_description or NO_DATA_TEXT
            resolved = "已解决" if record.inspected else "未解决"
            handling_data.append([
                _make_cell_paragraph(fault, styles, 'HandlingFault'),
                _make_cell_paragraph(solution, styles, 'HandlingSolution'),
                _make_cell_paragraph(resolved, styles, 'HandlingResolved'),
            ])
        handling_table = Table(handling_data, colWidths=[180, 180, 80])
        _, log_style = _get_table_styles()
        handling_table.setStyle(log_style)
        elements.append(handling_table)
    else:
        elements.append(Paragraph(NO_DATA_TEXT, styles['ChineseNoData']))
    elements.append(Spacer(1, 10))


def render_section(section_def: dict, obj, project, styles, elements, **kwargs):
    section_type = section_def.get("type")
    label = section_def.get("label", "")
    field = section_def.get("field")

    if section_type == "divider":
        divider_elements = create_divider(section_def.get("text", ""), styles)
        elements.extend(divider_elements)
    elif section_type == "text":
        value = resolve_field_value(obj, {"field": field}, project) if field else None
        if value == NO_DATA_TEXT:
            raw_value = getattr(obj, field, None) if field else None
            value = raw_value
        render_text_section(label, value, styles, elements)
    elif section_type == "status":
        value = getattr(obj, field, None) if field else None
        render_status_section(label, value, styles, elements)
    elif section_type == "photos":
        photos_value = getattr(obj, field, None) if field else None
        db = kwargs.get("db")
        render_photos_section(label, photos_value, styles, elements, db=db)
    elif section_type == "signature":
        sig_value = getattr(obj, field, None) if field else None
        db = kwargs.get("db")
        render_signature_section(label, sig_value, styles, elements, db=db)
    elif section_type == "logs":
        logs = kwargs.get("logs", [])
        render_logs_section(label, logs, styles, elements)
    elif section_type == "workers":
        workers = kwargs.get("workers", [])
        render_workers_section(label, workers, styles, elements)
    elif section_type == "inspection_photos":
        records = kwargs.get("records", [])
        db = kwargs.get("db")
        render_inspection_photos_section(label, records, styles, elements, db=db)
    elif section_type == "inspection_items":
        inspection_items_data = kwargs.get("inspection_items", [])
        render_inspection_items_section(label, inspection_items_data, styles, elements)
    elif section_type == "field_handling":
        records = kwargs.get("records", [])
        render_field_handling_section(label, records, styles, elements)


@router.get("/periodic-inspection/{inspection_id}")
def export_periodic_inspection_pdf(
    inspection_id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
) -> StreamingResponse:
    try:
        logger.info(f"开始导出定期巡检单PDF, inspection_id={inspection_id}")
        repo = PeriodicInspectionRepository(db)
        inspection = repo.find_by_id(inspection_id)
        if not inspection:
            raise HTTPException(status_code=404, detail="巡检单不存在")
        if inspection.status != "已完成":
            raise HTTPException(status_code=400, detail="只能导出已完成的工单")
        pdf_bytes = generate_periodic_inspection_pdf(inspection, db)
        filename = f"定期巡检单_{inspection.inspection_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": get_encoded_filename(filename)}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出定期巡检单PDF失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"导出PDF失败: {str(e)}")


@router.get("/temporary-repair/{repair_id}")
def export_temporary_repair_pdf(
    repair_id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
) -> StreamingResponse:
    repo = TemporaryRepairRepository(db)
    repair = repo.find_by_id(repair_id)
    if not repair:
        raise HTTPException(status_code=404, detail="维修单不存在")
    if repair.status != "已完成":
        raise HTTPException(status_code=400, detail="只能导出已完成的工单")
    pdf_bytes = generate_temporary_repair_pdf(repair, db)
    filename = f"临时维修单_{repair.repair_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": get_encoded_filename(filename)}
    )


@router.get("/spot-work/{work_id}")
def export_spot_work_pdf(
    work_id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
) -> StreamingResponse:
    repo = SpotWorkRepository(db)
    work = repo.find_by_id(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="用工单不存在")
    if work.status != "已完成":
        raise HTTPException(status_code=400, detail="只能导出已完成的工单")
    pdf_bytes = generate_spot_work_pdf(work, db)
    filename = f"零星用工单_{work.work_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": get_encoded_filename(filename)}
    )


def calculate_remaining_time(end_date) -> str:
    from datetime import date
    if not end_date:
        return NO_DATA_TEXT
    if isinstance(end_date, str):
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return NO_DATA_TEXT
    today = date.today()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    diff_time = (end_date - today).days
    if diff_time < 0:
        return "已过期"
    years = diff_time // 365
    months = (diff_time % 365) // 30
    days = diff_time % 30
    parts = []
    if years > 0:
        parts.append(f"{years}年")
    if months > 0:
        parts.append(f"{months}月")
    if days > 0 or not parts:
        parts.append(f"{days}日")
    return "".join(parts)


def _get_project_info(obj):
    project = getattr(obj, 'project', None)
    client_contact = ''
    client_contact_position = ''
    client_contact_info = ''
    address = ''
    if project:
        client_contact = project.client_contact or ''
        client_contact_position = project.client_contact_position or ''
        client_contact_info = project.client_contact_info or ''
        address = project.address or ''
    return project, client_contact, client_contact_position, client_contact_info, address


def generate_temporary_repair_pdf(repair: TemporaryRepair, db: Session) -> bytes:
    """
    生成临时维修单PDF
    布局配置: LAYOUT_CONFIG["temporary_repair"]
    前端对应: src/views/TemporaryRepairDetail.vue
    """
    from app.repositories.work_order_operation_log import WorkOrderOperationLogRepository

    log_repo = WorkOrderOperationLogRepository(db)
    logs = log_repo.find_by_work_order_no("temporary_repair", repair.repair_id)
    project, _, _, _, _ = _get_project_info(repair)

    config = LAYOUT_CONFIG["temporary_repair"]
    styles = get_styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
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


def generate_periodic_inspection_pdf(inspection: PeriodicInspection, db: Session) -> bytes:
    """
    生成定期巡检单PDF
    布局配置: LAYOUT_CONFIG["periodic_inspection"]
    前端对应: src/views/PeriodicInspectionQuery.vue
    """
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
            buffer,
            pagesize=A4,
            leftMargin=15 * mm,
            rightMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )

        elements = []
        elements.append(Paragraph(config["title"], styles['ChineseTitle']))
        elements.append(Spacer(1, 10))

        info_data = []
        font_name = get_chinese_font_name()
        label_style = ParagraphStyle(
            name='InfoLabelPI',
            fontName=font_name,
            fontSize=10,
            leading=14,
            wordWrap='CJK',
            alignment=TA_LEFT,
        )
        value_style = ParagraphStyle(
            name='InfoValuePI',
            fontName=font_name,
            fontSize=10,
            leading=14,
            wordWrap='CJK',
            alignment=TA_LEFT,
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
            render_section(section_def, inspection, project, styles, elements, logs=logs, records=records, inspection_items=inspection_items_data, db=db)

        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"打印时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['ChineseFooter']))

        doc.build(elements, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"生成PDF时发生错误: {str(e)}", exc_info=True)
        raise


def generate_spot_work_pdf(work: SpotWork, db: Session) -> bytes:
    """
    生成零星用工单PDF
    布局配置: LAYOUT_CONFIG["spot_work"]
    前端对应: src/views/SpotWorkDetail.vue
    """
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
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    elements = []
    elements.append(Paragraph(config["title"], styles['ChineseTitle']))
    elements.append(Spacer(1, 10))

    info_data = []
    font_name = get_chinese_font_name()
    label_style = ParagraphStyle(
        name='InfoLabelSW',
        fontName=font_name,
        fontSize=10,
        leading=14,
        wordWrap='CJK',
        alignment=TA_LEFT,
    )
    value_style = ParagraphStyle(
        name='InfoValueSW',
        fontName=font_name,
        fontSize=10,
        leading=14,
        wordWrap='CJK',
        alignment=TA_LEFT,
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
