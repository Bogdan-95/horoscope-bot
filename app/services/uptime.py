# Uptime / метрика жизни бота
from datetime import datetime

START_TIME = datetime.now()

# Получает время работы с момента старта в формате ЧЧ:ММ:СС

def get_uptime() -> str:
    delta = datetime.now() - START_TIME
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours}h {minutes}m {seconds}s"
