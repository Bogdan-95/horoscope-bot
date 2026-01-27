import asyncio
import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from loguru import logger

import app.database.requests as rq
import app.keyboards.inline as kb
from app.services.horoscope_api import HoroscopeAPI

router = Router()
api = HoroscopeAPI()

ANIM_LOADING = (
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZjJoaTEyaWJ2dnZxdG5wdXRudnU0bWo3NzR5dzlzZjc3cDlyeG1xZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3og0IFrHkIglEOg8Ba/giphy.gif"
)

# ==================================================
# START / ГЛАВНОЕ МЕНЮ
# ==================================================

@router.message(CommandStart())
async def cmd_start(message: Message):
    logger.info(f"START: Пользователь {message.from_user.id}")
    await rq.set_user(message.from_user.id, message.from_user.username)

    await message.answer("✨ Звезды сошлись!", reply_markup=kb.reply_main_menu())
    await message.answer(
        "🌟 *Добро пожаловать в мир астрологии!*\n\n"
        "Я — ваш персональный астрологический помощник.\n"
        "Что вы хотите узнать сегодня?",
        parse_mode="Markdown",
        reply_markup=kb.main_menu()
    )


@router.message(F.text == "✨ Главное меню")
async def msg_main_menu(message: Message):
    logger.info(f"MENU: Главное меню ({message.from_user.id})")
    await message.answer(
        "🔮 *Главное меню:*",
        parse_mode="Markdown",
        reply_markup=kb.main_menu()
    )


@router.callback_query(F.data == "to_main")
async def back_to_main(callback: CallbackQuery):
    logger.info(f"NAV: Возврат в главное меню ({callback.from_user.id})")
    try:
        await callback.message.edit_text(
            "🔮 *Главное меню:*",
            parse_mode="Markdown",
            reply_markup=kb.main_menu()
        )
    except TelegramBadRequest:
        await callback.message.answer(
            "🔮 *Главное меню:*",
            parse_mode="Markdown",
            reply_markup=kb.main_menu()
        )
    await callback.answer()


# ==================================================
# ГОРОСКОП
# ==================================================

@router.callback_query(F.data == "get_horo")
async def list_signs(callback: CallbackQuery):
    logger.info(f"HORO_LIST: {callback.from_user.id}")
    await callback.message.edit_text(
        "✨ Выберите ваш знак зодиака:",
        reply_markup=kb.signs_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("show_sign_"))
async def show_horo(callback: CallbackQuery):
    sign = callback.data.split("_")[2]
    logger.info(f"HORO: {sign.upper()} ({callback.from_user.id})")

    await callback.message.delete()

    loading = await callback.message.answer_animation(
        animation=ANIM_LOADING,
        caption=f"🔮 *Связь с космосом для {sign.capitalize()}...*",
        parse_mode="Markdown"
    )

    text = await api.get_daily_horoscope(sign)
    await loading.delete()

    await callback.message.answer(
        f"{text}\n\n🍀 *Число удачи:* `{random.randint(1, 99)}`",
        parse_mode="Markdown",
        reply_markup=kb.back_to_main_kb()
    )
    await callback.answer()


# ==================================================
# СОВМЕСТИМОСТЬ
# ==================================================

@router.callback_query(F.data == "compat_start")
async def compat_step_1(callback: CallbackQuery):
    logger.info(f"COMPAT: Старт ({callback.from_user.id})")
    await callback.message.edit_text(
        "❤️ *Совместимость*\n\nВыберите **ВАШ** знак зодиака:",
        parse_mode="Markdown",
        reply_markup=kb.compat_signs_kb(step="first")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("compat_1_"))
async def compat_step_2(callback: CallbackQuery):
    sign1 = callback.data.split("_")[2]
    await callback.message.edit_text(
        f"❤️ Первый знак: *{sign1.capitalize()}*\n\n"
        f"Теперь выберите знак **ПАРТНЕРА**:",
        parse_mode="Markdown",
        reply_markup=kb.compat_signs_kb(step="second", sign1=sign1)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("compat_calc_"))
