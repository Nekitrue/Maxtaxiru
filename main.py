import asyncio
import json

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.types import WebAppInfo, MenuButtonWebApp

# ================= НАСТРОЙКИ =================

API_TOKEN = "8200947498:AAHkXrN4ypCsRwtBCS1CJGfOiSW1R8Zf-0s"
ADMIN_ID = 7778609997

WEBAPP_URL = "https://nekitrue.github.io/Maxtaxiru/"

# =============================================

# Инициализация бота
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode="Markdown")
)

dp = Dispatcher()

# Функция для установки кнопки меню (Menu Button), которая видна ВСЕГДА
async def set_main_menu(bot: Bot):
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="ПОЕХАЛИ",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    )

# ---------- /start ----------
@dp.message(CommandStart())
async def start(message: types.Message):
    # Создаем клавиатуру с кнопкой "ПОЕХАЛИ"
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(
                    text="ПОЕХАЛИ",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ],
        resize_keyboard=True,
        persistent=True
    )

    await message.answer(
        "🚕 *Такси MAX приветствует вас!*\n\n"
        "Кнопка заказа теперь всегда доступна в меню слева или на клавиатуре 👇",
        reply_markup=keyboard
    )


# ---------- ПРИЁМ ДАННЫХ ИЗ WEB APP ----------
@dp.message(F.web_app_data.data)
async def handle_webapp_data(message: types.Message):
    try:
        # Парсим JSON данные из Web App
        data = json.loads(message.web_app_data.data)

        # Формируем текст для администратора (включая новые поля: Класс и Фото)
        order_text = (
            f"🚕 *НОВЫЙ ЗАКАЗ!*\n"
            f"━━━━━━━━━━━━━━\n"
            f"🏙 *Город:* {data.get('city')}\n"
            f"🚘 *Класс:* {data.get('car_class', 'Эконом')}\n"
            f"📍 *Откуда:* {data.get('from')}\n"
            f"🏁 *Куда:* {data.get('to')}\n"
            f"🛑 *Остановки:* {data.get('inter')}\n"
            f"💬 *Комментарий:* {data.get('comment') or 'Нет'}\n"
            f"📷 *Фото:* {data.get('has_photo')}\n"
            f"💰 *Цена:* {data.get('price')} ₽\n"
            f"💳 *Оплата:* {data.get('pay')}\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 *Клиент:* @{message.from_user.username or 'скрыт'}\n"
            f"🆔 *ID:* `{message.from_user.id}`"
        )

        # Отправка администратору
        await bot.send_message(ADMIN_ID, order_text)

        # Подтверждение пользователю
        await message.answer(
            "✅ *Заказ принят!*\n"
            "Ожидайте, водитель скоро свяжется с вами 🚗"
        )

    except Exception as e:
        print(f"Ошибка обработки данных: {e}")
        await bot.send_message(
            ADMIN_ID,
            f"❌ *Ошибка обработки заказа:*\n`{e}`"
        )


# ---------- ЗАПУСК ----------
async def main():
    # Удаляем вебхуки и настраиваем кнопку меню
    await bot.delete_webhook(drop_pending_updates=True)
    await set_main_menu(bot)

    print("🤖 Бот запущен. Кнопка 'ПОЕХАЛИ' активна.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
