from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import sentiment
from backend.api import movies, reviews
from backend.db import Base, engine

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용 (프로덕션에서는 특정 도메인으로 제한)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_tasks():
    Base.metadata.create_all(bind=engine)
    sentiment.warmup()


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(movies.router, prefix="/movies", tags=["movies"])
app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
