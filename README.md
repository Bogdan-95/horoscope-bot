# 🔮 Daily Horoscope Telegram Bot 2.0

![Python](https://img.shields.io/badge/Python-3.11-blue)
![aiogram](https://img.shields.io/badge/aiogram-3.x-green)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![SQLite](https://img.shields.io/badge/SQLite-async-lightgrey)
![Status](https://img.shields.io/badge/status-production--ready-success)

Полнофункциональный **Telegram-бот для ежедневных гороскопов**  
с подпиской, автоматической рассылкой, переводом и Docker-развёртыванием.

> Проект выполнен как **production / portfolio-проект**  
> с упором на архитектуру, стабильность и читаемость кода.

---

## 🚀 Возможности бота

### 🔮 Гороскопы
- Гороскоп на день по знаку зодиака
- Реальные данные через внешний API
- Автоматический перевод на русский язык

### 🔔 Подписка и рассылка
- Подписка на ежедневный гороскоп
- Выбор знака зодиака
- Настройка времени рассылки (утро)
- Асинхронная отправка без блокировок

### ❤️ Совместимость знаков
- Выбор двух знаков
- Расчёт совместимости

### 🧠 Технические возможности
- Асинхронная архитектура (`aiogram 3`)
- Планировщик задач (`APScheduler`)
- SQLite + `aiosqlite`
- Docker + docker-compose
- Логирование (`loguru`)
- Хранение данных вне контейнера

---

## 📸 Демонстрация

<p align="center">
  <img src="screenshots/Start.png.png" width="30%" />
  <img src="screenshots/answer.png.png" width="30%" />
  <img src="screenshots/compatibility.png.png" width="30%" />
</p>

---

## 🏗️ Архитектура проекта







## 🧠 Архитектура проекта
```markdown
horoscope_bot/
├── app/
│   ├── database/
│   │   └── requests.py        # Работа с SQLite (aiosqlite)
│   ├── handlers/
│   │   └── user.py            # Все пользовательские сценарии
│   ├── keyboards/
│   │   └── inline.py          # Inline / Reply клавиатуры
│   ├── services/
│   │   ├── horoscope_api.py   # API + fallback + совместимость
│   │   └── translator_service.py
│   └── __init__.py
│
├── data/
│   └── database.db            # SQLite база
│
├── screenshots/               # Скриншоты бота
├── docker-compose.yml
├── requirements.txt
├── main.py                    # Точка входа
├── README.md
└── .env.example
```

---

## ⚙️ Технологический стек

- **Python 3.11**
- **aiogram 3**
- **SQLite + aiosqlite**
- **APScheduler**
- **Docker / Docker Compose**
- **deep-translator**
- **loguru**
- **dotenv**

---

## 🐳 Запуск через Docker (рекомендуется)

### 1️⃣ Подготовка `.env`

```env
BOT_TOKEN=your_telegram_bot_token
ASTROLOGY_API_KEY=your_api_key
```
### 2️⃣ Сборка и запуск
```bash
docker compose up -d --build
```
### 3️⃣ Просмотр логов
```bash
docker logs -f horoscope_bot_v2
```
### 4️⃣ Остановка
```bash
docker compose down
```

### 🐳 docker-compose.yml

Проект полностью готов к запуску в Docker.

```yaml
services:
  bot:
    build: .
    container_name: horoscope_bot_v2
    restart: always
    env_file:
      - .env
    volumes:
      - ./data:/app/data

```
## Почему Docker:
- одинаковая среда запуска
- лёгкий деплой на VPS
- безопасное хранение данных
- автоперезапуск контейнера


## 🔄 Логика работы бота 
```text
Пользователь
   ↓
Inline-меню
   ↓
Выбор действия
   ├─ Гороскоп → API → Перевод → Ответ
   ├─ Совместимость → Логика стихий → Ответ
   └─ Подписка → SQLite → APScheduler → Рассылка

```

## ⏰ Планировщик рассылки
Для автоматической отправки гороскопов используется
APScheduler (AsyncIO Scheduler).

### Логика работы:

- проверка подписок каждую минуту
- отправка сообщений строго по выбранному времени
- таймзона: Europe/Moscow

```python
scheduler.add_job(
    daily_broadcast_task,
    trigger='cron',
    minute='*'
)
```

## 🗄️ База данных
### SQLite (aiosqlite)
В проекте используется SQLite с асинхронным доступом через aiosqlite.

### Таблица users:

- tg_id — Telegram ID пользователя (PRIMARY KEY)
- username — username в Telegram
- sign — выбранный знак зодиака
- is_subscribed — статус подписки
- mailing_time — время рассылки (МСК)
- last_forecast — последний отправленный прогноз

### Особенности:

- база хранится вне Docker-контейнера
- легко подключается к DBeaver
- данные не теряются при перезапуске контейнера
```yaml
volumes:
  - ./data:/app/data
```


## 🌐 Источники данных
### Основной

1. Ohmanda Horoscope API
    - https://ohmanda.com/api/horoscope/{sign}
    - Реальные гороскопы на сегодня для всех знаков
### Перевод
1. GoogleTranslator (deep-translator)
2. Асинхронная обертка через run_in_executor

### Fallback - механизм

1. Локальный генератор прогнозов
2. Бот не падает без интернета

# 🚀 Запуск проекта
### 🚀🐳 Запуск проекта (Docker)

```bash
docker compose up -d --build
```
### Остановка:
```bash
docker compose down
```
### Просмотр логов:
```bash
docker logs -f horoscope_bot_v2
```


## 🚀 Локальный запуск 🐍 

```bash
git clone https://github.com/Bogdan-95/horoscope-bot.git
cd horoscope-bot

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
python main.py

```

## 📦 Зависимости 
```text
aiogram==3.15.0
aiosqlite==0.20.0
apscheduler==3.11.2
python-dotenv==1.0.1
loguru==0.7.2
aiohttp==3.10.11
deep-translator==1.11.4
tzdata
```

# 👤 Автор 
## Bogdan-95
* ### GitHub: https://github.com/Bogdan-95
* ### Telegram: @bodya_95

### ⭐ Если проект был полезен — поставьте звезду на GitHub