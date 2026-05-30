from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


API_DIR = Path(__file__).resolve().parent
MODEL_PATH = API_DIR / "no_degree_classifier_pipeline.joblib"
METADATA_PATH = API_DIR / "model_metadata.json"

pipeline = joblib.load(MODEL_PATH)
metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
top_countries = set(metadata["top_countries"])

app = FastAPI(title="No-Degree Mention Classifier API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class NoDegreePredictionRequest(BaseModel):
    job_title_short: str = Field(..., examples=["Data Engineer"])
    job_country: str = Field(..., examples=["United States"])
    job_schedule_type: str = Field(..., examples=["Full-time"])
    company_size: str = Field(..., examples=["5000+"])
    job_work_from_home: bool = Field(..., examples=[False])
    job_health_insurance: bool = Field(..., examples=[False])
    job_title: str = Field(..., examples=["Data Engineer Python SQL"])
    job_skills: list[str] = Field(default_factory=list, examples=[["python", "sql", "aws"]])
    threshold: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional decision threshold. Uses the trained selected threshold when omitted.",
    )


def skills_to_text(skills: list[str]) -> str:
    return " ".join(
        str(skill).strip().lower().replace(" ", "_")
        for skill in skills
        if str(skill).strip()
    )


def build_model_input(payload: NoDegreePredictionRequest) -> pd.DataFrame:
    country_grouped = payload.job_country if payload.job_country in top_countries else "Other"
    return pd.DataFrame(
        [
            {
                "job_title_short": payload.job_title_short,
                "job_country_grouped": country_grouped,
                "job_schedule_type": payload.job_schedule_type,
                "company_size": payload.company_size,
                "job_work_from_home": payload.job_work_from_home,
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
def predict(payload: NoDegreePredictionRequest) -> dict[str, Any]:
    model_input = build_model_input(payload)
    probability = float(pipeline.predict_proba(model_input)[0, 1])
    threshold = (
        float(payload.threshold)
        if payload.threshold is not None
        else float(metadata["selected_threshold"])
    )
    predicted_class = int(probability >= threshold)

    return {
        "predicted_no_degree_mention": bool(predicted_class),
        "predicted_label": (
            metadata["positive_class"] if predicted_class else metadata["negative_class"]
        ),
        "probability_no_degree_mention": probability,
        "probability_no_degree_mention_percent": round(probability * 100, 2),
        "threshold_used": threshold,
        "model_input": model_input.iloc[0].to_dict(),
    }
