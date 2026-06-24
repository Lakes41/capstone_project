
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.weather_pipeline.loader import WeatherLoader


def test_loader_initialization():
    """Test loader initialization."""
    loader = WeatherLoader("sqlite:///:memory:")
    assert loader.engine is not None


@patch("src.weather_pipeline.loader.create_engine")
def test_loader_initialization_mocked(mock_create_engine):
    """Test loader initialization with mocked engine."""
    mock_create_engine.return_value = MagicMock()
    loader = WeatherLoader("test_db_url")
    mock_create_engine.assert_called_once_with("test_db_url")
