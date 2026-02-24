# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

# 注册中文字体
font_path = "C:/Windows/Fonts/msyh.ttc"
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('SimHei', font_path))
    chinese_font = 'SimHei'
else:
    chinese_font = 'Helvetica'

# 创建PDF文档
pdf_file = r"D:\共享文件\SSTCP-paidan260120\培训手册\SSTCP维保管理系统培训手册.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=A4, 
                        rightMargin=20*mm, leftMargin=20*mm,
                        topMargin=20*mm, bottomMargin=20*mm)

# 创建样式
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='ChineseTitle', fontName=chinese_font, fontSize=28, 
                          alignment=TA_CENTER, spaceAfter=30, textColor=colors.HexColor('#1a5fb4')))
styles.add(ParagraphStyle(name='ChineseH1', fontName=chinese_font, fontSize=22, 
                          spaceAfter=15, textColor=colors.HexColor('#1a5fb4'),
                          borderWidth=1, borderColor=colors.HexColor('#1a5fb4'), borderPadding=5))
styles.add(ParagraphStyle(name='ChineseH2', fontName=chinese_font, fontSize=18, 
                          spaceAfter=10, textColor=colors.HexColor('#26a269')))
styles.add(ParagraphStyle(name='ChineseH3', fontName=chinese_font, fontSize=14, 
                          spaceAfter=8, textColor=colors.HexColor('#e66100')))
styles.add(ParagraphStyle(name='ChineseBody', fontName=chinese_font, fontSize=11, 
                          spaceAfter=8, firstLineIndent=22))
styles.add(ParagraphStyle(name='ChineseBodyNoIndent', fontName=chinese_font, fontSize=11, 
                          spaceAfter=8))
styles.add(ParagraphStyle(name='ChineseBullet', fontName=chinese_font, fontSize=11, 
                          leftIndent=20, spaceAfter=5))

# 构建文档内容
story = []

# 封面
story.append(Spacer(1, 100*mm))
story.append(Paragraph("SSTCP维保管理系统", styles['ChineseTitle']))
story.append(Spacer(1, 10*mm))
story.append(Paragraph("培 训 手 册", ParagraphStyle(name='Subtitle', fontName=chinese_font, 
                                                      fontSize=24, alignment=TA_CENTER, textColor=colors.HexColor('#666'))))
story.append(Spacer(1, 50*mm))
story.append(Paragraph("适用于：管理员、部门经理、材料员、运维人员", 
                       ParagraphStyle(name='Info', fontName=chinese_font, fontSize=14, alignment=TA_CENTER)))
story.append(Spacer(1, 20*mm))
story.append(Paragraph("版本：V1.0", 
                       ParagraphStyle(name='Version', fontName=chinese_font, fontSize=12, alignment=TA_CENTER, textColor=colors.gray)))
story.append(Paragraph("编制日期：2026年2月", 
                       ParagraphStyle(name='Date', fontName=chinese_font, fontSize=12, alignment=TA_CENTER, textColor=colors.gray)))
story.append(PageBreak())

# 目录
story.append(Paragraph("目 录", styles['ChineseTitle']))
story.append(Spacer(1, 10*mm))
toc_items = [
    "第一章 系统概述",
    "第二章 系统登录",
    "第三章 电脑端操作指南",
    "第四章 手机端操作指南",
    "第五章 业务流程说明",
    "第六章 常见问题解答",
    "第七章 附录"
]
for item in toc_items:
    story.append(Paragraph(item, styles['ChineseBodyNoIndent']))
story.append(PageBreak())

# 第一章 系统概述
story.append(Paragraph("第一章 系统概述", styles['ChineseH1']))
story.append(Paragraph("1.1 系统简介", styles['ChineseH2']))
story.append(Paragraph("SSTCP维保管理系统是一套专业的设施设备维护保养管理平台，旨在提高维保工作效率，规范维保流程，实现维保工作的数字化、智能化管理。", styles['ChineseBody']))

story.append(Paragraph("1.2 系统架构", styles['ChineseH2']))
story.append(Paragraph("系统采用B/S架构，支持电脑端和手机端两种访问方式：", styles['ChineseBody']))

