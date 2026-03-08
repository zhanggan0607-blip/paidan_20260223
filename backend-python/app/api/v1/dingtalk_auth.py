"""
钉钉认证API接口
提供钉钉免登认证功能
"""
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import create_access_token
from app.database import get_db
from app.dependencies import UserInfo, get_manager_user
from app.models.online_user import OnlineUser
from app.models.personnel import Personnel
from app.schemas.common import ApiResponse
from app.services.dingtalk_service import DingTalkService, get_dingtalk_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dingtalk", tags=["DingTalk Authentication"])


class DingTalkLoginRequest(BaseModel):
    auth_code: str
    device_type: str = "h5"


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def record_user_login(db: Session, user: Personnel, device_type: str, ip_address: str):
    """
    记录用户登录到在线用户表
    """
    from sqlalchemy import and_

    existing = db.query(OnlineUser).filter(
        and_(
            OnlineUser.user_id == user.id,
            OnlineUser.is_active
        )
    ).first()

    now = datetime.utcnow()

    if existing:
        existing.last_activity = now
        existing.login_time = now
        existing.ip_address = ip_address
        existing.device_type = device_type
        existing.department = user.department
        existing.role = user.role
    else:
        online_user = OnlineUser(
            user_id=user.id,
            user_name=user.name,
            department=user.department,
            role=user.role,
            login_time=now,
            last_activity=now,
            ip_address=ip_address,
            device_type=device_type,
            is_active=True
        )
        db.add(online_user)

    db.commit()


@router.post("/login", response_model=ApiResponse)
def dingtalk_login(
    request: Request,
    login_req: DingTalkLoginRequest,
    db: Session = Depends(get_db)
):
    """
    钉钉免登接口
    通过钉钉授权码获取用户信息并完成登录

    Args:
        login_req: 包含auth_code的请求体

    Returns:
        ApiResponse: 包含JWT token和用户信息
    """
    try:
        dingtalk_service = get_dingtalk_service()

        user_info = dingtalk_service.get_user_info_by_code(login_req.auth_code)
        userid = user_info.get("userid")

        if not userid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="钉钉授权失败，无法获取用户ID"
            )

        user_detail = dingtalk_service.get_user_detail(userid)

        dingtalk_name = user_detail.get("name", "")
        dingtalk_mobile = user_detail.get("mobile", "")
        dingtalk_dept = user_detail.get("dept_name", "") or user_detail.get("main_dept_name", "")
        dingtalk_avatar = user_detail.get("avatar", "")
        dingtalk_title = user_detail.get("title", "")
        dingtalk_unionid = user_detail.get("unionid", "")

        user = db.query(Personnel).filter(Personnel.dingtalk_userid == userid).first()

        if not user:
            user = db.query(Personnel).filter(Personnel.phone == dingtalk_mobile).first()

            if user:
                user.dingtalk_userid = userid
                user.dingtalk_unionid = dingtalk_unionid
                user.dingtalk_avatar = dingtalk_avatar
                user.dingtalk_title = dingtalk_title
                user.is_synced = True
            else:
                system_role = DingTalkService.map_role_to_system(dingtalk_title)

                user = Personnel(
                    name=dingtalk_name,
                    gender="男",
                    phone=dingtalk_mobile,
                    department=dingtalk_dept,
                    role=system_role,
                    dingtalk_userid=userid,
                    dingtalk_unionid=dingtalk_unionid,
                    dingtalk_avatar=dingtalk_avatar,
                    dingtalk_title=dingtalk_title,
                    is_synced=True,
                    must_change_password=True
                )
                db.add(user)

        if not user.department and dingtalk_dept:
            user.department = dingtalk_dept
        if not user.dingtalk_avatar and dingtalk_avatar:
            user.dingtalk_avatar = dingtalk_avatar
        if dingtalk_title and user.dingtalk_title != dingtalk_title:
            user.dingtalk_title = dingtalk_title

        db.commit()
        db.refresh(user)

        access_token = create_access_token(
            data={
                "sub": user.name,
                "name": user.name,
                "role": user.role,
                "user_id": user.id
            }
        )

        client_ip = get_client_ip(request)
        device_type = login_req.device_type if login_req.device_type in ["pc", "h5"] else "h5"
        record_user_login(db, user, device_type, client_ip)

        return ApiResponse(
            code=200,
            message="钉钉登录成功",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "role": user.role,
                    "department": user.department,
                    "phone": user.phone,
                    "avatar": user.dingtalk_avatar
                }
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 钉钉登录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"钉钉登录失败，错误ID: {error_id}，请联系管理员"
        ) from None


@router.post("/sync-users", response_model=ApiResponse)
def sync_dingtalk_users(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    同步钉钉通讯录到本地数据库
    需要管理员或部门经理权限

    Returns:
        ApiResponse: 同步结果统计
    """
    try:
        dingtalk_service = get_dingtalk_service()

        all_users = dingtalk_service.get_all_users()

        added_count = 0
        updated_count = 0
        skipped_count = 0

        for dingtalk_user in all_users:
            userid = dingtalk_user.get("userid")
            name = dingtalk_user.get("name", "")
            mobile = dingtalk_user.get("mobile", "")
            dept_name = dingtalk_user.get("dept_name", "")
            avatar = dingtalk_user.get("avatar", "")
            title = dingtalk_user.get("title", "")
            unionid = dingtalk_user.get("unionid", "")

            if not userid or not name:
                skipped_count += 1
                continue

            existing = db.query(Personnel).filter(
                (Personnel.dingtalk_userid == userid) | (Personnel.phone == mobile)
            ).first()

            if existing:
                existing.dingtalk_userid = userid
                existing.dingtalk_unionid = unionid
                existing.dingtalk_avatar = avatar
                existing.dingtalk_title = title
                existing.is_synced = True
                if dept_name and not existing.department:
                    existing.department = dept_name
                updated_count += 1
            else:
                system_role = DingTalkService.map_role_to_system(title)

                new_user = Personnel(
                    name=name,
                    gender="男",
                    phone=mobile,
                    department=dept_name,
                    role=system_role,
                    dingtalk_userid=userid,
                    dingtalk_unionid=unionid,
                    dingtalk_avatar=avatar,
                    dingtalk_title=title,
                    is_synced=True,
                    must_change_password=True
                )
                db.add(new_user)
                added_count += 1

        db.commit()

        return ApiResponse(
            code=200,
            message="同步完成",
            data={
                "total": len(all_users),
                "added": added_count,
                "updated": updated_count,
                "skipped": skipped_count
            }
        )

    except Exception as e:
        db.rollback()
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 钉钉用户同步失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步失败，错误ID: {error_id}，请联系管理员"
        ) from None


@router.get("/check-config", response_model=ApiResponse)
def check_dingtalk_config():
    """
    检查钉钉配置是否正确

    Returns:
        ApiResponse: 配置状态
    """
    try:
        dingtalk_service = get_dingtalk_service()

        if not dingtalk_service.app_key:
            return ApiResponse(
                code=400,
                message="钉钉AppKey未配置",
                data={"configured": False}
            )

        if not dingtalk_service.app_secret:
            return ApiResponse(
                code=400,
                message="钉钉AppSecret未配置",
                data={"configured": False}
            )

        access_token = dingtalk_service.get_access_token()

        return ApiResponse(
            code=200,
            message="钉钉配置正常",
            data={
                "configured": True,
                "has_token": bool(access_token)
            }
        )

    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 钉钉配置检查异常: {str(e)}")
        return ApiResponse(
            code=400,
            message=f"钉钉配置异常，错误ID: {error_id}，请联系管理员",
            data={"configured": False}
        )
