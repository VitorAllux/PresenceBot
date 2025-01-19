import discord
from discord.ext import commands
from collections import defaultdict
import asyncio
import matplotlib.pyplot as plt
import io

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
        """Finaliza uma enquete e exibe os resultados com um gráfico."""
        if message_id not in self.active_polls:
            await ctx.send("❌ `BOT`: ID de enquete inválido!")
            return

        poll = self.active_polls.pop(message_id)
        total_votes = sum(len(opt["votes"]) for opt in poll["options"].values())
        labels = []
        votes = []
        for emoji, data in poll["options"].items():
            labels.append(f"{emoji} {data['text']}")
            votes.append(len(data["votes"]))

        # Criando gráfico de pizza
        fig, ax = plt.subplots()
        ax.pie(votes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
        ax.axis('equal')
        plt.title(f"Resultados da Enquete: {poll['title']}")

        # Salvando o gráfico em um buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()

        file = discord.File(buffer, filename="poll_results.png")
        embed = discord.Embed(title=f"📊 **{poll['title']} - ENCERRADO**", description=f"Criado por {poll['author'].display_name}\n\n", color=discord.Color.red())
        embed.set_image(url="attachment://poll_results.png")

        await ctx.send(embed=embed, file=file)

    @commands.command(name="helpPoll")
    async def poll_help(self, ctx):
        """Exibe os comandos disponíveis para enquetes."""
        embed = discord.Embed(title="📊 **Comandos de Enquete**", color=discord.Color.blue())
        embed.add_field(name="!createPoll <max_votos> \"Título\" \"Opção 1, Opção 2, ...\"", value="Cria uma nova enquete.", inline=False)
        embed.add_field(name="!endPoll <id_mensagem>", value="Finaliza a enquete e mostra os resultados com gráfico.", inline=False)
        embed.add_field(name="!helpPoll", value="Mostra esta ajuda.", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Poll(bot))
