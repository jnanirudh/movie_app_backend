from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.watchlist import WatchlistOut
from app.services import watchlist_service

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

@router.get("/", response_model=list[WatchlistOut])
def get_watchlist(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return watchlist_service.get_watchlist(db, current_user.id)

@router.post("/{movie_id}", status_code=201)
def add_to_watchlist(movie_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    watchlist_service.add_to_watchlist(db, current_user.id, movie_id)
    return {"message": "Added to watchlist"}

@router.delete("/{movie_id}", status_code=204)
def remove_from_watchlist(movie_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    watchlist_service.remove_from_watchlist(db, current_user.id, movie_id)

@router.get("/{movie_id}/check")
def check_watchlist(movie_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"in_watchlist": watchlist_service.is_in_watchlist(db, current_user.id, movie_id)}