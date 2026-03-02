from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewOut
from app.services import review_service
import uuid

router = APIRouter(tags=["Reviews"])

@router.post("/movies/{movie_id}/reviews", response_model=ReviewOut, status_code=201)
def create_review(movie_id: int, data: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return review_service.create_review(db, current_user.id, movie_id, data)

@router.get("/movies/{movie_id}/reviews", response_model=list[ReviewOut])
def get_movie_reviews(movie_id: int, db: Session = Depends(get_db)):
    return review_service.get_reviews_for_movie(db, movie_id)

@router.get("/users/me/reviews", response_model=list[ReviewOut])
def get_my_reviews(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return review_service.get_reviews_by_user(db, current_user.id)

@router.patch("/reviews/{review_id}", response_model=ReviewOut)
def update_review(review_id: uuid.UUID, data: ReviewUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return review_service.update_review(db, review_id, current_user.id, data)

@router.delete("/reviews/{review_id}", status_code=204)
def delete_review(review_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review_service.delete_review(db, review_id, current_user.id)