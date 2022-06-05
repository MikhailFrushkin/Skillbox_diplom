from aiogram import executor
from loguru import logger
from loader import dp
import handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dp):
    """Установка стандартных команд, отправка сообщению админу и запуск бота"""
    logger.add('logs/info.log', format='{time} {level} {message}', level='INFO')
    logger.info('Бот запускается')
    await set_default_commands(dp)
    await on_startup_notify(dp)


async def on_shutdown(dp):
    """Остановка бота"""

    await dp.storage.close()
    await dp.storage.wait_closed()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)

