import sys
from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>",
    serialize=False,
)


def get_logger(name: str = "app"):
    return logger.bind(scope=name)
