import asyncio
import json
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.types import WebAppInfo, MenuButtonWebApp
from dotenv import load_dotenv

# ================= НАСТРОЙКИ =================
load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

WEBAPP_URL = "https://nekitrue.github.io/Maxtaxiru/"

if not API_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Проверьте файл .env")

# =============================================

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode="Markdown")
)

dp = Dispatcher()


async def set_main_menu(bot: Bot):
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="ПОЕХАЛИ",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    )


@dp.message(CommandStart())
async def start(message: types.Message):
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


@dp.message(F.web_app_data.data)
async def handle_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        print(f"📦 Получен заказ от {message.from_user.id}: {data}")

        order_text = (
            f"🚕 *НОВЫЙ ЗАКАЗ!*\n"
            f"━━━━━━━━━━━━━━\n"
            f"🏙 *Город:* {data.get('city', 'Не определён')}\n"
            f"🚘 *Класс:* {data.get('car_class', 'Эконом')}\n"
            f"📍 *Откуда:* {data.get('from', '—')}\n"
            f"🏁 *Куда:* {data.get('to', '—')}\n"
            f"🛑 *Остановки:* {data.get('inter', 'Нет')}\n"
            f"💬 *Комментарий:* {data.get('comment') or 'Нет'}\n"
            f"📷 *Фото:* {data.get('has_photo', 'Нет')}\n"
            f"💰 *Цена:* {data.get('price', '—')} ₽\n"
            f"💳 *Оплата:* {data.get('pay', '—')}\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 *Клиент:* @{message.from_user.username or 'скрыт'}\n"
            f"🆔 *ID:* `{message.from_user.id}`"
        )

        await bot.send_message(ADMIN_ID, order_text)

        await message.answer(
            "✅ *Заказ принят!*\n"
            "Ожидайте, водитель скоро свяжется с вами 🚗"
        )

    except Exception as e:
        print(f"❌ Ошибка обработки данных: {e}")
        await bot.send_message(ADMIN_ID, f"❌ *Ошибка обработки заказа:*\n`{e}`")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await set_main_menu(bot)
    print("🤖 Бот запущен. Кнопка 'ПОЕХАЛИ' активна.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
