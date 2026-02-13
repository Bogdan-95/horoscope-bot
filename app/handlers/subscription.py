# app/handlers/subscription.py
# Обработчики для управления подпиской

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.utils.logger import logger
from app.database.crud import (
    get_user, get_subscription, update_subscription
)

from app.keyboards.subscription import (
    subscription_menu_kb, time_selection_kb,
    subscription_info_kb, unsubscribe_confirm_kb,
    subscribe_confirm_kb
)
from app.keyboards.main import back_to_menu_kb
from app.utils.message_formatter import format_subscription_message

router = Router()


def u(user) -> str:
    """Форматирует информацию о пользователе для логов"""
    if not user:
        return "Unknown"
    name = user.first_name or user.username or "NoName"
    return f"{name} ({user.id})"


# Константа для сообщений об ошибке
NO_SIGN_ERROR = "❗ Сначала выберите свой знак зодиака в меню"


# ===================== SUBSCRIPTION COMMANDS =====================

@router.message(F.text == "/subscription")
async def subscription_command(message: Message):
    """Обработчик команды /subscription"""
    logger.info(f"[SUBSCRIPTION_CMD] {u(message.from_user)}")
    await show_subscription_menu(message)


@router.callback_query(F.data == "subscription")
async def subscription_menu_callback(callback: CallbackQuery):
    """Меню управления подпиской"""
    logger.info(f"[SUBSCRIPTION_MENU] {u(callback.from_user)}")
    await show_subscription_menu_callback(callback)


async def show_subscription_menu(message: Message):
    """Показывает меню подписки"""
    await message.answer(
        "🔔 *Управление рассылкой*\n\n"
        "✨ *Настройте ежедневную рассылку гороскопов:*\n"
        "• ✅ Включить/выключить\n"
        "• ⏰ Выбрать удобное время\n"
        "• 📋 Посмотреть текущие настройки\n\n"
        "Выберите действие:",
        reply_markup=subscription_menu_kb()
    )


async def show_subscription_menu_callback(callback: CallbackQuery):
    """Показывает меню подписки через callback"""
    await callback.message.edit_text(
        "🔔 *Управление рассылкой*\n\n"
        "✨ *Настройте ежедневную рассылку гороскопов:*\n"
        "• ✅ Включить/выключить\n"
        "• ⏰ Выбрать удобное время\n"
        "• 📋 Посмотреть текущие настройки\n\n"
        "Выберите действие:",
        reply_markup=subscription_menu_kb()
    )
    await callback.answer()


# ===================== SUBSCRIBE ON/OFF =====================

