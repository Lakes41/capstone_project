import pytest
from unittest.mock import patch, MagicMock
from src.weather_pipeline.extractor import WeatherExtractor


def test_extractor_initialization():
    """Test extractor initialization with custom and default parameters."""
    extractor = WeatherExtractor(
        base_url="https://test.api",
        latitude=50.0,
        longitude=-100.0,
        location_name="Test City"
    )
    
    assert extractor.base_url == "https://test.api"
    assert extractor.latitude == 50.0
    assert extractor.longitude == -100.0
    assert extractor.location_name == "Test City"


def test_extractor_initialization_defaults():
    """Test extractor initialization with default values."""
    extractor = WeatherExtractor()
    assert extractor.base_url is not None
    assert extractor.latitude is not None
    assert extractor.longitude is not None


@patch("src.weather_pipeline.extractor.requests.get")
def test_fetch_weather_data_success(mock_get):
    """Test successful API call."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "daily": {
            "time": ["2024-01-01"],
            "temperature_2m_mean": [20.0]
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    extractor = WeatherExtractor()
    result = extractor.fetch_weather_data("2024-01-01", "2024-01-01")
    
    assert "raw_data" in result
    assert "location_name" in result
    assert result["raw_data"]["daily"]["time"][0] == "2024-01-01"


@patch("src.weather_pipeline.extractor.requests.get")
def test_fetch_weather_data_failure(mock_get):
    """Test failed API call."""
    mock_get.side_effect = Exception("API error")
    
    extractor = WeatherExtractor()
    
    with pytest.raises(Exception):
        extractor.fetch_weather_data("2024-01-01", "2024-01-01")
