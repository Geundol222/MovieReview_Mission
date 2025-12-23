# Movies & Reviews

영화 리뷰 감성 분석 애플리케이션

## 기능
- 영화 등록 및 관리
- 리뷰 작성 및 감성 분석 (NSMC 모델 사용)
- 영화 검색
- 평균 감성 점수 계산

## 실행 방법

### 백엔드 실행
```bash
uvicorn backend.main:app --reload
```

### 프론트엔드 실행
```bash
streamlit run frontend/app.py
```

## 기술 스택
- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Database**: SQLite
- **ML Model**: sangrimlee/bert-base-multilingual-cased-nsmc (ONNX)
