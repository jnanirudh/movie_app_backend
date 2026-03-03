import random
import string
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.otp import OTPRecord
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_otp(length: int = 6) -> str:
    """Generate a random 6-digit OTP string."""
    return ''.join(random.choices(string.digits, k=length))


def create_otp_record(db: Session, phone_number: str) -> str:
    """
    Generate an OTP, store its hash in DB, return the raw OTP.
    The raw OTP is sent to the user via SMS — never stored.
    """
    # Delete any existing unused OTPs for this number first
    db.query(OTPRecord).filter(
        OTPRecord.phone_number == phone_number,
        OTPRecord.is_used == False
    ).delete()

    raw_otp = generate_otp()
    hashed = pwd_context.hash(raw_otp)

    record = OTPRecord(phone_number=phone_number, hashed_otp=hashed)
    db.add(record)
    db.commit()

    return raw_otp


def verify_otp(db: Session, phone_number: str, raw_otp: str) -> bool:

    # Get the most recent unused OTP for this number
    record = db.query(OTPRecord).filter(
        OTPRecord.phone_number == phone_number,
        OTPRecord.is_used == False
    ).order_by(OTPRecord.created_at.desc()).first()

    if not record:
        return False

    # Check expiry
    now = datetime.now(timezone.utc)
    age_minutes = (now - record.created_at.replace(tzinfo=timezone.utc)).total_seconds() / 60
    if age_minutes > settings.OTP_EXPIRE_MINUTES:
        return False

    # Check OTP value
    if not pwd_context.verify(raw_otp, record.hashed_otp):
        return False

    # Mark as used — can never be reused
    record.is_used = True
    db.commit()
    return True