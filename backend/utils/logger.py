import logging
import colorlog

# Define log colors
log_colors = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}

# Create a colored formatter
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s %(levelname)s - %(message)s",
    log_colors=log_colors,
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Configure logger with the colored formatter
handler = logging.StreamHandler()
handler.setFormatter(formatter)

# Create logger instance
logger = logging.getLogger("custom_logger")  # Use a unique logger name
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# Avoid duplicate logs if imported multiple times
if not logger.hasHandlers():
    logger.addHandler(handler)
