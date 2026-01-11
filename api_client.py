import requests
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class HoroscopeAPI:
    def __init__(self):
        self.base_url = "https://ohmanda.com/api/horoscope"

        # Маппинг наших названий на английские (для API)
        self.sign_mapping = {
            'овен': 'aries',
            'телец': 'taurus',
            'близнецы': 'gemini',
            'рак': 'cancer',
            'лев': 'leo',
            'дева': 'virgo',
            'весы': 'libra',
            'скорпион': 'scorpio',
            'стрелец': 'sagittarius',
            'козерог': 'capricorn',
            'водолей': 'aquarius',
            'рыбы': 'pisces'
        }

        # Эмодзи для знаков
        self.zodiac_emojis = {
            'овен': '♈',
            'телец': '♉',
            'близнецы': '♊',
            'рак': '♋',
            'лев': '♌',
            'дева': '♍',
            'весы': '♎',
            'скорпион': '♏',
            'стрелец': '♐',
            'козерог': '♑',
            'водолей': '♒',
            'рыбы': '♓'
        }

        # Кэш для API запросов
        self.cache = {}
        self.rate_limit_delay = 1  # Задержка между запросами в секундах
        self.last_request_time = 0

        logger.info("OhMana API клиент инициализирован (бесплатный, без ограничений)")

    def get_daily_horoscope(self, sign_ru, max_retries=3):
        """Получить ежедневный гороскоп из OhMana API"""
        sign_lower = sign_ru.lower()

        # Проверяем кэш
        cache_key = f"{sign_lower}_{datetime.now().strftime('%Y-%m-%d')}"
        if cache_key in self.cache:
            logger.debug(f"Используем кэшированный API гороскоп для {sign_ru}")
            return self.cache[cache_key]

        # Получаем английское название знака
        sign_en = self.sign_mapping.get(sign_lower)
        if not sign_en:
            logger.error(f"Неизвестный знак для API: {sign_ru}")
            return None

        logger.info(f"Запрос к OhMana API для знака: {sign_en}")

        for attempt in range(max_retries):
            try:
                # Соблюдаем rate limit
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                if time_since_last < self.rate_limit_delay:
                    sleep_time = self.rate_limit_delay - time_since_last
                    logger.debug(f"Rate limit: ждем {sleep_time:.2f} сек")
                    time.sleep(sleep_time)

                # Отправляем запрос
                url = f"{self.base_url}/{sign_en}/"
                response = requests.get(url, timeout=15)
                self.last_request_time = time.time()

                if response.status_code == 200:
                    data = response.json()

                    if data and 'horoscope' in data:
                        horoscope_text = data['horoscope']

                        # Проверяем, нужно ли переводить
                        if self._is_english_text(horoscope_text):
                            logger.info(f"Текст на английском, пытаемся перевести...")
                            horoscope_text = self._translate_horoscope(horoscope_text)

                        formatted = self._format_response(sign_ru, horoscope_text)

                        # Сохраняем в кэш
                        self.cache[cache_key] = formatted
                        logger.info(f"✅ Гороскоп получен из API для {sign_ru}")
                        return formatted
                    else:
                        logger.warning(f"Неожиданный формат ответа API для {sign_ru}: {data}")
                        return None

                elif response.status_code == 404:
                    logger.error(f"API вернул 404 для знака {sign_en}")
                    return None
                else:
                    logger.warning(
                        f"API ошибка {response.status_code} для {sign_ru}, попытка {attempt + 1}/{max_retries}")

            except requests.exceptions.Timeout:
                logger.warning(f"Таймаут API для {sign_ru}, попытка {attempt + 1}/{max_retries}")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Ошибка соединения с API для {sign_ru}, попытка {attempt + 1}/{max_retries}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка запроса API для {sign_ru}: {e}")
            except Exception as e:
                logger.error(f"Неожиданная ошибка API для {sign_ru}: {type(e).__name__}: {e}")

            # Ждем перед повторной попыткой (экспоненциальная задержка)
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                logger.debug(f"Повтор через {wait_time} сек...")
                time.sleep(wait_time)

        logger.error(f"Не удалось получить гороскоп из API для {sign_ru} после {max_retries} попыток")
        return None

    def _is_english_text(self, text):
        """Проверяем, на английском ли текст"""
        if not text:
            return False

        # Простая проверка по наличию английских слов
        english_words = ['the', 'and', 'you', 'that', 'this', 'with', 'for', 'are', 'not']
        text_lower = text.lower()

        english_count = sum(1 for word in english_words if word in text_lower)
        latin_ratio = sum(1 for char in text if 'a' <= char <= 'z' or 'A' <= char <= 'Z') / max(len(text), 1)

        return english_count > 2 or latin_ratio > 0.7

    def _translate_horoscope(self, text, max_retries=2):
        """Простейший перевод через MyMemory API или замена ключевых слов"""
        if not text or len(text.strip()) < 10:
            return text

        logger.info(f"Пытаемся перевести текст ({len(text)} символов)...")

        # Сначала пробуем MyMemory API
        translated = self._try_mymemory_translation(text, max_retries)
        if translated and translated != text:
            return translated

        # Если API не сработало, делаем простую замену ключевых слов
        return self._simple_keyword_translation(text)

    def _try_mymemory_translation(self, text, max_retries=2):
        """Пробуем перевести через MyMemory API"""
        api_url = "https://api.mymemory.translated.net/get"

        # Ограничиваем длину текста
        if len(text) > 500:
            text_to_translate = text[:500]
        else:
            text_to_translate = text

        for attempt in range(max_retries):
            try:
                params = {
                    'q': text_to_translate,
                    'langpair': 'en|ru',
                    'de': 'user@example.com'
                }

                response = requests.get(api_url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    if 'responseData' in data and 'translatedText' in data['responseData']:
                        translated = data['responseData']['translatedText']
                        if translated and len(translated) > 10 and translated != text_to_translate:
                            logger.info("✅ Перевод через MyMemory API выполнен успешно")
                            return translated

                logger.debug(f"Попытка {attempt + 1} перевода не удалась")

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                logger.debug(f"Ошибка соединения при переводе, попытка {attempt + 1}")
            except Exception as e:
                logger.debug(f"Ошибка перевода: {type(e).__name__}")

            # Ждем перед повторной попыткой
            if attempt < max_retries - 1:
                time.sleep(1)

        return None

    def _simple_keyword_translation(self, text):
        """Простая замена ключевых слов"""
        translations = {
            'love': 'любовь',
            'money': 'деньги',
            'work': 'работа',
            'health': 'здоровье',
            'family': 'семья',
            'friends': 'друзья',
            'today': 'сегодня',
            'tomorrow': 'завтра',
            'week': 'неделя',
            'month': 'месяц',
            'year': 'год',
            'happy': 'счастливый',
            'success': 'успех',
            'problem': 'проблема',
            'solution': 'решение',
            'opportunity': 'возможность',
            'challenge': 'испытание',
            'energy': 'энергия',
            'peace': 'мир',
            'balance': 'баланс',
            'change': 'перемена',
            'Aries': 'Овен',
            'Taurus': 'Телец',
            'Gemini': 'Близнецы',
            'Cancer': 'Рак',
            'Leo': 'Лев',
            'Virgo': 'Дева',
            'Libra': 'Весы',
            'Scorpio': 'Скорпион',
            'Sagittarius': 'Стрелец',
            'Capricorn': 'Козерог',
            'Aquarius': 'Водолей',
            'Pisces': 'Рыбы'
        }

        # Простая замена ключевых слов
        result = text
        for eng, rus in translations.items():
            # Заменяем с учетом регистра
            result = result.replace(f' {eng} ', f' {rus} ')
            result = result.replace(f' {eng.capitalize()} ', f' {rus.capitalize()} ')
            result = result.replace(f' {eng},', f' {rus},')
            result = result.replace(f' {eng}.', f' {rus}.')

        # Если замена что-то изменила
        if result != text:
            logger.info("✅ Выполнена замена ключевых слов")
            return result

        logger.warning("Перевод не удался, используем оригинальный текст")
        return text

    def _format_response(self, sign_ru, horoscope_text):
        """Форматируем ответ API в читаемый вид"""
        try:
            emoji = self.zodiac_emojis.get(sign_ru.lower(), '✨')
            date = datetime.now().strftime("%d.%m.%Y")

            # Определяем источник
            if self._is_english_text(horoscope_text):
                source = "OhMana API (английский)"
            else:
                source = "OhMana API с переводом"

            # Форматируем
            formatted = f"""
{emoji} *Гороскоп для {sign_ru.capitalize()} на {date}* {emoji}

{horoscope_text}

✨ *Источник:* {source}
💫 *Обновлено:* {datetime.now().strftime('%H:%M')}
"""
            return formatted

        except Exception as e:
            logger.error(f"Ошибка форматирования ответа API: {e}")
            return None

    def check_api_status(self):
        """Проверить статус API"""
        try:
            response = requests.get(f"{self.base_url}/aries/", timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False