# 访问方式表格
access_data = [
    ['访问方式', '访问地址', '适用人员'],
    ['电脑端', 'http://www.sstcp.top/', '管理员、部门经理、材料员'],
    ['手机端', 'http://www.sstcp.top/h5/', '运维人员、部门经理']
]
access_table = Table(access_data, colWidths=[40*mm, 60*mm, 60*mm])
access_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5fb4')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, -1), chinese_font),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ddd'))
]))
story.append(access_table)
story.append(Spacer(1, 10*mm))

story.append(Paragraph("1.3 用户角色与权限", styles['ChineseH2']))
role_data = [
    ['角色', '主要权限', '主要功能'],
    ['管理员', '全部权限', '系统管理、人员管理、数据统计、全部业务操作'],
    ['部门经理', '部门管理权限', '维保计划制定、工单审批、巡检事项维护、周报管理'],
    ['材料员', '物资管理权限', '备品备件入库、领用管理、维修工具管理'],
    ['运维人员', '执行权限', '工单执行、巡检填报、维保日志填写、签字确认']
]
role_table = Table(role_data, colWidths=[30*mm, 40*mm, 90*mm])
role_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#26a269')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, -1), chinese_font),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ddd'))
]))
story.append(role_table)
story.append(PageBreak())

# 第二章 系统登录
story.append(Paragraph("第二章 系统登录", styles['ChineseH1']))
story.append(Paragraph("2.1 电脑端登录", styles['ChineseH2']))
story.append(Paragraph("登录步骤：", styles['ChineseH3']))
story.append(Paragraph("1. 打开浏览器，输入系统地址：http://www.sstcp.top/", styles['ChineseBullet']))
story.append(Paragraph("2. 进入登录页面，输入用户名和密码", styles['ChineseBullet']))
story.append(Paragraph("3. 点击「登录」按钮进入系统", styles['ChineseBullet']))

story.append(Paragraph("默认账号信息：", styles['ChineseH3']))
account_data = [
    ['用户名', '密码', '角色'],
    ['管理员', '000000', '管理员'],
    ['部门经理', '000001', '部门经理'],
    ['材料员', '000002', '材料员'],
    ['运维人员', '000003', '运维人员']
]
account_table = Table(account_data, colWidths=[50*mm, 50*mm, 50*mm])
account_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5fb4')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, -1), chinese_font),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ddd'))
]))
story.append(account_table)
story.append(Spacer(1, 5*mm))

story.append(Paragraph("安全提示：首次登录后请及时修改默认密码，确保账号安全。", styles['ChineseBody']))

story.append(Paragraph("2.2 手机端登录", styles['ChineseH2']))
story.append(Paragraph("登录步骤：", styles['ChineseH3']))
story.append(Paragraph("1. 打开手机浏览器，输入地址：http://www.sstcp.top/h5/", styles['ChineseBullet']))
story.append(Paragraph("2. 输入用户名和密码登录系统", styles['ChineseBullet']))
story.append(PageBreak())

# 第三章 电脑端操作指南
story.append(Paragraph("第三章 电脑端操作指南", styles['ChineseH1']))

story.append(Paragraph("3.1 项目信息管理", styles['ChineseH2']))
story.append(Paragraph("项目信息管理是系统的基础模块，用于维护项目的基本信息，为后续维保计划制定和工单生成提供数据支撑。", styles['ChineseBody']))
story.append(Paragraph("新增项目步骤：", styles['ChineseH3']))
story.append(Paragraph("1. 点击左侧菜单「项目信息管理」", styles['ChineseBullet']))
story.append(Paragraph("2. 点击右上角「新增」按钮", styles['ChineseBullet']))
story.append(Paragraph("3. 填写项目基本信息（项目编号、项目名称、项目地址、项目负责人等）", styles['ChineseBullet']))
story.append(Paragraph("4. 点击「保存」完成新增", styles['ChineseBullet']))

story.append(Paragraph("3.2 人员管理", styles['ChineseH2']))
story.append(Paragraph("人员管理模块用于维护系统用户信息，包括新增、编辑、删除人员等操作。", styles['ChineseBody']))
story.append(Paragraph("提示：新增人员后，系统会自动生成登录账号，用户名为人员姓名，初始密码为手机号后6位。", styles['ChineseBody']))

