from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


API_DIR = Path(__file__).resolve().parent
MODEL_PATH = API_DIR / "salary_prediction_pipeline.joblib"
METADATA_PATH = API_DIR / "model_metadata.json"

pipeline = joblib.load(MODEL_PATH)
metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
top_countries = set(metadata["top_countries"])

app = FastAPI(title="Salary Prediction API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class SalaryPredictionRequest(BaseModel):
    job_title_short: str = Field(..., examples=["Data Scientist"])
    job_country: str = Field(..., examples=["United States"])
    job_schedule_type: str = Field(..., examples=["Full-time"])
    company_size: str = Field(..., examples=["5000+"])
    job_work_from_home: bool = Field(..., examples=[True])
    job_no_degree_mention: bool = Field(..., examples=[False])
    job_health_insurance: bool = Field(..., examples=[True])
    job_title: str = Field(..., examples=["Senior Machine Learning Data Scientist"])
    job_skills: list[str] = Field(default_factory=list, examples=[["python", "sql", "aws"]])


def skills_to_text(skills: list[str]) -> str:
    return " ".join(
        str(skill).strip().lower().replace(" ", "_")
        for skill in skills
        if str(skill).strip()
    )


def build_model_input(payload: SalaryPredictionRequest) -> pd.DataFrame:
    country_grouped = payload.job_country if payload.job_country in top_countries else "Other"
    return pd.DataFrame(
        [
            {
                "job_title_short": payload.job_title_short,
                "job_country_grouped": country_grouped,
                "job_schedule_type": payload.job_schedule_type,
                "company_size": payload.company_size,
                "job_work_from_home": payload.job_work_from_home,
                "job_no_degree_mention": payload.job_no_degree_mention,
                "job_health_insurance": payload.job_health_insurance,
                "job_title": payload.job_title or "",
                "skills_text": skills_to_text(payload.job_skills),
            }
        ]
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metadata")
def get_metadata() -> dict[str, Any]:
    return metadata


@app.post("/predict")
def predict(payload: SalaryPredictionRequest) -> dict[str, Any]:
    model_input = build_model_input(payload)
    predicted_log_salary = pipeline.predict(model_input)[0]
    predicted_salary = float(np.expm1(predicted_log_salary))
    predicted_salary = max(predicted_salary, 0.0)

    return {
        "predicted_salary": predicted_salary,
        "predicted_salary_rounded": round(predicted_salary),
        "model_input": model_input.iloc[0].to_dict(),
    }
