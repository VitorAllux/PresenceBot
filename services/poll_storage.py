# helpers ----------------------------------------------------
async def _pool(self):
    return asyncpg.create_pool(self.db_url, min_size=1, max_size=10)

# CRUD -------------------------------------------------------
async def create_poll(self, poll: Dict):
    sql = """
    INSERT INTO public.polls
        (message_id, channel_id, guild_id, author_id, title, options, max_votes)
    VALUES ($1,$2,$3,$4,$5,$6,$7)
    """
    async with (await self._pool()) as pool, pool.acquire() as conn:
        await conn.execute(
            sql,
            poll["message_id"],
            poll["channel_id"],
            poll["guild_id"],
            poll["author_id"],
            poll["title"],
            json.dumps({e: d["text"] for e, d in poll["options"].items()}),
            poll["max_votes"],
        )

async def end_poll(self, message_id: int):
    sql = "UPDATE public.polls SET active = FALSE WHERE message_id = $1"
    async with (await self._pool()) as pool, pool.acquire() as conn:
        await conn.execute(sql, message_id)
    sql = "DELETE FROM public.poll_votes WHERE poll_message_id = $1"
    async with (await self._pool()) as pool, pool.acquire() as conn:
        await conn.execute(sql, message_id)

async def add_vote(self, message_id: int, user_id: int, emoji: str):
    sql = """
    INSERT INTO public.poll_votes (poll_message_id, user_id, emoji)
    VALUES ($1,$2,$3)
    ON CONFLICT DO NOTHING
    """
    async with (await self._pool()) as pool, pool.acquire() as conn:
        await conn.execute(sql, message_id, user_id, emoji)

async def remove_vote(self, message_id: int, user_id: int, emoji: str):
    sql = """
    DELETE FROM public.poll_votes
    WHERE poll_message_id = $1 AND user_id = $2 AND emoji = $3
    """
    async with (await self._pool()) as pool, pool.acquire() as conn:
        await conn.execute(sql, message_id, user_id, emoji)

async def load_active_polls(self) -> List[Dict]:
    sql_polls = "SELECT * FROM public.polls WHERE active = TRUE"
    sql_votes = "SELECT * FROM public.poll_votes WHERE poll_message_id = ANY($1::bigint[])"
    async with (await self._pool()) as pool, pool.acquire() as conn:
        polls_rows = await conn.fetch(sql_polls)
        if not polls_rows:
            return []
        msg_ids = [r["message_id"] for r in polls_rows]
        votes_rows = await conn.fetch(sql_votes, msg_ids)

    polls = {}
    for row in polls_rows:
        polls[row["message_id"]] = {
            "message_id": row["message_id"],
            "channel_id": row["channel_id"],
            "guild_id": row["guild_id"],
            "author_id": row["author_id"],
            "title": row["title"],
            "max_votes": row["max_votes"],
            "options": {e: {"text": t, "votes": set()} for e, t in row["options"].items()},
        }

    for v in votes_rows:
        p = polls.get(v["poll_message_id"])
        if p and v["emoji"] in p["options"]:
            p["options"][v["emoji"]]["votes"].add(v["user_id"])
    return list(polls.values())