story.append(Paragraph("3.3 维保计划管理", styles['ChineseH2']))
story.append(Paragraph("维保计划管理是系统的核心模块，用于制定和管理维保计划，包括定期巡检计划和临时维修计划。", styles['ChineseBody']))
story.append(Paragraph("制定维保计划步骤：", styles['ChineseH3']))
story.append(Paragraph("1. 点击左侧菜单「维保计划管理」", styles['ChineseBullet']))
story.append(Paragraph("2. 点击「新增计划」按钮", styles['ChineseBullet']))
story.append(Paragraph("3. 选择计划类型（定期巡检/临时维修）", styles['ChineseBullet']))
story.append(Paragraph("4. 填写计划基本信息", styles['ChineseBullet']))
story.append(Paragraph("5. 选择巡检事项或维修事项", styles['ChineseBullet']))
story.append(Paragraph("6. 指定执行人员", styles['ChineseBullet']))
story.append(Paragraph("7. 点击「保存并下发」完成计划制定", styles['ChineseBullet']))

story.append(Paragraph("注意：计划需要在开始日期前5天内才能下发，下发后不可修改。", styles['ChineseBody']))

story.append(Paragraph("3.4 工单管理", styles['ChineseH2']))
story.append(Paragraph("工单管理模块用于查看和管理各类工单，包括定期巡检工单、临时维修工单和零星用工单。", styles['ChineseBody']))

order_data = [
    ['工单类型', '编号前缀', '说明'],
    ['定期巡检单', 'XJ', '定期巡检生成的工单'],
    ['临时维修单', 'WX', '临时维修生成的工单'],
    ['零星用工单', 'YG', '零星用工申请单']
]
order_table = Table(order_data, colWidths=[40*mm, 40*mm, 70*mm])
order_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5fb4')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, -1), chinese_font),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ddd'))
]))
story.append(order_table)
story.append(Spacer(1, 5*mm))

story.append(Paragraph("工单编号格式：前缀-项目编号-年月日，例如：XJ-PRJ001-20260224", styles['ChineseBody']))
story.append(PageBreak())

story.append(Paragraph("3.5 备品备件管理", styles['ChineseH2']))
story.append(Paragraph("备品备件管理模块用于管理备品备件的入库、领用和库存查询。", styles['ChineseBody']))

story.append(Paragraph("3.6 维修工具管理", styles['ChineseH2']))
story.append(Paragraph("维修工具管理模块用于管理维修工具的入库、领用、归还和库存查询。", styles['ChineseBody']))

story.append(Paragraph("3.7 数据统计", styles['ChineseH2']))
story.append(Paragraph("数据统计模块提供各类统计数据和图表，帮助管理层了解维保工作情况。统计内容包括：工单完成情况统计、巡检完成率统计、维修工时统计、备品备件消耗统计、人员工作量统计等。", styles['ChineseBody']))

story.append(Paragraph("3.8 超期预警", styles['ChineseH2']))
story.append(Paragraph("超期预警模块用于显示未按时完成的工单和即将到期的维保计划，提醒相关人员及时处理。", styles['ChineseBody']))
story.append(PageBreak())

# 第四章 手机端操作指南
story.append(Paragraph("第四章 手机端操作指南", styles['ChineseH1']))

story.append(Paragraph("4.1 手机端首页", styles['ChineseH2']))
story.append(Paragraph("手机端首页显示当前用户的待办事项和快捷入口，方便运维人员快速处理工单。首页功能包括：待办工单、已完成工单、超期工单、快捷入口等。", styles['ChineseBody']))

