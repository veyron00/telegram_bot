from aiogram import types, Dispatcher
from loguru import logger

from database.connect_db import view_history
from loader import dp


@dp.message_handler(commands='history')
async def history_view(message: types.Message):
    data = view_history(message)
    if len(data) > 0:
        logger.info(f"user_id - {message['from']['id']}, command_name - {message.text}")
        for i in data:
            await message.answer(f'Команда - /{i[0]},'
                                 f'\nЗапрос - {i[1]},'
                                 f'\nДата поиска - {i[2]}, '
                                 f'\nНайденные результаты:'
                                 f'\n{i[3]}')

    else:
        await message.answer('Истории поиска не обнаружено.')
        logger.error(f"user_id - {message['from']['id']}, NO SEARCH HISTORY")


def register_handler_history(dp: Dispatcher):
    dp.register_message_handler(history_view, commands='history')
