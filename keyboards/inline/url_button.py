from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def url_button(data: list) -> InlineKeyboardMarkup:
    """
    Формирует инлайн кнопку с, ссылкой на страничку отеля.
    С полученного списка берется ID отеля для создания ссылки на страницу отеля

    :param data: Список с данными отеля полученный от RapidAPI.
    :return: InlineKeyboardMarkup
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Страничка отеля ↗', url=f'https://www.hotels.com/ho{data[1]}'))
    return keyboard