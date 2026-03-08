"""
API接口测试验证脚本
测试所有修改的接口是否正常工作
"""
import requests
import json
from typing import Optional, Dict, Any

BASE_URL = "http://localhost:8000/api/v1"

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"✅ {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ {test_name}: {error}")
    
    def print_summary(self):
        print("\n" + "=" * 60)
        print(f"测试结果: 通过 {self.passed}, 失败 {self.failed}")
        if self.errors:
            print("\n失败详情:")
            for error in self.errors:
                print(f"  - {error}")
        print("=" * 60)


def test_health_check(result: TestResult):
    """测试健康检查接口"""
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        if response.status_code == 200:
            result.add_pass("健康检查接口")
        else:
            result.add_fail("健康检查接口", f"状态码: {response.status_code}")
    except Exception as e:
        result.add_fail("健康检查接口", str(e))


def test_login(result: TestResult) -> Optional[str]:
    """测试登录接口"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login-json",
            json={"username": "管理员", "password": "123456", "device_type": "pc"}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200 and data.get("data", {}).get("access_token"):
                result.add_pass("登录接口")
                return data["data"]["access_token"]
            else:
                result.add_fail("登录接口", f"响应格式错误: {data}")
        else:
            result.add_fail("登录接口", f"状态码: {response.status_code}")
    except Exception as e:
        result.add_fail("登录接口", str(e))
    return None


def test_login_invalid(result: TestResult):
    """测试登录接口 - 无效凭据"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login-json",
            json={"username": "invalid_user", "password": "wrong_password", "device_type": "pc"}
        )
        if response.status_code == 401:
            result.add_pass("登录接口 - 无效凭据拒绝")
        else:
            result.add_fail("登录接口 - 无效凭据拒绝", f"应该返回401，实际返回: {response.status_code}")
    except Exception as e:
        result.add_fail("登录接口 - 无效凭据拒绝", str(e))


def test_protected_endpoint_without_token(result: TestResult):
    """测试无token访问受保护接口"""
    try:
        response = requests.get(f"{BASE_URL}/auth/me")
        if response.status_code == 401:
            result.add_pass("无token访问受保护接口被拒绝")
        else:
            result.add_fail("无token访问受保护接口被拒绝", f"应该返回401，实际返回: {response.status_code}")
    except Exception as e:
        result.add_fail("无token访问受保护接口被拒绝", str(e))


def test_protected_endpoint_with_token(result: TestResult, token: str):
    """测试有token访问受保护接口"""
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200 and data.get("data"):
                result.add_pass("有token访问受保护接口成功")
            else:
                result.add_fail("有token访问受保护接口成功", f"响应格式错误: {data}")
        else:
            result.add_fail("有token访问受保护接口成功", f"状态码: {response.status_code}")
    except Exception as e:
        result.add_fail("有token访问受保护接口成功", str(e))


def test_migrate_endpoint_without_token(result: TestResult):
    """测试无token访问迁移接口"""
    try:
        response = requests.post(f"{BASE_URL.replace('/api/v1', '')}/migrate/add-indexes")
        if response.status_code == 401:
            result.add_pass("迁移接口无token被拒绝")
        else:
            result.add_fail("迁移接口无token被拒绝", f"应该返回401，实际返回: {response.status_code}")
    except Exception as e:
        result.add_fail("迁移接口无token被拒绝", str(e))


def test_spare_parts_usage_without_token(result: TestResult):
    """测试无token访问备件领用接口"""
    try:
        response = requests.post(
            f"{BASE_URL}/spare-parts/usage",
            json={
                "product_name": "测试备件",
                "quantity": 1,
                "user_name": "测试用户",
                "issue_time": "2026-03-07"
            }
        )
        if response.status_code == 401:
            result.add_pass("备件领用接口无token被拒绝")
        else:
            result.add_fail("备件领用接口无token被拒绝", f"应该返回401，实际返回: {response.status_code}")
    except Exception as e:
        result.add_fail("备件领用接口无token被拒绝", str(e))


def test_spare_parts_usage_with_token(result: TestResult, token: str):
    """测试有token访问备件领用接口 - 无库存"""
    try:
        response = requests.post(
            f"{BASE_URL}/spare-parts/usage",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "product_name": "不存在的备件_测试",
                "quantity": 1,
                "user_name": "测试用户",
                "issue_time": "2026-03-07"
            }
        )
        if response.status_code == 400:
            result.add_pass("备件领用接口 - 无库存时正确拒绝")
        else:
            result.add_fail("备件领用接口 - 无库存时正确拒绝", f"应该返回400，实际返回: {response.status_code}")
    except Exception as e:
        result.add_fail("备件领用接口 - 无库存时正确拒绝", str(e))


def test_change_password(result: TestResult, token: str):
    """测试修改密码接口"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "old_password": "123456",
                "new_password": "12345678"
            }
        )
        if response.status_code == 400:
            result.add_pass("修改密码接口 - 新旧密码相同被拒绝")
        elif response.status_code == 200:
            result.add_pass("修改密码接口 - 成功")
        else:
            result.add_fail("修改密码接口", f"状态码: {response.status_code}")
    except Exception as e:
        result.add_fail("修改密码接口", str(e))


def test_header_auth_disabled(result: TestResult):
    """测试请求头认证已禁用"""
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={
                "X-User-Name": "管理员",
                "X-User-Role": "管理员"
            }
        )
        if response.status_code == 401:
            result.add_pass("请求头认证已禁用 - 无token时正确拒绝")
        else:
            result.add_fail("请求头认证已禁用 - 无token时正确拒绝", f"应该返回401，实际返回: {response.status_code}")
    except Exception as e:
        result.add_fail("请求头认证已禁用 - 无token时正确拒绝", str(e))


def main():
    print("=" * 60)
    print("API接口测试验证")
    print("=" * 60)
    print()
    
    result = TestResult()
    
    print("1. 基础接口测试")
    print("-" * 40)
    test_health_check(result)
    
    print("\n2. 认证接口测试")
    print("-" * 40)
    test_login_invalid(result)
    test_header_auth_disabled(result)
    token = test_login(result)
    
    print("\n3. 受保护接口测试")
    print("-" * 40)
    test_protected_endpoint_without_token(result)
    if token:
        test_protected_endpoint_with_token(result, token)
    
    print("\n4. 迁移接口安全测试")
    print("-" * 40)
    test_migrate_endpoint_without_token(result)
    
    print("\n5. 备件接口测试")
    print("-" * 40)
    test_spare_parts_usage_without_token(result)
    if token:
        test_spare_parts_usage_with_token(result, token)
    
    print("\n6. 密码接口测试")
    print("-" * 40)
    if token:
        test_change_password(result, token)
    
    result.print_summary()


if __name__ == "__main__":
    main()
