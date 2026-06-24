
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.weather_pipeline.pipeline import WeatherETLPipeline


@patch("src.weather_pipeline.pipeline.WeatherLoader")
def test_pipeline_initialization(mock_loader):
    """Test pipeline initialization with mocked loader."""
    mock_loader_instance = MagicMock()
    mock_loader.return_value = mock_loader_instance
    
    pipeline = WeatherETLPipeline()
    assert pipeline.extractor is not None
    assert pipeline.transformer is not None
    assert pipeline.validator is not None
    assert pipeline.loader is mock_loader_instance


@patch("src.weather_pipeline.pipeline.WeatherLoader")
def test_run_etl(mock_loader):
    """Test calling run_etl method."""
    mock_loader_instance = MagicMock()
    mock_loader.return_value = mock_loader_instance
    
    pipeline = WeatherETLPipeline()
    with patch.object(pipeline, "run_etl") as mock_run_etl:
        pipeline.run_etl("2026-06-01", "2026-06-10")
        mock_run_etl.assert_called_once_with("2026-06-01", "2026-06-10")


@patch("src.weather_pipeline.pipeline.WeatherLoader")
def test_run_elt(mock_loader):
    """Test calling run_elt method."""
    mock_loader_instance = MagicMock()
    mock_loader.return_value = mock_loader_instance
    
    pipeline = WeatherETLPipeline()
    with patch.object(pipeline, "run_elt") as mock_run_elt:
        pipeline.run_elt("2026-06-01", "2026-06-10")
        mock_run_elt.assert_called_once_with("2026-06-01", "2026-06-10")
