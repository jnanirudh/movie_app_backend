from pydantic import BaseModel, EmailStr, field_validator, model_validator
import re


class SignupRequest(BaseModel):
    phone: str | None = None
    email: EmailStr | None = None
    password: str
    display_name: str | None = None

    @model_validator(mode="after")
    def at_least_one_identifier(self):
        if not self.phone and not self.email:
            raise ValueError("Provide at least one of phone or email")
        return self

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        cleaned = re.sub(r"\s+", "", v)
        if not re.match(r"^(\+91)?[6-9]\d{9}$", cleaned):
            raise ValueError("Enter a valid Indian phone number")
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
    phone: str | None = None
    email: EmailStr | None = None
    password: str

    @model_validator(mode="after")
    def at_least_one_identifier(self):
        if not self.phone and not self.email:
            raise ValueError("Provide either phone or email to login")
        return self


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"