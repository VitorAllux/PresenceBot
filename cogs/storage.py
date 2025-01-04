import asyncpg
import os
from datetime import datetime, timedelta

class Storage:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")

    async def save_presence(self, participants):
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        insert_query = """
        INSERT INTO public.presences (timestamp, participant)
        VALUES ($1, $2);
        """
        async with asyncpg.create_pool(self.db_url, min_size=1, max_size=10) as pool:
            async with pool.acquire() as conn:
                for participant in participants:
                    await conn.execute(insert_query, timestamp, participant)

    async def get_presences_last_week(self):
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        select_query = """
        SELECT id, timestamp, participant
        FROM public.presences
        WHERE timestamp >= $1
        ORDER BY timestamp DESC;
        """
        async with asyncpg.create_pool(self.db_url, min_size=1, max_size=10) as pool:
            async with pool.acquire() as conn:
                rows = await conn.fetch(select_query, one_week_ago)
                return [
                    {
                        "id": row["id"],
                        "timestamp": row["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                        "participant": row["participant"],
                    }
                    for row in rows
                ]
