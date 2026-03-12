"""
Unified logging — everything goes to terminal, one format.
Intercepts stdlib logging (uvicorn/fastapi) and routes through loguru.
"""
import sys
import logging
from loguru import logger
from app.core.config import settings

FORMAT = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>[{extra[module]:<12}]</level> | "
    "<level>{level:<7}</level> | "
    "<level>{message}</level>"
)

logger.remove()
logger.add(sys.stdout, format=FORMAT, level=settings.log_level, colorize=True, enqueue=False)

# File sink — rotated every 10MB, kept for 7 days
logger.add(
    "logs/skillbridge.log",
    format=FORMAT,
    level=settings.log_level,
    rotation="10 MB",
    retention="7 days",
    enqueue=True
)


class _Intercept(logging.Handler):
    """Sends all stdlib log records into loguru."""
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        # Walk up the stack to find the real caller, not the logging internals
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        module_tag = record.name.split(".")[0].upper()[:12]
        logger.bind(module=module_tag).opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# Kill all existing stdlib handlers, replace with our interceptor at root level.
# This catches uvicorn, fastapi, watchfiles, everything — including handlers
# that uvicorn sets up after import.
logging.basicConfig(handlers=[_Intercept()], level=0, force=True)
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).handlers = []
    logging.getLogger(name).propagate = True


def get_logger(module: str):
    return logger.bind(module=module)
