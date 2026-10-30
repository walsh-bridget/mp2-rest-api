import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import DatasetInfo, DatasetStorage, HealthResponse, setup_logging

setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")
storage = DatasetStorage()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    # checks that application is responding, doesn't read or store any data
    return {"status": "ok", "version": "1.0.0"}

@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """Read and store a CSV upload."""
    
    # checks file extension, makes lowercase
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    # ensures file is a CSV
    if extension != ".csv":
        logger.warning("Unsupported file format: %s", extension)
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a CSV file."
        )

    # reads the uploaded file as bytes, await makes it async
    contents = await file.read()

    # parse CSV
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except (
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        UnicodeDecodeError
    ): 
        # if parsing fails returns status 400 warning
        logger.warning("Unable to read CSV file: %s", filename)
        raise HTTPException(
            status_code=400,
            detail="Unable to read CSV file. Please upload a valid, readable CSV."
        )

    # saves dataframe and returns metadata
    dataset_id = storage.save(df, filename)
    metadata = storage.get_metadata(dataset_id)

    logger.info(
        "Uploaded dataset: id=%s, filename=%s, rows=%s",
        dataset_id,
        filename,
        len(df)
    )

    return metadata



@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, limit: int = Query(default=100, ge=1)): # default limit 100, limit must be at least 1, 
                                                                         # limit=0 rejected with status 422
    """Return up to limit rows from a stored dataset."""
    df = storage.get(dataset_id)

    if df is None:
        logger.warning("Dataset not found: %s", dataset_id)
        raise HTTPException(
            status_code=404,
            detail="Dataset not found."
        )

    # takes the first limit rows, preserves their oder, converts to dictionaries. missing values are represented as null
    records = json.loads(df.head(limit).to_json(orient="records"))

    logger.info(
        "Retrieved dataset: id=%s, returned_rows=%s",
        dataset_id,
        len(records)
    )

    return {
        "id": dataset_id,
        "data": records,
        "total_rows": len(df)
    }

