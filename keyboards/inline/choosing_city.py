from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def choosing_city(cities: dict) -> InlineKeyboardMarkup:
    """
    Формирует инлайн кнопки с названиями городов нашедшиеся по запросу пользователя.

    :param cities: Словарь с данными полученный от RapidAPI
    :return: InlineKeyboardMarkup инлайн кнопки с названиями городов.
    """
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [InlineKeyboardButton(text=i_key, callback_data='next' + i_value) for i_key, i_value in
               cities.items()]
    keyboard.add(*buttons)
    return keyboard