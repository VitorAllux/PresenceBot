import asyncpg
import os
from datetime import datetime, timedelta


class DatabaseService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")

    async def save_presence(self, participants):
        query = """
        INSERT INTO public.presences (timestamp, participant)
        VALUES ($1, $2);
        """
        timestamp = datetime.utcnow()
        async with asyncpg.create_pool(self.db_url) as pool:
            async with pool.acquire() as conn:
                for participant in participants:
                    await conn.execute(query, timestamp, participant)

    async def get_presences(self, days):
        query = """
        SELECT id, timestamp, participant
        FROM public.presences
        WHERE timestamp >= $1
        ORDER BY timestamp DESC;
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        async with asyncpg.create_pool(self.db_url) as pool:
            async with pool.acquire() as conn:
                rows = await conn.fetch(query, cutoff_date)
                return [
                    {"id": row["id"], "timestamp": row["timestamp"], "participant": row["participant"]}
                    for row in rows
                ]
