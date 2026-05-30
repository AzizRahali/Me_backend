"""
DL Forecast -- Local Training & Export Pipeline
----------------------------------------------
Converts the Kaggle notebook (job_market_forecasting_v3) into a runnable script.
Reads raw CSVs from DATA_INPUT_DIR, trains LSTM/GRU/BiLSTM ensembles,
generates 6-month forecasts, and exports everything to DATA_OUTPUT_DIR.

Usage:
    pip install -r requirements-train.txt
    python train.py

Output (in ./data/):
    historical.csv       -- raw long-format data for all countries
    forecast.csv         -- 6-month forecast (date, sector, mean, low, high)
    model_metrics.json   -- per-architecture evaluation metrics
    models/              -- saved Keras model weights
"""

import json
import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.seasonal import STL

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # suppress TF info logs

import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.layers import GRU, LSTM, Bidirectional, Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.regularizers import l2


# ===========================================================
# CONFIGURATION
# ===========================================================

DATA_INPUT_DIR = Path(os.getenv("DATA_INPUT_DIR", r"D:\ME\deep_learning_ME"))
DATA_OUTPUT_DIR = Path(os.getenv("DATA_OUTPUT_DIR", "./data"))
MODEL_OUTPUT_DIR = DATA_OUTPUT_DIR / "models"

COUNTRIES = {
    "US": "job_postings_by_sector_US.csv",
    "AU": "job_postings_by_sector_AU.csv",
    "CA": "job_postings_by_sector_CA.csv",
    "DE": "job_postings_by_sector_DE.csv",
    "FR": "job_postings_by_sector_FR.csv",
    "GB": "job_postings_by_sector_GB.csv",
}

DESIRED_SECTORS = [
    "Software Development",
    "Data & Analytics",
    "IT Systems & Solutions",
    "Project Management",
    "Marketing",
    "Management",
    "Banking & Finance",
    "Human Resources",
]

LOOK_BACK = 12
FORECAST_MONTHS = 6
N_ENSEMBLE = 7
SEEDS = [7, 23, 42, 101, 314, 1729, 2718]
MODEL_TYPES = ["lstm", "gru", "bilstm"]


# ===========================================================
# STEP 1 -- LOAD ALL COUNTRY DATASETS
# ===========================================================

def smart_read_csv(filepath):
    """Auto-detect separator and parse date column robustly."""
    with open(filepath, "r", encoding="utf-8") as f:
        first_line = f.readline()
    sep = ";" if first_line.count(";") > first_line.count(",") else ","
    df = pd.read_csv(filepath, sep=sep)
    # Normalize date column name
    date_col = next((c for c in df.columns if c.lower() == "date"), None)
    if date_col is None:
        raise ValueError(f"No date column in {filepath}. Columns: {list(df.columns)}")
    if date_col != "date":
        df = df.rename(columns={date_col: "date"})
    # Try month-first then day-first
    parsed = pd.to_datetime(df["date"], errors="coerce", dayfirst=False)
    if parsed.isna().any():
        parsed = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
    df["date"] = parsed
    return df


def load_all_countries():
    print("\n" + "=" * 60)
    print("  STEP 1 -- Loading country datasets")
    print("=" * 60)

    dfs_raw = {}
    all_raw_frames = []

    for country, filename in COUNTRIES.items():
        filepath = DATA_INPUT_DIR / country / filename
        # Also try flat directory (no country subfolder)
        if not filepath.exists():
            filepath = DATA_INPUT_DIR / filename
        if not filepath.exists():
            print(f"  X {country}: file not found")
            continue

        df_c = smart_read_csv(filepath)
        df_c["country"] = country
        # Fix: some files have jobcountry=US even for non-US files
        df_c["jobcountry"] = country
        dfs_raw[country] = df_c
        all_raw_frames.append(df_c)
        print(
            f"  OK {country}: {df_c.shape[0]:>7,} rows | "
            f"{df_c['display_name'].nunique():>2} sectors | "
            f"{df_c['date'].min().date()} -> {df_c['date'].max().date()}"
        )

    print(f"\n  Loaded {len(dfs_raw)} countries")

    # Combine into one raw DataFrame for historical export
    raw_combined = pd.concat(all_raw_frames, ignore_index=True)
    return dfs_raw, raw_combined


