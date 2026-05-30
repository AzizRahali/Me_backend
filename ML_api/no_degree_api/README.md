# No-Degree Mention Classifier API

This is the ready-to-run API package. The model is already trained and saved.

## Files

- `app.py`: FastAPI app.
- `no_degree_classifier_pipeline.joblib`: trained model pipeline.
- `model_metadata.json`: model metrics, frontend dropdown values, and schema.
- `requirements.txt`: Python dependencies.

## Start the API

From this folder:

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

## Endpoints

```http
GET /health
GET /metadata
POST /predict
```

## Example Request

```json
{
  "job_title_short": "Data Engineer",
  "job_country": "United States",
  "job_schedule_type": "Full-time",
  "company_size": "5000+",
  "job_work_from_home": false,
  "job_health_insurance": false,
  "job_title": "Data Engineer Python SQL",
  "job_skills": ["python", "sql", "aws"]
}
```

## Example Response

```json
{
  "predicted_no_degree_mention": true,
  "predicted_label": "no degree mentioned",
  "probability_no_degree_mention": 0.72,
  "probability_no_degree_mention_percent": 72.0,
  "threshold_used": 0.52
}
```

Use `GET /metadata` to populate frontend dropdowns and see model metrics.
