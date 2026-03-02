from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.interaction import Review
from app.schemas.review import ReviewCreate, ReviewUpdate
import uuid

def create_review(db: Session, user_id: uuid.UUID, movie_id: int, data: ReviewCreate) -> Review:
    existing = db.query(Review).filter_by(user_id=user_id, movie_id=movie_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already reviewed this movie")

    review = Review(user_id=user_id, movie_id=movie_id, body=data.body, rating=data.rating)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

def get_reviews_for_movie(db: Session, movie_id: int) -> list[Review]:
    return db.query(Review).filter(Review.movie_id == movie_id).all()

def get_reviews_by_user(db: Session, user_id: uuid.UUID) -> list[Review]:
    return db.query(Review).filter(Review.user_id == user_id).all()

def update_review(db: Session, review_id: uuid.UUID, user_id: uuid.UUID, data: ReviewUpdate) -> Review:
    review = db.query(Review).filter_by(id=review_id, user_id=user_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    if data.body is not None:
        review.body = data.body
    if data.rating is not None:
        review.rating = data.rating

    db.commit()
    db.refresh(review)
    return review

def delete_review(db: Session, review_id: uuid.UUID, user_id: uuid.UUID):
    review = db.query(Review).filter_by(id=review_id, user_id=user_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    db.delete(review)
    db.commit()