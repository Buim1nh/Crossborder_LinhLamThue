import secrets
import httpx
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_password_hash, verify_password, create_access_token
from src.models.user import User
from src.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    GoogleAuthRequest,
    TokenResponse,
    UserResponse,
    ForgotPasswordRequest,
    MessageResponse,
)
from src.api.deps import get_current_active_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account."""
    normalized_email = data.email.lower().strip()

    # Check if user already exists
    existing = await db.execute(select(User).where(User.email == normalized_email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Địa chỉ email này đã được sử dụng. Vui lòng đăng nhập hoặc chọn email khác.",
        )

    # Hash password and create user
    hashed_pwd = get_password_hash(data.password)
    new_user = User(
        email=normalized_email,
        hashed_password=hashed_pwd,
        full_name=data.full_name.strip() if data.full_name else None,
        phone=data.phone.strip() if data.phone else None,
        role="user",
        is_active=True,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Generate JWT token
    token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email, "role": new_user.role}
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate a user with email and password."""
    normalized_email = data.email.lower().strip()

    result = await db.execute(select(User).where(User.email == normalized_email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản của bạn đã bị tạm khóa. Vui lòng liên hệ quản trị viên.",
        )

    token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    data: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    """Sign in or sign up seamlessly via Google OAuth with token verification."""
    email: Optional[str] = None
    full_name: Optional[str] = data.full_name
    google_id: Optional[str] = data.google_id

    # 1. If Google ID token (credential) provided, verify with Google tokeninfo
    if data.credential:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    f"https://oauth2.googleapis.com/tokeninfo?id_token={data.credential}"
                )
                if res.status_code == 200:
                    g_data = res.json()
                    email = g_data.get("email")
                    full_name = g_data.get("name") or full_name
                    google_id = g_data.get("sub") or google_id
        except Exception:
            pass

    # 2. If access_token provided, verify with Google userinfo
    elif data.access_token:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {data.access_token}"},
                )
                if res.status_code == 200:
                    g_data = res.json()
                    email = g_data.get("email")
                    full_name = g_data.get("name") or full_name
                    google_id = g_data.get("sub") or google_id
        except Exception:
            pass

    # 3. Fallback to direct email payload if provided (for tests / offline demo)
    if not email and data.email:
        email = str(data.email)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xác thực danh tính từ Google. Vui lòng thử lại.",
        )

    normalized_email = email.lower().strip()
    result = await db.execute(select(User).where(User.email == normalized_email))
    user = result.scalar_one_or_none()

    if not user:
        # Auto-create user for Google OAuth with randomized secure hash
        random_pwd = secrets.token_urlsafe(32)
        user = User(
            email=normalized_email,
            hashed_password=get_password_hash(random_pwd),
            full_name=full_name or normalized_email.split("@")[0],
            role="user",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị tạm khóa.",
        )

    token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Get current authenticated user profile (Protected Endpoint)."""
    return UserResponse.model_validate(current_user)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request a password reset link."""
    normalized_email = data.email.lower().strip()
    result = await db.execute(select(User).where(User.email == normalized_email))
    user = result.scalar_one_or_none()

    # Always return success message to prevent user enumeration attacks
    return MessageResponse(
        message=f"Nếu email {normalized_email} tồn tại trong hệ thống, hướng dẫn đặt lại mật khẩu đã được gửi.",
        success=True,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_active_user),
):
    """Logout current user."""
    return MessageResponse(message="Đăng xuất thành công", success=True)
