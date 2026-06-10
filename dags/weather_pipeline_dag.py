from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from weather_pipeline.pipeline import WeatherETLPipeline
from weather_pipeline.config import settings


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def run_etl_task(**kwargs):
    """Run the ETL pipeline task"""
    execution_date = kwargs["ds"]
    end_date = execution_date
    start_date = (datetime.strptime(execution_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    
    pipeline = WeatherETLPipeline()
    pipeline.run_etl(start_date=start_date, end_date=end_date)


def run_elt_task(**kwargs):
    """Run the ELT workflow task"""
    execution_date = kwargs["ds"]
    end_date = execution_date
    start_date = (datetime.strptime(execution_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    
    pipeline = WeatherETLPipeline()
    pipeline.run_elt(start_date=start_date, end_date=end_date)


with DAG(
    "weather_analytics_pipeline",
    default_args=default_args,
    description="Weather analytics ETL/ELT pipeline",
    schedule_interval="0 2 * * *",  # Run daily at 2 AM
    catchup=False,
    tags=["weather", "etl", "analytics"],
) as dag:
    
    etl_task = PythonOperator(
        task_id="run_etl_pipeline",
        python_callable=run_etl_task,
        provide_context=True,
    )
    
    elt_task = PythonOperator(
        task_id="run_elt_workflow",
        python_callable=run_elt_task,
        provide_context=True,
    )
    
    etl_task >> elt_task
