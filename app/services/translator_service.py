from deep_translator import GoogleTranslator
from typing import Optional
from app.utils.logger import logger

class TranslatorService:
    """
    Сервис перевода текста.
    Используется для локализации гороскопов.
    """

    DEFAULT_SOURCE_LANG = "en"
    DEFAULT_TARGET_LANG = "ru"

    @classmethod
    def translate(
        cls,
        text: str,
        source: str = DEFAULT_SOURCE_LANG,
        target: str = DEFAULT_TARGET_LANG
    ) -> Optional[str]:
        """
        Перевести текст.

        :param text: исходный текст
        :param source: язык источника
        :param target: язык перевода
        :return: переведённый текст или None
        """
        if not text:
            return None

        try:
            translator = GoogleTranslator(source=source, target=target)
            return translator.translate(text)
        except Exception as e:
            print(f"[TranslatorService] Error: {e}")
            return None

class SimpleTranslator:
    async def translate_text(self, text: str) -> str:
        if not text:
            return ""

        try:
            translator = GoogleTranslator(source="en", target="ru")
            result = translator.translate(text)

            logger.debug("[TRANSLATOR] Translation OK")
            return result

        except Exception as e:
            logger.error(f"[TRANSLATOR] Error: {e}")
            return text



#
#
#
# # Перевод текста с английского на русский с использованием deep-translator
#
# import asyncio
# from deep_translator import GoogleTranslator
#
# class SimpleTranslator:
#     def __init__(self):
#         """ Инициализация переводчика с английского на русский. """
#         self.translator = GoogleTranslator(source='en', target='ru')
#
#     async def translate_text(self, text):
#         """
#                 Асинхронная обертка для синхронной библиотеки перевода.
#                 Запускает перевод в отдельном потоке, чтобы бот не «зависал».
#                 """
#         loop = asyncio.get_event_loop()
#         try:
#             return await loop.run_in_executor(None, self.translator.translate, text)
#         except Exception:
#             return text # В случае ошибки возвращаем оригинал