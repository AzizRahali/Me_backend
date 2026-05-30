# Salary Prediction API

This folder contains a small FastAPI backend for the salary prediction model.

## Files

- `train_model.py`: trains and exports the fitted pipeline and metadata.
- `app.py`: serves the API.
- `salary_prediction_pipeline.joblib`: generated model artifact.
- `model_metadata.json`: generated dropdown/options metadata.

## Train/export the model

Run from the project root:

```bash
python salary_api/train_model.py
```

## Start the API

Run from the `salary_api` folder:

```bash
uvicorn app:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

## Endpoints

```http
GET /health
GET /metadata
POST /predict
```

Example request:

```json
{
  "job_title_short": "Data Scientist",
  "job_country": "United States",
  "job_schedule_type": "Full-time",
  "company_size": "5000+",
  "job_work_from_home": true,
  "job_no_degree_mention": false,
  "job_health_insurance": true,
  "job_title": "Senior Machine Learning Data Scientist",
  "job_skills": ["python", "sql", "aws", "spark"]
}
```

Example Streamlit call:

```python
import requests

metadata = requests.get("http://127.0.0.1:8000/metadata").json()
prediction = requests.post("http://127.0.0.1:8000/predict", json=payload).json()
```
