import logging
import asyncio
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot, Dispatcher
import os
from dotenv import load_dotenv
import handlers


# Логирование
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('bot.log', encoding='utf-8'),
                              logging.StreamHandler()])

load_dotenv()

# Прокси
PROXY_URL = os.getenv('PROXY_URL')

# Создаём сессию с прокси
session = AiohttpSession(proxy=PROXY_URL)

# Передаём сессию боту (ЭТО ГЛАВНОЕ!)
bot = Bot(token=os.getenv('TELEGRAM_TOKEN'), session=session)

dp = Dispatcher()
dp.include_routers(handlers.router,)


async def main():
    try:
        logging.info("Запуск бота...")
        await dp.start_polling(bot)
    finally:
        logging.info("Остановка бота...")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
