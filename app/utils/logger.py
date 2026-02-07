from loguru import logger
import sys

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
    level="INFO"
)

logger.add(
    "logs/bot.log",
    rotation="1 MB",
    level="DEBUG",
    encoding="utf-8"
)