# ===========================================================
# STEP 2 -- AGGREGATE TO MONTHLY GLOBAL INDEX
# ===========================================================

def aggregate_global(dfs_raw):
    print("\n" + "=" * 60)
    print("  STEP 2 -- Aggregating to monthly global index")
    print("=" * 60)

    # Common sectors across all countries
    sector_sets = [set(dfs_raw[c]["display_name"].unique()) for c in COUNTRIES if c in dfs_raw]
    common_all = set.intersection(*sector_sets)
    sectors = [s for s in DESIRED_SECTORS if s in common_all]
    dropped = [s for s in DESIRED_SECTORS if s not in common_all]

    print(f"  Sectors kept: {len(sectors)} / {len(DESIRED_SECTORS)}")
    for s in sectors:
        print(f"    OK {s}")
    if dropped:
        print("  Dropped (not in every country):")
        for s in dropped:
            print(f"    X {s}")

    # Per-country monthly aggregation
    country_monthly = {}
    for c in COUNTRIES:
        if c not in dfs_raw:
            continue
        df = dfs_raw[c]
        df = df[(df["variable"] == "new postings") & (df["display_name"].isin(sectors))].copy()
        df["period"] = df["date"].dt.to_period("M")
        m = (
            df.groupby(["period", "display_name"])["indeed_job_postings_index"]
            .mean()
            .unstack()
            .sort_index()
        )
        m.index = m.index.to_timestamp()
        country_monthly[c] = m[sectors]

    # Global = mean across all countries
    global_monthly = sum(country_monthly[c] for c in country_monthly) / len(country_monthly)

    print(f"\n  Global monthly index: {global_monthly.shape[0]} months x {global_monthly.shape[1]} sectors")
    print(f"  Date range: {global_monthly.index.min().date()} -> {global_monthly.index.max().date()}")
    print(f"  Index range: {global_monthly.values.min():.1f} -- {global_monthly.values.max():.1f}")

    return global_monthly, country_monthly, sectors


# ===========================================================
# STEP 3 -- STL DENOISING
# ===========================================================

def stl_denoise(global_monthly):
    print("\n" + "=" * 60)
    print("  STEP 3 -- STL decomposition (denoising)")
    print("=" * 60)

    g_trend = pd.DataFrame(index=global_monthly.index, columns=global_monthly.columns, dtype=float)
    g_seas = pd.DataFrame(index=global_monthly.index, columns=global_monthly.columns, dtype=float)

    for sector in global_monthly.columns:
        result = STL(global_monthly[sector], period=12, robust=True).fit()
        g_trend[sector] = result.trend
        g_seas[sector] = result.seasonal

    global_denoised = g_trend + g_seas
    print(f"  Denoised shape: {global_denoised.shape}")
    return global_denoised


# ===========================================================
# STEP 4 -- FEATURE ENGINEERING
# ===========================================================

