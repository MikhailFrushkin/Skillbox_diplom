from aiogram.utils.exceptions import (Unauthorized, InvalidQueryID, TelegramAPIError,
                                      CantDemoteChatCreator, MessageNotModified, MessageToDeleteNotFound,
                                      MessageTextIsEmpty, RetryAfter,
                                      CantParseEntities, MessageCantBeDeleted)
from loguru import logger

from loader import dp


@dp.errors_handler()
async def errors_handler(update, exception):
    """
    Обработака ошибок телеграма
    """

    if isinstance(exception, CantDemoteChatCreator):
        logger.error("Can't demote chat creator")
        return True

    if isinstance(exception, MessageNotModified):
        logger.error('Message is not modified')
        return True

    if isinstance(exception, MessageCantBeDeleted):
        logger.error('Message cant be deleted')
        return True

    if isinstance(exception, MessageToDeleteNotFound):
        logger.error('Message to delete not found')
        return True

    if isinstance(exception, MessageTextIsEmpty):
        logger.error('MessageTextIsEmpty')
        return True

    if isinstance(exception, Unauthorized):
        logger.error(f'Unauthorized: {exception}')
        return True

    if isinstance(exception, InvalidQueryID):
        logger.error(f'InvalidQueryID: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, TelegramAPIError):
        logger.error(f'TelegramAPIError: {exception} \nUpdate: {update}')
        return True
    if isinstance(exception, RetryAfter):
        logger.error(f'RetryAfter: {exception} \nUpdate: {update}')
        return True
    if isinstance(exception, CantParseEntities):
        logger.error(f'CantParseEntities: {exception} \nUpdate: {update}')
        return True

    logger.error(f'Update: {update} \n{exception}')
    return True
