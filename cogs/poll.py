import discord
from discord.ext import commands
from collections import defaultdict
import asyncio

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {}

    @commands.command(name="createPoll")
    async def create_poll(self, ctx, max_votes: int, title: str, *, options: str):
        """
        Cria uma enquete.
        Uso: !createPoll <max_votos_por_pessoa> "Título da Enquete" "Opção 1, Opção 2, Opção 3"
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
            "title": title,
            "options": {reactions[i]: {"text": opt, "votes": set()} for i, opt in enumerate(options_list)},
            "max_votes": max_votes,
        }

        embed = discord.Embed(title=f"📊 **{title}**", description=f"Criado por {ctx.author.display_name}\n\n", color=discord.Color.gold())
        for i, opt in enumerate(options_list):
            embed.add_field(name=f"{reactions[i]} {opt}", value="⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ (0%)", inline=False)
        embed.set_footer(text=f"Máximo de {max_votes} votos por pessoa. Reaja para votar!")

        poll_message = await ctx.send(embed=embed)
        for i in range(len(options_list)):
            await poll_message.add_reaction(reactions[i])

        self.active_polls[poll_message.id] = poll_data

    @commands.command(name="endPoll")
    async def end_poll(self, ctx, message_id: int):
        """Finaliza uma enquete e exibe os resultados."""
        if message_id not in self.active_polls:
            await ctx.send("❌ `BOT`: ID de enquete inválido!")
            return

        poll = self.active_polls.pop(message_id)
        total_votes = sum(len(opt["votes"]) for opt in poll["options"].values())
        embed = discord.Embed(title=f"📊 **{poll['title']} - ENCERRADO**", description=f"Criado por {poll['author'].display_name}\n\n", color=discord.Color.red())

        for emoji, data in poll["options"].items():
            votes = len(data["votes"])
            percentage = (votes / total_votes * 100) if total_votes > 0 else 0
            bar = "🟩" * int(percentage / 10) + "⬜" * (10 - int(percentage / 10))
            embed.add_field(name=f"{emoji} {data['text']}", value=f"{bar} ({percentage:.1f}%) - `{votes}` votos", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="pollHelp")
    async def poll_help(self, ctx):
        """Exibe os comandos disponíveis para enquetes."""
        embed = discord.Embed(title="📊 **Comandos de Enquete**", color=discord.Color.blue())
        embed.add_field(name="!createPoll <max_votos> \"Título\" \"Opção 1, Opção 2, ...\"", value="Cria uma nova enquete.", inline=False)
        embed.add_field(name="!endPoll <id_mensagem>", value="Finaliza a enquete e mostra os resultados.", inline=False)
        embed.add_field(name="!pollHelp", value="Mostra esta ajuda.", inline=False)
        await ctx.send(embed=embed)

    async def update_poll_message(self, message):
        if message.id not in self.active_polls:
            return

        poll = self.active_polls[message.id]
        total_votes = sum(len(opt["votes"]) for opt in poll["options"].values())
        embed = discord.Embed(title=f"📊 **{poll['title']}**", description=f"Criado por {poll['author'].display_name}\n\n", color=discord.Color.gold())

        for emoji, data in poll["options"].items():
            votes = len(data["votes"])
            percentage = (votes / total_votes * 100) if total_votes > 0 else 0
            bar = "🟩" * int(percentage / 10) + "⬜" * (10 - int(percentage / 10))
            embed.add_field(name=f"{emoji} {data['text']}", value=f"{bar} ({percentage:.1f}%) - `{votes}` votos", inline=False)
        
        embed.set_footer(text=f"Máximo de {poll['max_votes']} votos por pessoa. Reaja para votar!")
        await message.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(Poll(bot))