def engineer_features(global_monthly, global_denoised):
    print("\n" + "=" * 60)
    print("  STEP 4 -- Feature engineering")
    print("=" * 60)

    values = global_denoised.values.astype(np.float32)
    raw_values = global_monthly.values.astype(np.float32)

    diff_values = np.diff(values, axis=0)
    diff_index = global_monthly.index[1:]

    months_arr = diff_index.month.values
    month_sin = np.sin(2 * np.pi * months_arr / 12).reshape(-1, 1)
    month_cos = np.cos(2 * np.pi * months_arr / 12).reshape(-1, 1)

    rolling_std = pd.DataFrame(values, index=global_monthly.index).rolling(3, min_periods=1).std().values[1:]

    covid_flag = np.asarray(
        (diff_index >= "2020-03") & (diff_index <= "2020-06"), dtype=float
    ).reshape(-1, 1)

    extra = np.hstack([month_sin, month_cos, rolling_std, covid_flag])

    n_sectors = diff_values.shape[1]
    n_features_in = n_sectors + extra.shape[1]

    print(f"  Sectors: {n_sectors}")
    print(f"  Extra features: {extra.shape[1]} (2 seasonal + {rolling_std.shape[1]} volatility + 1 covid)")
    print(f"  Total input features: {n_features_in}")

    # Chronological split 70/15/15
    n_diff = len(diff_values)
    train_end = int(n_diff * 0.70)
    val_end = int(n_diff * 0.85)

    diff_train = diff_values[:train_end]
    diff_val = diff_values[train_end:val_end]
    diff_test = diff_values[val_end:]
    extra_train = extra[:train_end]
    extra_val = extra[train_end:val_end]
    extra_test = extra[val_end:]

    scaler_diff = MinMaxScaler(feature_range=(-1, 1))
    scaler_extra = MinMaxScaler()

    diff_train_s = scaler_diff.fit_transform(diff_train)
    diff_val_s = scaler_diff.transform(diff_val)
    diff_test_s = scaler_diff.transform(diff_test)

    extra_train_s = scaler_extra.fit_transform(extra_train)
    extra_val_s = scaler_extra.transform(extra_val)
    extra_test_s = scaler_extra.transform(extra_test)

    train_feat = np.hstack([diff_train_s, extra_train_s])
    val_feat = np.hstack([diff_val_s, extra_val_s])
    test_feat = np.hstack([diff_test_s, extra_test_s])

    def create_sequences(feat, target, look_back):
        X, y = [], []
        for i in range(len(feat) - look_back):
            X.append(feat[i : i + look_back])
            y.append(target[i + look_back])
        return np.array(X), np.array(y)

    X_train, y_train = create_sequences(train_feat, diff_train_s, LOOK_BACK)
    X_val, y_val = create_sequences(
        np.vstack([train_feat[-LOOK_BACK:], val_feat]),
        np.vstack([diff_train_s[-LOOK_BACK:], diff_val_s]),
        LOOK_BACK,
    )
    X_test, y_test = create_sequences(
        np.vstack([val_feat[-LOOK_BACK:], test_feat]),
        np.vstack([diff_val_s[-LOOK_BACK:], diff_test_s]),
        LOOK_BACK,
    )

    print(f"  X_train: {X_train.shape} | X_val: {X_val.shape} | X_test: {X_test.shape}")

    return {
        "X_train": X_train, "y_train": y_train,
        "X_val": X_val, "y_val": y_val,
        "X_test": X_test, "y_test": y_test,
        "values": values, "raw_values": raw_values,
        "diff_values": diff_values,
        "scaler_diff": scaler_diff, "scaler_extra": scaler_extra,
        "train_end": train_end, "val_end": val_end,
        "n_sectors": n_sectors, "n_features_in": n_features_in,
        "train_feat": train_feat, "val_feat": val_feat, "test_feat": test_feat,
        "diff_train_s": diff_train_s, "diff_val_s": diff_val_s, "diff_test_s": diff_test_s,
        "extra": extra,
    }


# ===========================================================
# STEP 5 -- BUILD MODELS
# ===========================================================

def build_model(seed, model_type, n_features_in, n_sectors):
    tf.keras.utils.set_random_seed(seed)
    if model_type == "lstm":
        rnn = LSTM(
            48, input_shape=(LOOK_BACK, n_features_in),
            dropout=0.20, recurrent_dropout=0.20,
            kernel_regularizer=l2(5e-3), recurrent_regularizer=l2(5e-3),
        )
    elif model_type == "gru":
        rnn = GRU(
            48, input_shape=(LOOK_BACK, n_features_in),
            dropout=0.20, recurrent_dropout=0.20,
            kernel_regularizer=l2(5e-3), recurrent_regularizer=l2(5e-3),
        )
    elif model_type == "bilstm":
        rnn = Bidirectional(
            LSTM(
                24, dropout=0.20, recurrent_dropout=0.20,
                kernel_regularizer=l2(5e-3), recurrent_regularizer=l2(5e-3),
            ),
            input_shape=(LOOK_BACK, n_features_in),
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    model = Sequential(
        [rnn, Dropout(0.35), Dense(n_sectors)],
        name=f"{model_type}_seed{seed}",
    )
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss=tf.keras.losses.Huber(delta=1.0),
        metrics=["mae"],
    )
    return model


# ===========================================================
# STEP 6 -- TRAIN ALL ENSEMBLES
# ===========================================================

