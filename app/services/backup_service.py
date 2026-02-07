# app/services/backup_service.py
import shutil
from datetime import datetime
from pathlib import Path
from app.utils.logger import logger


class BackupService:
    """
    Сервис резервного копирования базы данных с автоочисткой.
    """

    def __init__(self, db_path: str, backup_dir: str, max_backups: int = 10):
        """
        :param db_path: путь к database.db
        :param backup_dir: папка для бэкапов
        :param max_backups: максимальное количество хранимых бэкапов
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups

    def create_backup(self) -> Path:
        """
        Создать резервную копию базы данных и удалить старые.

        :return: путь к созданному бэкапу
        """
        try:
            if not self.db_path.exists():
                logger.warning(f"База данных не найдена: {self.db_path}")
                return None

            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # Создаём имя файла с timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            backup_path = self.backup_dir / f"database_{timestamp}.db"

            # Копируем файл
            shutil.copy(self.db_path, backup_path)
            logger.info(f"✅ Бэкап создан: {backup_path.name}")

            # Очищаем старые бэкапы
            self._cleanup_old_backups()

            return backup_path

        except Exception as e:
            logger.exception(f"❌ Ошибка при создании бэкапа: {e}")
            return None

    def _cleanup_old_backups(self):
        """Удаляет старые бэкапы, если превышен лимит"""
        try:
            # Получаем все файлы бэкапов
            backups = list(self.backup_dir.glob("database_*.db"))

            if len(backups) <= self.max_backups:
                return

            # Сортируем по дате создания (старые первые)
            backups.sort(key=lambda x: x.stat().st_mtime)

            # Удаляем лишние
            for old_backup in backups[:-self.max_backups]:
                old_backup.unlink()
                logger.info(f"🗑️ Удалён старый бэкап: {old_backup.name}")

        except Exception as e:
            logger.error(f"Ошибка при очистке старых бэкапов: {e}")

    def get_backup_count(self) -> int:
        """Возвращает количество сохранённых бэкапов"""
        return len(list(self.backup_dir.glob("database_*.db")))

    def get_latest_backup(self) -> Path:
        """Возвращает путь к последнему бэкапу"""
        backups = list(self.backup_dir.glob("database_*.db"))
        if not backups:
            return None

        # Возвращаем самый новый файл
        return max(backups, key=lambda x: x.stat().st_mtime)