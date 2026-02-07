# Сервис для обновления статуса здоровья приложения
from datetime import datetime
import os

HEALTH_FILE = "data/health.txt"

# Обновляет файл здоровья с текущей меткой времени
def update_health():
    os.makedirs("data", exist_ok=True)
    with open(HEALTH_FILE, "w", encoding="utf-8") as f:
        f.write(f"OK {datetime.now().isoformat()}")