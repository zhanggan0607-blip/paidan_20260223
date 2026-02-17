from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.schemas.common import ApiResponse
from app.models.personnel import Personnel
from app.auth import create_access_token, get_current_user, get_current_user_required

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    role: str = "运维人员"


@router.post("/login", response_model=ApiResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    使用OAuth2密码模式，用户名为人员姓名，密码默认为手机号后6位
    """
    user = db.query(Personnel).filter(Personnel.name == form_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    default_password = (user.phone or "")[-6:] if user.phone else "123456"
    
    if not user.phone:
        default_password = "123456"
    
    if form_data.password != default_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={
            "sub": user.name,
            "name": user.name,
            "role": user.role,
            "user_id": user.id
        }
    )
    
    return ApiResponse(
        code=200,
        message="登录成功",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "role": user.role,
                "department": user.department,
                "phone": user.phone
            }
        }
    )


@router.post("/login-json", response_model=ApiResponse)
def login_json(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录接口（JSON格式）
    用户名为人员姓名，密码默认为手机号后6位
    """
    user = db.query(Personnel).filter(Personnel.name == request.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    default_password = (user.phone or "")[-6:] if user.phone else "123456"
    
    if not user.phone:
        default_password = "123456"
    
    if request.password != default_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    access_token = create_access_token(
        data={
            "sub": user.name,
            "name": user.name,
            "role": user.role,
            "user_id": user.id
        }
    )
    
    return ApiResponse(
        code=200,
        message="登录成功",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "role": user.role,
                "department": user.department,
                "phone": user.phone
            }
        }
    )


@router.get("/me", response_model=ApiResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户信息
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户信息无效"
        )
    
    user = db.query(Personnel).filter(Personnel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            "id": user.id,
            "name": user.name,
            "role": user.role,
            "department": user.department,
            "phone": user.phone
        }
    )
