from aiogram import executor

from handlers.default_handlers import best_deal_handler, high_price_handler, low_price_handler, other_cmd, history_cmd
from loader import dp

other_cmd.register_handler_other_cmd(dp)
low_price_handler.register_handler_low_price(dp)
high_price_handler.register_handler_high_price(dp)
best_deal_handler.register_handler_bestdeal(dp)
history_cmd.register_handler_history(dp)

if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
