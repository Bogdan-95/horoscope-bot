from loguru import logger
import sys


# Отключаем обработчик по умолчанию Loguru (нужен для кастомной настройки)
logger.remove()

# 1. Настройка цветного вывода в консоль (уровень INFO и выше)
# Формат: время | уровень | сообщение с цветовой разметкой
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
    level="INFO"
)

# 2. Настройка файлового логирования (уровень DEBUG и выше)
# Автоматическая ротация файлов при достижении 1 MB
logger.add(
    "logs/bot.log",
    rotation="1 MB",
    level="DEBUG",
    encoding="utf-8"
)
