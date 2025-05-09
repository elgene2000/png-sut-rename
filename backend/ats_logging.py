import logging
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

DEFAULT_LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")
PRINT_LOG_TO_STDOUT = bool(os.environ.get("PRINT_LOG_TO_STDOUT", False))


def get_logger(
    log_name: str = "scheduler",
    log_file_dir: str = None,
    log_level: str = DEFAULT_LOG_LEVEL,
    print_logs=PRINT_LOG_TO_STDOUT,
):
    if log_file_dir is None:
        log_file_dir = tempfile.gettempdir()
    log_file_name = log_name + ".log"

    log_levels = {
        "info": logging.INFO,
        "debug": logging.DEBUG,
        "warning": logging.WARNING,
    }
    logger = logging.getLogger(log_name)
    if not logger.hasHandlers():
        log_level = log_levels.get(log_level.lower(), logging.INFO)
        formatter = logging.Formatter(
            fmt=r"%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = logging.FileHandler(os.path.join(log_file_dir, log_file_name))
        file_handler.setFormatter(formatter)

        if print_logs:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        logger.addHandler(file_handler)
        logger.setLevel(log_level)

    return logger
