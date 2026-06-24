# Weather Analytics Data Engineering Pipeline

A professional, maintainable ETL/ELT pipeline for weather analytics using the Open-Meteo API, Python, and PostgreSQL with Airflow orchestration.

## Project Overview

This project implements both ETL (Extract, Transform, Load) and ELT (Extract, Load, Transform) workflows for processing weather data. It features:
- Data extraction from the Open-Meteo public weather API
- Comprehensive data validation and quality checks
- Transformation and cleaning in Python
- Star schema design for analytics
- PostgreSQL database integration
- Daily Airflow orchestration
- Unit tests with pytest
- Structured logging

## Project Structure

```
.
├── AGENTS.md
├── README.md
├── requirements.txt
├── .env.example
├── dags/
│   └── weather_pipeline_dag.py       # Airflow DAG
├── sql/
│   └── schema.sql                     # Database star schema
├── src/
│   └── weather_pipeline/
│       ├── __init__.py
│       ├── config.py                  # Environment configuration
│       ├── extractor.py               # Data extraction from API
│       ├── transformer.py             # Data transformation
│       ├── validator.py               # Data validation
│       ├── loader.py                  # Database loading
│       ├── pipeline.py                # Main ETL/ELT pipeline class
│       └── utils/
│           ├── __init__.py
│           └── logging_config.py      # Logging setup
├── tests/
│   ├── test_extractor.py
│   ├── test_transformer.py
│   └── test_validator.py
├── data/
│   ├── raw/
│   ├── staging/
│   └── processed/
└── logs/
```

## Architecture

### ETL Workflow
1. **Extract**: Fetch daily weather data from Open-Meteo API
2. **Validate**: Check API response and data quality
3. **Transform**: Clean, convert data types, handle missing values
4. **Load**: Insert into fact and dimension tables

### ELT Workflow
1. **Extract**: Fetch raw weather data
2. **Load**: Insert raw JSON data into staging table
3. **Transform**: Process staged data and load into final tables

### Star Schema
```
dim_location (location_id PK, location_name, latitude, longitude)
dim_date (date_id PK, date, day, month, year, quarter, day_of_week, is_weekend)
fact_weather_observations (observation_id PK, location_id FK, date_id FK, temperature_2m_mean, temperature_2m_max, temperature_2m_min, relative_humidity_2m_mean, precipitation_sum, wind_speed_10m_max)
staging_weather_raw (staging_id PK, raw_data JSONB, location_name, extraction_date)
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Apache Airflow 2.7+

### Installation

1. **Clone or navigate to project directory**:
   ```bash
   cd "AICA CAPSTONE PROJECT"
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # Or on Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and preferences
   ```

5. **Set up PostgreSQL database**:
   - Create a database named `weather_db`
   - Update `DATABASE_URL` in `.env`

## Configuration

The `.env` file supports:
- `OPEN_METEO_BASE_URL`: Open-Meteo API base URL
- `WEATHER_LATITUDE`: Latitude of weather location
- `WEATHER_LONGITUDE`: Longitude of weather location
- `WEATHER_LOCATION_NAME`: Name of location
- `DATABASE_URL`: PostgreSQL connection string
- `PIPELINE_START_DATE`: Default pipeline start date
- `PIPELINE_END_DATE`: Default pipeline end date
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

## Running the Pipeline Locally

### Run ETL Pipeline
```python
from src.weather_pipeline.pipeline import WeatherETLPipeline

pipeline = WeatherETLPipeline()
pipeline.run_etl(start_date="2026-06-01", end_date="2026-06-30")
```

### Run ELT Workflow
```python
from src.weather_pipeline.pipeline import WeatherETLPipeline

pipeline = WeatherETLPipeline()
pipeline.run_elt(start_date="2026-06-01", end_date="2026-06-30")
```

## Airflow Setup

1. **Initialize Airflow database**:
   ```bash
   airflow db init
   ```

2. **Create Airflow user**:
   ```bash
   airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
   ```

3. **Copy or symlink DAG file**:
   - Ensure the `dags/` directory is in your Airflow DAGs folder
   - Or configure `dags_folder` in `airflow.cfg` to point to this project's `dags/` directory

4. **Start Airflow services**:
   ```bash
   # Terminal 1
   airflow webserver --port 8080
   
   # Terminal 2
   airflow scheduler
   ```

5. **Access Airflow UI**:
   Open your browser and go to `http://localhost:8080`
   Log in with the admin credentials you created

## Running Tests

```bash
pytest tests/ -v
```

## Sample SQL Queries

Get average temperature by month:
```sql
SELECT 
    d.year,
    d.month,
    AVG(f.temperature_2m_mean) as avg_temp
FROM fact_weather_observations f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.year, d.month
ORDER BY d.year, d.month;
```

Get top 5 windiest days:
```sql
SELECT 
    d.date,
    l.location_name,
    f.wind_speed_10m_max
FROM fact_weather_observations f
JOIN dim_date d ON f.date_id = d.date_id
JOIN dim_location l ON f.location_id = l.location_id
ORDER BY f.wind_speed_10m_max DESC
LIMIT 5;
```

## Data Quality Checks

The pipeline includes checks for:
- Presence of required columns
- Valid temperature ranges (-50°C to 50°C)
- Valid humidity ranges (0% to 100%)
- Non-negative precipitation
- Reasonable wind speeds (< 200 km/h)
- Duplicate record removal
- Missing value handling

## Logging

Logs are written to:
- Console (stdout)
- `logs/pipeline.log`

## Assumptions

- Using PostgreSQL as the database
- Daily weather data is sufficient for analytics
- Single location (configurable)
- No external authentication required for Open-Meteo
- Local development without cloud infrastructure

## Known Limitations

- Single location support (easily extensible)
- Basic error handling for production
- No automated schema migration system
- No data partitioning for large datasets