story.append(Paragraph("4.2 定期巡检", styles['ChineseH2']))
story.append(Paragraph("定期巡检模块用于运维人员执行定期巡检工单。", styles['ChineseBody']))
story.append(Paragraph("执行巡检工单步骤：", styles['ChineseH3']))
story.append(Paragraph("1. 点击首页「定期巡检」或底部「工单」菜单", styles['ChineseBullet']))
story.append(Paragraph("2. 选择待执行的巡检工单", styles['ChineseBullet']))
story.append(Paragraph("3. 查看巡检事项列表", styles['ChineseBullet']))
story.append(Paragraph("4. 逐项检查并填写检查结果", styles['ChineseBullet']))
story.append(Paragraph("5. 拍照上传现场照片（系统自动添加水印）", styles['ChineseBullet']))
story.append(Paragraph("6. 全部检查完成后点击「提交」", styles['ChineseBullet']))

story.append(Paragraph("提示：照片只能通过拍照上传，不支持从图库选择，确保照片的真实性。上传的照片会自动添加水印，包含拍摄人员姓名、拍摄时间、拍摄地点（经纬度）。", styles['ChineseBody']))

story.append(Paragraph("4.3 临时维修", styles['ChineseH2']))
story.append(Paragraph("临时维修模块用于运维人员执行临时维修工单。", styles['ChineseBody']))

story.append(Paragraph("4.4 零星用工", styles['ChineseH2']))
story.append(Paragraph("零星用工模块用于申报和管理零星用工工单。系统支持身份证拍照自动识别，识别后会自动填充姓名、身份证号等信息。", styles['ChineseBody']))

story.append(Paragraph("4.5 签字确认", styles['ChineseH2']))
story.append(Paragraph("部分工单需要签字确认，签字时请将手机横屏进行签名。", styles['ChineseBody']))

story.append(Paragraph("4.6 维保日志", styles['ChineseH2']))
story.append(Paragraph("维保日志模块用于运维人员填写日常维保日志。", styles['ChineseBody']))

story.append(Paragraph("4.7 备品备件领用", styles['ChineseH2']))
story.append(Paragraph("备品备件领用模块用于运维人员申请领用备品备件。", styles['ChineseBody']))

story.append(Paragraph("4.8 维修工具管理", styles['ChineseH2']))
story.append(Paragraph("维修工具管理模块用于运维人员领用和归还维修工具。", styles['ChineseBody']))
story.append(PageBreak())

# 第五章 业务流程说明
story.append(Paragraph("第五章 业务流程说明", styles['ChineseH1']))

story.append(Paragraph("5.1 维保计划流程", styles['ChineseH2']))
story.append(Paragraph("维保计划从制定到完成的完整流程：制定计划 -> 选择事项 -> 下发工单 -> 执行填写 -> 审批确认", styles['ChineseBody']))

flow_data = [
    ['步骤', '操作人', '说明'],
    ['制定计划', '管理员/部门经理', '基于项目信息，制定维保计划'],
    ['选择事项', '管理员/部门经理', '选择需要执行的巡检或维修事项'],
    ['下发工单', '管理员/部门经理', '计划开始前5天内下发，系统自动生成工单'],
    ['执行填写', '运维人员', '接收工单，执行并填写工单内容'],
    ['审批确认', '部门经理', '审批工单，通过则流程结束，不通过则退回修改']
]
flow_table = Table(flow_data, colWidths=[30*mm, 45*mm, 75*mm])
flow_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5fb4')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, -1), chinese_font),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ddd'))
]))
story.append(flow_table)
story.append(Spacer(1, 5*mm))

story.append(Paragraph("5.2 工单审批流程", styles['ChineseH2']))
story.append(Paragraph("工单提交后的审批流程：提交工单 -> 主管审批 -> 通过（流程结束）或不通过（退回修改 -> 重新提交 -> 再次审批）", styles['ChineseBody']))

story.append(Paragraph("注意事项：退回的工单会保留修改痕迹；所有删除操作均为非物理删除；删除前会弹出确认提示。", styles['ChineseBody']))

story.append(Paragraph("5.3 零星用工流程", styles['ChineseH2']))
story.append(Paragraph("零星用工从申报到完成的流程：申报用工 -> 录入人员 -> 班组签字 -> 提交审批", styles['ChineseBody']))
story.append(Paragraph("零星用工注意事项：需要录入施工人员信息（支持身份证识别）；班组签字需要工人签字确认；用户签字不强制要求；不展示计划用工字段。", styles['ChineseBody']))
story.append(PageBreak())

