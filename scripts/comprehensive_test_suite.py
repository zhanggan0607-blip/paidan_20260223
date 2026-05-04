"""
SSTCP维保管理系统 - 全面测试套件
覆盖：功能测试、安全性测试、性能测试、兼容性测试、易用性测试
"""
import json
import time
import threading
import statistics
import sys
import os
from datetime import datetime
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    print("请安装requests库: pip install requests")
    sys.exit(1)


BASE_URL = "https://www.paidan.sstcp.top"
API_PREFIX = "/api/v1"
TEST_USER = {"username": os.environ.get("TEST_USERNAME", ""), "password": os.environ.get("TEST_PASSWORD", "")}
ADMIN_USER = {"username": os.environ.get("TEST_USERNAME", ""), "password": os.environ.get("TEST_PASSWORD", "")}

results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "defects": [],
    "performance": [],
    "details": [],
}


def record_result(module, test_name, status, message="", response_time=0, severity=""):
    results["total"] += 1
    if status == "PASS":
        results["passed"] += 1
        symbol = "✅"
    elif status == "FAIL":
        results["failed"] += 1
        symbol = "❌"
        if severity:
            results["defects"].append({
                "module": module,
                "test": test_name,
                "severity": severity,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            })
    else:
        results["skipped"] += 1
        symbol = "⏭️"

    if response_time > 0:
        results["performance"].append({
            "test": test_name,
            "response_time_ms": round(response_time * 1000, 2),
        })

    results["details"].append({
        "module": module,
        "test": test_name,
        "status": status,
        "message": message,
        "response_time_ms": round(response_time * 1000, 2) if response_time > 0 else None,
    })

    print(f"  {symbol} [{module}] {test_name}: {message}")


