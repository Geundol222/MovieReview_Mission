from fastapi import FastAPI

from backend import sentiment
from backend.api import movies, reviews
from backend.db import Base, engine

app = FastAPI()


@app.on_event("startup")
def startup_tasks():
    Base.metadata.create_all(bind=engine)
    sentiment.warmup()


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(movies.router, prefix="/movies", tags=["movies"])
app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
