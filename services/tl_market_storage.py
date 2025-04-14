import asyncpg
import os
from datetime import datetime

class TlMarketStorage:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")

    async def _pool(self):
        return asyncpg.create_pool(self.db_url, min_size=1, max_size=10)

    async def set_user_server(self, user_id, server_id):
        sql = """
        INSERT INTO tl_market_users (user_id, server_id)
        VALUES ($1, $2)
        ON CONFLICT (user_id) DO UPDATE SET server_id = EXCLUDED.server_id
        """
        async with (await self._pool()) as pool, pool.acquire() as conn:
            await conn.execute(sql, user_id, server_id)

    async def add_search(self, user_id, item_id, interval):
        sql = """
        INSERT INTO tl_market_searches (user_id, item_id, interval)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_id, item_id) DO UPDATE SET interval = EXCLUDED.interval
        """
        async with (await self._pool()) as pool, pool.acquire() as conn:
            await conn.execute(sql, user_id, item_id, interval)

    async def get_all_searches(self):
        sql = """
        SELECT s.user_id, u.server_id, s.item_id, s.interval, s.last_checked
        FROM tl_market_searches s
        JOIN tl_market_users u ON u.user_id = s.user_id
        """
        async with (await self._pool()) as pool, pool.acquire() as conn:
            return await conn.fetch(sql)

    async def update_last_checked(self, user_id, item_id):
        sql = """
        UPDATE tl_market_searches SET last_checked = NOW()
        WHERE user_id = $1 AND item_id = $2
        """
        async with (await self._pool()) as pool, pool.acquire() as conn:
            await conn.execute(sql, user_id, item_id)
