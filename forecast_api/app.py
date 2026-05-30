"""
DL Forecast API — serves pre-computed forecast data from local training pipeline.

Run train.py first to generate the data files, then start this API.

Endpoints:
    GET  /health     → health check
    GET  /metadata   → regions, sectors, model info
    POST /forecast   → historical + 6-month forecast for a region/sector pair
"""

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="DL Forecast API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
VARIABLE_FILTER = os.getenv("VARIABLE_FILTER", "new postings")
HIST_DISPLAY_MONTHS = 24


# ═══════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════

DB = {}
DATA_LOADED = False


def load_data():
    """Load CSV/JSON files and pivot into lookup-friendly structures."""
    data = {}

    # ── Historical data (long format) ──
    hist_path = DATA_DIR / "historical.csv"
    if not hist_path.exists():
        raise FileNotFoundError(f"Missing {hist_path}. Run train.py first.")

    raw = pd.read_csv(hist_path, parse_dates=["date"])

    # Filter to the chosen variable
    if "variable" in raw.columns:
        raw = raw[raw["variable"] == VARIABLE_FILTER].copy()

    # Normalise column names
    raw.rename(columns={
        "jobcountry": "country",
        "display_name": "sector",
        "indeed_job_postings_index": "value",
    }, inplace=True)

    data["raw"] = raw

    countries = sorted(raw["country"].dropna().unique().tolist())
    data["countries"] = countries

    sectors = sorted(raw["sector"].dropna().unique().tolist())
    data["sectors"] = sectors

    # Aggregate daily data to monthly means before pivoting
    raw["month"] = raw["date"].dt.to_period("M")

    # Per-country monthly pivoted DataFrames
    for country in countries:
        subset = raw[raw["country"] == country]
        pivot = (
            subset.groupby(["month", "sector"])["value"]
            .mean()
            .unstack()
            .sort_index()
        )
        pivot.index = pivot.index.to_timestamp()
        data[country] = pivot

    # Global = mean across all countries (monthly)
    global_pivot = (
        raw.groupby(["month", "sector"])["value"]
        .mean()
        .unstack()
        .sort_index()
    )
    global_pivot.index = global_pivot.index.to_timestamp()
    data["Global"] = global_pivot

    # ── Forecast data ──
    fc_path = DATA_DIR / "forecast.csv"
    if fc_path.exists():
        fc = pd.read_csv(fc_path)
        col_map = {"display_name": "sector", "forecast_mean": "mean",
                    "forecast_low": "low", "forecast_high": "high"}
        fc.rename(columns={k: v for k, v in col_map.items() if k in fc.columns}, inplace=True)
        data["forecast"] = fc

        # Only keep sectors that have both historical AND forecast data
        fc_sectors = set(fc["sector"].dropna().unique())
        data["sectors"] = sorted([s for s in sectors if s in fc_sectors])
    else:
        data["forecast"] = None
        print(f"WARNING: No forecast.csv found at {fc_path}")

    # ── Model metrics ──
    metrics_path = DATA_DIR / "model_metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            data["metrics"] = json.load(f)
    else:
        data["metrics"] = {}

    return data


def init_data():
    global DB, DATA_LOADED
    try:
        DB = load_data()
        DATA_LOADED = True
        print(f"Data loaded: {len(DB.get('sectors', []))} sectors, "
              f"{len(DB.get('countries', []))} countries")
    except FileNotFoundError as e:
        DB = {}
        DATA_LOADED = False
        print(f"WARNING: {e}")


init_data()


# ═══════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════

class ForecastRequest(BaseModel):
    region: str
    sector: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"region": "Global", "sector": "Accounting"}]
        }
    }


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.get("/health")
def health():
    return {
        "status": "ok",
        "data_loaded": DATA_LOADED,
        "sectors_count": len(DB.get("sectors", [])),
        "countries_count": len(DB.get("countries", [])),
    }


@app.get("/metadata")
def get_metadata():
    if not DATA_LOADED:
        raise HTTPException(503, "Data not loaded. Run train.py first.")

    regions = ["Global"] + DB["countries"]
    sectors = DB["sectors"]

    metrics = DB.get("metrics", {})
    best = metrics.get("best_model", "gru")
    best_m = metrics.get(best, {})

    global_df = DB["Global"]

    return {
        "regions": regions,
        "sectors": sectors,
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


@app.post("/forecast")
def forecast(req: ForecastRequest):
    if not DATA_LOADED:
        raise HTTPException(503, "Data not loaded.")

    region = req.region
    sector = req.sector

    valid_regions = ["Global"] + DB["countries"]
    if region not in valid_regions:
        raise HTTPException(400, f"Unknown region '{region}'. Available: {valid_regions}")

    hist_df = DB.get(region)
    if hist_df is None:
        raise HTTPException(400, f"No historical data for region '{region}'")

    if sector not in hist_df.columns:
        raise HTTPException(400, f"Unknown sector '{sector}'. Available: {hist_df.columns.tolist()}")

    # Historical (last N months)
    hist_series = hist_df[sector].dropna().tail(HIST_DISPLAY_MONTHS)
    hist_dates = [d.strftime("%Y-%m") for d in hist_series.index]
    hist_values = hist_series.round(1).tolist()

    # Forecast
    fc_df = DB.get("forecast")
    if fc_df is None or fc_df.empty:
        raise HTTPException(400, "No forecast data. Run train.py first.")

    fc_sector = fc_df[fc_df["sector"] == sector].copy()
    if fc_sector.empty:
        raise HTTPException(400, f"No forecast for sector '{sector}'")

    fc_sector = fc_sector.sort_values("date")
    fc_dates = fc_sector["date"].tolist()
    fc_values = fc_sector["mean"].round(1).tolist()
    fc_low_vals = fc_sector["low"].round(1).tolist()
    fc_high_vals = fc_sector["high"].round(1).tolist()

    current_value = float(hist_series.iloc[-1])
    projected_value = float(fc_values[-1])

    # Scale for non-Global regions
    if region != "Global":
        global_hist = DB["Global"][sector].dropna()
        global_last = float(global_hist.iloc[-1])
        if global_last > 0:
            scale = current_value / global_last
            fc_values = [round(v * scale, 1) for v in fc_values]
            fc_low_vals = [round(v * scale, 1) for v in fc_low_vals]
            fc_high_vals = [round(v * scale, 1) for v in fc_high_vals]
            projected_value = float(fc_values[-1])

    change_pct = round(
        (projected_value - current_value) / current_value * 100, 1
    ) if current_value != 0 else 0.0

    return {
        "region": region,
        "sector": sector,
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
