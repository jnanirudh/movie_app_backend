from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class ReviewCreate(BaseModel):
    body: str
    rating: int = Field(..., ge=1, le=10)  # Validation: must be 1-10

class ReviewUpdate(BaseModel):
    body: str | None = None
    rating: int | None = Field(None, ge=1, le=10)

class ReviewOut(BaseModel):
    id: uuid.UUID
    movie_id: int
    user_id: uuid.UUID
    display_name: str | None   # Flattened from user for convenience
    body: str
    rating: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True