import logging
from pathlib import Path
from .config import settings
from .utils.logging_config import setup_logging
from .extractor import WeatherExtractor
from .transformer import WeatherTransformer
from .validator import WeatherValidator
from .loader import WeatherLoader

logger = logging.getLogger(__name__)


class WeatherETLPipeline:
    def __init__(self):
        setup_logging(settings.LOG_LEVEL)
        self.extractor = WeatherExtractor()
        self.transformer = WeatherTransformer()
        self.validator = WeatherValidator()
        self.loader = WeatherLoader()
        self.schema_path = Path(__file__).parent.parent.parent / "sql" / "schema.sql"
    
    def run_etl(self, start_date: str = None, end_date: str = None):
        """Run the full ETL pipeline"""
        start_date = start_date or settings.PIPELINE_START_DATE
        end_date = end_date or settings.PIPELINE_END_DATE
        
        logger.info("Starting ETL pipeline")
        
        try:
            # Extract
            logger.info("Extracting weather data")
            extract_result = self.extractor.fetch_weather_data(start_date, end_date)
            raw_df = self.extractor.raw_data_to_dataframe(extract_result["raw_data"])
            
            # Validate raw data
            validation_result = self.validator.validate_dataframe(raw_df)
            if not validation_result["success"]:
                raise Exception(f"Data validation failed: {validation_result['issues']}")
            
            # Transform
            logger.info("Transforming weather data")
            transformed_df = self.transformer.transform_data(raw_df)
            
            # Validate transformed data
            transformed_validation = self.validator.validate_dataframe(transformed_df)
            if not transformed_validation["success"] and len(transformed_validation["issues"]) > 0:
                logger.warning(f"Transformed data has issues: {transformed_validation['issues']}")
            
            # Prepare fact and dimension data
            location_dim, date_dim, weather_fact = self.transformer.prepare_fact_dimension_data(transformed_df)
            
            # Load
            logger.info("Loading data into database")
            with self.loader.engine.connect() as conn:
                self.loader.execute_schema_script(str(self.schema_path))
                location_map = self.loader.load_dim_location(location_dim, conn)
                date_map = self.loader.load_dim_date(date_dim, conn)
                self.loader.load_fact_weather(weather_fact, location_map, date_map, conn)
            
            logger.info("ETL pipeline completed successfully")
        except Exception as e:
            logger.error(f"ETL pipeline failed: {str(e)}", exc_info=True)
            raise
    
    def run_elt(self, start_date: str = None, end_date: str = None):
        """Run the simple ELT workflow (staging first)"""
        start_date = start_date or settings.PIPELINE_START_DATE
        end_date = end_date or settings.PIPELINE_END_DATE
        
        logger.info("Starting ELT workflow")
        
        try:
            # Extract
            logger.info("Extracting weather data")
            extract_result = self.extractor.fetch_weather_data(start_date, end_date)
            
            # Load raw data to staging
            logger.info("Loading raw data into staging table")
            self.loader.execute_schema_script(str(self.schema_path))
            self.loader.load_staging_raw(extract_result["raw_data"], extract_result["location_name"])
            
            # Transform in pipeline (simulating SQL transformation)
            raw_df = self.extractor.raw_data_to_dataframe(extract_result["raw_data"])
            transformed_df = self.transformer.transform_data(raw_df)
            location_dim, date_dim, weather_fact = self.transformer.prepare_fact_dimension_data(transformed_df)
            
            # Load final tables
            logger.info("Loading transformed data into final tables")
            with self.loader.engine.connect() as conn:
                location_map = self.loader.load_dim_location(location_dim, conn)
                date_map = self.loader.load_dim_date(date_dim, conn)
                self.loader.load_fact_weather(weather_fact, location_map, date_map, conn)
            
            logger.info("ELT workflow completed successfully")
        except Exception as e:
            logger.error(f"ELT workflow failed: {str(e)}", exc_info=True)
            raise


if __name__ == "__main__":
    pipeline = WeatherETLPipeline()
    pipeline.run_etl()
