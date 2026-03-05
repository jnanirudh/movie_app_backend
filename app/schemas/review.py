from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.schemas.movie import MovieListItem


class ReviewCreate(BaseModel):
    rating: float = Field(..., ge=1.0, le=5.0)
    comment: str = Field(..., min_length=1, max_length=500)

    @field_validator("rating", mode="before")
    @classmethod
    def coerce_rating(cls, v):
        return float(v)


class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    comment: Optional[str] = Field(None, max_length=500)  # removed min_length

    @field_validator("rating", mode="before")
    @classmethod
    def coerce_rating(cls, v):
        if v is None:
            return v
        return float(v)


class ReviewOut(BaseModel):
    id: UUID
    movie_id: int
    user_id: UUID
    display_name: Optional[str] = None
    rating: float
    comment: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReviewWithMovie(ReviewOut):
    movie: Optional[MovieListItem] = None

    class Config:
        from_attributes = True