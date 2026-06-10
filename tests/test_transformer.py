import pandas as pd
import pytest
from src.weather_pipeline.transformer import WeatherTransformer


def test_clean_column_names():
    """Test that column names are cleaned properly."""
    data = {"Temperature 2m": [20.0], "Wind Speed": [10.0]}
    df = pd.DataFrame(data)
    cleaned_df = WeatherTransformer.clean_column_names(df)
    assert "temperature_2m" in cleaned_df.columns
    assert "wind_speed" in cleaned_df.columns


def test_convert_datetime():
    """Test datetime conversion and date component extraction."""
    data = {"time": ["2024-01-01", "2024-01-05"]}
    df = pd.DataFrame(data)
    transformed_df = WeatherTransformer.convert_datetime(df)
    assert "date" in transformed_df.columns
    assert "day" in transformed_df.columns
    assert "month" in transformed_df.columns
    assert "year" in transformed_df.columns
    assert transformed_df["year"][0] == 2024


def test_remove_duplicates():
    """Test duplicate removal."""
    data = {"time": ["2024-01-01", "2024-01-01", "2024-01-02"], "value": [1, 2, 3]}
    df = pd.DataFrame(data)
    deduped_df = WeatherTransformer.remove_duplicates(df)
    assert len(deduped_df) == 2


def test_prepare_fact_dimension_data():
    """Test preparing fact and dimension data."""
    data = {
        "time": ["2024-01-01", "2024-01-02"],
        "location_name": ["New York", "New York"],
        "latitude": [40.7128, 40.7128],
        "longitude": [-74.0060, -74.0060],
        "temperature_2m_mean": [20.0, 22.0],
        "date": [pd.to_datetime("2024-01-01").date(), pd.to_datetime("2024-01-02").date()],
        "day": [1, 2],
        "month": [1, 1],
        "year": [2024, 2024],
        "quarter": [1, 1],
        "day_of_week": [0, 1],
        "is_weekend": [False, False]
    }
    df = pd.DataFrame(data)
    location_dim, date_dim, weather_fact = WeatherTransformer.prepare_fact_dimension_data(df)
    
    assert len(location_dim) == 1
    assert len(date_dim) == 2
    assert len(weather_fact) == 2
