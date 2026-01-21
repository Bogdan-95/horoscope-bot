import asyncio
import random
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from loguru import logger
from aiogram.exceptions import TelegramBadRequest

import app.database.requests as rq
import app.keyboards.inline as kb
from app.services.horoscope_api import HoroscopeAPI

router = Router()
api = HoroscopeAPI()

ANIM_LOADING = "https://media.giphy.com/media/3o7TKSjRrfIPjeiVyM/giphy.gif"


@router.message(CommandStart())
async def cmd_start(message: Message):
    logger.info(f"START: Пользователь {message.from_user.id}")
    await rq.set_user(message.from_user.id, message.from_user.username)

    welcome_text = (
        "🌟 *Добро пожаловать в мир астрологии!*\n\n"
        "Я — ваш персональный астрологический помощник.\n"
        "Что вы хотите узнать сегодня?"
    )
    await message.answer("✨ Звезды сошлись!", reply_markup=kb.reply_main_menu())
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=kb.main_menu())


@router.message(F.text == "✨ Главное меню")
async def msg_main_menu(message: Message):
    logger.info(f"MENU: Текстовая кнопка 'Главное меню' ({message.from_user.id})")  # Теперь это будет в логах!
    welcome_text = "🔮 *Главное меню:*\nВыбирайте действие:"
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=kb.main_menu())


@router.callback_query(F.data == "to_main")
async def back_to_main(callback: CallbackQuery):
    logger.info(f"NAV: Возврат в главное меню ({callback.from_user.id})")
    try:
        await callback.message.edit_text(
            "🌟 *Главное меню:*\nВыберите действие:",
            parse_mode="Markdown", reply_markup=kb.main_menu()
        )
    except TelegramBadRequest:
        await callback.message.answer("🌟 *Главное меню:*", reply_markup=kb.main_menu())
    await callback.answer()


# --- ГОРОСКОП ---
@router.callback_query(F.data == "get_horo")
async def list_signs(callback: CallbackQuery):
    logger.info(f"HORO_LIST: Пользователь {callback.from_user.id} открыл выбор знаков")  # Добавь это
    await callback.message.edit_text("✨ Выберите ваш знак зодиака:", reply_markup=kb.signs_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("show_sign_"))
async def show_horo(callback: CallbackQuery):
    sign = callback.data.split("_")[2]

    # Лог выбора конкретного знака
    logger.info(f"HORO: Запрос прогноза для знака {sign.upper()} ({callback.from_user.id})")

    await callback.message.delete()  # Удаляем меню
    loading_msg = await callback.message.answer_animation(
        animation=ANIM_LOADING,
        caption=f"🔮 *Связь с космосом для знака {sign.capitalize()}...*",
        parse_mode="Markdown"
    )

    text = await api.get_daily_horoscope(sign)
    await loading_msg.delete()  # Удаляем анимацию

    lucky_number = random.randint(1, 99)
    await callback.message.answer(
        f"{text}\n\n🍀 *Число удачи:* `{lucky_number}`",
        parse_mode="Markdown", reply_markup=kb.back_to_main_kb()
    )
    await callback.answer()


# --- СОВМЕСТИМОСТЬ ---
@router.callback_query(F.data == "compat_start")
async def compat_step_1(callback: CallbackQuery):
    """ Шаг 1: Выбор первого знака """
    logger.info(f"COMPAT: Начало ({callback.from_user.id})")
    await callback.message.edit_text(
        "❤️ *Совместимость*\n\nВыберите **ВАШ** знак зодиака:",
        parse_mode="Markdown", reply_markup=kb.compat_signs_kb(step="first")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("compat_1_"))
async def compat_step_2(callback: CallbackQuery):
    """ Шаг 2: Выбор второго знака """
    sign1 = callback.data.split("_")[2]
    await callback.message.edit_text(
        f"❤️ Первый знак: *{sign1.capitalize()}*\n\nТеперь выберите знак **ПАРТНЕРА**:",
        parse_mode="Markdown",
        reply_markup=kb.compat_signs_kb(step="second", sign1=sign1)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("compat_calc_"))
async def compat_finish(callback: CallbackQuery):
    """ Финал: Расчет """
    data = callback.data.split("_")
    sign1, sign2 = data[2], data[3]
    # Лог финального расчета
    logger.info(f"COMPAT: Расчет совместимости {sign1.upper()} + {sign2.upper()} ({callback.from_user.id})")


    # Визуальный эффект расчета
    await callback.message.edit_text("💞 *Звезды анализируют вашу совместимость...*", parse_mode="Markdown")
    await asyncio.sleep(1.5)

    result_text = api.get_compatibility(sign1, sign2)
    await callback.message.edit_text(result_text, parse_mode="Markdown", reply_markup=kb.back_to_main_kb())
    await callback.answer()


# --- ПОДПИСКА ---
@router.callback_query(F.data == "sub_manage")
@router.message(F.text == "🔔 Подписка")
async def sub_manage(event: [Message, CallbackQuery]):
    user_id = event.from_user.id
    user_data = await rq.get_user_info(user_id)
    is_active = user_data.get('is_subscribed') if user_data else False

    text = "🔔 *Настройка уведомлений*\n\n"
    if is_active:
        time = user_data.get('mailing_time', '07:00')
        sign = user_data.get('sign', 'не выбран')
        text += f"✅ Активно для: *{sign.capitalize()}*\n⏰ Время: *{time}* (МСК)"
        markup = kb.unsubscribe_kb()
    else:
        text += "❌ Уведомления выключены.\nВыберите знак для подписки:"
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
        f"⏰ Знак: *{sign.capitalize()}*\nВыберите время (МСК):",
        parse_mode="Markdown", reply_markup=kb.time_kb(sign)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_time_"))
async def sub_final_confirm(callback: CallbackQuery):
    data = callback.data.split("_")
    time, sign = data[2], data[3]
    # Лог успешного оформления
    logger.info(f"SUB: Успешная подписка на {sign.upper()} в {time} ({callback.from_user.id})")

    await rq.update_subscription(callback.from_user.id, status=True, sign=sign, time=time)

    await callback.message.edit_text(
        f"✅ *Успешно!*\nЯ буду присылать гороскоп для *{sign.capitalize()}* каждый день в *{time}*.",
        parse_mode="Markdown", reply_markup=kb.back_to_main_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "unsub")
async def process_unsub(callback: CallbackQuery):
    logger.info(f"SUB: Пользователь отменил подписку ({callback.from_user.id})")

    await rq.update_subscription(callback.from_user.id, status=False)
    await callback.message.edit_text("🔕 *Подписка отменена.*", parse_mode="Markdown", reply_markup=kb.back_to_main_kb())
    await callback.answer()


@router.callback_query(F.data == "help_guide")
@router.message(F.text == "🆘 Помощь")
async def help_cmd(event: [Message, CallbackQuery]):
    logger.info(f"HELP: Просмотр справки ({event.from_user.id})")
    help_text = (
        "📖 *Меню помощи*\n\n"
        "• *Узнать гороскоп* — прогноз на сегодня.\n"
        "• *Совместимость* — узнайте, подходите ли вы друг другу.\n"
        "• *Подписка* — ежедневный гороскоп в удобное время.\n\n"
        r"👨‍💻 Разработчик: @bodya\_95"
    )
    if isinstance(event, Message):
        await event.answer(help_text, parse_mode="Markdown", reply_markup=kb.back_to_main_kb())
    else:
        await event.message.edit_text(help_text, parse_mode="Markdown", reply_markup=kb.back_to_main_kb())
        await event.answer()