from pydantic import BaseModel

class GenreOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True  # Lets Pydantic read SQLAlchemy model objects directly

class MovieListItem(BaseModel):
    id: int
    title: str
    poster_path: str | None
    release_date: str | None
    vote_average: float | None

    class Config:
        from_attributes = True

class MovieDetail(MovieListItem):
    overview: str | None
    backdrop_path: str | None
    original_language: str | None
    genres: list[GenreOut] = []

    class Config:
        from_attributes = True