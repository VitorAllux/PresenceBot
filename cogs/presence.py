from discord.ext import commands
from cogs.storage import Storage
import pandas as pd
import discord
import json
class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.presence_message = None
        self.users_marked = set()
        self.storage = Storage()

    @commands.command(name="helpPresence")
    async def help_command(self, ctx):
        await ctx.message.delete()

        help_text = """
            **Comandos de presença:**
            `!startPresence` - Inicia a presença.
            `!endPresence` - Finaliza a presença.
            `!listPresence` - Lista os usuários que marcaram presença.
            `!exportPresenceExcel` - Exporta a lista de presença em Excel.
            `!exportPresenceJson` - Exporta a lista de presença em JSON.
            `!savePresence` - Salva a lista de presença em um arquivo (Coming).
            `!listWeekPresence` - Lista a presença da semana (Coming).
            `!listMonthPresence` - Lista a presença do mês (Coming).
        """
        await ctx.send(help_text)

    @commands.command(name="savePresence")
    async def save_presence(self, ctx):
        await ctx.message.delete()

        if not self.presence_message:
            await ctx.send("Nenhuma presença está em andamento para salvar.")
            return

        if not self.users_marked:
            await ctx.send("Nenhum usuário marcou presença para salvar.")
            return

        self.storage.save_presence(list(self.users_marked))

        await ctx.send("Presença salva com sucesso!")

    @commands.command(name="startPresence")
    async def start_presence(self, ctx):
        await ctx.message.delete()

        if self.presence_message:
            await ctx.send("A presença já está em andamento.")
            return
        
        message = await ctx.send("Reaja com ✅ nesta mensagem para marcar sua presença.")
        await message.add_reaction("✅")
        self.presence_message = message.id
        self.users_marked.clear()
        
    @commands.command(name="endPresence")
    async def end_presence(self, ctx):
        await ctx.message.delete()

        if not self.presence_message:
            await ctx.send("Nenhuma presença está em andamento.")
            return
        
        message = await ctx.channel.fetch_message(self.presence_message)
        await message.delete()
        
        self.presence_message = None
        self.users_marked.clear()
        await ctx.send("Presença finalizada com sucesso.")

    @commands.command(name="listPresence")
    async def list_presence(self, ctx):
        await ctx.message.delete()

        if not self.presence_message:
            await ctx.send("Nenhuma presença está em andamento.")
            return

        if not self.users_marked:
            await ctx.send("Nenhum usuário marcou presença.")
            return

        header = f"{'Nome do Usuário':<25} {'✅ Presença'}\n{'-'*40}\n"
        user_list = "\n".join([f"👤 {user:<25}" for user in sorted(self.users_marked)])
        panel = f"```\n{header}{user_list}```"

        await ctx.send(panel)


    @commands.command(name="exportPresenceExcel")
    async def export_presence(self, ctx):
        await ctx.message.delete()

        if not self.users_marked:
            await ctx.send("Nenhum usuário marcou presença.")
            return

        timestamp = discord.utils.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f"presenca_{timestamp}.xlsx"

        data = {"Nome do Usuário": list(self.users_marked)}
        df = pd.DataFrame(data)

        df.to_excel(file_path, index=False)

        await ctx.send("Lista de presença exportada com sucesso!", file=discord.File(file_path))


    @commands.command(name="exportPresenceJson")
    async def export_presence_json(self, ctx):
        await ctx.message.delete()

        if not self.users_marked:
            await ctx.send("Nenhum usuário marcou presença.")
            return

        data = {"presenca": [{"nome": user} for user in self.users_marked]}

        timestamp = discord.utils.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f"presenca_{timestamp}.json"

        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

        await ctx.send("Lista de presença exportada com sucesso em JSON!", file=discord.File(file_path))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.id == self.presence_message and reaction.emoji == "✅":
            guild_member = reaction.message.guild.get_member(user.id)
            if guild_member:
                self.users_marked.add(guild_member.display_name)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if reaction.message.id == self.presence_message and reaction.emoji == "✅":
            guild_member = reaction.message.guild.get_member(user.id)
            if guild_member:
                self.users_marked.discard(guild_member.display_name)

    @commands.command(name="listWeekPresence")
    async def list_week_presence(self, ctx):
        await ctx.message.delete()

        recent_presences = self.storage.get_presences_last_week()

        if not recent_presences:
            await ctx.send("Nenhuma presença registrada nos últimos 7 dias.")
            return

        participant_counts = {}
        for presence in recent_presences:
            for participant in presence["participants"]:
                participant_counts[participant] = participant_counts.get(participant, 0) + 1

        report = "Presenças na última semana:\n"
        for participant, count in participant_counts.items():
            report += f"👤 {participant}: {count} presenças\n"

        await ctx.send(f"```\n{report}```")
        
async def setup(bot):
    await bot.add_cog(Presence(bot))