# 第六章 常见问题解答
story.append(Paragraph("第六章 常见问题解答", styles['ChineseH1']))

story.append(Paragraph("Q1：忘记密码怎么办？", styles['ChineseH3']))
story.append(Paragraph("请联系管理员重置密码，重置后密码将恢复为手机号后6位。", styles['ChineseBody']))

story.append(Paragraph("Q2：登录后页面空白怎么办？", styles['ChineseH3']))
story.append(Paragraph("请尝试以下操作：清除浏览器缓存；更换浏览器（推荐使用Chrome、Edge）；检查网络连接。", styles['ChineseBody']))

story.append(Paragraph("Q3：工单提交后可以修改吗？", styles['ChineseH3']))
story.append(Paragraph("工单提交后，在审批前可以撤回修改。审批通过后不可修改。", styles['ChineseBody']))

story.append(Paragraph("Q4：工单被退回怎么办？", styles['ChineseH3']))
story.append(Paragraph("工单被退回后，会显示退回原因。请根据退回原因修改工单内容后重新提交。", styles['ChineseBody']))

story.append(Paragraph("Q5：照片上传失败怎么办？", styles['ChineseH3']))
story.append(Paragraph("请检查以下事项：确保使用手机拍照，不支持从图库选择；检查手机是否授权相机权限；检查网络连接是否正常。", styles['ChineseBody']))

story.append(Paragraph("Q6：为什么无法下发计划？", styles['ChineseH3']))
story.append(Paragraph("计划需要在开始日期前5天内才能下发。请检查计划开始日期是否符合要求。", styles['ChineseBody']))

story.append(Paragraph("Q7：手机端提示「权限不足」怎么办？", styles['ChineseH3']))
story.append(Paragraph("请联系管理员确认您的账号角色和权限设置。", styles['ChineseBody']))
story.append(PageBreak())

# 第七章 附录
story.append(Paragraph("第七章 附录", styles['ChineseH1']))

story.append(Paragraph("7.1 系统配置要求", styles['ChineseH2']))

story.append(Paragraph("电脑端要求：", styles['ChineseH3']))
story.append(Paragraph("- 浏览器：Chrome 80+、Edge 80+、Firefox 75+、Safari 13+", styles['ChineseBullet']))
story.append(Paragraph("- 分辨率：1920x1080或更高", styles['ChineseBullet']))
story.append(Paragraph("- 网络：稳定的网络连接", styles['ChineseBullet']))

story.append(Paragraph("手机端要求：", styles['ChineseH3']))
story.append(Paragraph("- 操作系统：Android 8.0+、iOS 12.0+", styles['ChineseBullet']))
story.append(Paragraph("- 浏览器：Chrome、Safari、微信内置浏览器", styles['ChineseBullet']))
story.append(Paragraph("- 权限：相机权限、位置权限", styles['ChineseBullet']))

story.append(Paragraph("7.2 技术支持", styles['ChineseH2']))
story.append(Paragraph("如遇到系统使用问题，请通过以下方式获取帮助：", styles['ChineseBody']))
story.append(Paragraph("- 系统地址：http://www.sstcp.top/", styles['ChineseBullet']))
story.append(Paragraph("- 手机端地址：http://www.sstcp.top/h5/", styles['ChineseBullet']))
story.append(Paragraph("- API文档：http://www.sstcp.top/api/docs", styles['ChineseBullet']))

story.append(Paragraph("7.3 版本更新记录", styles['ChineseH2']))
version_data = [
    ['版本', '日期', '更新内容'],
    ['V1.0', '2026-02-24', '初始版本发布']
]
version_table = Table(version_data, colWidths=[30*mm, 40*mm, 80*mm])
version_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5fb4')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, -1), chinese_font),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ddd'))
]))
story.append(version_table)

story.append(Spacer(1, 30*mm))
story.append(Paragraph("- 培训手册结束 -", ParagraphStyle(name='End', fontName=chinese_font, fontSize=12, alignment=TA_CENTER, textColor=colors.gray)))

# 生成PDF
print("正在生成PDF...")
doc.build(story)
print(f"PDF生成成功: {pdf_file}")
