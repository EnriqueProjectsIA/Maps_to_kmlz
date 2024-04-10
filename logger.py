import logging
import logging.config
from logging.handlers import RotatingFileHandler
from pathlib import Path
import time


unique_id = time.strftime("%Y-%m-%dT%H-%M-%S")
log_file_name = f"story_teller_{unique_id}.log"
path = Path(__file__).parent / "logs"
path.mkdir(exist_ok=True)
path = path / log_file_name
path = str(path.resolve())
name = 'story_teller'
maxBytes = 10485760  # 10MB
backupCount = 5

class StdoutFilter(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.WARNING


def configure_logger(name:str = name, path:str=path,
                     maxBytes:int=maxBytes, backupCount:int=backupCount,
                     identifier:str|None = None) -> logging.Logger:
    """
    Configures and returns a logger object based on provided specifications.

    Parameters:
    - name: Name of the logger.
    - path: Path for the log file.
    - maxBytes: Maximum file size before rotation.
    - backupCount: Number of backup files to keep.

    Returns:
    - A configured logger object.
    """
    if identifier is not None:
        log_file_name = f"{identifier}_extract_coords.log"
        path = Path(__file__).parent / "logs"
        path.mkdir(exist_ok=True)
        path = path / log_file_name
        path = str(path.resolve())
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z"
            }
        },
        "filters": {
            "stdout_filter": {
                "()": StdoutFilter,
                }
            },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "default",
                "stream": "ext://sys.stdout",
                "filters": ["stdout_filter"]
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "level": "WARNING",
                "formatter": "default",
                "stream": "ext://sys.stderr"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": path,
                "maxBytes": maxBytes,
                "backupCount": backupCount
            }
        },
        "loggers": {
            name: {
                "handlers": ["stdout", "stderr", "file"],
                "level": "DEBUG",
                "propagate": False
            }
        }
    }
    logging.config.dictConfig(logging_config)
    return logging.getLogger(name)

if __name__ == "__main__":
    logger = configure_logger("my_logger", "my_log.log", 10485760, 5)
    logger.debug("This is a debug message")