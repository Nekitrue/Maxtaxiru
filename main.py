import asyncio
import json

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties

# ================= НАСТРОЙКИ =================

API_TOKEN = "8200947498:AAHkXrN4ypCsRwtBCS1CJGfOiSW1R8Zf-0s"
ADMIN_ID = 7778609997

# Убедитесь, что эта ссылка совпадает с вашим GitHub Pages
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
    # Установка синей кнопки (Menu Button) для этого пользователя
    await bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=types.MenuButtonWebApp(
            text="Заказать такси",
            web_app=types.WebAppInfo(url=WEBAPP_URL)
        )
    )

    # Обычная кнопка в чате для подстраховки
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
        "Синяя кнопка заказа теперь всегда доступна в углу меню 👇",
        reply_markup=keyboard
    )


# ---------- ПРИЁМ ДАННЫХ ИЗ WEB APP ----------
@dp.message(F.web_app_data.data)
async def handle_webapp_data(message: types.Message):
    try:
        # Распаковываем JSON от index.html
        data = json.loads(message.web_app_data.data)

        # Формируем сообщение для администратора (вас)
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

        # Отправка администратору
        await bot.send_message(ADMIN_ID, order_text)

        # Ответ клиенту (согласно вашему требованию)
        await message.answer(
            "✅ *Спасибо за заказ!*\n"
            "Водитель скоро свяжется с вами 🚗"
        )

    except Exception as e:
        # Уведомление об ошибке в лог и администратору
        await bot.send_message(ADMIN_ID, f"❌ Ошибка обработки: {e}")


async def main():
    print("Сервер запущен...")
    # Запуск бота в режиме polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
