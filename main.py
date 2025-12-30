import json
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart

# Вставьте сюда ваши данные аккуратно (в кавычках)
API_TOKEN = '8200947498:AAHkXrN4ypCsRwtBCS1CJGfOiSW1R8Zf-0s'
ADMIN_ID = 7778609997

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("✅ Связь установлена! Бот работает. Ожидаю заказы из Web App.")

@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        order_card = (
            f"🚕 НОВЫЙ ЗАКАЗ!\n"
            f"📍 Откуда: {data.get('from')}\n"
            f"🏁 Куда: {data.get('to')}\n"
            f"🛑 Остановка: {data.get('inter')}\n"
            f"💰 Цена: {data.get('price')} ₽\n"
            f"💳 Оплата: {data.get('pay')}\n"
            f"💬 Коммент: {data.get('comment')}"
        )
        await bot.send_message(chat_id=ADMIN_ID, text=order_card)
        await message.answer("✅ Заказ принят! Водитель свяжется с вами.")
    except Exception as e:
        await bot.send_message(chat_id=ADMIN_ID, text=f"❌ Ошибка данных: {e}")

async def main():
    print("Приемник запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
