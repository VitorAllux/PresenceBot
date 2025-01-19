import discord
from discord.ext import commands
from collections import defaultdict
import asyncio

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {}

    @commands.command(name="createPoll")
    async def create_poll(self, ctx, max_votes: str, title: str, *, options: str):
        """
        Cria uma enquete.
        Uso: !createPoll <max_votos_por_pessoa> "Título da Enquete" "Opção 1, Opção 2, Opção 3"
        """
        await ctx.message.delete()

        if not max_votes.isdigit():
            await ctx.send("❌ `BOT`: O número máximo de votos deve ser um número inteiro válido!")
            return

        max_votes = int(max_votes)
        if max_votes < 1:
            await ctx.send("❌ `BOT`: O número máximo de votos deve ser pelo menos 1!")
            return

        options_list = [opt.strip() for opt in options.split(",") if opt.strip()]
        if len(options_list) < 2:
            await ctx.send("❌ `BOT`: A enquete deve ter pelo menos duas opções!")
            return

        reactions = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"]
        if len(options_list) > len(reactions):
            await ctx.send("❌ `BOT`: Número máximo de opções é 25!")
            return

        poll_data = {
            "author": ctx.author,
            "title": title,
            "options": {reactions[i]: {"text": opt, "votes": set()} for i, opt in enumerate(options_list)},
            "max_votes": max_votes,
            "message": None
        }

        embed = discord.Embed(title=f"📊 **{title}**", description=f"Criado por {ctx.author.display_name}\n\n", color=discord.Color.gold())
        for i, opt in enumerate(options_list):
            embed.add_field(name=f"{reactions[i]} {opt}", value="`[⠀⠀⠀⠀⠀⠀⠀] 0% (0 votos)`", inline=False)
        embed.set_footer(text=f"Máximo de {max_votes} votos por pessoa. Reaja para votar!")

        poll_message = await ctx.send(embed=embed)
        for i in range(len(options_list)):
            await poll_message.add_reaction(reactions[i])

        poll_data["message"] = poll_message
        self.active_polls[poll_message.id] = poll_data

    async def update_poll_message(self, message):
        if message.id not in self.active_polls:
            return

        poll = self.active_polls[message.id]
        total_votes = sum(len(opt["votes"]) for opt in poll["options"].values())
        embed = discord.Embed(title=f"📊 **{poll['title']}**", description=f"Criado por {poll['author'].display_name}\n\n", color=discord.Color.gold())

        for emoji, data in poll["options"].items():
            votes_count = len(data["votes"])
            percentage = (votes_count / total_votes * 100) if total_votes > 0 else 0
            bar = "🟩" * int(percentage / 10) + "⬜" * (10 - int(percentage / 10))
            embed.add_field(name=f"{emoji} {data['text']}", value=f"`[{bar}] {percentage:.1f}% ({votes_count} votos)`", inline=False)

        await message.edit(embed=embed)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or reaction.message.id not in self.active_polls:
            return

        poll = self.active_polls[reaction.message.id]
        if reaction.emoji not in poll["options"]:
            return

        total_votes = sum(len(opt["votes"]) for opt in poll["options"].values() if user in opt["votes"])
        if total_votes >= poll["max_votes"]:
            await reaction.message.remove_reaction(reaction.emoji, user)
            return

        poll["options"][reaction.emoji]["votes"].add(user)
        await self.update_poll_message(reaction.message)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot or reaction.message.id not in self.active_polls:
            return

        poll = self.active_polls[reaction.message.id]
        if reaction.emoji not in poll["options"]:
            return

        poll["options"][reaction.emoji]["votes"].discard(user)
        await self.update_poll_message(reaction.message)

async def setup(bot):
    await bot.add_cog(Poll(bot))
