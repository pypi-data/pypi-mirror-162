"""Handles application logger."""
import logging
import logging.config
import os


def set_logger(debug: bool):
    """Setup logging configuration."""
    logger_config_file = os.path.join(os.path.dirname(__file__), "logger.ini")
    logging.config.fileConfig(logger_config_file)
    if debug:
        logging.basicConfig(level=logging.DEBUG)


def get_logger() -> logging.Logger:
    """Returns a logger."""
    return logging.getLogger("sensornet")
