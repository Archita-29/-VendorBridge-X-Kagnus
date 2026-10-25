from fastapi import Response
from app.schemas.auth import LoginRequest
from app.services.auth import verify_password
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import hashlib
from fastapi import Request
import secrets
from app.models import UserSession
from app.services.session import get_current_user
from app.models import UserSession
from sqlalchemy import select, delete
from app.config import settings
from app.models import PasswordResetToken, User, UserSession
from app.schemas.auth import PasswordResetRequest, PasswordResetConfirm
from app.services.auth import hash_password
from app.database import get_db
from app.models import User
from app.schemas.auth import RegisterRequest, UserResponse
from app.services.auth import hash_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    email = str(payload.email).strip().lower()

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User(
        full_name=payload.full_name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        role="vendor",
        is_active=True,
    )

    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from None

    return user


@router.post("/login", response_model=UserResponse)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    email = str(payload.email).strip().lower()

    user = db.scalar(select(User).where(User.email == email))

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive",
        )

    # Generate a random session token; store only its SHA-256 hash.
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    session = UserSession(
        session_token_hash=token_hash,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=12),
    )

    db.add(session)
    db.commit()

    response.set_cookie(
        key="vendorbridge_session",
        value=token,
        httponly=True,
        secure=False,  # Set to True when deployed over HTTPS.
        samesite="lax",
        max_age=12 * 60 * 60,
        path="/",
    )

    return user

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user



@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
):
    token = request.cookies.get("vendorbridge_session")

    if token:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        session = db.scalar(
            select(UserSession).where(
                UserSession.session_token_hash == token_hash
            )
        )

        if session:
            db.delete(session)
            db.commit()

    response.delete_cookie(
        key="vendorbridge_session",
        path="/",
        httponly=True,
        secure=False,
        samesite="lax",
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response

@router.post("/forgot-password")
def forgot_password(
    payload: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    email = str(payload.email).strip().lower()
    user = db.scalar(select(User).where(User.email == email))

    # Same public response whether the account exists or not.
    result = {
        "message": "If an account exists, reset instructions will be provided."
    }

    if not user or not user.is_active:
        return result

    now = datetime.now(timezone.utc)
    raw_token = secrets.token_urlsafe(32)

    # Invalidate earlier unused reset tokens for this user.
    db.execute(
        delete(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
    )

    reset_record = PasswordResetToken(
        token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
        user_id=user.id,
        expires_at=now + timedelta(minutes=30),
    )

    db.add(reset_record)
    db.commit()

    # Development-only convenience; never expose tokens in production.
    if (
        settings.app_env.lower() == "development"
        and settings.expose_reset_token
    ):
        result["reset_token"] = raw_token

    return result

@router.post("/reset-password")
def reset_password(
    payload: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    token_hash = hashlib.sha256(payload.token.encode()).hexdigest()

    reset_record = db.scalar(
        select(PasswordResetToken)
        .where(PasswordResetToken.token_hash == token_hash)
        .with_for_update()
    )

    now = datetime.now(timezone.utc)

    if (
        not reset_record
        or reset_record.used_at is not None
        or reset_record.expires_at <= now
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token",
        )

    user = db.get(User, reset_record.user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token",
        )

    reset_record.used_at = now
    user.password_hash = hash_password(payload.new_password)

    # Revoke existing sessions after the password changes.
    db.execute(
        delete(UserSession).where(UserSession.user_id == user.id)
    )

    db.commit()
    return {"message": "Password reset successfully. Please log in again."}