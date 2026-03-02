from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserOut
from app.utils.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new account. Returns JWT tokens immediately — user is logged in on register."""
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        display_name=data.display_name or data.email.split("@")[0],
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password. Returns JWT tokens."""
    user = db.query(User).filter(User.email == data.email).first()

    # Check user exists AND password is correct in the same condition
    # (don't leak whether email exists via different error messages)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest):
    """
    Get a new access token using your refresh token.
    Flutter should call this when it gets a 401 response.
    """
    user_id = decode_token(data.refresh_token, expected_type="refresh")
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),  # Rotate refresh token too
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently logged-in user's profile."""
    return current_user


@router.put("/me", response_model=UserOut)
def update_profile(
    display_name: str | None = None,
    avatar_url: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update display name or avatar URL."""
    if display_name is not None:
        current_user.display_name = display_name
    if avatar_url is not None:
        current_user.avatar_url = avatar_url
    db.commit()
    db.refresh(current_user)
    return current_user