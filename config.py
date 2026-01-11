# Конфигурация
import os
import logging
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ASTROLOGY_API_KEY = os.getenv('ASTROLOGY_API_KEY')


if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not found")

if not ASTROLOGY_API_KEY:
    print("⚠️  ASTROLOGY_API_KEY не найден, будет использован парсинг с сайтов")


# Настройка логирования
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()