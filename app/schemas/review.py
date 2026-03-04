from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.schemas.movie import MovieListItem


class ReviewCreate(BaseModel):
    rating: float = Field(..., ge=1.0, le=5.0, description="Star rating 1.0 to 5.0")
    comment: str = Field(..., min_length=1, max_length=500)


class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    comment: Optional[str] = Field(None, min_length=1, max_length=500)


class ReviewOut(BaseModel):
    id: UUID
    movie_id: int
    user_id: UUID
    display_name: Optional[str] = None   # Pulled from user relationship
    rating: float
    comment: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReviewWithMovie(ReviewOut):
    """Used on profile screen — review + the movie it belongs to"""
    movie: Optional[MovieListItem] = None

    class Config:
        from_attributes = True