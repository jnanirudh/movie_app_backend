from pydantic import BaseModel
from datetime import datetime
from app.schemas.movie import MovieListItem


class WatchlistOut(BaseModel):
    movie: MovieListItem
    added_at: datetime

    class Config:
        from_attributes = True


class WatchlistAdd(BaseModel):
    movie_id: int