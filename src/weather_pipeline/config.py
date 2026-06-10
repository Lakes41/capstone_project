from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    WEATHER_LATITUDE: float = 40.7128
    WEATHER_LONGITUDE: float = -74.0060
    WEATHER_LOCATION_NAME: str = "New York"
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/weather_db"
    PIPELINE_START_DATE: str = "2024-01-01"
    PIPELINE_END_DATE: str = "2024-12-31"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = Path(__file__).parent.parent.parent / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