@router.callback_query(F.data == "subscribe_on")
async def subscribe_on(callback: CallbackQuery):
    """Включение подписки"""
    logger.info(f"[SUBSCRIBE_ON] {u(callback.from_user)}")

    user_data = get_user(callback.from_user.id)

    if not user_data or not user_data.get("sign"):
        await callback.answer(NO_SIGN_ERROR, show_alert=True)
        return

    # Получаем текущую подписку
    subscription = get_subscription(callback.from_user.id)
    current_time = subscription['notification_time'] if subscription else "09:00"

    message_text = (
        f"✨ *Включение ежедневной рассылки*\n\n"
        f"📅 *Ваш знак:* {user_data['sign'].capitalize()}\n"
        f"⏰ *Время получения:* {current_time}\n\n"
        f"📬 Вы будете получать гороскопы каждый день в указанное время.\n\n"
        f"Хотите включить подписку?"
    )

    await callback.message.edit_text(
        message_text,
        reply_markup=subscribe_confirm_kb(current_time)
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_subscribe")
async def confirm_subscribe(callback: CallbackQuery):
    """Подтверждение включения подписки"""
    logger.info(f"[CONFIRM_SUBSCRIBE] {u(callback.from_user)}")

    # Включаем подписку
    update_subscription(callback.from_user.id, is_subscribed=True)

    user_data = get_user(callback.from_user.id)
    subscription = get_subscription(callback.from_user.id)

    message_text = format_subscription_message(user_data, subscription)

    await callback.message.edit_text(
        message_text,
        reply_markup=subscription_info_kb(has_subscription=True)
    )
    await callback.answer()


@router.callback_query(F.data == "subscribe_off")
async def subscribe_off(callback: CallbackQuery):
    """Отключение подписки"""
    logger.info(f"[SUBSCRIBE_OFF] {u(callback.from_user)}")

    await callback.message.edit_text(
        "❌ *Отключение рассылки*\n\n"
        "Вы уверены, что хотите отписаться от ежедневных гороскопов?",
        reply_markup=unsubscribe_confirm_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_unsubscribe")
async def confirm_unsubscribe(callback: CallbackQuery):
    """Подтверждение отписки"""
    logger.info(f"[CONFIRM_UNSUBSCRIBE] {u(callback.from_user)}")

    update_subscription(callback.from_user.id, is_subscribed=False)

    await callback.message.edit_text(
        "📭 *Вы отписались от рассылки*\n\n"
        "Ежедневные гороскопы больше не будут приходить.\n"
        "Вы можете включить их снова в любой момент.",
        reply_markup=back_to_menu_kb()
    )
    await callback.answer()


# ===================== MY SUBSCRIPTION =====================

@router.callback_query(F.data == "my_subscription")
async def my_subscription(callback: CallbackQuery):
    """Информация о текущей подписке"""
    logger.info(f"[MY_SUBSCRIPTION] {u(callback.from_user)}")

    user_data = get_user(callback.from_user.id)
    subscription = get_subscription(callback.from_user.id)

    if not user_data or not user_data.get("sign"):
        await callback.answer(NO_SIGN_ERROR, show_alert=True)
        return

    if not subscription or not subscription.get("is_subscribed"):
        # Нет активной подписки
        message_text = (
            "📭 *У вас нет активной подписки*\n\n"
            f"✨ *Ваш знак:* {user_data['sign'].capitalize()}\n\n"
            "Включите ежедневную рассылку гороскопов, "
            "чтобы получать их автоматически каждое утро."
        )
        markup = subscription_info_kb(has_subscription=False)
    else:
        # Показываем информацию о подписке
        message_text = format_subscription_message(user_data, subscription)
        markup = subscription_info_kb(has_subscription=True)

    await callback.message.edit_text(message_text, reply_markup=markup)
    await callback.answer()


# ===================== CHANGE TIME =====================

@router.callback_query(F.data == "change_time")
async def change_time(callback: CallbackQuery):
    """Изменение времени рассылки"""
    logger.info(f"[CHANGE_TIME] {u(callback.from_user)}")

    user_data = get_user(callback.from_user.id)

    if not user_data or not user_data.get("sign"):
        await callback.answer(NO_SIGN_ERROR, show_alert=True)
        return

    subscription = get_subscription(callback.from_user.id)
    current_time = subscription['notification_time'] if subscription else "09:00"

    await callback.message.edit_text(
        f"⏰ *Изменение времени рассылки*\n\n"
        f"📅 Текущий знак: *{user_data['sign'].capitalize()}*\n"
        f"🕐 Текущее время: *{current_time}*\n\n"
        "Выберите новое время получения гороскопа (МСК):",
        reply_markup=time_selection_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_time:"))
async def set_notification_time(callback: CallbackQuery):
    """Установка времени рассылки"""
    try:
        # Получаем время в формате "HH:MM"
        time_str = callback.data.replace("set_time:", "")

        # Проверяем формат времени
        if ":" not in time_str:
            # Если пришло только "07", добавляем ":00"
            time_str = f"{time_str}:00"

        logger.info(f"[SET_TIME] {u(callback.from_user)} → {time_str}")

        user_data = get_user(callback.from_user.id)

        if not user_data or not user_data.get("sign"):
            await callback.answer("❗ Сначала выберите свой знак зодиака", show_alert=True)
            return

        # Обновляем время в подписке
        update_subscription(callback.from_user.id, notification_time=time_str)

        subscription = get_subscription(callback.from_user.id)

        if subscription and subscription.get("is_subscribed"):
            # Подписка уже активна
            message_text = format_subscription_message(user_data, subscription)
            markup = subscription_info_kb(has_subscription=True)
        else:
            # Предлагаем включить подписку
            message_text = (
                f"⏰ *Время установлено:* {time_str}\n\n"
                f"📅 *Ваш знак:* {user_data['sign'].capitalize()}\n\n"
                "Хотите включить ежедневную рассылку гороскопов на это время?"
            )
            markup = subscribe_confirm_kb(time_str)

        await callback.message.edit_text(message_text, reply_markup=markup)

    except Exception as e:
        logger.error(f"[SET_TIME_ERROR] Invalid time format: {callback.data} - {e}")
        await callback.answer("❌ Неверный формат времени", show_alert=True)
    finally:
        await callback.answer()


@router.callback_query(F.data == "unsubscribe")
async def unsubscribe(callback: CallbackQuery):
    """Отписка от рассылки"""
    logger.info(f"[UNSUBSCRIBE] {u(callback.from_user)}")
    await subscribe_off(callback)