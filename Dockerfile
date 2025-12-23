FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements-hf.txt .
RUN pip install --no-cache-dir -r requirements-hf.txt

# Copy application code
COPY backend/ ./backend/
COPY app.py .

# Pre-download and convert model to ONNX
RUN python -c "from backend.sentiment import download_model; download_model()"

# Expose port
EXPOSE 7860

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
