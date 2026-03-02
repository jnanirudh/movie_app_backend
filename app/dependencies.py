from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.auth_service import decode_access_token
from app.models.user import User

bearer_scheme = HTTPBearer()

# Provides a DB session for each request, closes it after
def get_db():
    db = SessionLocal()
    try:
        yield db  # Like try-with-resources in Java
    finally:
        db.close()

# Validates JWT and returns the current user — add to any protected route
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    user_id = decode_access_token(token)  # Raises exception if invalid

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user