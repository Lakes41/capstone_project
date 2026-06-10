import pandas as pd
import pytest
from src.weather_pipeline.validator import WeatherValidator


def test_validate_required_columns_success():
    """Test that required columns validation passes when all are present."""
    data = {
        "time": ["2024-01-01"],
        "temperature_2m_mean": [20.0],
        "temperature_2m_max": [25.0],
        "temperature_2m_min": [15.0],
        "relative_humidity_2m_mean": [70.0],
        "precipitation_sum": [0.0],
        "wind_speed_10m_max": [10.0]
    }
    df = pd.DataFrame(data)
    valid, issues = WeatherValidator.validate_required_columns(df)
    assert valid is True
    assert len(issues) == 0


def test_validate_required_columns_missing():
    """Test missing required columns."""
    data = {
        "time": ["2024-01-01"],
        "temperature_2m_mean": [20.0]
    }
    df = pd.DataFrame(data)
    valid, issues = WeatherValidator.validate_required_columns(df)
    assert valid is False
    assert len(issues) > 0


def test_validate_temperature_range_success():
    """Test temperature validation passes with reasonable values."""
    data = {
        "temperature_2m_mean": [20.0],
        "temperature_2m_max": [25.0],
        "temperature_2m_min": [15.0]
    }
    df = pd.DataFrame(data)
    valid, issues = WeatherValidator.validate_temperature_range(df)
    assert valid is True
    assert len(issues) == 0


def test_validate_temperature_range_invalid():
    """Test temperature validation catches invalid values."""
    data = {
        "temperature_2m_mean": [100.0]
    }
    df = pd.DataFrame(data)
    valid, issues = WeatherValidator.validate_temperature_range(df)
    assert valid is False
    assert len(issues) > 0


def test_validate_humidity_range_success():
    """Test humidity validation passes with reasonable values."""
    data = {"relative_humidity_2m_mean": [70.0]}
    df = pd.DataFrame(data)
    valid, issues = WeatherValidator.validate_humidity_range(df)
    assert valid is True
    assert len(issues) == 0


def test_validate_humidity_range_invalid():
    """Test humidity validation catches invalid values."""
    data = {"relative_humidity_2m_mean": [150.0]}
    df = pd.DataFrame(data)
    valid, issues = WeatherValidator.validate_humidity_range(df)
    assert valid is False
    assert len(issues) > 0
