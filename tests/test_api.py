def test_upload_csv(client, sample_csv_bytes):
    # TODO: Upload the sample CSV to POST /upload.
    # Assert status 200, six rows, two columns,
    # and a positive integer dataset ID.
    response = client.post(
        "/upload",
        files={
            "file": (
                "sample_data.csv",
                sample_csv_bytes,
                "text/csv"
            )
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["rows"] == 6
    assert data["columns"] == 2
    assert isinstance(data["id"], int)
    assert data["id"] > 0


def test_process_and_retrieve(
    client, uploaded_dataset_id, processing_body
):
    # TODO 1: Send a POST request to
    # /datasets/{uploaded_dataset_id}/process
    # using json=processing_body.
    # Assert status 200, one validation removal,
    # and a cleaning report showing 5 → 3 rows.

    # process the dataset
    response = client.post(
        f"/datasets/{uploaded_dataset_id}/process",
        json=processing_body
    )

    assert response.status_code == 200
    result = response.json()
    assert result["validation_rows_removed"] == 1
    assert result["cleaning_report"]["rows_before"] == 5
    assert result["cleaning_report"]["rows_after"] == 3

    # TODO 2: GET /datasets/{uploaded_dataset_id}.
    # Assert status 200 and total_rows == 3.
    # Check that the returned records contain student IDs
    # 1, 2, and 5 with scores 80, 90, and 85.
  

    # retrieve the processed dataset
    response = client.get(f"/datasets/{uploaded_dataset_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 3

    records = data["records"]
    pairs = [(r["student_id"], r["score"]) for r in records]
    assert pairs == [(1, 80), (2, 90), (5, 85)]
    pass


def test_retrieve_missing_dataset(client):
    # TODO: Retrieve a dataset ID that does not exist.
    # Assert status 404.
    response = client.get("/datasets/999")
    assert response.status_code == 404