"""
Migration script: SQL Server (.bak restored) → PostgreSQL

Usage:
  1. Update the connection strings below
  2. pip install pyodbc psycopg2-binary sqlalchemy pandas
  3. python migrate.py
"""

import pyodbc
import pandas as pd
from sqlalchemy import create_engine, text

# ── Configuration ──────────────────────────────────────────────
# SQL Server (source)
SQL_SERVER = "localhost"  # or localhost\\SQLEXPRESS
SQL_DATABASE = "ME"
SQL_DRIVER = "ODBC Driver 17 for SQL Server"

# PostgreSQL (target)
PG_URL = "postgresql://postgres:postgres@localhost:5432/me_project"
# ───────────────────────────────────────────────────────────────

TABLES_IN_ORDER = [
    "DimDate",
    "DimCompany",
    "DimLocation",
    "DimSkill",
    "DimJob",
    "FactJobPosting",
    "StagingJobs",
]

PG_SCHEMA = """
DROP TABLE IF EXISTS fact_job_posting CASCADE;
DROP TABLE IF EXISTS staging_jobs CASCADE;
DROP TABLE IF EXISTS dim_job CASCADE;
DROP TABLE IF EXISTS dim_skill CASCADE;
DROP TABLE IF EXISTS dim_location CASCADE;
DROP TABLE IF EXISTS dim_company CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;

CREATE TABLE dim_date (
    date_id       INTEGER PRIMARY KEY,
    full_date     DATE NOT NULL,
    day           INTEGER,
    day_name      VARCHAR(20),
    month         INTEGER,
    month_name    VARCHAR(20),
    quarter       INTEGER,
    year          INTEGER,
    is_weekend    BOOLEAN,
    is_holiday    BOOLEAN
);

CREATE TABLE dim_company (
    company_id    INTEGER PRIMARY KEY,
    company_name  VARCHAR(1000) NOT NULL,
    company_size  VARCHAR(255),
    industry      VARCHAR(500)
);

CREATE TABLE dim_location (
    location_id   INTEGER PRIMARY KEY,
    city          VARCHAR(255),
    country       VARCHAR(100),
    region        VARCHAR(100),
    continent     VARCHAR(100)
);

CREATE TABLE dim_skill (
    skill_id       INTEGER PRIMARY KEY,
    skill_name     VARCHAR(255) NOT NULL,
    skill_category VARCHAR(255)
);

CREATE TABLE dim_job (
    job_id             INTEGER PRIMARY KEY,
    job_title_short    VARCHAR(255),
    job_via            VARCHAR(255),
    schedule_type      VARCHAR(100),
    is_remote          BOOLEAN,
    no_degree_mention  BOOLEAN,
    health_insurance   BOOLEAN,
    yearly_salary      DECIMAL,
    hourly_salary      DECIMAL
);

CREATE TABLE fact_job_posting (
    posting_id              INTEGER PRIMARY KEY,
    date_id                 INTEGER REFERENCES dim_date(date_id),
    company_id              INTEGER REFERENCES dim_company(company_id),
    location_id             INTEGER REFERENCES dim_location(location_id),
    job_id                  INTEGER REFERENCES dim_job(job_id),
    representative_skill_id INTEGER REFERENCES dim_skill(skill_id)
);

CREATE TABLE staging_jobs (
    staging_id             INTEGER PRIMARY KEY,
    job_title_short        VARCHAR(500),
    job_title              TEXT,
    job_location           TEXT,
    job_via                TEXT,
    job_schedule_type      VARCHAR(255),
    job_work_from_home     BOOLEAN,
    search_location        TEXT,
    job_posted_date        TIMESTAMP,
    job_no_degree_mention  BOOLEAN,
    job_health_insurance   BOOLEAN,
    job_country            VARCHAR(255),
    salary_rate            VARCHAR(100),
    salary_year_avg        DECIMAL,
    salary_hour_avg        DECIMAL,
    company_name           TEXT,
    job_skills             TEXT,
    job_type_skills        TEXT,
    industry               TEXT,
    company_size           VARCHAR(255)
);
"""

# Map SQL Server table names to PostgreSQL table names
TABLE_MAP = {
    "DimDate": "dim_date",
    "DimCompany": "dim_company",
    "DimLocation": "dim_location",
    "DimSkill": "dim_skill",
    "DimJob": "dim_job",
    "FactJobPosting": "fact_job_posting",
    "StagingJobs": "staging_jobs",
}


def get_sql_server_conn():
    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)


def migrate():
    print("Connecting to SQL Server...")
    sql_conn = get_sql_server_conn()

    print("Connecting to PostgreSQL...")
    pg_engine = create_engine(PG_URL)

    print("Creating PostgreSQL schema...")
    with pg_engine.connect() as conn:
        conn.execute(text(PG_SCHEMA))
        conn.commit()
    print("Schema created.\n")

    for sql_table in TABLES_IN_ORDER:
        pg_table = TABLE_MAP[sql_table]
        print(f"Migrating {sql_table} → {pg_table}...", end=" ")

        df = pd.read_sql(f"SELECT * FROM {sql_table}", sql_conn)
        df.columns = [c.lower() for c in df.columns]

        df.to_sql(pg_table, pg_engine, if_exists="append", index=False, method="multi", chunksize=5000)
        print(f"{len(df):,} rows done.")

    sql_conn.close()
    pg_engine.dispose()
    print("\nMigration complete!")


if __name__ == "__main__":
    migrate()
