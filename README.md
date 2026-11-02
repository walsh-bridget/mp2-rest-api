# MP2: Data Processing API

This project is a FastAPI application that wraps the MP1 data pipeline in a REST API. Users upload a CSV file (POST /upload), retrieve a stored dataset with an optional row limit (GET /datasets/{id}), and validate and clean it with configurable settings (POST /datasets/{id}/process). A /health endpoint reports the service status. Middleware logs each request's ID, method, path, status code, and duration, and returns the ID in an X-Request-ID header. Tests use pytest and FastAPI's TestClient.

## Run

    pip install -r requirements.txt
    uvicorn main:app --reload

Then open http://127.0.0.1:8000/docs.

## Test

    python -m pytest tests -v