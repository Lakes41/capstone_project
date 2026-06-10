import logging
import pandas as pd
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class WeatherTransformer:
    @staticmethod
    def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Clean column names to be more readable and consistent"""
        df = df.copy()
        df.columns = [col.lower().replace(" ", "_") for col in df.columns]
        return df
    
    @staticmethod
    def convert_datetime(df: pd.DataFrame, time_col: str = "time") -> pd.DataFrame:
        """Convert time column to datetime and extract date components"""
        df = df.copy()
        df[time_col] = pd.to_datetime(df[time_col])
        df["date"] = df[time_col].dt.date
        df["day"] = df[time_col].dt.day
        df["month"] = df[time_col].dt.month
        df["year"] = df[time_col].dt.year
        df["quarter"] = df[time_col].dt.quarter
        df["day_of_week"] = df[time_col].dt.dayofweek
        df["is_weekend"] = df["day_of_week"].isin([5, 6])
        return df
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values by forward filling or using mean"""
        df = df.copy()
        numeric_cols = df.select_dtypes(include=["number"]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        return df
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: list = None) -> pd.DataFrame:
        """Remove duplicate rows"""
        if subset is None:
            subset = ["time"]
        df = df.copy()
        initial_count = len(df)
        df = df.drop_duplicates(subset=subset, keep="first")
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate records")
        return df
    
    @staticmethod
    def prepare_fact_dimension_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Prepare data for fact and dimension tables.
        
        Returns:
            Tuple of (location_dim, date_dim, weather_fact) DataFrames
        """
        # Dimension: Location
        location_dim = df[["location_name", "latitude", "longitude"]].drop_duplicates().reset_index(drop=True)
        
        # Dimension: Date
        date_dim = df[["date", "day", "month", "year", "quarter", "day_of_week", "is_weekend"]].drop_duplicates().reset_index(drop=True)
        
        # Fact Table: Weather Observations
        weather_fact = df[
            ["location_name", "date", "temperature_2m_mean", "temperature_2m_max", 
             "temperature_2m_min", "relative_humidity_2m_mean", "precipitation_sum", 
             "wind_speed_10m_max"]
        ].copy()
        
        return location_dim, date_dim, weather_fact
    
    @staticmethod
    def transform_data(df: pd.DataFrame) -> pd.DataFrame:
        """Run all transformation steps"""
        logger.info("Starting data transformation")
        initial_rows = len(df)
        
        df = WeatherTransformer.clean_column_names(df)
        df = WeatherTransformer.convert_datetime(df)
        df = WeatherTransformer.handle_missing_values(df)
        df = WeatherTransformer.remove_duplicates(df)
        
        final_rows = len(df)
        logger.info(f"Transformation complete: {initial_rows} rows → {final_rows} rows")
        
        return df
