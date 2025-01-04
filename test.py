import asyncpg
import os

async def test_connection():
    db_url = os.getenv("DATABASE_URL")
    try:
        conn = await asyncpg.connect(db_url)
        print("Conexão estabelecida com sucesso!")
        await conn.close()
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")

import asyncio
asyncio.run(test_connection())