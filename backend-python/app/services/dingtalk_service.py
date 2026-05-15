import time
from typing import Any

import requests

from app.config import get_settings
from app.utils.logging_config import log_external_call


class DingTalkService:

    def __init__(self):
        self.settings = get_settings()
        self.app_key = self.settings.dingtalk_app_key
        self.app_secret = self.settings.dingtalk_app_secret
        self.agent_id = self.settings.dingtalk_agent_id
        self._access_token: str | None = None
        self._token_expire_time: int = 0

    @log_external_call("钉钉-获取Token")
    def get_access_token(self) -> str:
        current_time = int(time.time())

        if self._access_token and current_time < self._token_expire_time:
            return self._access_token

        url = "https://oapi.dingtalk.com/gettoken"
        params = {
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }

        response = requests.get(url, params=params, timeout=10)
        result = response.json()

        if result.get("errcode") != 0:
            raise Exception(f"获取钉钉access_token失败: {result.get('errmsg')}")

        self._access_token = result.get("access_token")
        self._token_expire_time = current_time + result.get("expires_in", 7200) - 300

        return self._access_token

    @log_external_call("钉钉-用户信息")
    def get_user_info_by_code(self, auth_code: str) -> dict[str, Any]:
        access_token = self.get_access_token()

        url = "https://oapi.dingtalk.com/user/getuserinfo"
        params = {
            "access_token": access_token,
            "code": auth_code
        }

        response = requests.get(url, params=params, timeout=10)
        result = response.json()

        if result.get("errcode") != 0:
            raise Exception(f"获取用户信息失败: {result.get('errmsg')}")

        return result

    @log_external_call("钉钉-用户详情")
    def get_user_detail(self, userid: str) -> dict[str, Any]:
        access_token = self.get_access_token()

        url = "https://oapi.dingtalk.com/topapi/v2/user/get"
        params = {"access_token": access_token}
        data = {"userid": userid}

        response = requests.post(url, params=params, json=data, timeout=10)
        result = response.json()

        if result.get("errcode") != 0:
            raise Exception(f"获取用户详情失败: {result.get('errmsg')}")

        return result.get("result", {})

    def get_department_list(self, dept_id: int = 1) -> list[dict[str, Any]]:
        access_token = self.get_access_token()

        url = "https://oapi.dingtalk.com/topapi/v2/department/listsub"
        params = {"access_token": access_token}
        data = {"dept_id": dept_id}

        response = requests.post(url, params=params, json=data, timeout=10)
        result = response.json()

        if result.get("errcode") != 0:
            raise Exception(f"获取部门列表失败: {result.get('errmsg')}")

        return result.get("result", [])

    def get_department_users(self, dept_id: int, cursor: int = 0, size: int = 100) -> dict[str, Any]:
        access_token = self.get_access_token()

        url = "https://oapi.dingtalk.com/topapi/v2/user/list"
        params = {"access_token": access_token}
        data = {
            "dept_id": dept_id,
            "cursor": cursor,
            "size": size
        }

        response = requests.post(url, params=params, json=data, timeout=10)
        result = response.json()

        if result.get("errcode") != 0:
            raise Exception(f"获取部门用户失败: {result.get('errmsg')}")

        return result.get("result", {})

    def get_all_users(self) -> list[dict[str, Any]]:
        all_users = []

        def fetch_dept_users(dept_id: int):
            cursor = 0
            while True:
                result = self.get_department_users(dept_id, cursor)
                users = result.get("user_list", [])
                all_users.extend(users)

                if not result.get("has_more"):
                    break
                cursor = result.get("next_cursor", 0)

        def fetch_all_depts(dept_id: int):
            fetch_dept_users(dept_id)

            sub_depts = self.get_department_list(dept_id)
            for dept in sub_depts:
                fetch_all_depts(dept.get("dept_id"))

        fetch_all_depts(1)

        return all_users

    @staticmethod
    def map_role_to_system(title: str | None) -> str:
        return "运维人员"


_dingtalk_service: DingTalkService | None = None


def get_dingtalk_service() -> DingTalkService:
    global _dingtalk_service
    if _dingtalk_service is None:
        _dingtalk_service = DingTalkService()
    return _dingtalk_service
