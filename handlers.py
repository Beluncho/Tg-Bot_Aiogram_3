
from aiogram.types import Message, BotCommand, CallbackQuery
from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
from libs import get_ai_response, get_user_history, clear_user_history, SYSTEM_PROMPT

router = Router()


def kb_clear_memory():
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🗑️ Очистить память", callback_data="clear_memory")
        ]]
    )


@router.callback_query(F.data == "clear_memory")
async def handle_clear_callback(callback: CallbackQuery):
    clear_user_history(callback.from_user.id)
    await callback.answer("История очищена ✅")
    await callback.message.delete()


@router.message(Command('start'))
async def cmd_start(message: Message):
    clear_user_history(message.from_user.id)
    await message.answer(
        "🌟 Здравствуй, путник!\n\n"
        "Я поэт-консультант по игре Манчкин.\n"
        "Спрашивай о правилах - отвечу стихами,\n"
        "Словно Есенин над березовой Русью.\n\n"
        "Примеры вопросов:\n"
        "• Как победить монстра?\n"
        "• Что такое класс Воина?\n"
        "• Как получить уровень?"
    )


@router.message(F.text)
async def handle_dialog(message: Message):
    user_id = message.from_user.id
    user_query = message.text.strip()

    logging.info(f"Поэтический запрос от {user_id}: {user_query}")

    # Получаем историю
    history = get_user_history(user_id)

    # Формируем историю для AI
    history_messages = []
    for exchange in history:
        history_messages.append({"role": "user", "content": exchange["user"]})
        history_messages.append({"role": "assistant", "content": exchange["assistant"]})

    # Получаем ответ в стихах
    response = await get_ai_response(
        system=SYSTEM_PROMPT,
        user_query=user_query,
        history=history_messages,
        temp=0.8  # Для стихов повыше температура
    )

    await message.answer(response)

    # Кнопка очистки
    if len(history) > 0:
        await message.answer(
            "✨ Задай новый вопрос или очисти память ✨",
            reply_markup=kb_clear_memory()
        )

    # Сохраняем в историю
    history.append({
        "user": user_query,
        "assistant": response
    })