async def compat_finish(callback: CallbackQuery):
    _, _, sign1, sign2 = callback.data.split("_")
    logger.info(f"COMPAT: {sign1.upper()} + {sign2.upper()} ({callback.from_user.id})")

    await callback.message.edit_text(
        "💞 *Звезды анализируют вашу совместимость...*",
        parse_mode="Markdown"
    )
    await asyncio.sleep(1.5)

    result = api.get_compatibility(sign1, sign2)
    await callback.message.edit_text(
        result,
        parse_mode="Markdown",
        reply_markup=kb.back_to_main_kb()
    )
    await callback.answer()


# ==================================================
# ПОДПИСКА
# ==================================================

@router.callback_query(F.data == "sub_manage")
@router.message(F.text == "🔔 Подписка")
async def sub_manage(event: Message | CallbackQuery):
    user_id = event.from_user.id
    user = await rq.get_user_info(user_id)
    is_active = user.get("is_subscribed") if user else False

    text = "🔔 *Настройка уведомлений*\n\n"

    if is_active:
        text += (
            f"✅ Активно для: *{user['sign'].capitalize()}*\n"
            f"⏰ Время: *{user['mailing_time']}* (МСК)"
        )
        markup = kb.unsubscribe_kb()
    else:
        text += "❌ Уведомления выключены.\nВыберите знак:"
        markup = kb.signs_kb(prefix="sub_sign_")

    if isinstance(event, Message):
        await event.answer(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await event.message.edit_text(text, parse_mode="Markdown", reply_markup=markup)
        await event.answer()


@router.callback_query(F.data.startswith("sub_sign_"))
async def sub_choose_time(callback: CallbackQuery):
    sign = callback.data.split("_")[2]
    await callback.message.edit_text(
        f"⏰ *{sign.capitalize()}*\nВыберите время (МСК):",
        parse_mode="Markdown",
        reply_markup=kb.time_kb(sign)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_time_"))
async def sub_confirm(callback: CallbackQuery):
    _, _, time, sign = callback.data.split("_")
    logger.info(f"SUB: {callback.from_user.id} → {sign} {time}")

    await rq.subscribe_user(callback.from_user.id, sign, time)

    await callback.message.edit_text(
        f"✅ *Подписка оформлена!*\n\n"
        f"*{sign.capitalize()}* — каждый день в *{time}* (МСК)",
        parse_mode="Markdown",
        reply_markup=kb.back_to_main_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "unsub")
async def unsub(callback: CallbackQuery):
    logger.info(f"UNSUB: {callback.from_user.id}")
    await rq.unsubscribe_user(callback.from_user.id)

    await callback.message.edit_text(
        "🔕 *Подписка отключена.*",
        parse_mode="Markdown",
        reply_markup=kb.back_to_main_kb()
    )
    await callback.answer()


# ==================================================
# ПОМОЩЬ
# ==================================================

@router.callback_query(F.data == "help_guide")
@router.message(F.text == "🆘 Помощь")
async def help_cmd(event: Message | CallbackQuery):
    logger.info(f"HELP: Просмотр справки ({event.from_user.id})")

    help_text = (
        "📖 *Меню помощи*\n\n"
        "• *Узнать гороскоп* — прогноз на сегодня\n"
        "• *Совместимость* — проверка отношений\n"
        "• *Подписка* — ежедневный гороскоп\n\n"
        r"👨‍💻 Разработчик: @bodya\_95"
    )

    if isinstance(event, Message):
        await event.answer(
            help_text,
            parse_mode="Markdown",
            reply_markup=kb.back_to_main_kb()
        )
    else:
        await event.message.edit_text(
            help_text,
            parse_mode="Markdown",
            reply_markup=kb.back_to_main_kb()
        )
        await event.answer()
