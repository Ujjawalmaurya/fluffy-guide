"""
Loguru setup — call get_logger(module_name) in each module.
Format: TIMESTAMP | [MODULE] | LEVEL | message
Writes to console (colored) and logs/skillbridge.log (rotated).
"""
import io
import sys
from loguru import logger
from app.core.config import settings

# Force UTF-8 encoding for standard output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Custom log format...
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>[{extra[module]:<12}]</level> | "
    "<level>{level:^7}</level> | "
    "<level>{message}</level>"
)

# Remove default handler
logger.remove()

# Add custom console handler with consistent format and explicit UTF-8 encoding
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level=settings.log_level,
    colorize=True,
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

# File — rotating, 7-day retention
logger.add(
    "logs/skillbridge.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | [{extra[module]:<12}] | {level:<7} | {message}", # This format is for the file, not console
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    enqueue=True,  # thread-safe
)


def get_logger(module: str):
    """Return a logger bound to a specific module tag."""
    return logger.bind(module=module)
