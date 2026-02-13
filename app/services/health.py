# Сервис для обновления статуса здоровья приложения
from datetime import datetime
from app.utils.logger import logger
import os

HEALTH_FILE = "data/health.txt"

# Обновляет файл здоровья с текущей меткой времени
def update_health():
    logger.debug("🔄 Updating health file...")
    os.makedirs("data", exist_ok=True)
    try:
        with open(HEALTH_FILE, "w", encoding="utf-8") as f:
            f.write(f"OK {datetime.now().isoformat()}")
        logger.debug("✅ Health file updated")
    except Exception as e:
        logger.error(f"❌ Failed to update health file: {e}")