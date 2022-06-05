from aiogram import Dispatcher
from loguru import logger

from data.config import ADMINS


async def on_startup_notify(dp: Dispatcher):
    """Отправка абминам сообщения, что бот запущен"""
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "Бот Запущен")

        except Exception as err:
            logger.exception(err)
