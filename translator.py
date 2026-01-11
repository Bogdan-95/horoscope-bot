import logging
from deep_translator import GoogleTranslator
import time

logger = logging.getLogger(__name__)


class SimpleTranslator:
    def __init__(self):
        self.translator = GoogleTranslator(source='en', target='ru')
        self.cache = {}

    def translate_text(self, text, max_retries=3):
        """Перевод текста с английского на русский"""
        if not text or len(text.strip()) < 10:
            return text

        # Проверяем кэш
        if text in self.cache:
            logger.debug("Используем кэшированный перевод")
            return self.cache[text]

        logger.info(f"Перевод текста ({len(text)} символов)...")

        for attempt in range(max_retries):
            try:
                # Ограничиваем длину текста для перевода (Google Translator имеет лимиты)
                if len(text) > 4500:  # Безопасный лимит
                    text_to_translate = text[:4500] + "..."
                else:
                    text_to_translate = text

                translated = self.translator.translate(text_to_translate)

                if translated and len(translated) > 10:
                    self.cache[text] = translated
                    logger.info("✅ Перевод выполнен успешно")
                    return translated
                else:
                    logger.warning(f"Пустой перевод, попытка {attempt + 1}/{max_retries}")

            except Exception as e:
                logger.warning(f"Ошибка перевода ({type(e).__name__}), попытка {attempt + 1}/{max_retries}: {e}")

            # Ждем перед повторной попыткой
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                time.sleep(wait_time)

        logger.error(f"Не удалось перевести текст после {max_retries} попыток")
        return text  # Возвращаем оригинальный текст если перевод не удался

    def is_english(self, text):
        """Проверяем, на английском ли текст"""
        if not text:
            return False

        # Простая проверка по наличию английских слов
        english_words = ['the', 'and', 'you', 'that', 'this', 'with', 'for', 'are', 'not']
        text_lower = text.lower()

        # Если есть английские артикли/предлоги и много латинских букв
        english_count = sum(1 for word in english_words if word in text_lower)
        latin_ratio = sum(1 for char in text if 'a' <= char <= 'z' or 'A' <= char <= 'Z') / max(len(text), 1)

        return english_count > 2 or latin_ratio > 0.7