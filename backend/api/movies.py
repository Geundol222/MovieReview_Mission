from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models
from backend.db import Movie, get_db

router = APIRouter()


@router.post("/", response_model=models.Movie)
def create_movie(movie_create: models.MovieCreate, db: Session = Depends(get_db)):
    movie = Movie(**movie_create.model_dump())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


@router.get("/", response_model=list[models.Movie])
def list_movies(db: Session = Depends(get_db)):
    return db.query(Movie).all()


@router.get("/{movie_id}", response_model=models.Movie)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.delete("/{movie_id}", response_model=dict)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(movie)
    db.commit()
    return {"ok": True}
