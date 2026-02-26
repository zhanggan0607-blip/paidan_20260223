import sys
sys.path.insert(0, 'D:\\共享文件\\SSTCP-paidan260120\\backend-python')

from app.auth import get_current_user_from_headers
from starlette.requests import Request

class MockRequest:
    def __init__(self, headers):
        self._headers = headers
    
    @property
    def headers(self):
        return self._headers

headers = {"X-User-Name": "admin", "X-User-Role": "admin"}
mock_request = MockRequest(headers)
user_info = get_current_user_from_headers(mock_request)
print(f"User info: {user_info}")

if user_info:
    user_name = user_info.get('sub') or user_info.get('name')
    role = user_info.get('role', '')
    is_manager = role in ['管理员', '部门经理', '主管']
    print(f"User name: {user_name}")
    print(f"Role: {role}")
    print(f"Is manager: {is_manager}")
