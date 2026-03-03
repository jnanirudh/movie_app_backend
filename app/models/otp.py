import uuid
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class OTPRecord(Base):
    __tablename__ = "otp_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # The phone number this OTP was sent to
    phone_number = Column(String, nullable=False, index=True)
    
    # Hashed OTP — never store raw OTPs, same reason you don't store raw passwords
    hashed_otp = Column(String, nullable=False)
    
    # When it was created — used to check expiry
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Once used, mark it so it can't be used again
    is_used = Column(Boolean, default=False)