from __future__ import annotations

import ast
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_jobs_enriched.csv"
MODEL_PATH = Path(__file__).resolve().parent / "salary_prediction_pipeline.joblib"
METADATA_PATH = Path(__file__).resolve().parent / "model_metadata.json"


def parse_skills_to_text(value: object) -> str:
    if pd.isna(value) or value == "Unknown":
        return ""
    try:
        skills = ast.literal_eval(value) if isinstance(value, str) else value
    except (ValueError, SyntaxError):
        return ""
    if not isinstance(skills, list):
        return ""
    return " ".join(
        str(skill).strip().lower().replace(" ", "_")
        for skill in skills
        if str(skill).strip()
    )


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    salary_df = df[df["salary_year_avg"].notna()].copy()
    salary_df["log_salary_year_avg"] = np.log1p(salary_df["salary_year_avg"])

    lower_salary_limit = salary_df["salary_year_avg"].quantile(0.01)
    upper_salary_limit = salary_df["salary_year_avg"].quantile(0.99)
    salary_df = salary_df[
        salary_df["salary_year_avg"].between(lower_salary_limit, upper_salary_limit)
    ].copy()

    categorical_fill_cols = [
        "job_title_short",
        "job_country",
        "job_schedule_type",
        "company_size",
    ]
    salary_df[categorical_fill_cols] = salary_df[categorical_fill_cols].fillna("Unknown")

    top_n_countries = 10
    top_countries = salary_df["job_country"].value_counts().head(top_n_countries).index.tolist()
    salary_df["job_country_grouped"] = salary_df["job_country"].where(
        salary_df["job_country"].isin(top_countries),
        "Other",
    )

    salary_df["job_title"] = salary_df["job_title"].fillna("")
    salary_df["job_skills"] = salary_df["job_skills"].fillna("Unknown")
    salary_df["skills_text"] = salary_df["job_skills"].apply(parse_skills_to_text)

    categorical_features = [
        "job_title_short",
        "job_country_grouped",
        "job_schedule_type",
        "company_size",
    ]
    boolean_features = [
        "job_work_from_home",
        "job_no_degree_mention",
        "job_health_insurance",
    ]
    text_features = [
        "job_title",
        "skills_text",
    ]
    features = categorical_features + boolean_features + text_features
    target = "log_salary_year_avg"

    model_df = salary_df[features + ["salary_year_avg", target]].copy()

    X = model_df[features]
    y = model_df[target]
    raw_salary = model_df["salary_year_avg"]

    X_train, X_test, y_train, y_test, raw_train, raw_test = train_test_split(
        X,
        y,
        raw_salary,
        test_size=0.2,
        random_state=42,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical_one_hot",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            ),
            ("boolean", "passthrough", boolean_features),
            (
                "job_title_tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    ngram_range=(1, 2),
                    max_features=300,
                    min_df=10,
                ),
                "job_title",
            ),
            (
                "skills_tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    token_pattern=r"(?u)\b\w[\w+#.-]+\b",
                    max_features=100,
                    min_df=20,
                ),
                "skills_text",
            ),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        max_depth=None,
        min_samples_leaf=5,
        n_jobs=1,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )
    pipeline.fit(X_train, y_train)

    pred_log = pipeline.predict(X_test)
    pred_salary = np.maximum(np.expm1(pred_log), 0)
    metrics = {
        "MAE_dollars": float(mean_absolute_error(raw_test, pred_salary)),
        "MedianAE_dollars": float(median_absolute_error(raw_test, pred_salary)),
        "RMSE_dollars": float(np.sqrt(mean_squared_error(raw_test, pred_salary))),
        "R2_log_target": float(r2_score(y_test, pred_log)),
    }

    metadata = {
        "model_name": "RandomForestRegressor + OneHot + job_title/skills TF-IDF",
        "target": "log_salary_year_avg",
        "prediction_transform": "salary = expm1(model_prediction)",
        "salary_outlier_limits": {
            "lower": float(lower_salary_limit),
            "upper": float(upper_salary_limit),
        },
        "metrics": metrics,
        "input_schema": {
            "job_title_short": "string",
            "job_country": "string; grouped to Other if not in top_countries",
            "job_schedule_type": "string",
            "company_size": "string",
            "job_work_from_home": "boolean",
            "job_no_degree_mention": "boolean",
            "job_health_insurance": "boolean",
            "job_title": "string",
            "job_skills": "list of strings",
        },
        "model_features": features,
        "categorical_features": categorical_features,
        "boolean_features": boolean_features,
        "text_features": text_features,
        "top_countries": top_countries,
        "options": {
            "job_title_short": sorted(salary_df["job_title_short"].dropna().unique().tolist()),
            "job_country": top_countries + ["Other"],
            "job_schedule_type": sorted(salary_df["job_schedule_type"].dropna().unique().tolist()),
            "company_size": sorted(salary_df["company_size"].dropna().unique().tolist()),
        },
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Saved model to {MODEL_PATH}")
    print(f"Saved metadata to {METADATA_PATH}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
