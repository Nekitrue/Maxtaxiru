import asyncio
import json
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import WebAppInfo, MenuButtonWebApp
from dotenv import load_dotenv

import database as db

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


# ---------- /start ----------
@dp.message(CommandStart())
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[
            types.KeyboardButton(
                text="ПОЕХАЛИ",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]],
        resize_keyboard=True,
        persistent=True
    )
    await message.answer(
        "🚕 *Такси MAX приветствует вас!*\n\n"
        "Кнопка заказа теперь всегда доступна в меню слева или на клавиатуре 👇",
        reply_markup=keyboard
    )


# ---------- /my — история заказов клиента ----------
@dp.message(Command("my"))
async def my_orders(message: types.Message):
    orders = await db.get_user_orders(message.from_user.id, limit=5)
    if not orders:
        await message.answer("📭 У вас ещё нет заказов.")
        return

    text = "🧾 *Ваши последние заказы:*\n\n"
    for o in orders:
        text += (
            f"*#{o['id']}* · {o['created_at'][:16]}\n"
            f"📍 {o['from_addr']} → {o['to_addr']}\n"
            f"🚘 {o['car_class']} · {o['price']} ₽ · _{o['status']}_\n"
            f"━━━━━━━━━━━━━━\n"
        )
    await message.answer(text)


# ---------- /stats — статистика для админа ----------
@dp.message(Command("stats"))
async def stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Команда доступна только администратору.")
        return

    s = await db.get_stats()
    await message.answer(
        f"📊 *Статистика сервиса*\n"
        f"━━━━━━━━━━━━━━\n"
        f"📦 Всего заказов: *{s['total']}*\n"
        f"🆕 Новых (в ожидании): *{s['new']}*\n"
        f"💰 Сумма всех заказов: *{s['total_sum']} ₽*\n"
    )


# ---------- Приём заказов из Mini App ----------
@dp.message(F.web_app_data.data)
async def handle_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        print(f"📦 Получен заказ от {message.from_user.id}: {data}")

        # 1. Сохраняем заказ в базу
        order_id = await db.create_order(
            data=data,
            user_id=message.from_user.id,
            username=message.from_user.username or "скрыт"
        )

        # 2. Уведомляем админа
        admin_text = (
            f"🚕 *НОВЫЙ ЗАКАЗ #{order_id}!*\n"
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
        await bot.send_message(ADMIN_ID, admin_text)

        # 3. Подтверждение клиенту
        await message.answer(
            f"✅ *Заказ #{order_id} принят!*\n"
            f"Ожидайте, водитель скоро свяжется с вами 🚗\n\n"
            f"_Посмотреть историю: /my_"
        )

    except Exception as e:
        print(f"❌ Ошибка обработки данных: {e}")
        await bot.send_message(ADMIN_ID, f"❌ *Ошибка обработки заказа:*\n`{e}`")


# ---------- Запуск ----------
async def main():
    await db.init_db()  # ← создаём таблицу при старте
    await bot.delete_webhook(drop_pending_updates=True)
    await set_main_menu(bot)
    print("🤖 Бот запущен. База данных готова.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