def get_auth_token(user=None):
    if user is None:
        user = TEST_USER
    try:
        resp = requests.post(
            f"{BASE_URL}{API_PREFIX}/auth/login-json",
            json={"username": user["username"], "password": user["password"], "device_type": "pc"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("data", {}).get("access_token")
    except Exception as e:
        print(f"  ⚠️ 获取Token失败: {e}")
    return None


def timed_request(method, url, **kwargs):
    kwargs.setdefault("timeout", 30)
    start = time.time()
    try:
        resp = getattr(requests, method)(url, **kwargs)
        elapsed = time.time() - start
        return resp, elapsed
    except requests.exceptions.Timeout:
        elapsed = time.time() - start
        return None, elapsed
    except Exception as e:
        elapsed = time.time() - start
        return None, elapsed


# ============================================================
# 1. 功能测试 - 认证模块
# ============================================================
def test_auth_module(headers):
    print("\n📋 功能测试 - 认证模块")
    module = "认证模块"

    resp, t = timed_request("post", f"{BASE_URL}{API_PREFIX}/auth/login-json",
                            json={"username": TEST_USER["username"], "password": TEST_USER["password"], "device_type": "pc"})
    if resp and resp.status_code == 200:
        data = resp.json().get("data", {})
        record_result(module, "正常登录-JSON", "PASS", f"状态码200, Token获取成功", t)
    else:
        record_result(module, "正常登录-JSON", "FAIL", f"登录失败: {resp.status_code if resp else 'Timeout'}", t, "P0-致命")

    resp, t = timed_request("post", f"{BASE_URL}{API_PREFIX}/auth/login",
                            data={"username": TEST_USER["username"], "password": TEST_USER["password"]})
    if resp and resp.status_code == 200:
        record_result(module, "正常登录-OAuth2表单", "PASS", f"状态码200", t)
    else:
        record_result(module, "正常登录-OAuth2表单", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P0-致命")

    resp, t = timed_request("post", f"{BASE_URL}{API_PREFIX}/auth/login-json",
                            json={"username": "不存在的用户", "password": "wrong", "device_type": "pc"})
    if resp and resp.status_code == 401:
        record_result(module, "错误密码登录", "PASS", f"正确返回401", t)
    else:
        record_result(module, "错误密码登录", "FAIL", f"预期401, 实际: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/auth/me", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "获取当前用户信息", "PASS", f"状态码200", t)
    else:
        record_result(module, "获取当前用户信息", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/auth/me")
    if resp and resp.status_code == 401:
        record_result(module, "无Token访问受保护端点", "PASS", f"正确返回401", t)
    else:
        record_result(module, "无Token访问受保护端点", "FAIL", f"预期401, 实际: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/auth/me",
                            headers={"Authorization": "Bearer invalid_token_12345"})
    if resp and resp.status_code == 401:
        record_result(module, "无效Token访问", "PASS", f"正确返回401", t)
    else:
        record_result(module, "无效Token访问", "FAIL", f"预期401, 实际: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("post", f"{BASE_URL}{API_PREFIX}/auth/logout", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "登出功能", "PASS", f"状态码200", t)
    else:
        record_result(module, "登出功能", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("post", f"{BASE_URL}{API_PREFIX}/auth/login-json",
                            json={"username": TEST_USER["username"], "password": TEST_USER["password"], "device_type": "h5"})
    if resp and resp.status_code == 200:
        record_result(module, "H5端登录", "PASS", f"H5设备类型登录成功", t)
    else:
        record_result(module, "H5端登录", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")


# ============================================================
# 2. 功能测试 - 项目信息模块
# ============================================================
def test_project_info_module(headers):
    print("\n📋 功能测试 - 项目信息模块")
    module = "项目信息"

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/project-info", headers=headers)
    if resp and resp.status_code == 200:
        data = resp.json()
        record_result(module, "获取项目列表", "PASS", f"状态码200, 数据条数: {len(data.get('data', {}).get('items', []))}", t)
    else:
        record_result(module, "获取项目列表", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/project-info/all/list", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "获取所有项目", "PASS", f"状态码200", t)
    else:
        record_result(module, "获取所有项目", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/project-info/99999", headers=headers)
    if resp and resp.status_code == 404:
        record_result(module, "获取不存在项目", "PASS", f"正确返回404", t)
    else:
        record_result(module, "获取不存在项目", "FAIL", f"预期404, 实际: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    new_project = {
        "project_name": f"测试项目_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "project_code": f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "project_manager": "测试经理",
        "status": "执行中",
    }
    resp, t = timed_request("post", f"{BASE_URL}{API_PREFIX}/project-info", json=new_project, headers=headers)
    created_id = None
    if resp and resp.status_code == 200:
        data = resp.json().get("data", {})
        created_id = data.get("id")
        record_result(module, "创建项目", "PASS", f"创建成功, ID: {created_id}", t)
    else:
        record_result(module, "创建项目", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}, 响应: {resp.text[:200] if resp else 'Timeout'}", t, "P1-严重")

    if created_id:
        resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/project-info/{created_id}", headers=headers)
        if resp and resp.status_code == 200:
            record_result(module, "获取项目详情", "PASS", f"状态码200", t)
        else:
            record_result(module, "获取项目详情", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

        update_data = {"project_name": f"更新项目_{datetime.now().strftime('%H%M%S')}"}
        resp, t = timed_request("put", f"{BASE_URL}{API_PREFIX}/project-info/{created_id}", json=update_data, headers=headers)
        if resp and resp.status_code == 200:
            record_result(module, "更新项目", "PASS", f"状态码200", t)
        else:
            record_result(module, "更新项目", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

        resp, t = timed_request("delete", f"{BASE_URL}{API_PREFIX}/project-info/{created_id}", headers=headers)
        if resp and resp.status_code == 200:
            record_result(module, "删除项目", "PASS", f"状态码200", t)
        else:
            record_result(module, "删除项目", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("post", f"{BASE_URL}{API_PREFIX}/project-info", json={}, headers=headers)
    if resp and resp.status_code in [400, 422]:
        record_result(module, "创建项目-空数据验证", "PASS", f"正确返回{resp.status_code}", t)
    else:
        record_result(module, "创建项目-空数据验证", "FAIL", f"预期400/422, 实际: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")


# ============================================================
# 3. 功能测试 - 人员管理模块
# ============================================================
def test_personnel_module(headers):
    print("\n📋 功能测试 - 人员管理模块")
    module = "人员管理"

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/personnel", headers=headers)
    if resp and resp.status_code == 200:
        data = resp.json()
        items = data.get("data", {}).get("items", [])
        record_result(module, "获取人员列表", "PASS", f"状态码200, 人员数: {len(items)}", t)
    else:
        record_result(module, "获取人员列表", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/personnel/all/list", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "获取所有人员", "PASS", f"状态码200", t)
    else:
        record_result(module, "获取所有人员", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/personnel/99999", headers=headers)
    if resp and resp.status_code == 404:
        record_result(module, "获取不存在人员", "PASS", f"正确返回404", t)
    else:
        record_result(module, "获取不存在人员", "FAIL", f"预期404, 实际: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    new_person = {
        "name": f"测试人员_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "role": "运维人员",
        "department": "测试部门",
        "phone": "13800000001",
    }
    resp, t = timed_request("post", f"{BASE_URL}{API_PREFIX}/personnel", json=new_person, headers=headers)
    created_id = None
    if resp and resp.status_code == 200:
        data = resp.json().get("data", {})
        created_id = data.get("id")
        record_result(module, "创建人员", "PASS", f"创建成功, ID: {created_id}", t)
    else:
        record_result(module, "创建人员", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}, 响应: {resp.text[:200] if resp else 'Timeout'}", t, "P1-严重")

    if created_id:
        resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/personnel/{created_id}", headers=headers)
        if resp and resp.status_code == 200:
            record_result(module, "获取人员详情", "PASS", f"状态码200", t)
        else:
            record_result(module, "获取人员详情", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

        update_data = {"name": f"更新人员_{datetime.now().strftime('%H%M%S')}"}
        resp, t = timed_request("put", f"{BASE_URL}{API_PREFIX}/personnel/{created_id}", json=update_data, headers=headers)
        if resp and resp.status_code == 200:
            record_result(module, "更新人员", "PASS", f"状态码200", t)
        else:
            record_result(module, "更新人员", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

        resp, t = timed_request("delete", f"{BASE_URL}{API_PREFIX}/personnel/{created_id}", headers=headers)
        if resp and resp.status_code == 200:
            record_result(module, "删除人员", "PASS", f"状态码200", t)
        else:
            record_result(module, "删除人员", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")


# ============================================================
# 4. 功能测试 - 工单模块（临时维修/定期巡检/零星用工）
# ============================================================
def test_work_order_modules(headers):
    print("\n📋 功能测试 - 工单模块")
    module = "工单管理"

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/work-order", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "合并查询所有工单", "PASS", f"状态码200", t)
    else:
        record_result(module, "合并查询所有工单", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/work-order/all/list", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "获取所有工单列表", "PASS", f"状态码200", t)
    else:
        record_result(module, "获取所有工单列表", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/work-order/completed-this-year", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "本年已完成工单", "PASS", f"状态码200", t)
    else:
        record_result(module, "本年已完成工单", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    # 临时维修
    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/temporary-repair", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "临时维修-列表查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "临时维修-列表查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/temporary-repair/generate-id", headers=headers)
    if resp and resp.status_code == 200:
        data = resp.json().get("data", {})
        record_result(module, "临时维修-生成编号", "PASS", f"编号: {data}", t)
    else:
        record_result(module, "临时维修-生成编号", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    # 定期巡检
    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/periodic-inspection", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "定期巡检-列表查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "定期巡检-列表查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    # 零星用工
    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/spot-work", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "零星用工-列表查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "零星用工-列表查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/spot-work/generate-id", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "零星用工-生成编号", "PASS", f"状态码200", t)
    else:
        record_result(module, "零星用工-生成编号", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/spot-work/workers", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "零星用工-施工人员列表", "PASS", f"状态码200", t)
    else:
        record_result(module, "零星用工-施工人员列表", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/spot-work/workers/all", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "零星用工-所有施工人员", "PASS", f"状态码200", t)
    else:
        record_result(module, "零星用工-所有施工人员", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")


# ============================================================
# 5. 功能测试 - 维保计划模块
# ============================================================
def test_maintenance_plan_module(headers):
    print("\n📋 功能测试 - 维保计划模块")
    module = "维保计划"

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/maintenance-plan", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "获取维保计划列表", "PASS", f"状态码200", t)
    else:
        record_result(module, "获取维保计划列表", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/maintenance-plan/all/list", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "获取所有维保计划", "PASS", f"状态码200", t)
    else:
        record_result(module, "获取所有维保计划", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/maintenance-plan/upcoming/list", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "即将到期计划", "PASS", f"状态码200", t)
    else:
        record_result(module, "即将到期计划", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    resp, t = timed_request("post", f"{BASE_URL}{API_PREFIX}/maintenance-plan", json={}, headers=headers)
    if resp and resp.status_code in [400, 422]:
        record_result(module, "创建计划-空数据验证", "PASS", f"正确返回{resp.status_code}", t)
    else:
        record_result(module, "创建计划-空数据验证", "FAIL", f"预期400/422, 实际: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")


# ============================================================
# 6. 功能测试 - 备品备件模块
# ============================================================
def test_spare_parts_module(headers):
    print("\n📋 功能测试 - 备品备件模块")
    module = "备品备件"

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/spare-parts/usage", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "领用记录查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "领用记录查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/spare-parts-stock", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "备件库存查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "备件库存查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")


# ============================================================
# 7. 功能测试 - 维修工具模块
# ============================================================
def test_repair_tools_module(headers):
    print("\n📋 功能测试 - 维修工具模块")
    module = "维修工具"

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/repair-tools/stock", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "工具库存查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "工具库存查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/repair-tools/inbound", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "入库记录查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "入库记录查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/repair-tools/issue", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "领用记录查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "领用记录查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/repair-tools/personnel-projects", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "人员项目关联", "PASS", f"状态码200", t)
    else:
        record_result(module, "人员项目关联", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")


# ============================================================
# 8. 功能测试 - 统计模块
# ============================================================
def test_statistics_module(headers):
    print("\n📋 功能测试 - 统计模块")
    module = "统计分析"

    endpoints = [
        ("统计概览", "/statistics/overview"),
        ("准时完成率", "/statistics/completion-rate"),
        ("前五项目", "/statistics/top-projects"),
        ("前五维修", "/statistics/top-repairs"),
        ("员工统计", "/statistics/employee-stats"),
        ("维修统计", "/statistics/repair-stats"),
        ("用工统计", "/statistics/spotwork-stats"),
        ("巡检统计", "/statistics/inspection-stats"),
    ]

    for name, path in endpoints:
        resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}{path}", headers=headers)
        if resp and resp.status_code == 200:
            record_result(module, name, "PASS", f"状态码200", t)
        else:
            record_result(module, name, "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")


# ============================================================
# 9. 功能测试 - 周报/日志模块
# ============================================================
def test_weekly_report_and_log(headers):
    print("\n📋 功能测试 - 周报/日志模块")

    module = "周报管理"
    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/weekly-report", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "周报列表查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "周报列表查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/weekly-report/generate-id", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "周报编号生成", "PASS", f"状态码200", t)
    else:
        record_result(module, "周报编号生成", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    module = "维保日志"
    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/maintenance-log", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "日志列表查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "日志列表查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/maintenance-log/my", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "我的日志", "PASS", f"状态码200", t)
    else:
        record_result(module, "我的日志", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/maintenance-log/today", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "今日日志", "PASS", f"状态码200", t)
    else:
        record_result(module, "今日日志", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")


# ============================================================
# 10. 功能测试 - 其他模块
# ============================================================
def test_other_modules(headers):
    print("\n📋 功能测试 - 其他模块")

    module = "数据字典"
    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/dictionary", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "数据字典查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "数据字典查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    module = "超期提醒"
    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/overdue-alert", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "超期提醒查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "超期提醒查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    module = "临期提醒"
    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/expiring-soon", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "临期提醒查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "临期提醒查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    module = "在线用户"
    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/online/users", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "在线用户查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "在线用户查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    module = "巡检事项"
    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/inspection-item", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "巡检事项查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "巡检事项查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    module = "客户管理"
    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/customer", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "客户列表查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "客户列表查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    module = "工作计划"
    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/work-plan", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "工作计划查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "工作计划查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    module = "操作日志"
    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/work-order-operation-log", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "操作日志查询", "PASS", f"状态码200", t)
    else:
        record_result(module, "操作日志查询", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")


# ============================================================
# 11. 安全性测试
# ============================================================
def test_security(headers):
    print("\n🔒 安全性测试")
    module = "安全性"

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/personnel")
    if resp and resp.status_code == 401:
        record_result(module, "未认证访问拦截", "PASS", f"正确返回401", t)
    else:
        record_result(module, "未认证访问拦截", "FAIL", f"预期401, 实际: {resp.status_code if resp else 'Timeout'}", t, "P0-致命")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/personnel",
                            headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.expired"})
    if resp and resp.status_code == 401:
        record_result(module, "伪造Token拦截", "PASS", f"正确返回401", t)
    else:
        record_result(module, "伪造Token拦截", "FAIL", f"预期401, 实际: {resp.status_code if resp else 'Timeout'}", t, "P0-致命")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/personnel",
                            headers={"Authorization": "Bearer " + "A" * 500})
    if resp and resp.status_code == 401:
        record_result(module, "超长Token拦截", "PASS", f"正确返回401", t)
    else:
        record_result(module, "超长Token拦截", "FAIL", f"预期401, 实际: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    sql_injection_payloads = [
        "' OR 1=1 --",
        "'; DROP TABLE personnel; --",
        "1 UNION SELECT * FROM personnel --",
        "<script>alert('xss')</script>",
        "../../../etc/passwd",
    ]
    for payload in sql_injection_payloads:
        resp, t = timed_request("post", f"{BASE_URL}{API_PREFIX}/auth/login-json",
                                json={"username": payload, "password": "test", "device_type": "pc"})
        if resp and resp.status_code in [401, 422, 400]:
            record_result(module, f"注入攻击防护-{payload[:20]}", "PASS", f"正确拦截", t)
        else:
            record_result(module, f"注入攻击防护-{payload[:20]}", "FAIL",
                          f"预期401/422/400, 实际: {resp.status_code if resp else 'Timeout'}", t, "P0-致命")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/project-info?page=1&page_size=-1", headers=headers)
    if resp and resp.status_code in [200, 400, 422]:
        record_result(module, "负数分页参数", "PASS", f"状态码: {resp.status_code}", t)
    else:
        record_result(module, "负数分页参数", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/project-info?page=1&page_size=999999", headers=headers)
    if resp and resp.status_code in [200, 400, 422]:
        record_result(module, "超大分页参数", "PASS", f"状态码: {resp.status_code}", t)
    else:
        record_result(module, "超大分页参数", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    resp, t = timed_request("get", f"{BASE_URL}/api/docs")
    if resp and resp.status_code == 404:
        record_result(module, "生产环境API文档禁用", "PASS", f"Swagger文档已禁用", t)
    else:
        record_result(module, "生产环境API文档禁用", "FAIL", f"Swagger文档不应在生产环境暴露", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}/")
    if resp:
        has_security_headers = (
            resp.headers.get("X-Content-Type-Options") or
            resp.headers.get("x-content-type-options")
        )
        if has_security_headers:
            record_result(module, "安全响应头-X-Content-Type-Options", "PASS", f"存在安全头", t)
        else:
            record_result(module, "安全响应头-X-Content-Type-Options", "FAIL", f"缺少X-Content-Type-Options头", t, "P2-一般")
    else:
        record_result(module, "安全响应头检查", "SKIP", "请求超时", 0)

    resp, t = timed_request("get", f"{BASE_URL}/")
    if resp:
        hsts = resp.headers.get("Strict-Transport-Security") or resp.headers.get("strict-transport-security")
        if hsts:
            record_result(module, "HSTS安全头", "PASS", f"HSTS已配置: {hsts}", t)
        else:
            record_result(module, "HSTS安全头", "FAIL", f"缺少Strict-Transport-Security头", t, "P2-一般")

    resp, t = timed_request("options", f"{BASE_URL}{API_PREFIX}/auth/login-json")
    if resp:
        cors_header = resp.headers.get("Access-Control-Allow-Origin")
        if cors_header and cors_header != "*":
            record_result(module, "CORS配置-非通配符", "PASS", f"CORS: {cors_header}", t)
        elif cors_header == "*":
            record_result(module, "CORS配置-通配符", "FAIL", f"CORS允许所有来源(*), 存在安全风险", t, "P2-一般")
        else:
            record_result(module, "CORS配置", "PASS", f"OPTIONS请求正常", t)

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/health")
    if resp and resp.status_code == 200:
        data = resp.json()
        if "password" not in str(data) and "secret" not in str(data).lower():
            record_result(module, "健康检查-无敏感信息泄露", "PASS", f"未发现敏感信息", t)
        else:
            record_result(module, "健康检查-无敏感信息泄露", "FAIL", f"可能泄露敏感信息", t, "P1-严重")
    else:
        record_result(module, "健康检查-无敏感信息泄露", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    resp, t = timed_request("get", f"{BASE_URL}/.env")
    if resp and resp.status_code == 404:
        record_result(module, ".env文件不可访问", "PASS", f"正确返回404", t)
    else:
        record_result(module, ".env文件不可访问", "FAIL", f".env文件可能被暴露!", t, "P0-致命")

    resp, t = timed_request("get", f"{BASE_URL}/.git/config")
    if resp and resp.status_code == 404:
        record_result(module, ".git目录不可访问", "PASS", f"正确返回404", t)
    else:
        record_result(module, ".git目录不可访问", "FAIL", f".git目录可能被暴露!", t, "P0-致命")


# ============================================================
# 12. 性能测试
# ============================================================
def test_performance(headers):
    print("\n⚡ 性能测试")
    module = "性能"

    perf_endpoints = [
        ("健康检查", "get", f"{BASE_URL}{API_PREFIX}/health", None),
        ("项目列表", "get", f"{BASE_URL}{API_PREFIX}/project-info", headers),
        ("人员列表", "get", f"{BASE_URL}{API_PREFIX}/personnel", headers),
        ("工单列表", "get", f"{BASE_URL}{API_PREFIX}/work-order", headers),
        ("维保计划", "get", f"{BASE_URL}{API_PREFIX}/maintenance-plan", headers),
        ("统计概览", "get", f"{BASE_URL}{API_PREFIX}/statistics/overview", headers),
        ("临时维修", "get", f"{BASE_URL}{API_PREFIX}/temporary-repair", headers),
        ("定期巡检", "get", f"{BASE_URL}{API_PREFIX}/periodic-inspection", headers),
        ("零星用工", "get", f"{BASE_URL}{API_PREFIX}/spot-work", headers),
        ("周报列表", "get", f"{BASE_URL}{API_PREFIX}/weekly-report", headers),
    ]

    for name, method, url, hdrs in perf_endpoints:
        times = []
        for _ in range(5):
            resp, t = timed_request(method, url, headers=hdrs, timeout=10)
            if resp and resp.status_code == 200:
                times.append(t)
        if times:
            avg_time = statistics.mean(times)
            max_time = max(times)
            min_time = min(times)
            p95 = sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else max(times)
            status = "PASS" if avg_time < 2.0 else ("FAIL" if avg_time > 5.0 else "WARN")
            severity = "P1-严重" if avg_time > 5.0 else ("P2-一般" if avg_time > 2.0 else "")
            record_result(module, f"{name} - 平均{avg_time*1000:.0f}ms",
                          status if status != "WARN" else "PASS",
                          f"平均: {avg_time*1000:.0f}ms, 最大: {max_time*1000:.0f}ms, 最小: {min_time*1000:.0f}ms",
                          avg_time, severity)
        else:
            record_result(module, name, "FAIL", "所有请求失败", 0, "P1-严重")

    print("\n  🔄 并发测试 (10并发请求)...")
    concurrent_results = []
    def concurrent_request(url, hdrs):
        start = time.time()
        try:
            resp = requests.get(url, headers=hdrs, timeout=15)
            elapsed = time.time() - start
            concurrent_results.append({"status": resp.status_code, "time": elapsed})
        except Exception as e:
            concurrent_results.append({"status": "error", "time": time.time() - start, "error": str(e)})

    threads = []
    for _ in range(10):
        t = threading.Thread(target=concurrent_request,
                             args=(f"{BASE_URL}{API_PREFIX}/project-info", headers))
        threads.append(t)

    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=20)
    total_time = time.time() - start

    success_count = sum(1 for r in concurrent_results if r.get("status") == 200)
    if success_count == 10:
        avg_time = statistics.mean([r["time"] for r in concurrent_results if r.get("status") == 200])
        record_result(module, f"10并发-项目列表", "PASS",
                      f"全部成功, 平均: {avg_time*1000:.0f}ms, 总耗时: {total_time*1000:.0f}ms",
                      avg_time)
    else:
        record_result(module, f"10并发-项目列表", "FAIL",
                      f"成功: {success_count}/10, 总耗时: {total_time*1000:.0f}ms",
                      total_time, "P1-严重")


# ============================================================
# 13. 兼容性测试
# ============================================================
def test_compatibility(headers):
    print("\n🌐 兼容性测试")
    module = "兼容性"

    user_agents = {
        "Chrome桌面": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Firefox桌面": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Safari桌面": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Edge桌面": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "iPhone Safari": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Android Chrome": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "微信浏览器": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.44",
        "钉钉浏览器": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 DingTalk/7.6.0",
    }

    for ua_name, ua_string in user_agents.items():
        resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/health",
                                headers={"User-Agent": ua_string})
        if resp and resp.status_code == 200:
            record_result(module, f"{ua_name}兼容性", "PASS", f"状态码200", t)
        else:
            record_result(module, f"{ua_name}兼容性", "FAIL",
                          f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    resp, t = timed_request("get", f"{BASE_URL}/")
    if resp:
        content_type = resp.headers.get("Content-Type", "")
        if "utf-8" in content_type.lower() or "text/html" in content_type:
            record_result(module, "UTF-8编码支持", "PASS", f"Content-Type: {content_type}", t)
        else:
            record_result(module, "UTF-8编码支持", "FAIL", f"Content-Type: {content_type}", t, "P2-一般")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/project-info",
                            headers={**headers, "Accept": "application/xml"})
    if resp and resp.status_code in [200, 406]:
        record_result(module, "非JSON Accept头处理", "PASS", f"状态码: {resp.status_code}", t)
    else:
        record_result(module, "非JSON Accept头处理", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P3-轻微")

    resp, t = timed_request("post", f"{BASE_URL}{API_PREFIX}/auth/login-json",
                            data="username=test&password=test",
                            headers={"Content-Type": "application/x-www-form-urlencoded"})
    if resp and resp.status_code in [401, 422, 400]:
        record_result(module, "表单格式请求处理", "PASS", f"正确处理非JSON格式", t)
    else:
        record_result(module, "表单格式请求处理", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P3-轻微")


# ============================================================
# 14. 易用性测试
# ============================================================
def test_usability(headers):
    print("\n👤 易用性测试")
    module = "易用性"

    resp, t = timed_request("post", f"{BASE_URL}{API_PREFIX}/auth/login-json",
                            json={"username": "wrong", "password": "wrong", "device_type": "pc"})
    if resp:
        data = resp.json()
        error_msg = data.get("message", data.get("detail", ""))
        if error_msg and len(str(error_msg)) > 0:
            record_result(module, "错误信息可读性", "PASS", f"错误信息: {error_msg}", t)
        else:
            record_result(module, "错误信息可读性", "FAIL", f"错误信息不明确", t, "P2-一般")

    resp, t = timed_request("post", f"{BASE_URL}{API_PREFIX}/auth/login-json", json={})
    if resp and resp.status_code == 422:
        data = resp.json()
        if "errors" in str(data) or "field" in str(data).lower():
            record_result(module, "参数验证错误详情", "PASS", f"返回字段级错误信息", t)
        else:
            record_result(module, "参数验证错误详情", "FAIL", f"缺少字段级错误信息", t, "P2-一般")
    else:
        record_result(module, "参数验证错误详情", "FAIL", f"预期422, 实际: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/project-info", headers=headers)
    if resp and resp.status_code == 200:
        data = resp.json()
        if "data" in data:
            record_result(module, "统一响应格式-data字段", "PASS", f"响应包含data字段", t)
        else:
            record_result(module, "统一响应格式-data字段", "FAIL", f"缺少统一data字段", t, "P2-一般")
        if "code" in data:
            record_result(module, "统一响应格式-code字段", "PASS", f"响应包含code字段", t)
        else:
            record_result(module, "统一响应格式-code字段", "FAIL", f"缺少统一code字段", t, "P2-一般")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/project-info?page=1&page_size=10", headers=headers)
    if resp and resp.status_code == 200:
        data = resp.json().get("data", {})
        has_pagination = any(k in data for k in ["total", "items", "page", "page_size", "pages"])
        if has_pagination:
            record_result(module, "分页信息完整性", "PASS", f"包含分页字段", t)
        else:
            record_result(module, "分页信息完整性", "FAIL", f"缺少分页信息", t, "P2-一般")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/project-info", headers=headers)
    if resp and resp.status_code == 200:
        ct = resp.headers.get("Content-Type", "")
        if "application/json" in ct:
            record_result(module, "JSON响应Content-Type", "PASS", f"Content-Type: {ct}", t)
        else:
            record_result(module, "JSON响应Content-Type", "FAIL", f"Content-Type: {ct}", t, "P3-轻微")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/health")
    if resp and resp.status_code == 200:
        data = resp.json()
        if "version" in data:
            record_result(module, "版本号可查询", "PASS", f"版本: {data.get('version')}", t)
        else:
            record_result(module, "版本号可查询", "FAIL", f"健康检查缺少版本号", t, "P3-轻微")


# ============================================================
# 15. 回归测试 - 已知Bug验证
# ============================================================
def test_regression(headers):
    print("\n🔄 回归测试")
    module = "回归测试"

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/spot-work/workers", headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "零星用工-施工人员API可用", "PASS", f"之前saveWorkers Bug已修复", t)
    else:
        record_result(module, "零星用工-施工人员API可用", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    new_worker = {
        "name": f"回归测试工人_{datetime.now().strftime('%H%M%S')}",
        "id_card_number": "110101199001011234",
        "phone": "13800001111",
    }
    resp, t = timed_request("post", f"{BASE_URL}{API_PREFIX}/spot-work/workers",
                            json=new_worker, headers=headers)
    if resp and resp.status_code == 200:
        record_result(module, "零星用工-保存施工人员", "PASS", f"saveWorkers功能正常", t)
    else:
        record_result(module, "零星用工-保存施工人员", "FAIL",
                      f"状态码: {resp.status_code if resp else 'Timeout'}, 响应: {resp.text[:200] if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("post", f"{BASE_URL}{API_PREFIX}/auth/login-json",
                            json={"username": TEST_USER["username"], "password": TEST_USER["password"], "device_type": "pc"})
    if resp and resp.status_code == 200:
        data = resp.json().get("data", {})
        user_info = data.get("user", {})
        if "must_change_password" in user_info:
            record_result(module, "登录返回must_change_password字段", "PASS", f"字段存在", t)
        else:
            record_result(module, "登录返回must_change_password字段", "FAIL", f"缺少must_change_password字段", t, "P2-一般")
    else:
        record_result(module, "登录返回must_change_password字段", "FAIL", f"登录失败", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}{API_PREFIX}/health")
    if resp and resp.status_code == 200:
        data = resp.json()
        record_result(module, "健康检查端点可用", "PASS", f"状态: {data.get('status')}", t)
    else:
        record_result(module, "健康检查端点可用", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P1-严重")

    resp, t = timed_request("get", f"{BASE_URL}/")
    if resp and resp.status_code == 200:
        try:
            data = resp.json()
            if "version" in data:
                record_result(module, "版本号显示正确", "PASS", f"版本: {data.get('version')}", t)
            else:
                record_result(module, "版本号显示正确", "FAIL", f"缺少版本号", t, "P2-一般")
        except Exception:
            record_result(module, "版本号显示正确", "FAIL", f"响应解析失败", t, "P2-一般")
    else:
        record_result(module, "版本号显示正确", "FAIL", f"状态码: {resp.status_code if resp else 'Timeout'}", t, "P2-一般")


# ============================================================
# 主函数
# ============================================================
def main():
    print("=" * 70)
    print("  SSTCP维保管理系统 - 全面测试套件")
    print(f"  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  测试目标: {BASE_URL}")
    print("=" * 70)

    print("\n🔑 获取认证Token...")
    token = get_auth_token()
    if not token:
        print("❌ 无法获取认证Token，测试终止！")
        return

    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Token获取成功")

    print("\n" + "=" * 70)
    print("  开始执行测试")
    print("=" * 70)

    test_auth_module(headers)
    test_project_info_module(headers)
    test_personnel_module(headers)
    test_work_order_modules(headers)
    test_maintenance_plan_module(headers)
    test_spare_parts_module(headers)
    test_repair_tools_module(headers)
    test_statistics_module(headers)
    test_weekly_report_and_log(headers)
    test_other_modules(headers)
    test_security(headers)
    test_performance(headers)
    test_compatibility(headers)
    test_usability(headers)
    test_regression(headers)

    print("\n" + "=" * 70)
    print("  测试结果汇总")
    print("=" * 70)
    print(f"  总测试数: {results['total']}")
    print(f"  通过: {results['passed']} ✅")
    print(f"  失败: {results['failed']} ❌")
    print(f"  跳过: {results['skipped']} ⏭️")
    pass_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"  通过率: {pass_rate:.1f}%")

    if results["defects"]:
        print(f"\n  🐛 发现缺陷: {len(results['defects'])}个")
        severity_counts = {}
        for d in results["defects"]:
            sev = d["severity"]
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        for sev, count in sorted(severity_counts.items()):
            print(f"    {sev}: {count}个")

    perf_data = [p for p in results["performance"] if p["response_time_ms"] > 0]
    if perf_data:
        times = [p["response_time_ms"] for p in perf_data]
        print(f"\n  ⚡ 性能统计:")
        print(f"    平均响应时间: {statistics.mean(times):.0f}ms")
        print(f"    最大响应时间: {max(times):.0f}ms")
        print(f"    最小响应时间: {min(times):.0f}ms")

    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n  📄 详细测试报告已保存: {report_path}")


if __name__ == "__main__":
    main()
