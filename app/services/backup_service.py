# backup service.py
import shutil
from datetime import datetime
from pathlib import Path
from loguru import logger

# =========================
# НАСТРОЙКИ БЭКАПОВ
# =========================

DB_PATH = Path("data/database.db")
BACKUP_DIR = Path("data/backups")
MAX_BACKUPS = 10

# =========================
# ФУНКЦИИ БЭКАПОВ
# =========================

async def backup_database():
    try:
        if not DB_PATH.exists():
            logger.warning("База данных не найдена, бэкап пропущен")
            return

        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        backup_file = BACKUP_DIR / f"database_{timestamp}.db"

        shutil.copy(DB_PATH, backup_file)

        logger.info(f"Бэкап базы создан: {backup_file}")

    except Exception as e:
        logger.exception(f"Ошибка при бэкапе базы: {e}")

# Удаление старых бэкапов, если превышен лимит
def cleanup_old_backups():
    backups = sorted(
        BACKUP_DIR.glob("database_*.db"),
        key=lambda f: f.stat().st_mtime
    )

    if len(backups) <= MAX_BACKUPS:
        return

    for old_backup in backups[:-MAX_BACKUPS]:
        old_backup.unlink()
        logger.info(f"Удалён старый бэкап: {old_backup.name}")