def train_all_ensembles(feat):
    print("\n" + "=" * 60)
    print("  STEP 6 -- Training ensembles (3 architectures x 7 seeds)")
    print("=" * 60)

    all_ensembles = {}

    for mt in MODEL_TYPES:
        print(f"\n  {'-' * 50}")
        print(f"  Training {mt.upper()} ensemble")
        print(f"  {'-' * 50}")
        models = []
        for seed in SEEDS:
            mdl = build_model(seed, mt, feat["n_features_in"], feat["n_sectors"])
            cbs = [
                EarlyStopping(monitor="val_loss", patience=20, restore_best_weights=True, verbose=0),
                ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=8, min_lr=1e-5, verbose=0),
            ]
            h = mdl.fit(
                feat["X_train"], feat["y_train"],
                validation_data=(feat["X_val"], feat["y_val"]),
                epochs=250, batch_size=8, callbacks=cbs, verbose=0,
            )
            models.append(mdl)
            print(
                f"    seed {seed:>4} | best val_loss = {min(h.history['val_loss']):.4f}"
                f"  ({len(h.history['loss'])} epochs)"
            )
        all_ensembles[mt] = models

    return all_ensembles


def ensemble_predict(models, X, scaler):
    preds_s = np.stack([m.predict(X, verbose=0) for m in models], axis=0)
    mean_d = scaler.inverse_transform(preds_s.mean(axis=0))
    return mean_d


# ===========================================================
# STEP 7 -- EVALUATE & SELECT BEST
# ===========================================================

def evaluate_and_select(all_ensembles, feat, global_monthly):
    print("\n" + "=" * 60)
    print("  STEP 7 -- Evaluation & best architecture selection")
    print("=" * 60)

    raw_values = feat["raw_values"]
    val_end = feat["val_end"]
    scaler_diff = feat["scaler_diff"]
    values = feat["values"]
    train_end = feat["train_end"]

    model_predictions = {}
    for mt in MODEL_TYPES:
        mean_diff = ensemble_predict(all_ensembles[mt], feat["X_test"], scaler_diff)
        anchor = values[val_end : val_end + len(mean_diff)]
        model_predictions[mt] = anchor + mean_diff

    y_true = raw_values[val_end + 1 : val_end + 1 + len(model_predictions["lstm"])]
    test_dates = global_monthly.index[val_end + 1 : val_end + 1 + len(y_true)]
    yt_flat = y_true.flatten()

    # Naive baselines
    y_naive = np.vstack([raw_values[val_end].reshape(1, -1), y_true[:-1]])
    y_seasonal = np.vstack(
        [raw_values[global_monthly.index.get_loc(d - pd.DateOffset(years=1))] for d in test_dates]
    )

    def compute_metrics(yt, yp):
        return {
            "rmse": round(float(np.sqrt(mean_squared_error(yt, yp))), 4),
            "mae": round(float(mean_absolute_error(yt, yp)), 4),
            "r2": round(float(r2_score(yt, yp)), 4),
        }

    comparison = {
        "naive": compute_metrics(yt_flat, y_naive.flatten()),
        "seasonal_naive": compute_metrics(yt_flat, y_seasonal.flatten()),
    }

    print(f"\n  {'Model':<25} {'RMSE':>8}  {'MAE':>8}  {'R2':>8}")
    print("  " + "=" * 55)

    for label, yp in [("Naive (last value)", y_naive), ("Seasonal-Naive", y_seasonal)]:
        m = compute_metrics(yt_flat, yp.flatten())
        print(f"  {label:<25} {m['rmse']:>8.2f}  {m['mae']:>8.2f}  {m['r2']:>8.4f}")

    # Bias correction & selection
    best_mt = None
    best_rmse = float("inf")
    bias_d = {}
    corr_d = {}
    all_metrics = {}

    for mt in MODEL_TYPES:
        # Bias on validation
        vd = ensemble_predict(all_ensembles[mt], feat["X_val"], scaler_diff)
        va = values[train_end : train_end + len(vd)]
        vt = raw_values[train_end + 1 : train_end + 1 + len(vd)]
        b = np.mean(vt - (va + vd), axis=0)

        yp = model_predictions[mt]
        yp_c = yp + b
        r_o = np.sqrt(mean_squared_error(yt_flat, yp.flatten()))
        r_c = np.sqrt(mean_squared_error(yt_flat, yp_c.flatten()))

        if r_c < r_o:
            bias_d[mt] = b
            corr_d[mt] = yp_c
            fr = r_c
            bc_note = f"bias corrected ({r_o:.2f} -> {r_c:.2f})"
        else:
            bias_d[mt] = np.zeros_like(b)
            corr_d[mt] = yp
            fr = r_o
            bc_note = f"no bias correction ({r_o:.2f})"

        m = compute_metrics(yt_flat, corr_d[mt].flatten())
        all_metrics[mt] = m
        comparison[mt] = m
        print(f"  {mt.upper() + ' Ensemble':<25} {m['rmse']:>8.2f}  {m['mae']:>8.2f}  {m['r2']:>8.4f}  [{bc_note}]")

        if fr < best_rmse:
            best_rmse = fr
            best_mt = mt

    print(f"\n  * Best architecture: {best_mt.upper()} (RMSE = {best_rmse:.2f})")

    return best_mt, bias_d, all_metrics, comparison


