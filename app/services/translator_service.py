# Перевод текста с английского на русский с использованием deep-translator

import asyncio
from deep_translator import GoogleTranslator

class SimpleTranslator:
    def __init__(self):
        """ Инициализация переводчика с английского на русский. """
        self.translator = GoogleTranslator(source='en', target='ru')

    async def translate_text(self, text):
        """
                Асинхронная обертка для синхронной библиотеки перевода.
                Запускает перевод в отдельном потоке, чтобы бот не «зависал».
                """
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(None, self.translator.translate, text)
        except Exception:
            return text # В случае ошибки возвращаем оригинал