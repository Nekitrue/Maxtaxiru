import json
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart

# ДАННЫЕ ДЛЯ СВЯЗИ
API_TOKEN = '8200947498:AAHkXrN4ypCsRwtBCS1CJGfOiSW1R8Zf-0s'
ADMIN_ID = 7778609997 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("🚕 Такси MAX приветствует вас! Используйте меню для заказа.")

@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    try:
        # Распаковка данных из HTML
        data = json.loads(message.web_app_data.data)
        
        order_text = (
            f"🚕 **НОВЫЙ ЗАКАЗ!**\n"
            f"━━━━━━━━━━━━━━\n"
            f"📍 **ОТКУДА:** {data.get('from')}\n"
            f"🏁 **КУДА:** {data.get('to')}\n"
            f"🛑 **ОСТАНОВКИ:** {data.get('inter')}\n"
            f"💰 **ЦЕНА:** {data.get('price')} ₽\n"
            f"💳 **ОПЛАТА:** {data.get('pay')}\n"
            f"💬 **КОММЕНТ:** {data.get('comment') or 'Нет'}\n"
            f"🏙 **ГОРОД:** {data.get('city')}\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 **КЛИЕНТ:** @{message.from_user.username or 'скрыт'}"
        )
        
        # Отправка вам
        await bot.send_message(chat_id=ADMIN_ID, text=order_text, parse_mode="Markdown")
        # Ответ клиенту
        await message.answer("✅ **Заказ принят!** Водитель свяжется с вами.")
        
    except Exception as e:
        await bot.send_message(chat_id=ADMIN_ID, text=f"❌ Ошибка: {e}")

async def main():
    print("Сервер запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
