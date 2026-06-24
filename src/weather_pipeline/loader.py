import logging
import pandas as pd
import json
from typing import Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from .config import settings

logger = logging.getLogger(__name__)


class WeatherLoader:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = create_engine(self.database_url)
        
    def execute_schema_script(self, schema_path: str, conn=None) -> None:
        """Execute SQL schema script to create tables"""
        if conn is None:
            with self.engine.connect() as conn:
                return self.execute_schema_script(schema_path, conn)
        
        try:
            with open(schema_path, "r") as f:
                schema_sql = f.read()
            
            conn.execute(text(schema_sql))
            conn.commit()
            logger.info("Successfully created database schema")
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise
        except FileNotFoundError as e:
            logger.error(f"Schema file not found: {str(e)}")
            raise
    
    def load_dim_location(self, df: pd.DataFrame, conn=None) -> pd.DataFrame:
        """Load location dimension and return with location_ids"""
        if conn is None:
            with self.engine.connect() as conn:
                return self.load_dim_location(df, conn)
        
        existing = pd.read_sql("SELECT location_id, location_name, latitude, longitude FROM dim_location", conn)
        new_locations = df.merge(existing, on=["location_name", "latitude", "longitude"], how="left", indicator=True)
        new_locations = new_locations[new_locations["_merge"] == "left_only"]
        
        if not new_locations.empty:
            new_locations[["location_name", "latitude", "longitude"]].to_sql(
                "dim_location", conn, if_exists="append", index=False
            )
            logger.info(f"Loaded {len(new_locations)} new locations")
        else:
            logger.info("No new locations to load")
        
        all_locations = pd.read_sql("SELECT location_id, location_name, latitude, longitude FROM dim_location", conn)
        return all_locations
    
    def load_dim_date(self, df: pd.DataFrame, conn=None) -> pd.DataFrame:
        """Load date dimension and return with date_ids"""
        if conn is None:
            with self.engine.connect() as conn:
                return self.load_dim_date(df, conn)
        
        existing = pd.read_sql("SELECT date_id, date FROM dim_date", conn)
        
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"]).dt.date
        existing["date"] = pd.to_datetime(existing["date"]).dt.date
        
        new_dates = df.merge(existing, on="date", how="left", indicator=True)
        new_dates = new_dates[new_dates["_merge"] == "left_only"]
        
        if not new_dates.empty:
            new_dates[["date", "day", "month", "year", "quarter", "day_of_week", "is_weekend"]].to_sql(
                "dim_date", conn, if_exists="append", index=False
            )
            logger.info(f"Loaded {len(new_dates)} new dates")
        else:
            logger.info("No new dates to load")
        
        all_dates = pd.read_sql("SELECT date_id, date FROM dim_date", conn)
        all_dates["date"] = pd.to_datetime(all_dates["date"]).dt.date
        return all_dates
    
    def load_fact_weather(self, df: pd.DataFrame, location_map: pd.DataFrame, date_map: pd.DataFrame, conn=None) -> None:
        """Load weather fact table"""
        if conn is None:
            with self.engine.connect() as conn:
                return self.load_fact_weather(df, location_map, date_map, conn)
        
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"]).dt.date
        
        df = df.merge(location_map[["location_name", "location_id"]], on="location_name", how="left")
        df = df.merge(date_map[["date", "date_id"]], on="date", how="left")
        
        fact_df = df[
            ["location_id", "date_id", "temperature_2m_mean", "temperature_2m_max",
             "temperature_2m_min", "relative_humidity_2m_mean", "precipitation_sum",
             "wind_speed_10m_max"]
        ]
        
        for _, row in fact_df.iterrows():
            check_sql = text("""
                SELECT 1 FROM fact_weather_observations 
                WHERE location_id = :loc_id AND date_id = :date_id
            """)
            loc_id = int(row["location_id"])
            date_id = int(row["date_id"])
            exists = conn.execute(check_sql, {"loc_id": loc_id, "date_id": date_id}).fetchone()
            
            if not exists:
                insert_sql = text("""
                    INSERT INTO fact_weather_observations 
                    (location_id, date_id, temperature_2m_mean, temperature_2m_max, 
                     temperature_2m_min, relative_humidity_2m_mean, precipitation_sum, wind_speed_10m_max)
                    VALUES (:loc_id, :date_id, :t_mean, :t_max, :t_min, :humidity, :precip, :wind)
                """)
                conn.execute(insert_sql, {
                    "loc_id": loc_id,
                    "date_id": date_id,
                    "t_mean": float(row["temperature_2m_mean"]),
                    "t_max": float(row["temperature_2m_max"]),
                    "t_min": float(row["temperature_2m_min"]),
                    "humidity": float(row["relative_humidity_2m_mean"]),
                    "precip": float(row["precipitation_sum"]),
                    "wind": float(row["wind_speed_10m_max"])
                })
        conn.commit()
        
        logger.info(f"Loaded {len(fact_df)} weather observations")
    
    def load_staging_raw(self, raw_data: Dict[str, Any], location_name: str) -> None:
        """Load raw data into staging table for ELT workflow"""
        with self.engine.connect() as conn:
            insert_sql = text("""
                INSERT INTO staging_weather_raw (raw_data, location_name)
                VALUES (:raw_data, :location_name)
            """)
            conn.execute(insert_sql, {
                "raw_data": json.dumps(raw_data),
                "location_name": location_name
            })
            conn.commit()
        logger.info("Loaded raw data into staging table")
