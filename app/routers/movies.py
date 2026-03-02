from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models.movie import Movie
from app.schemas.movie import MovieDetail, MovieListItem

router = APIRouter(prefix="/movies", tags=["Movies"])

@router.get("/", response_model=list[MovieListItem])
def list_movies(
    skip: int = Query(0),
    limit: int = Query(20),
    search: str | None = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Movie)
    if search:
        query = query.filter(Movie.title.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

@router.get("/{movie_id}", response_model=MovieDetail)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie