import requests
from bs4 import BeautifulSoup
import random
from datetime import datetime
import logging
import time
from api_client import HoroscopeAPI

logger = logging.getLogger(__name__)


class Horoscope:
    def __init__(self):
        self.zodiac_signs = {
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

        # Добавляем API клиент
        self.api_client = HoroscopeAPI()

        # Список источников в порядке приоритета
        self.sources = [
            self._try_api_source,  # Пробуем API первым
            self._try_source_rambler,  # Потом парсинг
            self._try_source_goroskopru,
            self._try_source_astrology_com
        ]

        # Кэш для хранения гороскопов на сегодня
        self.cache = {}
        self.cache_date = datetime.now().date()

    def _try_api_source(self, sign_ru):
        """Пробуем получить гороскоп из API"""
        try:
            logger.debug(f"Пробуем API источник для {sign_ru}")
            result = self.api_client.get_daily_horoscope(sign_ru)

            if result:
                # Извлекаем только текст гороскопа без форматирования заголовка
                lines = result.split('\n')
                horoscope_lines = []
                in_horoscope = False

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Ищем начало гороскопа (после заголовка)
                    if '*Гороскоп для' in line:
                        in_horoscope = True
                        continue

                    # Если нашли источник - заканчиваем
                    if '*Источник:' in line or '*Обновлено:' in line:
                        break

                    # Собираем текст гороскопа
                    if in_horoscope and line:
                        horoscope_lines.append(line)

                if horoscope_lines:
                    horoscope_text = ' '.join(horoscope_lines)
                    logger.info(f"✅ API источник сработал для {sign_ru}")
                    return horoscope_text

            return None
        except Exception as e:
            logger.debug(f"Ошибка API источника для {sign_ru}: {e}")
            return None

    def get_online_horoscope(self, sign_ru, max_retries=2):
        """Получить гороскоп с нескольких источников с повторными попытками"""
        sign_lower = sign_ru.lower()

        # Проверяем кэш
        cache_key = f"{sign_lower}_{datetime.now().strftime('%Y-%m-%d')}"
        if cache_key in self.cache:
            logger.debug(f"Используем кэшированный гороскоп для {sign_ru}")
            return self.cache[cache_key]

        # Проверяем, нужно ли очистить кэш (новый день)
        current_date = datetime.now().date()
        if current_date != self.cache_date:
            self.cache.clear()
            self.cache_date = current_date
            logger.info("Кэш очищен (новый день)")

        logger.info(f"Поиск гороскопа для знака: {sign_ru}")

        for attempt in range(max_retries):
            for i, source_func in enumerate(self.sources):
                try:
                    logger.debug(f"Попытка {attempt + 1}, источник {i + 1} для {sign_ru}")
                    horoscope_text = source_func(sign_lower)

                    if horoscope_text:
                        formatted = self._format_horoscope(sign_ru, horoscope_text)
                        # Сохраняем в кэш
                        self.cache[cache_key] = formatted
                        logger.info(f"✅ Гороскоп получен для {sign_ru} из источника {i + 1}")
                        return formatted

                except Exception as e:
                    logger.debug(f"Ошибка в источнике {i + 1}: {e}")
                    continue

            # Если все источники не сработали, ждем перед повторной попыткой
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # Экспоненциальная задержка
                logger.debug(f"Повтор через {wait_time} секунд...")
                time.sleep(wait_time)

        # Если все источники не сработали
        logger.warning(f"Все источники не сработали для {sign_ru}, используем fallback")
        fallback = self._get_fallback_horoscope(sign_ru)
        self.cache[cache_key] = fallback
        return fallback

    def _try_source_rambler(self, sign_ru):
        """Парсинг с rambler.ru"""
        try:
            sign_en = self.zodiac_signs.get(sign_ru)
            if not sign_en:
                return None

            url = f"https://horoscopes.rambler.ru/{sign_en}/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }

            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Пробуем разные селекторы
            selectors = [
                '._1Sg55',  # Новый селектор Rambler
                '._3wtsS._3tdcC',
                '.mlrBf',
                '.mCyUf',
                'div[data-cy="text-block"]',
                'article p',
                '.content p'
            ]

            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        text = element.get_text(strip=True)
                        if len(text) > 100 and not any(
                                word in text.lower() for word in ['cookie', 'политика', 'конфиденциальность']):
                            logger.debug(f"Найден текст длиной {len(text)} символов с селектором {selector}")
                            return text

            return None

        except Exception as e:
            logger.debug(f"Ошибка парсинга Rambler: {e}")
            return None

    def _try_source_goroskopru(self, sign_ru):
        """Парсинг с goroskop.ru"""
        try:
            sign_mapping = {
                'овен': 'oven',
                'телец': 'telec',
                'близнецы': 'bliznecy',
                'рак': 'rak',
                'лев': 'lev',
                'дева': 'deva',
                'весы': 'vesy',
                'скорпион': 'skorpion',
                'стрелец': 'strelec',
                'козерог': 'kozerog',
                'водолей': 'vodolei',
                'рыбы': 'ryby'
            }

            sign_en = sign_mapping.get(sign_ru)
            if not sign_en:
                return None

            url = f"https://goroskop.ru/{sign_en}/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }

            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Пробуем найти текст гороскопа
            text_containers = soup.select('.text, .content, article, .horoscope-text, p')

            for container in text_containers:
                text = container.get_text(strip=True)
                if len(text) > 150 and 'гороскоп' in text.lower():
                    # Очищаем текст от лишнего
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    meaningful_lines = [line for line in lines if len(line) > 30]
                    if meaningful_lines:
                        return ' '.join(meaningful_lines[:3])  # Берем первые 3 осмысленные строки

            return None

        except Exception as e:
            logger.debug(f"Ошибка парсинга goroskop.ru: {e}")
            return None

    def _try_source_astrology_com(self, sign_ru):
        """Парсинг с astrology.com (английский)"""
        try:
            sign_en = self.zodiac_signs.get(sign_ru)
            if not sign_en:
                return None

            url = f"https://www.astrology.com/horoscope/daily/{sign_en}.html"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Ищем основной контент
            content = soup.select_one('article, .content, .horoscope-content, .daily-horoscope')
            if content:
                text = content.get_text(strip=True)
                if len(text) > 100:
                    # Простой перевод/адаптация (можно заменить на нормальный переводчик)
                    russian_phrases = {
                        'today': 'сегодня',
                        'you': 'вы',
                        'your': 'ваш',
                        'will': 'будет',
                        'good': 'хороший',
                        'day': 'день',
                        'love': 'любовь',
                        'work': 'работа',
                        'money': 'деньги',
                        'health': 'здоровье'
                    }

                    # Простая замена ключевых слов
                    for eng, rus in russian_phrases.items():
                        text = text.replace(f' {eng} ', f' {rus} ')

                    return text[:500]  # Ограничиваем длину

            return None

        except Exception as e:
            logger.debug(f"Ошибка парсинга astrology.com: {e}")
            return None

    def _get_fallback_horoscope(self, sign_ru):
        """Резервный вариант - случайный гороскоп"""
        logger.info(f"Используем fallback гороскоп для {sign_ru}")

        themes = {
            'овен': ['энергия', 'инициатива', 'спорт', 'соревнование'],
            'телец': ['деньги', 'стабильность', 'комфорт', 'природа'],
            'близнецы': ['общение', 'обучение', 'путешествия', 'новости'],
            'рак': ['семья', 'дом', 'эмоции', 'традиции'],
            'лев': ['творчество', 'признание', 'лидерство', 'роскошь'],
            'дева': ['работа', 'здоровье', 'организация', 'детали'],
            'весы': ['отношения', 'гармония', 'красота', 'партнерство'],
            'скорпион': ['трансформация', 'страсть', 'тайны', 'интуиция'],
            'стрелец': ['путешествия', 'философия', 'свобода', 'оптимизм'],
            'козерог': ['карьера', 'цели', 'дисциплина', 'успех'],
            'водолей': ['инновации', 'друзья', 'технологии', 'гуманизм'],
            'рыбы': ['мечты', 'искусство', 'духовность', 'сострадание']
        }

        sign_themes = themes.get(sign_ru.lower(), ['удача', 'развитие', 'возможности'])

        predictions = [
            f"Сегодня звезды благоволят {sign_ru}. Ожидайте приятных сюрпризов в сфере {random.choice(sign_themes)}.",
            f"Для {sign_ru} наступает время перемен. Проявите инициативу в вопросах {random.choice(sign_themes)}.",
            f"Сегодняшний день принесет {sign_ru} новые возможности. Будьте внимательны к знакам судьбы.",
            f"Энергия дня способствует {sign_ru} в решении вопросов {random.choice(sign_themes)}. Доверяйте интуиции.",
            f"Сегодня {sign_ru} может достичь успеха в {random.choice(sign_themes)}. Главное - действовать решительно.",
            f"Звезды советуют {sign_ru} проявить терпение в вопросах {random.choice(sign_themes)}. Все решится наилучшим образом."
        ]

        advice_list = [
            "Утром уделите время планированию дня.",
            "Днем проявите гибкость в общении.",
            "Вечером отдохните и восстановите силы.",
            "Не принимайте важных решений на эмоциях.",
            "Сегодня хороший день для новых начинаний.",
            "Обратите внимание на знаки судьбы вокруг вас."
        ]

        emoji = self.zodiac_emojis.get(sign_ru.lower(), '✨')
        main_prediction = random.choice(predictions)
        daily_advice = random.choice(advice_list)

        return self._format_horoscope(sign_ru, f"{main_prediction}\n\n{daily_advice}")

    def _format_horoscope(self, sign_ru, text):
        """Форматирование ответа"""
        emoji = self.zodiac_emojis.get(sign_ru.lower(), '✨')
        date = datetime.now().strftime("%d.%m.%Y")

        # Генерируем уникальные рекомендации для каждого знака
        colors = {
            'овен': 'красный',
            'телец': 'зеленый',
            'близнецы': 'желтый',
            'рак': 'серебристый',
            'лев': 'золотой',
            'дева': 'коричневый',
            'весы': 'голубой',
            'скорпион': 'черный',
            'стрелец': 'фиолетовый',
            'козерог': 'серый',
            'водолей': 'бирюзовый',
            'рыбы': 'синий'
        }

        lucky_numbers = {
            'овен': random.choice([1, 9, 19]),
            'телец': random.choice([2, 6, 24]),
            'близнецы': random.choice([3, 7, 21]),
            'рак': random.choice([4, 13, 31]),
            'лев': random.choice([5, 14, 23]),
            'дева': random.choice([6, 15, 33]),
            'весы': random.choice([7, 16, 25]),
            'скорпион': random.choice([8, 17, 26]),
            'стрелец': random.choice([9, 18, 27]),
            'козерог': random.choice([10, 19, 28]),
            'водолей': random.choice([11, 22, 29]),
            'рыбы': random.choice([12, 24, 30])
        }

        color = colors.get(sign_ru.lower(), random.choice(['синий', 'зеленый', 'золотой', 'фиолетовый']))
        number = lucky_numbers.get(sign_ru.lower(), random.randint(1, 9))

        return f"""
{emoji} *Гороскоп для {sign_ru.capitalize()} на {date}* {emoji}

{text}

💫 *Совет дня*: Прислушивайтесь к своей интуиции.
🎨 *Удачный цвет*: {color}
🔢 *Благоприятное число*: {number}
✨ *Источник*: Астрологический советник
"""

    def get_all_signs(self):
        """Список всех знаков с эмодзи"""
        return [f"{self.zodiac_emojis[sign]} {sign.capitalize()}" for sign in self.zodiac_signs.keys()]

    def get_keyboard_signs(self):
        """Знаки для клавиатуры (по 3 в строке)"""
        signs = list(self.zodiac_signs.keys())
        keyboard = []

        # Разбиваем на строки по 3 знака
        for i in range(0, len(signs), 3):
            row = signs[i:i + 3]
            keyboard.append([sign.capitalize() for sign in row])

        return keyboard