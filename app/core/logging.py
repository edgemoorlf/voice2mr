"""Logging configuration module"""
import os
import sys
import yaml
import logging
import logging.config
from datetime import datetime
from pathlib import Path

from app.core.config import settings


def setup_logging(
    default_path="logging.yaml",
    default_level=logging.INFO,
    logs_dir="logs"
):
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    logs_path = Path(logs_dir)
    logs_path.mkdir(exist_ok=True)
    
    # Generate a log filename with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_filename = f"voice2mr_{timestamp}.log"
    log_filepath = logs_path / log_filename
    
    # Create a symlink to the latest log file
    latest_log = logs_path / "latest.log"
    if latest_log.exists() and latest_log.is_symlink():
        latest_log.unlink()
    
    path = default_path
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                # Update the log filename in the config
                for handler in config.get('handlers', {}).values():
                    if handler.get('class') == 'logging.FileHandler':
                        handler['filename'] = str(log_filepath)
                
                logging.config.dictConfig(config)
                # Create symlink to latest log file
                try:
                    os.symlink(log_filepath, latest_log)
                except (OSError, AttributeError):
                    # Symlinks might not be supported on all platforms
                    pass
                    
            except Exception as e:
                print(f"Error in logging configuration: {e}")
                configure_basic_logging(log_filepath, default_level)
    else:
        configure_basic_logging(log_filepath, default_level)
    
    # Add console handler if in debug mode
    if settings.DEBUG:
        add_console_handler()
    
    return logging.getLogger("app")


def configure_basic_logging(log_filepath, level=logging.INFO):
    """Configure basic logging if config file is not available"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_filepath),
        ]
    )


def add_console_handler():
    """Add a console handler to the root logger"""
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add handler to the root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name"""
    return logging.getLogger(name) 