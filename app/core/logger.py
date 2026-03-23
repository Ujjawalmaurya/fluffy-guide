import logging
import sys
from datetime import datetime

# Simple logger that doesn't need loguru.
# Real world: just print it, or use standard logging if you're fancy.
# I'll keep it simple: print with a nice format.

class SimpleLogger:
    def __init__(self, module="APP"):
        self.module = module

    def info(self, msg, *args, **kwargs):
        self._log("INFO", msg)

    def error(self, msg, *args, **kwargs):
        self._log("ERROR", msg)

    def warning(self, msg, *args, **kwargs):
        self._log("WARN", msg)

    def debug(self, msg, *args, **kwargs):
        self._log("DEBUG", msg)

    def bind(self, **kwargs):
        # Loguru-style bind, just returns a new logger for now
        module = kwargs.get("module", self.module)
        return SimpleLogger(module=module)

    def opt(self, **kwargs):
        # Loguru-style opt, just returns self
        return self

    def _log(self, level, msg):
        time = datetime.now().strftime("%H:%M:%S")
        print(f"{time} | {level:<7} | [{self.module:<12}] | {msg}")


# Standard instance
logger = SimpleLogger()

# Intercept standard logging to keep things unified
class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        level = record.levelname
        msg = record.getMessage()
        logger.bind(module=record.name)._log(level, msg)

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)


def get_logger(module: str):
    return logger.bind(module=module)
