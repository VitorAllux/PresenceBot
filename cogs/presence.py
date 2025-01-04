from discord.ext import commands
import discord


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
        - `!exportPresenceExcel` : Exporta a lista de presença em Excel.
        - `!exportPresenceJson` : Exporta a lista de presença em JSON.
        - `!savePresence` : Salva a lista de presença no banco.
        - `!listWeekPresence` : Lista as presenças da última semana.
        - `!listMonthPresence` : Lista as presenças do último mês.
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
            await self.storage.save_presence(list(self.users_marked))
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
        user_list = "\n".join([f"👤 {user:<25}" for user in sorted(self.users_marked)])
        panel = f"```{header}{user_list}```"
        await ctx.send(f"🤖 `BOT`: {panel}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        if reaction.message.id == self.presence_message and reaction.emoji == "✅":
            guild_member = reaction.message.guild.get_member(user.id)
            if guild_member:
                self.users_marked.add(guild_member.display_name)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return

        if reaction.message.id == self.presence_message and reaction.emoji == "✅":
            guild_member = reaction.message.guild.get_member(user.id)
            if guild_member:
                self.users_marked.discard(guild_member.display_name)


async def setup(bot):
    from services.storage import Storage
    storage = Storage()
    await bot.add_cog(Presence(bot, storage))
