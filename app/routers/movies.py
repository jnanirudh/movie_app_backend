from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models.movie import Movie, Genre
from app.schemas.movie import MovieDetail, MovieListItem, MovieSearchResult

router = APIRouter(prefix="/api/v1/movies", tags=["Movies"])


@router.get("/popular", response_model=MovieSearchResult)
def popular_movies(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Returns movies from YOUR database — no TMDB call at all.
    Sorted by vote_average descending to mimic TMDB popular ordering.
    """
    offset = (page - 1) * limit
    total = db.query(Movie).count()
    movies = (
        db.query(Movie)
        .order_by(Movie.vote_average.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return MovieSearchResult(
        results=movies,
        page=page,
        total_pages=max(1, -(-total // limit)),  # ceiling division
        total_results=total,
    )


@router.get("/search", response_model=MovieSearchResult)
def search_movies(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search movies by title from your database. Case-insensitive."""
    offset = (page - 1) * limit
    base_query = db.query(Movie).filter(Movie.title.ilike(f"%{query}%"))
    total = base_query.count()
    movies = base_query.offset(offset).limit(limit).all()

    return MovieSearchResult(
        results=movies,
        page=page,
        total_pages=max(1, -(-total // limit)),
        total_results=total,
    )


@router.get("/{movie_id}", response_model=MovieDetail)
def movie_detail(movie_id: int, db: Session = Depends(get_db)):
    """Get full movie details from your database."""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie