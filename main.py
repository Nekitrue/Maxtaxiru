import asyncio
import json

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties

# ================= НАСТРОЙКИ =================

API_TOKEN = "8200947498:AAHkXrN4ypCsRwtBCS1CJGfOiSW1R8Zf-0s"
ADMIN_ID = 7778609997

WEBAPP_URL = "https://nekitrue.github.io/Maxtaxiru/"

# =============================================


# Инициализация бота (aiogram 3.7+)
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode="Markdown")
)

dp = Dispatcher()


# ---------- /start ----------
@dp.message(CommandStart())
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(
                    text="🚖 Заказать такси",
                    web_app=types.WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "🚕 *Такси MAX приветствует вас!*\n\n"
        "Нажмите кнопку ниже, чтобы оформить заказ 👇",
        reply_markup=keyboard
    )


# ---------- ПРИЁМ ДАННЫХ ИЗ WEB APP ----------
@dp.message(F.web_app_data.data)
async def handle_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)

        order_text = (
            f"🚕 *НОВЫЙ ЗАКАЗ!*\n"
            f"━━━━━━━━━━━━━━\n"
            f"🏙 *Город:* {data.get('city')}\n"
            f"📍 *Откуда:* {data.get('from')}\n"
            f"🏁 *Куда:* {data.get('to')}\n"
            f"🛑 *Остановки:* {data.get('inter')}\n"
            f"💬 *Комментарий:* {data.get('comment') or 'Нет'}\n"
            f"💰 *Цена:* {data.get('price')} ₽\n"
            f"💳 *Оплата:* {data.get('pay')}\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 *Клиент:* @{message.from_user.username or 'скрыт'}\n"
            f"🆔 *ID:* `{message.from_user.id}`"
        )

        # Отправка админу
        await bot.send_message(ADMIN_ID, order_text)

        # Ответ клиенту
        await message.answer(
            "✅ *Заказ принят!*\n"
            "Ожидайте, водитель скоро свяжется с вами 🚗"
        )

    except Exception as e:
        await bot.send_message(
            ADMIN_ID,
            f"❌ *Ошибка обработки заказа:*\n`{e}`"
        )


# ---------- ЗАПУСК ----------
async def main():
    # 🔥 ВАЖНО: удаляем webhook, чтобы не было конфликта getUpdates
    await bot.delete_webhook(drop_pending_updates=True)

    print("🤖 Бот запущен и ждёт заказы")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
