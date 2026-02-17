"""
SSTCP维保管理系统 - 缺陷记录
测试工程师: 张志芳
测试日期: 2026-02-18
"""

import json
from datetime import datetime

DEFECTS = [
    {
        "id": "BUG-001",
        "title": "更新项目信息时返回500内部服务器错误",
        "module": "项目信息管理",
        "severity": "高",
        "priority": "P1",
        "status": "待修复",
        "reporter": "张志芳",
        "assignee": "开发团队",
        "created_at": "2026-02-18T00:15:00",
        "description": """
调用PUT /api/v1/project-info/{id}接口更新项目信息时，系统返回500内部服务器错误。
该问题导致用户无法修改已创建的项目信息，严重影响业务流程。
        """.strip(),
        "steps_to_reproduce": [
            "1. 通过POST /api/v1/project-info接口创建一个新项目",
            "2. 获取返回的项目ID",
            "3. 调用PUT /api/v1/project-info/{id}接口，传入更新数据",
            "4. 观察返回结果"
        ],
        "expected_result": "返回200状态码，项目信息更新成功，响应包含更新后的项目数据",
        "actual_result": "返回500状态码，响应内容: {'code': 500, 'message': 'Internal server error', 'data': None}",
        "test_data": {
            "project_id": "TEST20260218002120",
            "project_name": "更新后的项目_002120",
            "completion_date": "2026-02-18",
            "maintenance_end_date": "2027-02-18",
            "maintenance_period": "每月",
            "client_name": "测试客户单位",
            "address": "测试地址"
        },
        "evidence": "业务流程测试日志显示更新项目返回500错误",
        "impact": "用户无法修改项目信息，影响项目维护流程",
        "workaround": "暂无",
        "suggested_fix": "检查项目更新接口的异常处理逻辑，确保所有字段正确处理",
        "related_defects": [],
        "tags": ["API", "500错误", "项目信息"]
    },
    {
        "id": "BUG-002",
        "title": "创建定期巡检工单时返回500内部服务器错误",
        "module": "定期巡检管理",
        "severity": "高",
        "priority": "P1",
        "status": "待修复",
        "reporter": "张志芳",
        "assignee": "开发团队",
        "created_at": "2026-02-18T00:17:00",
        "description": """
调用POST /api/v1/periodic-inspection接口创建定期巡检工单时，系统返回500内部服务器错误。
该问题导致用户无法创建定期巡检工单，严重影响核心业务流程。
        """.strip(),
        "steps_to_reproduce": [
            "1. 准备定期巡检工单数据（包含inspection_id, project_id等必填字段）",
            "2. 调用POST /api/v1/periodic-inspection接口",
            "3. 观察返回结果"
        ],
        "expected_result": "返回201状态码，工单创建成功，响应包含新创建的工单数据",
        "actual_result": "返回500状态码，响应内容: {'code': 500, 'message': 'Internal server error', 'data': None}",
        "test_data": {
            "inspection_id": "XJ-TEST20260218002120-20260218",
            "project_id": "TEST20260218002120",
            "project_name": "自动化测试项目_002120",
            "plan_start_date": "2026-02-18",
            "plan_end_date": "2026-02-25",
            "client_name": "测试客户",
            "maintenance_personnel": "张干",
            "status": "未进行"
        },
        "evidence": "业务流程测试日志显示创建巡检工单返回500错误",
        "impact": "用户无法创建定期巡检工单，影响维保计划执行",
        "workaround": "暂无",
        "suggested_fix": "检查定期巡检创建接口的数据验证和外键关联逻辑",
        "related_defects": [],
        "tags": ["API", "500错误", "定期巡检"]
    },
    {
        "id": "BUG-003",
        "title": "项目列表接口响应时间过长",
        "module": "性能",
        "severity": "高",
        "priority": "P2",
        "status": "待优化",
        "reporter": "张志芳",
        "assignee": "开发团队",
        "created_at": "2026-02-18T00:18:00",
        "description": """
GET /api/v1/periodic-inspection接口响应时间超过2秒，严重影响用户体验。
在数据量较小的情况下（约50条记录），响应时间仍然较长。
        """.strip(),
        "steps_to_reproduce": [
            "1. 调用GET /api/v1/periodic-inspection接口",
            "2. 测量接口响应时间",
            "3. 多次测试取平均值"
        ],
        "expected_result": "响应时间应小于1秒",
        "actual_result": "平均响应时间约2045ms",
        "test_data": {
            "page": 0,
            "size": 10
        },
        "evidence": "API测试报告显示响应时间为2045.71ms",
        "impact": "用户等待时间过长，体验较差",
        "workaround": "暂无",
        "suggested_fix": """
1. 为常用查询字段添加数据库索引
2. 优化SQL查询语句，避免N+1查询
3. 实现分页查询优化
4. 考虑添加Redis缓存
        """.strip(),
        "related_defects": [],
        "tags": ["性能", "响应时间", "数据库优化"]
    },
    {
        "id": "BUG-004",
        "title": "根路径访问返回404错误",
        "module": "健康检查",
        "severity": "中",
        "priority": "P3",
        "status": "待修复",
        "reporter": "张志芳",
        "assignee": "开发团队",
        "created_at": "2026-02-18T00:19:00",
        "description": """
访问根路径 / 时返回404错误，而非系统信息。
虽然不影响业务功能，但影响API的可用性检查。
        """.strip(),
        "steps_to_reproduce": [
            "1. 访问 http://localhost:8000/",
            "2. 观察返回结果"
        ],
        "expected_result": "返回系统信息，如版本号、API文档链接等",
        "actual_result": "返回404错误: {'code': 404, 'message': 'Not Found', 'data': None}",
        "test_data": {},
        "evidence": "API测试报告显示根路径访问返回404",
        "impact": "影响API健康检查和监控",
        "workaround": "使用 /health 端点进行健康检查",
        "suggested_fix": "确保根路径路由正确注册",
        "related_defects": [],
        "tags": ["API", "路由", "健康检查"]
    },
    {
        "id": "BUG-005",
        "title": "统计接口响应时间较长",
        "module": "性能",
        "severity": "中",
        "priority": "P3",
        "status": "待优化",
        "reporter": "张志芳",
        "assignee": "开发团队",
        "created_at": "2026-02-18T00:20:00",
        "description": """
GET /api/v1/statistics/overview接口响应时间接近2秒。
统计接口涉及多表查询和数据聚合，需要优化性能。
        """.strip(),
        "steps_to_reproduce": [
            "1. 调用GET /api/v1/statistics/overview接口",
            "2. 测量接口响应时间"
        ],
        "expected_result": "响应时间应小于1秒",
        "actual_result": "平均响应时间约1876ms",
        "test_data": {
            "year": 2026
        },
        "evidence": "API测试报告显示统计接口响应时间较长",
        "impact": "用户查看统计页面时等待时间较长",
        "workaround": "暂无",
        "suggested_fix": """
1. 优化统计查询SQL
2. 实现统计数据缓存
3. 考虑异步计算统计数据
        """.strip(),
        "related_defects": ["BUG-003"],
        "tags": ["性能", "统计", "缓存"]
    },
    {
        "id": "BUG-006",
        "title": "创建人员接口gender字段为必填但文档未说明",
        "module": "人员管理",
        "severity": "低",
        "priority": "P4",
        "status": "待完善",
        "reporter": "张志芳",
        "assignee": "开发团队",
        "created_at": "2026-02-18T00:21:00",
        "description": """
创建人员时gender字段为必填，但API文档未明确说明。
导致API调用时出现422参数验证错误。
        """.strip(),
        "steps_to_reproduce": [
            "1. 调用POST /api/v1/personnel接口",
            "2. 不传入gender字段",
            "3. 观察返回结果"
        ],
        "expected_result": "API文档应明确说明gender为必填字段，或设置默认值",
        "actual_result": "返回422错误: {'field': 'body.gender', 'message': 'Field required'}",
        "test_data": {
            "name": "测试员工",
            "department": "测试部门",
            "role": "员工",
            "phone": "13800138000"
        },
        "evidence": "API测试报告显示创建人员返回422错误",
        "impact": "影响API使用体验",
        "workaround": "传入gender字段",
        "suggested_fix": "更新API文档，明确说明必填字段；或为gender设置默认值",
        "related_defects": [],
        "tags": ["文档", "参数验证", "人员管理"]
    }
]