# ===========================================================
# STEP 8 -- 6-MONTH FORECAST
# ===========================================================

def generate_forecast(all_ensembles, best_mt, bias_d, feat, global_monthly, sectors):
    print("\n" + "=" * 60)
    print(f"  STEP 8 -- 6-month forecast ({best_mt.upper()} ensemble)")
    print("=" * 60)

    values = feat["values"]
    scaler_diff = feat["scaler_diff"]
    scaler_extra = feat["scaler_extra"]
    diff_values = feat["diff_values"]
    extra = feat["extra"]

    full_diff_s = scaler_diff.transform(diff_values)
    full_extra_s = scaler_extra.transform(extra)
    full_feat = np.hstack([full_diff_s, full_extra_s])

    def recursive_forecast(model, n_steps):
        last_window = full_feat[-LOOK_BACK:].copy()
        last_abs = values[-1].copy()
        last_month_num = global_monthly.index[-1].month
        recent_levels = list(values[-3:])

        out = []
        for _ in range(n_steps):
            pred_diff_s = model.predict(last_window[np.newaxis], verbose=0)[0]
            pred_diff_val = scaler_diff.inverse_transform(pred_diff_s.reshape(1, -1))[0]
            next_abs = last_abs + pred_diff_val
            out.append(next_abs)

            recent_levels = recent_levels[-2:] + [next_abs]
            next_rstd = np.std(np.stack(recent_levels), axis=0, ddof=1)
            next_month_num = (last_month_num % 12) + 1
            next_sin = np.sin(2 * np.pi * next_month_num / 12)
            next_cos = np.cos(2 * np.pi * next_month_num / 12)

            next_extra_raw = np.hstack([[[next_sin, next_cos]], next_rstd.reshape(1, -1), [[0.0]]])
            next_extra_s = scaler_extra.transform(next_extra_raw)
            next_row = np.hstack([pred_diff_s.reshape(1, -1), next_extra_s]).squeeze()
            last_window = np.vstack([last_window[1:], next_row])
            last_abs = next_abs
            last_month_num = next_month_num
        return np.array(out)

    best_models = all_ensembles[best_mt]
    best_bias = bias_d[best_mt]

    print("  Running recursive forecast for each ensemble member...")
    member_fc = np.stack([recursive_forecast(m, FORECAST_MONTHS) for m in best_models])
    fc_mean = member_fc.mean(axis=0) + best_bias
    fc_low = np.quantile(member_fc, 0.10, axis=0) + best_bias
    fc_high = np.quantile(member_fc, 0.90, axis=0) + best_bias

    fc_dates = pd.date_range(
        start=global_monthly.index[-1] + pd.DateOffset(months=1),
        periods=FORECAST_MONTHS, freq="MS",
    )

    # Build forecast DataFrame (long format for the API)
    rows = []
    for step in range(FORECAST_MONTHS):
        for j, sector in enumerate(sectors):
            rows.append({
                "date": fc_dates[step].strftime("%Y-%m"),
                "sector": sector,
                "mean": round(float(fc_mean[step, j]), 2),
                "low": round(float(fc_low[step, j]), 2),
                "high": round(float(fc_high[step, j]), 2),
            })

    forecast_df = pd.DataFrame(rows)

    # Summary
    print(f"\n  {'Sector':<28} {'Current':>8} {'Forecast':>9} {'Change':>8}")
    print("  " + "-" * 58)
    raw_values = feat["raw_values"]
    for j, sector in enumerate(sectors):
        cur = float(raw_values[-1, j])
        proj = float(fc_mean[-1, j])
        pct = (proj - cur) / cur * 100 if cur != 0 else 0
        arrow = "UP" if pct >= 0 else "DN"
        print(f"  {sector:<28} {cur:>8.1f} {proj:>9.1f} {arrow} {pct:>+6.1f}%")

    return forecast_df, fc_dates


