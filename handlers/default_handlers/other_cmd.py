from aiogram import types, Dispatcher
from aiogram.types import ParseMode
from loguru import logger

from keyboards.reply.default_buttons import default_buttons
from loader import dp


@dp.message_handler(commands='help')
async def cmd_help(message: types.Message):
    logger.info(f"user_id - {message['from']['id']}, command_name - {message.text}")
    await message.answer("Возможности и команды hotel_bot."
                         "\nКоманды бота:"
                         "\n/start - Запускает бота и выводит доступные команды."
                         '\n/help - Выводит подробную информацию по боту и его функционалу. '
                         '\n/lowprice - Подбирает самые дешевые предложения в указанном городе.'
                         '\n/highprice - Подбирает самые дорогие отели в указанном городе'
                         '\n/bestdeal - Подбирает наилучшие предложения согласно выбранным параметрам.'
                         '\n/history - Показывает историю поиска.'
                         )


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    logger.info(f"user_id - {message['from']['id']}, command_name - {message.text}")
    await message.answer("Приветствую Вас, я бот для поиска отелей."
                         "\nВыберите необходимое действие.", reply_markup=default_buttons())


@dp.message_handler(commands='hello_world')
async def cmd_world(message: types.Message):
    logger.info(f"user_id - {message['from']['id']}, command_name - {message.text}")
    star = '&#9733;'
    await message.answer(f'{star * 3} <b>Hello world!</b> {star * 3}', parse_mode=ParseMode.HTML)


@dp.message_handler(commands='photo')
async def cmd_photo(message: types.Message):
    logger.info(f"user_id - {message['from']['id']}, command_name - {message.text}")
    photo = await message.answer_photo(photo='AgACAgQAAxkDAAIPfWM0_TFD-v0mwzRJytUAAX9'
                                             'QZMx-GQACr64xG7p2rVGVvd5kEAcp4QEAAwIAA20AAyoE')


@dp.message_handler(text='Привет')
async def cmd_hi(message: types.Message):
    logger.info(f"user_id - {message['from']['id']}, command_name - {message.text}")
    await message.reply("Привет!")


def register_handler_other_cmd(dp: Dispatcher):
    dp.register_message_handler(cmd_help, commands='help')
    dp.register_message_handler(cmd_start, commands='start')
    dp.register_message_handler(cmd_world, commands='hello-world')
    dp.register_message_handler(cmd_photo, commands='photo')
    dp.register_message_handler(cmd_hi, text='Привет')
