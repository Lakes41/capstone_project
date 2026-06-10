import logging
import requests
import pandas as pd
from typing import Dict, Any, Optional
from .config import settings

logger = logging.getLogger(__name__)


class WeatherExtractor:
    def __init__(
        self,
        base_url: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        location_name: Optional[str] = None
    ):
        self.base_url = base_url or settings.OPEN_METEO_BASE_URL
        self.latitude = latitude or settings.WEATHER_LATITUDE
        self.longitude = longitude or settings.WEATHER_LONGITUDE
        self.location_name = location_name or settings.WEATHER_LOCATION_NAME
        
    def fetch_weather_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Fetch weather data from Open-Meteo API.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dictionary containing raw weather data and location info
        """
        url = f"{self.base_url}/forecast"
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": [
                "temperature_2m_mean",
                "temperature_2m_max",
                "temperature_2m_min",
                "relative_humidity_2m_mean",
                "precipitation_sum",
                "wind_speed_10m_max"
            ],
            "timezone": "auto"
        }
        
        logger.info(f"Fetching weather data from {start_date} to {end_date}")
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            logger.info("Successfully fetched weather data")
            return {
                "raw_data": data,
                "location_name": self.location_name,
                "latitude": self.latitude,
                "longitude": self.longitude
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch weather data: {str(e)}")
            raise

    def raw_data_to_dataframe(self, raw_data: Dict[str, Any]) -> pd.DataFrame:
        """Convert raw API response to a pandas DataFrame"""
        daily_data = raw_data["daily"]
        df = pd.DataFrame(daily_data)
        df["latitude"] = self.latitude
        df["longitude"] = self.longitude
        df["location_name"] = self.location_name
        return df
