import json
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart

# --- ЗАПОЛНИТЕ ЭТИ ДАННЫЕ ---
API_TOKEN = '8200947498:AAHkXrN4ypCsRwtBCS1CJGfOiSW1R8Zf-0s' # Возьмите у @BotFather
ADMIN_ID = 7778609997         # Ваш ID (узнайте у @userinfobot)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Приветствие при старте
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в Такси MAX! Оформляйте заказ через кнопку в меню.")

# ПРИЕМ ДАННЫХ ИЗ ПРИЛОЖЕНИЯ
@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    # Распаковываем JSON от вашего интерфейса 1.2.7
    data = json.loads(message.web_app_data.data)
    
    # Собираем карточку заказа для вас
    order_card = (
        f"🚕 **НОВЫЙ ЗАКАЗ!**\n"
        f"━━━━━━━━━━━━━━\n"
        f"📍 Откуда: {data.get('from', '—')}\n"
        f"🏁 Куда: {data.get('to', '—')}\n"
        f"🛑 Остановка: {data.get('inter', 'нет')}\n"
        f"💰 Цена: {data.get('price')} ₽\n"
        f"💳 Оплата: {data.get('pay', 'Нал')}\n"
        f"💬 Коммент: {data.get('comment', 'нет')}\n"
        f"━━━━━━━━━━━━━━\n"
        f"👤 Клиент: @{message.from_user.username or 'скрыт'}\n"
        f"🆔 ID: `{message.from_user.id}`"
    )

    # 1. Отправляем карточку вам (админу)
    await bot.send_message(chat_id=ADMIN_ID, text=order_card, parse_mode="Markdown")
    
    # 2. Отвечаем клиенту
    await message.answer("✅ **Заказ принят!**\nВодитель свяжется с вами в ближайшее время.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
