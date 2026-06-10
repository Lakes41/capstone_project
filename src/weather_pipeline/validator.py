import logging
import pandas as pd
from typing import List, Tuple

logger = logging.getLogger(__name__)


class WeatherValidator:
    REQUIRED_COLUMNS = [
        "time",
        "temperature_2m_mean",
        "temperature_2m_max",
        "temperature_2m_min",
        "relative_humidity_2m_mean",
        "precipitation_sum",
        "wind_speed_10m_max"
    ]
    
    @staticmethod
    def validate_required_columns(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate that all required columns are present"""
        missing_columns = [col for col in WeatherValidator.REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False, missing_columns
        logger.info("All required columns present")
        return True, []
    
    @staticmethod
    def validate_temperature_range(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate temperatures are within reasonable ranges (-50 to 50°C)"""
        issues = []
        temp_cols = ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min"]
        for col in temp_cols:
            if col in df.columns:
                invalid = df[(df[col] < -50) | (df[col] > 50)]
                if not invalid.empty:
                    issues.append(f"{col} has {len(invalid)} invalid values")
        
        if issues:
            logger.warning(f"Temperature validation issues: {issues}")
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_humidity_range(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate humidity is between 0 and 100"""
        issues = []
        if "relative_humidity_2m_mean" in df.columns:
            invalid = df[(df["relative_humidity_2m_mean"] < 0) | (df["relative_humidity_2m_mean"] > 100)]
            if not invalid.empty:
                issues.append(f"relative_humidity_2m_mean has {len(invalid)} invalid values")
        
        if issues:
            logger.warning(f"Humidity validation issues: {issues}")
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_precipitation_range(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate precipitation is non-negative"""
        issues = []
        if "precipitation_sum" in df.columns:
            invalid = df[df["precipitation_sum"] < 0]
            if not invalid.empty:
                issues.append(f"precipitation_sum has {len(invalid)} invalid values")
        
        if issues:
            logger.warning(f"Precipitation validation issues: {issues}")
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_wind_speed_range(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate wind speed is non-negative and reasonable (< 200 km/h)"""
        issues = []
        if "wind_speed_10m_max" in df.columns:
            invalid = df[(df["wind_speed_10m_max"] < 0) | (df["wind_speed_10m_max"] > 200)]
            if not invalid.empty:
                issues.append(f"wind_speed_10m_max has {len(invalid)} invalid values")
        
        if issues:
            logger.warning(f"Wind speed validation issues: {issues}")
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> dict:
        """Run all validations and return results"""
        results = {
            "success": True,
            "issues": []
        }
        
        valid_cols, cols_issues = WeatherValidator.validate_required_columns(df)
        if not valid_cols:
            results["success"] = False
            results["issues"].extend(cols_issues)
        
        if valid_cols:
            valid_temp, temp_issues = WeatherValidator.validate_temperature_range(df)
            if not valid_temp:
                results["issues"].extend(temp_issues)
            
            valid_humidity, humidity_issues = WeatherValidator.validate_humidity_range(df)
            if not valid_humidity:
                results["issues"].extend(humidity_issues)
            
            valid_precip, precip_issues = WeatherValidator.validate_precipitation_range(df)
            if not valid_precip:
                results["issues"].extend(precip_issues)
            
            valid_wind, wind_issues = WeatherValidator.validate_wind_speed_range(df)
            if not valid_wind:
                results["issues"].extend(wind_issues)
        
        return results
