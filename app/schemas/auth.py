from pydantic import BaseModel, field_validator
import re


class SignupRequest(BaseModel):
    phone: str
    password: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        # Accepts +91XXXXXXXXXX or 10-digit Indian numbers
        cleaned = re.sub(r"\s+", "", v)
        if not re.match(r"^(\+91)?[6-9]\d{9}$", cleaned):
            raise ValueError("Enter a valid Indian phone number")
        # Normalize to +91XXXXXXXXXX
        if not cleaned.startswith("+91"):
            cleaned = "+91" + cleaned
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    phone: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"