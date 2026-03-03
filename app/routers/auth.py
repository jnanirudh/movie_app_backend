from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.auth import PhoneSendOTPRequest, PhoneVerifyOTPRequest, PhoneSendOTPResponse
from app.services.otp_service import create_otp_record, verify_otp
from app.services.sms_service import send_otp_sms
from app.services.email_service import send_otp_email
from app.schemas.auth import EmailSendOTPRequest, EmailVerifyOTPRequest
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
    user_id = decode_token(data.refresh_token, expected_type="refresh")
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id), 
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

@router.post("/phone/send-otp", response_model=PhoneSendOTPResponse)
def send_otp(data: PhoneSendOTPRequest, db: Session = Depends(get_db)):

    otp = create_otp_record(db, data.phone_number)
    success = send_otp_sms(data.phone_number, otp)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send OTP. Please try again.")

    return PhoneSendOTPResponse(
        message=f"OTP sent to {data.phone_number}",
        expires_in_minutes=settings.OTP_EXPIRE_MINUTES,
    )


@router.post("/phone/verify-otp", response_model=TokenResponse)
def verify_otp_and_login(data: PhoneVerifyOTPRequest, db: Session = Depends(get_db)):
    is_valid = verify_otp(db, data.phone_number, data.otp)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )

    # Find existing user or create new one
    user = db.query(User).filter(User.phone_number == data.phone_number).first()

    if not user:
        # Auto-register — phone users don't need email/password
        user = User(
            phone_number=data.phone_number,
            hashed_password="",          # No password for phone users
            display_name=data.phone_number[-4:].zfill(4),  # Default name: last 4 digits
            is_phone_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Mark phone as verified on existing account
        user.is_phone_verified = True
        db.commit()

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/phone/link", response_model=UserOut)
def link_phone_to_account(
    data: PhoneSendOTPRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Check number not already used by someone else
    existing = db.query(User).filter(
        User.phone_number == data.phone_number
    ).first()

    if existing and existing.id != current_user.id:
        raise HTTPException(status_code=409, detail="Phone number already linked to another account")

    otp = create_otp_record(db, data.phone_number)
    send_otp_sms(data.phone_number, otp)

    return {"message": "OTP sent. Verify to link this number to your account."}


@router.post("/phone/link/verify", response_model=UserOut)
def verify_link_phone(
    data: PhoneVerifyOTPRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    is_valid = verify_otp(db, data.phone_number, data.otp)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")

    current_user.phone_number = data.phone_number
    current_user.is_phone_verified = True
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/email/send-otp")
def send_email_otp(data: EmailSendOTPRequest, db: Session = Depends(get_db)):
    """
    Step 1 of email registration.
    Sends OTP to email before account is created.
    """
    otp = create_otp_record(db, data.email)
    success = send_otp_email(data.email, otp)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send OTP email")
    return {"message": f"OTP sent to {data.email}", 
            "expires_in_minutes": settings.OTP_EXPIRE_MINUTES}


@router.post("/email/verify-otp", response_model=TokenResponse)
def verify_email_otp(data: EmailVerifyOTPRequest, db: Session = Depends(get_db)):
    """
    Step 2 of email registration.
    Verifies OTP then creates account and returns JWT.
    """
    is_valid = verify_otp(db, data.email, data.otp)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")

    # Check if account already exists (this is a login via OTP)
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    # New user — create account
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


@router.post("/email/login-otp")
def send_login_otp(data: EmailSendOTPRequest, db: Session = Depends(get_db)):
    """
    Send OTP for existing user login.
    Checks user exists first.
    """
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account found with this email")
    
    otp = create_otp_record(db, data.email)
    success = send_otp_email(data.email, otp)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send OTP email")
    return {"message": f"OTP sent to {data.email}"}


@router.post("/email/verify-login-otp", response_model=TokenResponse)
def verify_login_otp(
    email: str,
    otp: str,
    db: Session = Depends(get_db)
):
    """Verify OTP for login — no password needed."""
    is_valid = verify_otp(db, email, otp)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )