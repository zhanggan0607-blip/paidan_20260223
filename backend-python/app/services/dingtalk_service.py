"""
钉钉服务模块
提供钉钉API调用功能，包括免登认证、通讯录同步等
"""
import time
import hashlib
import requests
from typing import Optional, Dict, List, Any
from datetime import datetime
from functools import lru_cache
from app.config import get_settings


class DingTalkService:
    """
    钉钉服务类
    封装钉钉开放平台API调用
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.app_key = self.settings.dingtalk_app_key
        self.app_secret = self.settings.dingtalk_app_secret
        self.agent_id = self.settings.dingtalk_agent_id
        self._access_token: Optional[str] = None
        self._token_expire_time: int = 0
    
    def get_access_token(self) -> str:
        """
        获取企业access_token
        token有效期为2小时，自动缓存管理
        
        Returns:
            str: access_token
            
        Raises:
            Exception: 获取token失败时抛出异常
        """
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
    
    def get_user_info_by_code(self, auth_code: str) -> Dict[str, Any]:
        """
        通过免登授权码获取用户信息
        
        Args:
            auth_code: 钉钉免登授权码
            
        Returns:
            dict: 用户信息，包含userid等
            
        Raises:
            Exception: 获取失败时抛出异常
        """
        access_token = self.get_access_token()
        
        url = "https://oapi.dingtalk.com/topapi/v2/user/getuserinfo"
        headers = {"x-acs-dingtalk-access-token": access_token}
        data = {"code": auth_code}
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        
        if result.get("errcode") != 0:
            raise Exception(f"获取用户信息失败: {result.get('errmsg')}")
        
        return result.get("result", {})
    
    def get_user_detail(self, userid: str) -> Dict[str, Any]:
        """
        获取用户详细信息
        
        Args:
            userid: 钉钉用户ID
            
        Returns:
            dict: 用户详细信息
            
        Raises:
            Exception: 获取失败时抛出异常
        """
        access_token = self.get_access_token()
        
        url = "https://oapi.dingtalk.com/topapi/v2/user/get"
        headers = {"x-acs-dingtalk-access-token": access_token}
        data = {"userid": userid}
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        
        if result.get("errcode") != 0:
            raise Exception(f"获取用户详情失败: {result.get('errmsg')}")
        
        return result.get("result", {})
    
    def get_department_list(self, dept_id: int = 1) -> List[Dict[str, Any]]:
        """
        获取部门列表
        
        Args:
            dept_id: 父部门ID，根部门为1
            
        Returns:
            list: 部门列表
            
        Raises:
            Exception: 获取失败时抛出异常
        """
        access_token = self.get_access_token()
        
        url = "https://oapi.dingtalk.com/topapi/v2/department/listsub"
        headers = {"x-acs-dingtalk-access-token": access_token}
        data = {"dept_id": dept_id}
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        
        if result.get("errcode") != 0:
            raise Exception(f"获取部门列表失败: {result.get('errmsg')}")
        
        return result.get("result", [])
    
    def get_department_users(self, dept_id: int, cursor: int = 0, size: int = 100) -> Dict[str, Any]:
        """
        获取部门用户列表
        
        Args:
            dept_id: 部门ID
            cursor: 分页游标
            size: 每页大小，最大100
            
        Returns:
            dict: 包含用户列表和分页信息
            
        Raises:
            Exception: 获取失败时抛出异常
        """
        access_token = self.get_access_token()
        
        url = "https://oapi.dingtalk.com/topapi/v2/user/list"
        headers = {"x-acs-dingtalk-access-token": access_token}
        data = {
            "dept_id": dept_id,
            "cursor": cursor,
            "size": size
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        
        if result.get("errcode") != 0:
            raise Exception(f"获取部门用户失败: {result.get('errmsg')}")
        
        return result.get("result", {})
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        获取所有用户信息（递归获取所有部门的所有用户）
        
        Returns:
            list: 所有用户信息列表
        """
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
    def map_role_to_system(title: Optional[str]) -> str:
        """
        将钉钉职位映射到系统角色
        所有钉钉用户默认为运维人员，如需调整角色请在系统人员管理中修改
        
        Args:
            title: 钉钉职位名称
            
        Returns:
            str: 系统角色名称（固定返回"运维人员"）
        """
        return "运维人员"


_dingtalk_service: Optional[DingTalkService] = None


def get_dingtalk_service() -> DingTalkService:
    """
    获取钉钉服务实例（单例模式）
    
    Returns:
        DingTalkService: 钉钉服务实例
    """
    global _dingtalk_service
    if _dingtalk_service is None:
        _dingtalk_service = DingTalkService()
    return _dingtalk_service
