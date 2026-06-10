import logging
import sys
from pathlib import Path


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration for the weather pipeline.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    
    handlers = [
        logging.StreamHandler(sys.stdout),
    ]
    
    logs_dir = Path(__file__).parent.parent.parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    handlers.append(logging.FileHandler(logs_dir / "pipeline.log"))
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )
