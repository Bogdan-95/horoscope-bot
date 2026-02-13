# app/handlers/user.py
# Основные обработчики команд пользователя (/start, /help, /menu, гороскоп, выбор знака)
# Содержит все базовые функции бота + навигацию по меню

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.utils.logger import logger
from app.database.crud import get_user, create_user, update_user_sign
from app.services.horoscope_api import HoroscopeAPI
from app.keyboards.main import (
    main_menu_kb, zodiac_kb, help_kb, back_to_menu_kb,
    back_kb
)

router = Router()
horoscope_api = HoroscopeAPI()


def u(user) -> str:
    """Форматирует информацию о пользователе для логов"""
    if not user:
        return "Unknown"
    name = user.first_name or user.username or "NoName"
    return f"{name} ({user.id})"


# ===================== START =====================

@router.message(F.text == "/start")
async def start(message: Message):
    user = message.from_user
    logger.info(f"[START] {u(user)}")

    try:
        create_user(user.id, user.username, user.first_name)

        await message.answer(
            "🔮 *Добро пожаловать в Daily Horoscope Bot!*\n\n"
            "✨ *Возможности бота:*\n"
            "• 🔮 Персональный гороскоп\n"
            "• ❤️ Совместимость знаков\n"
            "• 🔔 Ежедневная рассылка\n"
            "• 📊 Детальный анализ\n\n"
            "Выберите действие 👇",
            reply_markup=main_menu_kb()
        )
    except Exception as e:
        # Проверяем, не заблокировал ли пользователь бота
        if "Forbidden: bot was blocked" in str(e):
            logger.warning(f"User {user.id} blocked the bot")
        else:
            logger.error(f"Error in start handler: {e}")



@router.message(F.text == "/help")
async def help_command(message: Message):
    """Обработчик команды /help - показывает справочную информацию."""

    logger.info(f"[HELP_CMD] {u(message.from_user)}")
    await show_help(message)


@router.message(F.text == "✨ Главное меню")
async def main_menu_reply(message: Message):
    """Обработчик текстового сообщения '✨ Главное меню'."""

    logger.info(f"[MAIN_MENU_REPLY] {u(message.from_user)}")
    await show_menu(message)


# ===================== MENU =====================

@router.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery):
    """
        Callback обработчик возврата в главное меню.
    """
    logger.info(f"[MENU] {u(callback.from_user)}")
    await callback.message.edit_text(
        "📋 *Главное меню*",
        reply_markup=main_menu_kb()
    )
    await callback.answer()


# ФИЛЬТР ТОЧНОГО ТЕКСТА "/menu"
@router.message(F.text == "/menu")
async def show_menu(message: Message):
    """Обработчик команды /menu"""
    logger.info(f"[MENU_CMD] {u(message.from_user)}")
    await message.answer(
        "📋 *Главное меню*",
        reply_markup=main_menu_kb()
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: CallbackQuery):
    """Быстрый возврат в главное меню из любой ветки."""

    logger.info(f"[BACK_TO_MENU] {u(callback.from_user)}")
    await menu_callback(callback)


# ===================== HELP =====================

@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    logger.info(f"[HELP_CALLBACK] {u(callback.from_user)}")
    await show_help_callback(callback)


async def show_help(message: Message):
    help_text = (
        "🆘 *Помощь по боту*\n\n"
        "✨ *Основные функции:*\n"
        "• 🔮 *Гороскоп* - ежедневный прогноз для вашего знака\n"
        "• ❤️ *Совместимость* - проверьте совместимость двух знаков\n"
        "• ♻️ *Выбрать знак* - установите свой знак зодиака\n"
        "• 🔔 *Рассылка* - получайте гороскопы автоматически\n\n"
        "📝 *Как пользоваться:*\n"
        "1. Сначала выберите свой знак в меню\n"
        "2. Получайте гороскопы ежедневно\n"
        "3. Проверяйте совместимость с друзьями\n"
        "4. Настройте удобное время рассылки\n\n"
        "❓ *Если возникли проблемы:*\n"
        "• Перезапустите бота командой /start\n"
        "• Обратитесь к разработчику через кнопку ниже\n\n"
        "💡 *Совет:* Используйте кнопку '✨ Главное меню' для быстрой навигации"
    )

    await message.answer(help_text, reply_markup=help_kb())


async def show_help_callback(callback: CallbackQuery):
    help_text = (
        "🆘 *Помощь по боту*\n\n"
        "✨ *Основные функции:*\n"
        "• 🔮 *Гороскоп* - ежедневный прогноз для вашего знака\n"
        "• ❤️ *Совместимость* - проверьте совместимость двух знаков\n"
        "• ♻️ *Выбрать знак* - установите свой знак зодиака\n"
        "• 🔔 *Рассылка* - получайте гороскопы автоматически\n\n"
        "📝 *Как пользоваться:*\n"
        "1. Сначала выберите свой знак в меню\n"
        "2. Получайте гороскопы ежедневно\n"
        "3. Проверяйте совместимость с друзьями\n"
        "4. Настройте удобное время рассылки\n\n"
        "❓ *Если возникли проблемы:*\n"
        "• Перезапустите бота командой /start\n"
        "• Обратитесь к разработчику через кнопку ниже"
    )

    await callback.message.edit_text(help_text, reply_markup=help_kb())
    await callback.answer()


@router.callback_query(F.data == "help_instructions")
async def help_instructions(callback: CallbackQuery):
    logger.info(f"[HELP_INSTRUCTIONS] {u(callback.from_user)}")

    instructions = (
        "📚 *ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ БОТА*\n\n"

        "1️⃣ *Начало работы:*\n"
        "• Нажмите /start для запуска бота\n"
        "• Выберите свой знак зодиака в меню\n\n"

        "2️⃣ *Получение гороскопа:*\n"
        "• Нажмите кнопку '🔮 Гороскоп'\n"
        "• Бот покажет ваш ежедневный прогноз\n"
        "• Гороскоп обновляется каждый день\n\n"

        "3️⃣ *Проверка совместимости:*\n"
        "• Нажмите '❤️ Совместимость'\n"
        "• Выберите первый знак\n"
        "• Выберите второй знак\n"
        "• Получите детальный анализ совместимости\n\n"

        "4️⃣ *Настройка рассылки:*\n"
        "• Нажмите '🔔 Рассылка'\n"
        "• Выберите удобное время\n"
        "• Включите ежедневные уведомления\n"
        "• Получайте гороскопы автоматически\n\n"

        "5️⃣ *Навигация:*\n"
        "• '⬅️ В меню' - вернуться в главное меню\n"
        "• '🔙 Назад' - вернуться на предыдущий экран\n"
        "• '❌ Отмена' - отменить текущее действие\n"
    )

    await callback.message.edit_text(instructions, reply_markup=back_kb("help"))
    await callback.answer()


@router.callback_query(F.data == "help_faq")
async def help_faq(callback: CallbackQuery):
    logger.info(f"[HELP_FAQ] {u(callback.from_user)}")

    faq = (
        "❓ *ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ*\n\n"

        "🤔 *Как часто обновляется гороскоп?*\n"
        "Гороскоп обновляется ежедневно в 00:00 по Московскому времени.\n\n"

        "🔮 *Откуда берутся прогнозы?*\n"
        "Прогнозы основаны на астрологических расчетах и обновляются из проверенных источников.\n\n"

        "❤️ *Насколько точна совместимость?*\n"
        "Совместимость рассчитывается на основе астрологических данных, но помните, что отношения зависят от людей.\n\n"

        "💾 *Сохраняется ли мой знак?*\n"
        "Да, ваш знак сохраняется в базе данных. Вы можете изменить его в любое время.\n\n"

        "⏰ *Можно ли получать гороскоп по расписанию?*\n"
        "Да! Настройте удобное время в разделе '🔔 Рассылка'.\n\n"

        "📱 *Бот работает на всех устройствах?*\n"
        "Да, бот работает на телефонах, планшетах и компьютерах через Telegram.\n\n"

        "🆘 *Как связаться с поддержкой?*\n"
        "Нажмите кнопку '📞 Связаться с поддержкой' в меню помощи."
    )

    await callback.message.edit_text(faq, reply_markup=back_kb("help"))
    await callback.answer()


# ===================== SIGN =====================

@router.callback_query(F.data == "choose_sign")
async def choose_sign(callback: CallbackQuery):
    logger.info(f"[CHOOSE_SIGN] {u(callback.from_user)}")

    await callback.message.edit_text(
        "♈ *Выберите ваш знак зодиака:*",
        reply_markup=zodiac_kb("set_sign:")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_sign:"))
async def set_sign(callback: CallbackQuery):
    logger.info(f"[SET_SIGN_START] {u(callback.from_user)}")
    logger.info(f"[SET_SIGN_DATA] Callback data: {callback.data}")

    try:
        sign = callback.data.split(":")[1]
        logger.info(f"[SET_SIGN_EXTRACT] Extracted sign: {sign}")

        logger.info(f"[SET_SIGN_UPDATE] Updating sign for user {callback.from_user.id}")
        update_user_sign(callback.from_user.id, sign)
        logger.info(f"[SET_SIGN_UPDATED] Sign updated successfully")

        await callback.message.edit_text(
            "✅ *Знак сохранён!*\n\n"
            f"✨ Теперь ваш знак: *{sign.capitalize()}*\n\n"
            "Теперь вы можете получать персональные гороскопы и настраивать рассылку.",
            reply_markup=back_to_menu_kb()
        )

        logger.info(f"[SET_SIGN_COMPLETE] Message sent successfully")

    except Exception as e:
        logger.exception(f"[SET_SIGN_ERROR] Error: {e}")
        await callback.answer("❌ Ошибка сохранения знака", show_alert=True)

    await callback.answer()


# ===================== HOROSCOPE =====================

@router.callback_query(F.data == "daily_horoscope")
async def daily_horoscope(callback: CallbackQuery):
    user_data = get_user(callback.from_user.id)
    logger.info(f"[HOROSCOPE_REQUEST] {u(callback.from_user)}")

    if not user_data:
        logger.warning(f"[HOROSCOPE_NO_USER] {u(callback.from_user)} - user not found in DB")
        await callback.answer("❌ Ошибка: пользователь не найден", show_alert=True)
        return

    if not user_data.get("sign"):
        logger.warning(f"[HOROSCOPE_NO_SIGN] {u(callback.from_user)} - no sign set")
        await callback.answer("❗ Сначала выберите знак зодиака", show_alert=True)
        return

    try:
        logger.info(f"[HOROSCOPE_FETCH] Getting horoscope for {user_data['sign']}")
        text = await horoscope_api.get_daily_horoscope(user_data["sign"])
        logger.info(f"[HOROSCOPE_OK] {u(callback.from_user)} | {user_data['sign']}")

        message = (
            f"✨ *ГОРОСКОП ДЛЯ {user_data['sign'].upper()}*\n\n"
            f"{text}\n\n"
            "💫 _Хорошего дня!_"
        )

        await callback.message.edit_text(
            message,
            reply_markup=back_to_menu_kb()
        )
    except Exception as e:
        logger.exception(f"[HOROSCOPE_ERROR] {u(callback.from_user)} | {e}")
        await callback.message.edit_text(
            "⚠️ *Ошибка получения гороскопа*\n\n"
            "Попробуйте позже или обратитесь в поддержку.",
            reply_markup=back_to_menu_kb()
        )

    await callback.answer()