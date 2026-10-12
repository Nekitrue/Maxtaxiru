import aiosqlite
from typing import Optional, List, Dict

DB_PATH = "taxi.db"


async def init_db():
    """Создаёт таблицу заказов, если её ещё нет."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                city TEXT,
                from_addr TEXT,
                to_addr TEXT,
                inter TEXT,
                car_class TEXT,
                price INTEGER,
                pay TEXT,
                comment TEXT,
                has_photo TEXT,
                status TEXT DEFAULT 'NEW',
                driver_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def create_order(data: dict, user_id: int, username: str) -> int:
    """Создаёт заказ, возвращает его ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO orders 
                (user_id, username, city, from_addr, to_addr, inter,
                 car_class, price, pay, comment, has_photo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            username,
            data.get('city', 'Не определён'),
            data.get('from', '—'),
            data.get('to', '—'),
            data.get('inter', 'Нет'),
            data.get('car_class', 'Эконом'),
            data.get('price', 0),
            data.get('pay', '—'),
            data.get('comment', 'Нет'),
            data.get('has_photo', 'Нет'),
        ))
        await db.commit()
        return cursor.lastrowid


async def get_order(order_id: int) -> Optional[Dict]:
    """Возвращает заказ по его ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def update_status(order_id: int, status: str, driver_id: Optional[int] = None):
    """Обновляет статус заказа (и водителя, если передан)."""
    async with aiosqlite.connect(DB_PATH) as db:
        if driver_id is not None:
            await db.execute(
                "UPDATE orders SET status = ?, driver_id = ? WHERE id = ?",
                (status, driver_id, order_id)
            )
        else:
            await db.execute(
                "UPDATE orders SET status = ? WHERE id = ?",
                (status, order_id)
            )
        await db.commit()


async def get_user_orders(user_id: int, limit: int = 10) -> List[Dict]:
    """Возвращает последние заказы пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_stats() -> Dict:
    """Возвращает статистику по заказам."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM orders")
        total = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM orders WHERE status = 'NEW'")
        new = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT SUM(price) FROM orders")
        total_sum = (await cursor.fetchone())[0] or 0

        return {"total": total, "new": new, "total_sum": total_sum}
