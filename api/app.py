"""
JobLens Unified API — Salary Prediction + Degree Classifier + DL Forecast

Single FastAPI service combining all three ML/DL endpoints.

Routes:
    /salary/predict     POST  → salary prediction
    /salary/metadata    GET   → salary model metadata
    /degree/predict     POST  → degree requirement classification
    /degree/metadata    GET   → degree model metadata
    /forecast/metadata  GET   → DL forecast metadata
    /forecast/forecast  POST  → 6-month job demand forecast
    /health             GET   → health check
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════

app = FastAPI(title="JobLens API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

# ═══════════════════════════════════════════════════════════
# SALARY MODEL
# ═══════════════════════════════════════════════════════════

SALARY_DIR = BASE_DIR / "models" / "salary"
salary_pipeline = joblib.load(SALARY_DIR / "salary_prediction_pipeline.joblib")
salary_metadata = json.loads((SALARY_DIR / "model_metadata.json").read_text(encoding="utf-8"))
salary_top_countries = set(salary_metadata["top_countries"])


class SalaryRequest(BaseModel):
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
        str(s).strip().lower().replace(" ", "_") for s in skills if str(s).strip()
    )


@app.get("/salary/metadata")
def salary_meta() -> dict[str, Any]:
    return salary_metadata


@app.post("/salary/predict")
def salary_predict(payload: SalaryRequest) -> dict[str, Any]:
    country = payload.job_country if payload.job_country in salary_top_countries else "Other"
    df = pd.DataFrame([{
        "job_title_short": payload.job_title_short,
        "job_country_grouped": country,
        "job_schedule_type": payload.job_schedule_type,
        "company_size": payload.company_size,
        "job_work_from_home": payload.job_work_from_home,
        "job_no_degree_mention": payload.job_no_degree_mention,
        "job_health_insurance": payload.job_health_insurance,
        "job_title": payload.job_title or "",
        "skills_text": skills_to_text(payload.job_skills),
    }])
    predicted_log = salary_pipeline.predict(df)[0]
    salary = max(float(np.expm1(predicted_log)), 0.0)
    return {
        "predicted_salary": salary,
        "predicted_salary_rounded": round(salary),
        "model_input": df.iloc[0].to_dict(),
    }


# ═══════════════════════════════════════════════════════════
# DEGREE CLASSIFIER
# ═══════════════════════════════════════════════════════════

DEGREE_DIR = BASE_DIR / "models" / "degree"
degree_pipeline = joblib.load(DEGREE_DIR / "no_degree_classifier_pipeline.joblib")
degree_metadata = json.loads((DEGREE_DIR / "model_metadata.json").read_text(encoding="utf-8"))
degree_top_countries = set(degree_metadata["top_countries"])


class DegreeRequest(BaseModel):
    job_title_short: str = Field(..., examples=["Data Engineer"])
    job_country: str = Field(..., examples=["United States"])
    job_schedule_type: str = Field(..., examples=["Full-time"])
    company_size: str = Field(..., examples=["5000+"])
    job_work_from_home: bool = Field(..., examples=[False])
    job_health_insurance: bool = Field(..., examples=[False])
    job_title: str = Field(..., examples=["Data Engineer Python SQL"])
    job_skills: list[str] = Field(default_factory=list, examples=[["python", "sql", "aws"]])
    threshold: float | None = Field(default=None, ge=0.0, le=1.0)


@app.get("/degree/metadata")
def degree_meta() -> dict[str, Any]:
    return degree_metadata


@app.post("/degree/predict")
def degree_predict(payload: DegreeRequest) -> dict[str, Any]:
    country = payload.job_country if payload.job_country in degree_top_countries else "Other"
    df = pd.DataFrame([{
        "job_title_short": payload.job_title_short,
        "job_country_grouped": country,
        "job_schedule_type": payload.job_schedule_type,
        "company_size": payload.company_size,
        "job_work_from_home": payload.job_work_from_home,
        "job_health_insurance": payload.job_health_insurance,
        "job_title": payload.job_title or "",
        "skills_text": skills_to_text(payload.job_skills),
    }])
    prob = float(degree_pipeline.predict_proba(df)[0, 1])
    threshold = (
        float(payload.threshold)
        if payload.threshold is not None
        else float(degree_metadata["selected_threshold"])
    )
    predicted = int(prob >= threshold)
    return {
        "predicted_no_degree_mention": bool(predicted),
        "predicted_label": degree_metadata["positive_class"] if predicted else degree_metadata["negative_class"],
        "probability_no_degree_mention": prob,
        "probability_no_degree_mention_percent": round(prob * 100, 2),
        "threshold_used": threshold,
        "model_input": df.iloc[0].to_dict(),
    }


# ═══════════════════════════════════════════════════════════
# DL FORECAST
# ═══════════════════════════════════════════════════════════

DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
VARIABLE_FILTER = os.getenv("VARIABLE_FILTER", "new postings")
HIST_DISPLAY_MONTHS = 24

FC_DB: dict = {}
FC_LOADED = False


def load_forecast_data():
    data: dict = {}
    hist_path = DATA_DIR / "historical.csv"
    if not hist_path.exists():
        raise FileNotFoundError(f"Missing {hist_path}")

    raw = pd.read_csv(hist_path, parse_dates=["date"])
    if "variable" in raw.columns:
        raw = raw[raw["variable"] == VARIABLE_FILTER].copy()
    raw.rename(columns={
        "jobcountry": "country", "display_name": "sector",
        "indeed_job_postings_index": "value",
    }, inplace=True)

    data["raw"] = raw
    countries = sorted(raw["country"].dropna().unique().tolist())
    data["countries"] = countries
    sectors = sorted(raw["sector"].dropna().unique().tolist())
    data["sectors"] = sectors
    raw["month"] = raw["date"].dt.to_period("M")

    for country in countries:
        subset = raw[raw["country"] == country]
        pivot = subset.groupby(["month", "sector"])["value"].mean().unstack().sort_index()
        pivot.index = pivot.index.to_timestamp()
        data[country] = pivot

    global_pivot = raw.groupby(["month", "sector"])["value"].mean().unstack().sort_index()
    global_pivot.index = global_pivot.index.to_timestamp()
    data["Global"] = global_pivot

    fc_path = DATA_DIR / "forecast.csv"
    if fc_path.exists():
        fc = pd.read_csv(fc_path)
        fc.rename(columns={"display_name": "sector", "forecast_mean": "mean",
                           "forecast_low": "low", "forecast_high": "high"}, inplace=True)
        data["forecast"] = fc
        fc_sectors = set(fc["sector"].dropna().unique())
        data["sectors"] = sorted([s for s in sectors if s in fc_sectors])
    else:
        data["forecast"] = None

    metrics_path = DATA_DIR / "model_metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            data["metrics"] = json.load(f)
    else:
        data["metrics"] = {}

    return data


def init_forecast():
    global FC_DB, FC_LOADED
    try:
        FC_DB = load_forecast_data()
        FC_LOADED = True
        print(f"Forecast data loaded: {len(FC_DB.get('sectors', []))} sectors, "
              f"{len(FC_DB.get('countries', []))} countries")
    except FileNotFoundError as e:
        FC_DB = {}
        FC_LOADED = False
        print(f"WARNING: {e}")


init_forecast()


class ForecastRequest(BaseModel):
    region: str
    sector: str


@app.get("/forecast/metadata")
def forecast_meta():
    if not FC_LOADED:
        raise HTTPException(503, "Forecast data not loaded.")
    regions = ["Global"] + FC_DB["countries"]
    metrics = FC_DB.get("metrics", {})
    best = metrics.get("best_model", "gru")
    best_m = metrics.get(best, {})
    global_df = FC_DB["Global"]
    return {
        "regions": regions,
        "sectors": FC_DB["sectors"],
        "model": {
            "best_architecture": best.upper(),
            "rmse": best_m.get("rmse", "—"),
            "mae": best_m.get("mae", "—"),
            "r2": best_m.get("r2", "—"),
            "ensemble_size": 7,
            "forecast_horizon": 6,
        },
        "data_range": {
            "start": global_df.index.min().strftime("%Y-%m"),
            "end": global_df.index.max().strftime("%Y-%m"),
            "months": len(global_df),
        },
    }


@app.post("/forecast/forecast")
def forecast(req: ForecastRequest):
    if not FC_LOADED:
        raise HTTPException(503, "Forecast data not loaded.")

    region, sector = req.region, req.sector
    valid_regions = ["Global"] + FC_DB["countries"]
    if region not in valid_regions:
        raise HTTPException(400, f"Unknown region '{region}'. Available: {valid_regions}")

    hist_df = FC_DB.get(region)
    if hist_df is None:
        raise HTTPException(400, f"No historical data for region '{region}'")
    if sector not in hist_df.columns:
        raise HTTPException(400, f"Unknown sector '{sector}'.")

    hist_series = hist_df[sector].dropna().tail(HIST_DISPLAY_MONTHS)
    hist_dates = [d.strftime("%Y-%m") for d in hist_series.index]
    hist_values = hist_series.round(1).tolist()

    fc_df = FC_DB.get("forecast")
    if fc_df is None or fc_df.empty:
        raise HTTPException(400, "No forecast data.")

    fc_sector = fc_df[fc_df["sector"] == sector].copy().sort_values("date")
    if fc_sector.empty:
        raise HTTPException(400, f"No forecast for sector '{sector}'")

    fc_dates = fc_sector["date"].tolist()
    fc_values = fc_sector["mean"].round(1).tolist()
    fc_low_vals = fc_sector["low"].round(1).tolist()
    fc_high_vals = fc_sector["high"].round(1).tolist()

    current_value = float(hist_series.iloc[-1])
    projected_value = float(fc_values[-1])

    if region != "Global":
        global_last = float(FC_DB["Global"][sector].dropna().iloc[-1])
        if global_last > 0:
            scale = current_value / global_last
            fc_values = [round(v * scale, 1) for v in fc_values]
            fc_low_vals = [round(v * scale, 1) for v in fc_low_vals]
            fc_high_vals = [round(v * scale, 1) for v in fc_high_vals]
            projected_value = float(fc_values[-1])

    change_pct = round((projected_value - current_value) / current_value * 100, 1) if current_value else 0.0

    return {
        "region": region, "sector": sector,
        "current_value": round(current_value, 1),
        "projected_value": round(projected_value, 1),
        "change_pct": change_pct,
        "change_pts": round(projected_value - current_value, 1),
        "low_value": round(float(fc_low_vals[-1]), 1),
        "high_value": round(float(fc_high_vals[-1]), 1),
        "historical_dates": hist_dates,
        "historical_values": hist_values,
        "forecast_dates": fc_dates,
        "forecast_values": fc_values,
        "forecast_low": fc_low_vals,
        "forecast_high": fc_high_vals,
    }


# ═══════════════════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════════════════

@app.get("/health")
def health():
    return {
        "status": "ok",
        "salary_model": True,
        "degree_model": True,
        "forecast_data": FC_LOADED,
    }
