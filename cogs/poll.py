import discord
from discord.ext import commands
from collections import defaultdict
import asyncio

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {}

    @commands.command(name="createPoll")
    async def create_poll(self, ctx, max_votes: int, *, options: str):
        """
        Cria uma enquete.
        Uso: !createPoll <max_votos_por_pessoa> "Opção 1, Opção 2, Opção 3"
        """
        await ctx.message.delete()

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
            "options": {reactions[i]: {"text": opt, "votes": set()} for i, opt in enumerate(options_list)},
            "max_votes": max_votes,
        }

        embed = discord.Embed(title=f"📊 **Enquete Criada por {ctx.author.display_name}**", color=discord.Color.gold())
        description = "\n".join([f"{reactions[i]} **{opt}**" for i, opt in enumerate(options_list)])
        embed.description = description
        embed.set_footer(text=f"Máximo de {max_votes} votos por pessoa.")

        poll_message = await ctx.send(embed=embed)
        for i in range(len(options_list)):
            await poll_message.add_reaction(reactions[i])

        self.active_polls[poll_message.id] = poll_data

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

    async def update_poll_message(self, message):
        if message.id not in self.active_polls:
            return

        poll = self.active_polls[message.id]
        total_votes = sum(len(opt["votes"]) for opt in poll["options"].values())
        embed = discord.Embed(title=f"📊 **Enquete Criada por {poll['author'].display_name}**", color=discord.Color.gold())

        description = ""
        for emoji, data in poll["options"].items():
            votes = len(data["votes"])
            percentage = (votes / total_votes * 100) if total_votes > 0 else 0
            bar = "🟩" * int(percentage / 10) + "⬜" * (10 - int(percentage / 10))
            description += f"{emoji} **{data['text']}** - `{votes}` votos ({percentage:.1f}%)\n{bar}\n\n"
        
        embed.description = description
        embed.set_footer(text=f"Máximo de {poll['max_votes']} votos por pessoa.")
        await message.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(Poll(bot))