def generate_defect_report():
    """生成缺陷报告"""
    report = {
        "summary": {
            "total_defects": len(DEFECTS),
            "severity_count": {
                "严重": 0,
                "高": 2,
                "中": 2,
                "低": 1
            },
            "status_count": {
                "待修复": 3,
                "待优化": 2,
                "待完善": 1
            },
            "generated_at": datetime.now().isoformat()
        },
        "defects": DEFECTS
    }
    
    # 保存JSON格式报告
    with open("defects_report.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 生成Markdown格式报告
    md_content = """# SSTCP维保管理系统 - 缺陷报告

## 缺陷统计

| 指标 | 数量 |
|------|------|
| 缺陷总数 | {total} |
| 高优先级 | {high} |
| 中优先级 | {medium} |
| 低优先级 | {low} |

---

## 缺陷列表

""".format(
        total=len(DEFECTS),
        high=sum(1 for d in DEFECTS if d["severity"] == "高"),
        medium=sum(1 for d in DEFECTS if d["severity"] == "中"),
        low=sum(1 for d in DEFECTS if d["severity"] == "低")
    )
    
    for defect in DEFECTS:
        md_content += f"""### {defect['id']}: {defect['title']}

**模块:** {defect['module']}  
**严重程度:** {defect['severity']}  
**状态:** {defect['status']}  

**描述:**  
{defect['description']}

**复现步骤:**
"""
        for step in defect['steps_to_reproduce']:
            md_content += f"- {step}\n"
        
        md_content += f"""
**预期结果:** {defect['expected_result']}

**实际结果:** {defect['actual_result']}

**建议修复方案:**  
{defect['suggested_fix']}

---

"""
    
    with open("defects_report.md", 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print("缺陷报告已生成:")
    print("  - defects_report.json")
    print("  - defects_report.md")

if __name__ == "__main__":
    generate_defect_report()
