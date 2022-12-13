from aiogram import types
from aiogram.types import ReplyKeyboardMarkup


def default_buttons() -> ReplyKeyboardMarkup:
    """
    Формирует кнопки основных команд, и выводит их вместо клавиатуры.

    :return: ReplyKeyboardMarkup
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['/lowprice', '/highprice', '/bestdeal', '/history']
    keyboard.add(*buttons)
    return keyboard