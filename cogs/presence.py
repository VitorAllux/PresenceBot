from discord.ext import commands
from io import BytesIO
import discord
import pandas as pd
from io import BytesIO

class Presence(commands.Cog):
    def __init__(self, bot, storage):
        self.bot = bot
        self.presence_message = None
        self.users_marked = set()
        self.storage = storage

    @commands.command(name="helpPresence")
    async def help_command(self, ctx):
        await ctx.message.delete()
        loading_message = await ctx.send("🤖 `BOT`: Carregando... ⏳")
        help_text = """
        ```
        🤖 Comandos de Presença
        - `!startPresence` : Inicia a presença.
        - `!endPresence` : Finaliza a presença.
        - `!listPresence` : Lista os usuários que marcaram presença.
        - `!savePresence` : Salva a lista de presença no banco.
        - `!listWeekPresence` : Lista as presenças da última semana.
        - `!listMonthPresence` : Lista as presenças do último mês.
        - `!exportPresenceByMonth` : Exporta a lista de presença por mês.
        ```
        """
        await loading_message.edit(content=help_text)

    @commands.command(name="savePresence")
    async def save_presence(self, ctx):
        await ctx.message.delete()

        if not self.presence_message:
            await ctx.send("🤖 `BOT`: ```Nenhuma presença está em andamento para salvar.```")
            return

        if not self.users_marked:
            await ctx.send("🤖 `BOT`: ```Nenhum usuário marcou presença para salvar.```")
            return

        loading_message = await ctx.send("🤖 `BOT`: Salvando presenças no banco de dados... ⏳")
        try:
            participants = [user[0] for user in self.users_marked]
            await self.storage.save_presence(participants)
            await loading_message.edit(content="🤖 `BOT`: ```Presença salva com sucesso!```")
        except Exception as e:
            await loading_message.edit(content=f"🤖 `BOT`: ```Erro ao salvar presença: {e}```")


    @commands.command(name="startPresence")
    async def start_presence(self, ctx):
        await ctx.message.delete()

        if self.presence_message:
            await ctx.send("🤖 `BOT`: ```A presença já está em andamento.```")
            return

        message = await ctx.send("🤖 `BOT`: ```Reaja com ✅ nesta mensagem para marcar sua presença.```")
        await message.add_reaction("✅")
        self.presence_message = message.id
        self.users_marked.clear()

    @commands.command(name="endPresence")
    async def end_presence(self, ctx):
        await ctx.message.delete()

        if not self.presence_message:
            await ctx.send("🤖 `BOT`: ```Nenhuma presença está em andamento.```")
            return

        loading_message = await ctx.send("🤖 `BOT`: Finalizando a presença... ⏳")
        try:
            message = await ctx.channel.fetch_message(self.presence_message)
            await message.delete()
            self.presence_message = None
            self.users_marked.clear()
            await loading_message.edit(content="🤖 `BOT`: ```Presença finalizada com sucesso.```")
        except Exception as e:
            await loading_message.edit(content=f"🤖 `BOT`: ```Erro ao finalizar presença: {e}```")

    @commands.command(name="listPresence")
    async def list_presence(self, ctx):
        await ctx.message.delete()

        if not self.presence_message:
            await ctx.send("🤖 `BOT`: ```Nenhuma presença está em andamento.```")
            return

        if not self.users_marked:
            await ctx.send("🤖 `BOT`: ```Nenhum usuário marcou presença.```")
            return

        header = f"{'Nome do Usuário':<25} {'✅ Presença'}\n{'-'*40}\n"
        user_list = "\n".join([f"👤 {user[1]:<25}" for user in sorted(self.users_marked, key=lambda x: x[1])])  # Nome no servidor
        panel = f"```{header}{user_list}```"
        await ctx.send(f"🤖 `BOT`: {panel}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        if reaction.message.id == self.presence_message and reaction.emoji == "✅":
            guild_member = reaction.message.guild.get_member(user.id)
            if guild_member:
                self.users_marked.add((user.name, guild_member.display_name))

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return

        if reaction.message.id == self.presence_message and reaction.emoji == "✅":
            guild_member = reaction.message.guild.get_member(user.id)
            if guild_member:
                self.users_marked.discard(guild_member.display_name)

    @commands.command(name="listWeekPresence")
    async def list_week_presence(self, ctx):
        await ctx.message.delete()

        loading_message = await ctx.send("🤖 `BOT`: Buscando presenças da última semana... ⏳")
        try:
            recent_presences = await self.storage.get_presences(7)

            if not recent_presences:
                await loading_message.edit(content="🤖 `BOT`: ```Nenhuma presença registrada nos últimos 7 dias.```")
                return

            guild_members = {member.name: member.display_name for member in ctx.guild.members}
            participant_counts = {}

            for presence in recent_presences:
                participant_counts[presence["participant"]] = participant_counts.get(presence["participant"], 0) + 1

            sorted_participants = sorted(participant_counts.items(), key=lambda x: x[1], reverse=True)

            report = "Presenças na última semana:\n"
            reports = []
            for participant, count in sorted_participants:
                display_name = guild_members.get(participant, f"{participant} (inválido)")
                line = f"👤 {display_name}: {count} presenças\n"
                if len(report) + len(line) > 1900:
                    reports.append(report)
                    report = ""
                report += line

            if report:
                reports.append(report)

            await loading_message.delete()

            for report in reports:
                await ctx.send(f"🤖 `BOT`: ```{report}```")
        except Exception as e:
            await loading_message.edit(content=f"🤖 `BOT`: ```Erro ao listar presenças: {e}```")


    @commands.command(name="listMonthPresence")
    async def list_month_presence(self, ctx):
        await ctx.message.delete()

        loading_message = await ctx.send("🤖 `BOT`: Buscando presenças do último mês... ⏳")
        try:
            recent_presences = await self.storage.get_presences(30)

            if not recent_presences:
                await loading_message.edit(content="🤖 `BOT`: ```Nenhuma presença registrada no último mês.```")
                return

            guild_members = {member.name: member.display_name for member in ctx.guild.members}
            participant_counts = {}
            for presence in recent_presences:
                participant_counts[presence["participant"]] = participant_counts.get(presence["participant"], 0) + 1

            sorted_participants = sorted(participant_counts.items(), key=lambda x: x[1], reverse=True)
            report = "Presenças no último mês:\n"
            reports = []

            for participant, count in sorted_participants:
                display_name = guild_members.get(participant, f"{participant} (inválido)")
                line = f"👤 {display_name}: {count} presenças\n"
                if len(report) + len(line) > 1900:
                    reports.append(report)
                    report = ""
                report += line

            if report:
                reports.append(report)

            await loading_message.delete()
            for part in reports:
                await ctx.send(f"🤖 `BOT`: ```{part}```")
        except Exception as e:
            await loading_message.edit(content=f"🤖 `BOT`: ```Erro ao listar presenças: {e}```")

    @commands.command(name="exportPresenceByMonth")
    async def export_presence_by_month(self, ctx):
        await ctx.message.delete()

        loading_message = await ctx.send("🤖 `BOT`: Gerando relatório de presença por mês... ⏳")
        try:
            all_presences = await self.storage.get_all_presences()

            if not all_presences:
                await loading_message.edit(content="🤖 `BOT`: ```Nenhuma presença encontrada no banco de dados.```")
                return

            guild_members = {member.name: member.display_name for member in ctx.guild.members}
            data = {
                "Ano": [presence["timestamp"].year for presence in all_presences],
                "Mês": [presence["timestamp"].month for presence in all_presences],
                "Usuário": [
                    guild_members.get(presence["participant"], f"{presence['participant']} (inválido)")
                    for presence in all_presences
                ],
            }
            df = pd.DataFrame(data)

            summary = df.groupby(["Ano", "Mês", "Usuário"]).size().reset_index(name="Presenças")

            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                summary.to_excel(writer, index=False, sheet_name="Presença Mensal")
            excel_buffer.seek(0)

            await loading_message.delete()
            await ctx.send(
                "🤖 `BOT`: ```Relatório de presença por mês gerado com sucesso!```",
                file=discord.File(excel_buffer, filename="presenca_por_mes.xlsx"),
            )
        except Exception as e:
            await loading_message.edit(content=f"🤖 `BOT`: ```Erro ao gerar relatório: {e}```")

async def setup(bot):
    from services.storage import Storage
    storage = Storage()
    await bot.add_cog(Presence(bot, storage))
