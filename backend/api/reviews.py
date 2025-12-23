from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models, sentiment
from backend.db import Movie, Review, get_db

router = APIRouter()


@router.post("/", response_model=models.Review)
def create_review(payload: models.ReviewCreate, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == payload.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    score, label = sentiment.analyze(payload.content)
    review = Review(
        movie_id=payload.movie_id,
        author=payload.author,
        content=payload.content,
        sentiment_score=score,
        sentiment_label=label,
    )

    db.add(review)
    db.commit()
    db.refresh(review)
    # refresh 후에도 sentiment_label이 유지되도록 다시 설정
    review.sentiment_label = label
    return review


@router.get("/", response_model=list[models.Review])
def list_reviews(db: Session = Depends(get_db)):
    reviews = db.query(Review).order_by(Review.created_at.desc()).limit(10).all()
    for r in reviews:
        if not getattr(r, "sentiment_label", None):
            try:
                _, label = sentiment.analyze(r.content)
                r.sentiment_label = label
            except Exception:
                r.sentiment_label = None
    return reviews


@router.get("/movie/{movie_id}", response_model=list[models.Review])
def list_reviews_by_movie(movie_id: int, limit: int | None = None, db: Session = Depends(get_db)):
    query = (
        db.query(Review)
        .filter(Review.movie_id == movie_id)
        .order_by(Review.created_at.desc())
    )
    if limit is not None:
        query = query.limit(limit)
    reviews = query.all()
    for r in reviews:
        if not getattr(r, "sentiment_label", None):
            try:
                _, label = sentiment.analyze(r.content)
                r.sentiment_label = label
            except Exception:
                r.sentiment_label = None
    return reviews


@router.get("/movie/{movie_id}/rating")
def average_rating(movie_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.movie_id == movie_id).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews")
    avg_score = sum(r.sentiment_score for r in reviews) / len(reviews)
    return {"movie_id": movie_id, "average_sentiment": avg_score}
