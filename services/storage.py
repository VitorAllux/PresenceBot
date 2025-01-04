import asyncpg
import os
from datetime import datetime, timedelta


class Storage:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")

    async def save_presence(self, participants):
        timestamp = datetime.utcnow()
        query = """
        INSERT INTO public.presences (timestamp, participant)
        VALUES ($1, $2);
        """
        async with asyncpg.create_pool(self.db_url, min_size=1, max_size=10) as pool:
            async with pool.acquire() as conn:
                for participant in participants:
                    await conn.execute(query, timestamp, participant)

    async def get_presences(self, days):
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = """
        SELECT id, timestamp, participant
        FROM public.presences
        WHERE timestamp >= $1
        ORDER BY timestamp DESC;
        """
        async with asyncpg.create_pool(self.db_url, min_size=1, max_size=10) as pool:
            async with pool.acquire() as conn:
                rows = await conn.fetch(query, cutoff)
                return [
                    {"id": row["id"], "timestamp": row["timestamp"], "participant": row["participant"]}
                    for row in rows
                ]
            
    async def get_all_presences(self):
        query = """
        SELECT id, timestamp, participant
        FROM public.presences
        ORDER BY timestamp ASC;
        """
        async with asyncpg.create_pool(self.db_url, min_size=1, max_size=10) as pool:
            async with pool.acquire() as conn:
                rows = await conn.fetch(query)
                return [
                    {"id": row["id"], "timestamp": row["timestamp"], "participant": row["participant"]}
                    for row in rows
                ]

