"""
KAGGLE EXPORT CELLS
━━━━━━━━━━━━━━━━━━
Paste these cells at the END of your Kaggle notebook (job_market_forecasting_v3).
They export all data the FastAPI backend needs into /kaggle/working/forecast_export/
Download the zip and unzip into forecast_api/data/.

⚠️  Adjust variable names to match YOUR notebook's actual DataFrame names.
    Look for comments marked with ← CHANGE THIS
"""

# ╔═══════════════════════════════════════════════════════════╗
# ║  CELL 1 — Export historical data (as-is, long format)    ║
# ╚═══════════════════════════════════════════════════════════╝

import os
import json

OUTPUT_DIR = "/kaggle/working/forecast_export"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ← CHANGE THIS: replace `df` with your main DataFrame variable name
# It should have columns: date, jobcountry, indeed_job_postings_index, variable, display_name
#
# Example rows:
#   date,       jobcountry, indeed_job_postings_index, variable,       display_name
#   2020-02-01, US,         100,                       total postings, Accounting
#   2020-02-01, US,         100,                       new postings,   Accounting

historical_df = df  # ← CHANGE THIS to your actual variable name

# Keep only the columns the API needs
cols_needed = ["date", "jobcountry", "indeed_job_postings_index", "variable", "display_name"]
historical_df = historical_df[cols_needed].copy()

historical_df.to_csv(f"{OUTPUT_DIR}/historical.csv", index=False)
print(f"✓ historical.csv  →  {historical_df.shape}")
print(f"  Countries: {sorted(historical_df['jobcountry'].unique())}")
print(f"  Sectors:   {sorted(historical_df['display_name'].unique())}")
print(f"  Variables: {sorted(historical_df['variable'].unique())}")
print(f"  Date range: {historical_df['date'].min()} → {historical_df['date'].max()}")


# ╔═══════════════════════════════════════════════════════════╗
# ║  CELL 2 — Export forecast results (model predictions)    ║
# ╚═══════════════════════════════════════════════════════════╝

import pandas as pd
import numpy as np

# ← CHANGE THESE: replace with your actual forecast variables
# The API expects a DataFrame with columns: date, sector, mean, low, high
#
# If your model outputs per-sector forecasts separately, gather them:
#   - forecast_dates:  list of 6 future date strings ["2025-01", "2025-02", ...]
#   - sector_name:     sector being forecasted
#   - predictions:     array of shape (n_seeds, 6) from ensemble
#
# Below is a TEMPLATE — adapt to your actual forecast loop output.

rows = []

# ── Option A: If you have separate arrays per sector ──
# for sector_name in sectors_list:   # ← CHANGE THIS
#     for i, date in enumerate(forecast_dates):  # ← CHANGE THIS
#         preds = ensemble_predictions[sector_name]  # shape (n_seeds, 6)  ← CHANGE THIS
#         mean_val = float(np.mean(preds[:, i]))
#         low_val  = float(np.percentile(preds[:, i], 10))
#         high_val = float(np.percentile(preds[:, i], 90))
#         rows.append({
#             "date": date,
#             "sector": sector_name,
#             "mean": round(mean_val, 2),
#             "low": round(low_val, 2),
#             "high": round(high_val, 2),
#         })

# ── Option B: If you already have a forecast DataFrame ──
# Uncomment and adjust:
# forecast_result_df = your_forecast_df  # ← CHANGE THIS
# forecast_result_df = forecast_result_df.rename(columns={
#     "display_name": "sector",       # if your column is named differently
#     "forecast_mean": "mean",
#     "forecast_low": "low",
#     "forecast_high": "high",
# })
# rows = forecast_result_df[["date", "sector", "mean", "low", "high"]].to_dict("records")

# ── Option C: Build from your recursive forecast output ──
# This is the most common pattern from the notebook:

for sector_name in sector_names:  # ← CHANGE THIS to your list of sector names
    # Get the ensemble predictions for this sector
    # preds should be shape (n_seeds, forecast_horizon) e.g. (7, 6)
    preds = all_forecasts[sector_name]  # ← CHANGE THIS

    for step in range(preds.shape[1]):  # 6 months
        # Generate future dates from the last historical date
        last_date = pd.Timestamp(global_monthly.index[-1])  # ← CHANGE THIS
        future_date = last_date + pd.DateOffset(months=step + 1)

        mean_val = float(np.mean(preds[:, step]))
        low_val = float(np.percentile(preds[:, step], 10))
        high_val = float(np.percentile(preds[:, step], 90))

        rows.append({
            "date": future_date.strftime("%Y-%m"),
            "sector": sector_name,
            "mean": round(mean_val, 2),
            "low": round(low_val, 2),
            "high": round(high_val, 2),
        })

forecast_df = pd.DataFrame(rows)
forecast_df.to_csv(f"{OUTPUT_DIR}/forecast.csv", index=False)
print(f"\n✓ forecast.csv  →  {forecast_df.shape}")
print(f"  Sectors: {sorted(forecast_df['sector'].unique())}")
print(f"  Dates:   {sorted(forecast_df['date'].unique())}")
print(forecast_df.head(12))


# ╔═══════════════════════════════════════════════════════════╗
# ║  CELL 3 — Export model metrics                           ║
# ╚═══════════════════════════════════════════════════════════╝

# ← CHANGE THESE: fill in your actual evaluation metrics

metrics = {
    "best_model": "gru",       # ← whichever had lowest RMSE: "gru", "lstm", or "bilstm"
    "gru": {
        "rmse": 0.0,           # ← fill from your evaluation
        "mae": 0.0,
        "r2": 0.0,
    },
    "lstm": {
        "rmse": 0.0,
        "mae": 0.0,
        "r2": 0.0,
    },
    "bilstm": {
        "rmse": 0.0,
        "mae": 0.0,
        "r2": 0.0,
    },
}

# If you have the metrics in variables, uncomment and fill:
# metrics["gru"]["rmse"] = float(gru_rmse)
# metrics["gru"]["mae"]  = float(gru_mae)
# metrics["gru"]["r2"]   = float(gru_r2)
# metrics["lstm"]["rmse"] = float(lstm_rmse)
# ... etc

with open(f"{OUTPUT_DIR}/model_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n✓ model_metrics.json exported")
print(json.dumps(metrics, indent=2))


# ╔═══════════════════════════════════════════════════════════╗
# ║  CELL 4 — Zip everything for download                    ║
# ╚═══════════════════════════════════════════════════════════╝

import shutil

shutil.make_archive("/kaggle/working/forecast_data", "zip", OUTPUT_DIR)

files = os.listdir(OUTPUT_DIR)
print(f"\n📦 forecast_data.zip ready! ({len(files)} files)")
for f in sorted(files):
    size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
    print(f"   {f:30s}  {size:>10,} bytes")
print(f"\n→ Download from the Output tab")
print(f"→ Unzip into: forecast_api/data/")
print(f"→ Then run:   docker restart dl_forecast_api")
