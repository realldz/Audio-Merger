import logging
import os
from core.models import LogSettings

LOG_DIR = 'logs'

def setup_logging(log_settings: LogSettings):
    # Ensure log directory exists
    if log_settings.handler in ['file', 'both'] and not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Get the root logger for the application
    logger = logging.getLogger("AudioMerger")
    logger.handlers.clear() # Clear any existing handlers

    # Set the logging level
    if log_settings.level.upper() == 'NONE':
        logger.disabled = True
        return
    else:
        logger.disabled = False
        try:
            level = getattr(logging, log_settings.level.upper())
            logger.setLevel(level)
        except AttributeError:
            logger.setLevel(logging.INFO) # Default to INFO if level is invalid

    # Define the formatter
    formatter = logging.Formatter(log_settings.format)

    # Add handlers based on configuration
    if log_settings.handler.lower() in ['file', 'both']:
        file_handler = logging.FileHandler(os.path.join(LOG_DIR, log_settings.file_name))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if log_settings.handler.lower() in ['stdout', 'both']:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    # Prevent log messages from being propagated to the root logger
    logger.propagate = False
