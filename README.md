---
title: Movie Review API
emoji: 🎬
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Movie Review Sentiment Analysis API

FastAPI backend for movie review sentiment analysis using BERT model.

## Features
- Movie management API
- Review creation with automatic sentiment analysis
- Korean language support
- ONNX optimized inference

## Endpoints
- `GET /health` - Health check
- `GET /movies` - List all movies
- `POST /movies` - Create a new movie
- `GET /movies/{movie_id}/reviews` - Get reviews for a movie
- `POST /reviews` - Create a review with sentiment analysis
