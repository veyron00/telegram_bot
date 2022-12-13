from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def need_photo_yes_or_no() -> InlineKeyboardMarkup:
    """
    Формирует инлайн кнопки с текстом ДА и НЕТ.
    При нажатии на одну из них отправляется callback_data, который обрабатывается хендлером.
    :return: InlineKeyboardMarkup
    """
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [InlineKeyboardButton(text='Да ✅', callback_data='yes'),
               InlineKeyboardButton(text='Нет ❎', callback_data='no')]
    keyboard.add(*buttons)
    return keyboard
