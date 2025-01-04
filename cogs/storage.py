import asyncpg
import os
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

class Storage:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")

    async def save_presence(self, participants):
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        insert_query = """
        INSERT INTO public.presences (timestamp, participant)
        VALUES ($1, $2);
        """
        try:
            async with asyncpg.create_pool(self.db_url) as pool:
                async with pool.acquire() as conn:
                    for participant in participants:
                        await conn.execute(insert_query, timestamp, participant)
                        logging.info(f"Presença salva: {timestamp}, {participant}")
        except Exception as e:
            logging.error(f"Erro ao salvar presença: {e}")
            raise

    async def get_presences_last_week(self):
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        select_query = """
        SELECT id, timestamp, participant
        FROM public.presences
        WHERE timestamp >= $1
        ORDER BY timestamp DESC;
        """
        try:
            async with asyncpg.create_pool(self.db_url) as pool:
                async with pool.acquire() as conn:
                    rows = await conn.fetch(select_query, one_week_ago)
                    logging.info(f"Presenças recuperadas: {len(rows)}")
                    return [
                        {
                            "id": row["id"],
                            "timestamp": row["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                            "participant": row["participant"],
                        }
                        for row in rows
                    ]
        except Exception as e:
            logging.error(f"Erro ao buscar presenças: {e}")
            raise
