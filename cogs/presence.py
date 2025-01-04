from discord.ext import commands
import pandas as pd
import discord

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.presence_message = None
        self.users_marked = set()

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

        # Cabeçalho e lista formatados
        header = f"{'Nome do Usuário':<25} {'✅ Presença'}\n{'-'*40}\n"
        user_list = "\n".join([f"👤 {user:<25}" for user in sorted(self.users_marked)])
        panel = f"```\n{header}{user_list}\n```"

        await ctx.send(panel)

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

    @commands.command(name="exportPresence")
    async def export_presence(self, ctx):
        if not self.users_marked:
            await ctx.send("Nenhum usuário marcou presença.")
            return

        data = {"Nome do Usuário": list(self.users_marked)}
        df = pd.DataFrame(data)
        file_path = "presenca.xlsx"

        df.to_excel(file_path, index=False)

        await ctx.send("Lista de presença exportada com sucesso!", file=discord.File(file_path))


async def setup(bot):
    await bot.add_cog(Presence(bot))
