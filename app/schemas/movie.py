from pydantic import BaseModel
from typing import Optional


class GenreOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class MovieListItem(BaseModel):
    id: int
    title: str
    poster_path: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None
    original_language: Optional[str] = None

    class Config:
        from_attributes = True


class MovieDetail(MovieListItem):
    overview: Optional[str] = None
    backdrop_path: Optional[str] = None
    runtime: Optional[int] = None
    director: Optional[str] = None
    certification: Optional[str] = None
    genres: list[GenreOut] = []

    class Config:
        from_attributes = True


class MovieSearchResult(BaseModel):
    results: list[MovieListItem]
    page: int
    total_pages: int
    total_results: int