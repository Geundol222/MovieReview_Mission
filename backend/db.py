import os
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/app.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    release_date = Column(Date, nullable=False)
    director = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    poster_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False, index=True)
    author = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    sentiment_label = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    movie = relationship("Movie", back_populates="reviews")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
