from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.interaction import Review
from app.models.movie import Movie
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewOut, ReviewWithMovie
import uuid

router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])


def _get_or_404(db: Session, review_id: uuid.UUID) -> Review:
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.get("/movie/{movie_id}", response_model=list[ReviewOut])
def get_movie_reviews(movie_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.movie_id == movie_id).all()
    return [ReviewOut(
        id=r.id, movie_id=r.movie_id, user_id=r.user_id,
        display_name=r.user.display_name if r.user else None,
        rating=r.rating, comment=r.comment,
        created_at=r.created_at, updated_at=r.updated_at,
    ) for r in reviews]


@router.get("/user/me", response_model=list[ReviewWithMovie])
def get_my_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(Review.user_id == current_user.id).all()
    result = []
    for r in reviews:
        movie_data = None
        if r.movie:
            movie_data = {
                "id": r.movie.id,
                "title": r.movie.title,
                "poster_path": r.movie.poster_path,
                "release_date": r.movie.release_date,
                "vote_average": r.movie.vote_average,
                "original_language": r.movie.original_language,
            }
        result.append(ReviewWithMovie(
            id=r.id, movie_id=r.movie_id, user_id=r.user_id,
            display_name=current_user.display_name,
            rating=r.rating, comment=r.comment,
            created_at=r.created_at, updated_at=r.updated_at,
            movie=movie_data,
        ))
    return result


@router.get("/user/{user_id}", response_model=list[ReviewOut])
def get_user_reviews(user_id: uuid.UUID, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.user_id == user_id).all()
    return [ReviewOut(
        id=r.id, movie_id=r.movie_id, user_id=r.user_id,
        display_name=r.user.display_name if r.user else None,
        rating=r.rating, comment=r.comment,
        created_at=r.created_at, updated_at=r.updated_at,
    ) for r in reviews]


@router.post("/movie/{movie_id}", response_model=ReviewOut, status_code=201)
def create_review(
    movie_id: int,
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(Review).filter_by(user_id=current_user.id, movie_id=movie_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="You have already reviewed this movie")

    review = Review(
        user_id=current_user.id,
        movie_id=movie_id,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return ReviewOut(
        id=review.id, movie_id=review.movie_id, user_id=review.user_id,
        display_name=current_user.display_name,
        rating=review.rating, comment=review.comment,
        created_at=review.created_at, updated_at=review.updated_at,
    )


@router.put("/{review_id}", response_model=ReviewOut)
def update_review(
    review_id: uuid.UUID,
    data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    review = _get_or_404(db, review_id)
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own reviews")

    if data.rating is not None:
        review.rating = data.rating
    if data.comment is not None:
        review.comment = data.comment

    db.commit()
    db.refresh(review)

    return ReviewOut(
        id=review.id, movie_id=review.movie_id, user_id=review.user_id,
        display_name=current_user.display_name, rating=review.rating,
        comment=review.comment, created_at=review.created_at, updated_at=review.updated_at,
    )


@router.delete("/{review_id}", status_code=204)
def delete_review(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    review = _get_or_404(db, review_id)
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own reviews")

    db.delete(review)
    db.commit()