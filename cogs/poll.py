import discord
import asyncio
from discord.ext import commands
from services.poll_storage import PollStorage

REACTIONS = [
    "🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯",
    "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹",
    "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"
]

class Poll(commands.Cog):
    def __init__(self, bot, storage):
        self.bot = bot
        self.storage = storage
        self.active_polls = {}

    @commands.Cog.listener()
    async def on_ready(self):
        if getattr(self.bot, "_polls_loaded", False):
            return
        self.bot._polls_loaded = True

        for p in await self.storage.load_active_polls():
            guild = self.bot.get_guild(p["guild_id"])
            if not guild:
                continue

            channel = guild.get_channel(p["channel_id"])
            if not channel:
                continue

            try:
                msg = await channel.fetch_message(p["message_id"])
            except discord.NotFound:
                continue

            author = guild.get_member(p["author_id"]) or await self.bot.fetch_user(p["author_id"])

            poll = {
                "author": author,
                "title": p["title"],
                "max_votes": p["max_votes"],
                "message": msg,
                "options": {e: {"text": d["text"], "votes": set()} for e, d in p["options"].items()}
            }

            for e, d in p["options"].items():
                for uid in d["votes"]:
                    user = guild.get_member(uid) or await self.bot.fetch_user(uid)
                    if user:
                        poll["options"][e]["votes"].add(user)

            self.active_polls[msg.id] = poll
            await self.update_poll_message(msg)

    @commands.command(name="createPoll")
    async def create_poll(self, ctx, max_votes: str, title: str, *, options: str):
        await ctx.message.delete()

        if not max_votes.isdigit() or int(max_votes) < 1:
            await ctx.send("❌ `BOT`: Número máximo de votos inválido!")
            return

        max_votes = int(max_votes)
        options_list = [o.strip() for o in options.split(",") if o.strip()]
        if len(options_list) < 2 or len(options_list) > len(REACTIONS):
            await ctx.send("❌ `BOT`: Informe entre 2 e 25 opções.")
            return

        poll = {
            "author": ctx.author,
            "title": title,
            "max_votes": max_votes,
            "options": {REACTIONS[i]: {"text": opt, "votes": set()} for i, opt in enumerate(options_list)},
            "message": None
        }

        embed = discord.Embed(
            title=f"📊 **{title}**",
            description=f"Criado por {ctx.author.display_name}\n\n",
            color=discord.Color.gold()
        )

        for i, opt in enumerate(options_list):
            embed.add_field(
                name=f"{REACTIONS[i]} {opt}",
                value="`[⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜] 0% (0 votos)`",
                inline=False
            )

        embed.set_footer(text=f"Máximo de {max_votes} votos por pessoa. Reaja para votar!")

        msg = await ctx.send(embed=embed)

        # Salva a enquete no banco antes de adicionar reações (corrigido aqui)
        await self.storage.create_poll({
            "message_id": msg.id,
            "channel_id": msg.channel.id,
            "guild_id": msg.guild.id,
            "author_id": ctx.author.id,
            "title": title,
            "options": {e: {"text": d["text"], "votes": []} for e, d in poll["options"].items()},
            "max_votes": max_votes
        })

        for i in range(len(options_list)):
            await msg.add_reaction(REACTIONS[i])

        poll["message"] = msg
        self.active_polls[msg.id] = poll

    @commands.command(name="endPoll")
    async def end_poll(self, ctx, message_id: int = None):
        await ctx.message.delete()

        for pid, poll in list(self.active_polls.items()):
            if poll["author"] == ctx.author and (message_id is None or pid == message_id):
                embed = discord.Embed(
                    title=f"📊 **Enquete Finalizada: {poll['title']}**",
                    description=f"Criado por {poll['author'].display_name}\n\n",
                    color=discord.Color.red()
                )

                for emoji, data in poll["options"].items():
                    embed.add_field(name=f"{emoji} {data['text']}", value=f"`{len(data['votes'])} votos`", inline=False)

                await poll["message"].edit(embed=embed)
                await ctx.send("✅ `BOT`: Enquete finalizada!")
                del self.active_polls[pid]
                await self.storage.end_poll(pid)
                return

        await ctx.send("❌ `BOT`: Nenhuma enquete sua encontrada.")

    @commands.command(name="helpPoll")
    async def help_poll(self, ctx):
        await ctx.message.delete()
        await ctx.send("```📊 Comandos de Enquete\n!createPoll <max_votos> \"Título\" \"Opção 1, Opção 2\" - cria.\n!endPoll [message_id] - finaliza.\n```")

    async def update_poll_message(self, message):
        poll = self.active_polls[message.id]
        total = sum(len(o["votes"]) for o in poll["options"].values())

        embed = discord.Embed(
            title=f"📊 **{poll['title']}**",
            description=f"Criado por {poll['author'].display_name}\n\n",
            color=discord.Color.gold()
        )

        for emoji, data in poll["options"].items():
            votes = len(data["votes"])
            pct = (votes / total * 100) if total else 0
            bar = "🟩" * int(pct / 10) + "⬜" * (10 - int(pct / 10))
            embed.add_field(name=f"{emoji} {data['text']}", value=f"`[{bar}] {pct:.1f}% ({votes} votos)`", inline=False)

        embed.set_footer(text=f"Máximo de {poll['max_votes']} votos por pessoa.")
        await message.edit(embed=embed)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or reaction.message.id not in self.active_polls:
            return

        poll = self.active_polls[reaction.message.id]
        if reaction.emoji not in poll["options"]:
            return

        user_votes = sum(1 for opt in poll["options"].values() if user in opt["votes"])
        if user_votes >= poll["max_votes"]:
            await reaction.message.remove_reaction(reaction.emoji, user)
            return

        poll["options"][reaction.emoji]["votes"].add(user)
        await self.storage.add_vote(reaction.message.id, user.id, reaction.emoji)
        await self.update_poll_message(reaction.message)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot or reaction.message.id not in self.active_polls:
            return

        poll = self.active_polls[reaction.message.id]
        if reaction.emoji not in poll["options"]:
            return

        poll["options"][reaction.emoji]["votes"].discard(user)
        await self.storage.remove_vote(reaction.message.id, user.id, reaction.emoji)
        await self.update_poll_message(reaction.message)

async def setup(bot):
    storage = PollStorage()
    await bot.add_cog(Poll(bot, storage))