# ===========================================================
# STEP 9 -- EXPORT EVERYTHING
# ===========================================================

def export_results(raw_combined, forecast_df, all_metrics, best_mt, all_ensembles, comparison):
    print("\n" + "=" * 60)
    print("  STEP 9 -- Exporting results")
    print("=" * 60)

    DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Historical data (raw long format)
    hist_cols = ["date", "jobcountry", "indeed_job_postings_index", "variable", "display_name"]
    available_cols = [c for c in hist_cols if c in raw_combined.columns]
    hist_export = raw_combined[available_cols].copy()
    hist_export["date"] = pd.to_datetime(hist_export["date"]).dt.strftime("%Y-%m-%d")
    hist_path = DATA_OUTPUT_DIR / "historical.csv"
    hist_export.to_csv(hist_path, index=False)
    print(f"  OK historical.csv  ({len(hist_export):,} rows)")

    # 2. Forecast data
    fc_path = DATA_OUTPUT_DIR / "forecast.csv"
    forecast_df.to_csv(fc_path, index=False)
    print(f"  OK forecast.csv    ({len(forecast_df)} rows)")

    # 3. Model metrics
    metrics = {
        "best_model": best_mt,
    }
    for mt in MODEL_TYPES:
        if mt in all_metrics:
            metrics[mt] = all_metrics[mt]

    # Add baselines
    if "naive" in comparison:
        metrics["naive"] = comparison["naive"]
    if "seasonal_naive" in comparison:
        metrics["seasonal_naive"] = comparison["seasonal_naive"]

    metrics_path = DATA_OUTPUT_DIR / "model_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"  OK model_metrics.json")

    # 4. Save model weights
    for mt in MODEL_TYPES:
        if mt in all_ensembles:
            for i, model in enumerate(all_ensembles[mt]):
                model_path = MODEL_OUTPUT_DIR / f"{mt}_seed{SEEDS[i]}.keras"
                model.save(model_path)
            print(f"  OK {mt} models ({len(all_ensembles[mt])} saved)")

    print(f"\n  All outputs saved to: {DATA_OUTPUT_DIR.resolve()}")


# ===========================================================
# MAIN
# ===========================================================

def main():
    print("=" * 60)
    print("  DL Forecast -- Local Training Pipeline")
    print("  LSTM / GRU / BiLSTM Ensemble (7 seeds each)")
    print("=" * 60)
    print(f"\n  Input:  {DATA_INPUT_DIR}")
    print(f"  Output: {DATA_OUTPUT_DIR}")

    # Check input exists
    if not DATA_INPUT_DIR.exists():
        print(f"\n  ERROR: Input directory not found: {DATA_INPUT_DIR}")
        print("  Set DATA_INPUT_DIR environment variable or update the script.")
        sys.exit(1)

    # Step 1: Load
    dfs_raw, raw_combined = load_all_countries()

    # Step 2: Aggregate
    global_monthly, country_monthly, sectors = aggregate_global(dfs_raw)

    # Step 3: Denoise
    global_denoised = stl_denoise(global_monthly)

    # Step 4: Features
    feat = engineer_features(global_monthly, global_denoised)

    # Step 6: Train (Step 5 is model definition, included in build_model)
    all_ensembles = train_all_ensembles(feat)

    # Step 7: Evaluate
    best_mt, bias_d, all_metrics, comparison = evaluate_and_select(
        all_ensembles, feat, global_monthly
    )

    # Step 8: Forecast
    forecast_df, fc_dates = generate_forecast(
        all_ensembles, best_mt, bias_d, feat, global_monthly, sectors
    )

    # Step 9: Export
    export_results(raw_combined, forecast_df, all_metrics, best_mt, all_ensembles, comparison)

    print("\n" + "=" * 60)
    print("  DONE: DONE -- Restart the API to load new data:")
    print("     docker restart dl_forecast_api")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
