import logging
import datetime
import os
from pathlib import Path
import tempfile


class CustomFormatter(logging.Formatter):
    """Logging colored formatter"""

    grey = "\x1b[38;20m"
    green = '\x1b[92m'
    blue = '\x1b[38;5;39m'
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, format):
        """Initializes the class

        Args:
            format: format of logger
        """
        super().__init__()
        self.fmt = format
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.green + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        """Given a record, format it

        Args:
            record: the record

        Returns:
            the formatted record
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def configure_logger(name: str, fmt=None):
    """Configure local logger

    Args:
        name (str): python name file
        fmt (_type_, optional): -. Defaults to None.

    Returns:
        logger
    """
    # Create custom logger logging all five levels
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Define format for logs
    if fmt is None:
        fmt = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'

    # Create stdout handler for logging to the console (logs all five levels)
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(CustomFormatter(fmt))

    # Create file handler for logging to a file (logs all five levels)
    today = datetime.date.today()
    
    logs_dir = os.getenv("LOGS_SAVING_PATH")
    
    if logs_dir is None:
        logs_dir = tempfile.gettempdir()
    
    log_file_path = str(Path(logs_dir).resolve() / 'acceleron_{}.log'.format(today.strftime('%Y_%m_%d')))
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt))

    # Add both handlers to the logger
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)

    return logger