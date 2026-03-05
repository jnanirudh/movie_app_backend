from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.interaction import Watchlist
from app.models.movie import Movie
from app.schemas.watchlist import WatchlistOut, WatchlistAdd

router = APIRouter(prefix="/api/v1/watchlist", tags=["Watchlist"])


@router.get("/", response_model=list[WatchlistOut])
def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entries = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == current_user.id)
        .all()
    )
    return [
        WatchlistOut(movie=entry.movie, added_at=entry.added_at)
        for entry in entries if entry.movie
    ]


@router.get("/check/{movie_id}")
def check_watchlist(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exists = db.query(Watchlist).filter_by(
        user_id=current_user.id, movie_id=movie_id
    ).first()
    return {"in_watchlist": exists is not None}


@router.post("/", status_code=201)
def add_to_watchlist(
    payload: WatchlistAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check movie exists
    movie = db.query(Movie).filter(Movie.id == payload.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Check not already in watchlist
    existing = db.query(Watchlist).filter_by(
        user_id=current_user.id, movie_id=payload.movie_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Already in watchlist")

    entry = Watchlist(user_id=current_user.id, movie_id=payload.movie_id)
    db.add(entry)
    db.commit()
    return {"message": "Added to watchlist"}


@router.delete("/{movie_id}", status_code=204)
def remove_from_watchlist(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(Watchlist).filter_by(
        user_id=current_user.id, movie_id=movie_id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Not in watchlist")
    db.delete(entry)
    db.commit()