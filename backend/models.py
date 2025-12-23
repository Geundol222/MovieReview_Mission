from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional

class MovieCreate(BaseModel):
    title: str
    release_date: date
    director: str
    genre: str
    poster_url: Optional[str] = None

class Movie(MovieCreate):
    id: int

    class Config:
        orm_mode = True

class ReviewCreate(BaseModel):
    movie_id: int
    author: str
    content: str

class Review(ReviewCreate):
    id: int
    sentiment_score: float
    created_at: datetime
    sentiment_label: Optional[str] = None

    class Config:
        orm_mode = True
