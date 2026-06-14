from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import logging
from collections import deque
from typing import Optional, List, Dict

load_dotenv()
PROXYAPI_KEY = os.getenv("PROXYAPI_KEY")

# Словарь для хранения истории (с ограничением!)
user_histories: Dict[int, deque] = {}
HISTORY_LIMIT = 5  # Для стихов достаточно 5 последних обменов

# Специальный системный промпт для поэта-манчкиноведа
SYSTEM_PROMPT = """Ты — поэт-консультант по игре Манчкин.
Твоя особенность: отвечаешь только стихами в стиле Сергея Есенина.
Сочетай лирику с правилами игры Манчкин.
Если не знаешь ответа — напиши стих о том, что ответ неизвестен.
Используй есенинские образы: березы, месяц, изба, поля, русская природа,
но применяй их к игровым ситуациям (уровни, сокровища, монстры)."""


async def get_ai_response(
        system: str,
        user_query: str,
        history: Optional[List[Dict[str, str]]] = None,
        model: str = 'gpt-4o-mini',
        temp: float = 0.7  # Для стихов повыше температура (0.7-0.9)
) -> str:
    """
    Запрос к OpenAI с поддержкой истории и стихов Есенина
    """
    # Формируем сообщения
    messages = [{"role": "system", "content": system}]

    # Добавляем историю диалога
    if history:
        messages.extend(history)

    # Формируем запрос с указанием стиля
    poetic_query = f"""Отвечай строго в стихотворной форме, подражая Сергею Есенину.
Используй его лексику, ритм, образы.
Вопрос пользователя: {user_query}

Твой поэтический ответ:"""

    messages.append({"role": "user", "content": poetic_query})

    try:
        client = AsyncOpenAI(
            api_key=PROXYAPI_KEY,
            base_url="https://openai.api.proxyapi.ru/v1"
        )

        response = await client.chat.completions.create(
            model=model,
            messages=messages,  # type: ignore
            temperature=temp,
            max_tokens=500  # Для стихов достаточно
        )

        return response.choices[0].message.content

    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return "Бела береза под моим окном,\nНо ответ неведом мне в полночь серебром.\nПовтори свой вопрос, добрый человек,\nСловно месяц встанет ответ через век."

# Функция для работы с историей в основном файле
def get_user_history(user_id: int) -> deque:
    """Получить историю пользователя"""
    if user_id not in user_histories:
        user_histories[user_id] = deque(maxlen=HISTORY_LIMIT)
    return user_histories[user_id]


def clear_user_history(user_id: int):
    """Очистить историю пользователя"""
    if user_id in user_histories:
        user_histories[user_id].clear()