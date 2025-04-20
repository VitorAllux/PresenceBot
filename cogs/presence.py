import discord
from discord.ext import commands
from discord import app_commands
from services.storage import Storage
from io import BytesIO
import pandas as pd


class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        self.presence_message = None
        self.users_marked = set()

    @app_commands.command(
        name="startpresence", description="Inicia uma chamada de presença"
    )
    async def start_presence(self, interaction: discord.Interaction):
        if self.presence_message:
            await interaction.response.send_message(
                "Presença já em andamento.", ephemeral=True
            )
            return
        msg = await interaction.channel.send("Reaja com ✅ para marcar presença.")
        await msg.add_reaction("✅")
        self.presence_message = msg.id
        self.users_marked.clear()
        await interaction.response.send_message("✅ Presença iniciada.", ephemeral=True)

    @app_commands.command(
        name="endpresence", description="Encerra a chamada de presença"
    )
    async def end_presence(self, interaction: discord.Interaction):
        if not self.presence_message:
            await interaction.response.send_message(
                "Nenhuma presença em andamento.", ephemeral=True
            )
            return
        try:
            msg = await interaction.channel.fetch_message(self.presence_message)
            await msg.delete()
        except:
            pass
        self.presence_message = None
        self.users_marked.clear()
        await interaction.response.send_message(
            "✅ Presença encerrada.", ephemeral=True
        )

    @app_commands.command(name="listpresence", description="Lista quem marcou presença")
    async def list_presence(self, interaction: discord.Interaction):
        if not self.users_marked:
            await interaction.response.send_message("Nenhum usuário marcou presença.")
            return
        lines = [
            f"👤 {user[1]}" for user in sorted(self.users_marked, key=lambda x: x[1])
        ]
        await interaction.response.send_message(
            "```Presenças:\n" + "\n".join(lines) + "```"
        )

    @app_commands.command(name="savepresence", description="Salva a presença no banco")
    async def save_presence(self, interaction: discord.Interaction):
        if not self.users_marked:
            await interaction.response.send_message(
                "Nenhum usuário marcou presença.", ephemeral=True
            )
            return
        participants = [user[0] for user in self.users_marked]
        await self.storage.save_presence(participants)
        await interaction.response.send_message("✅ Presença salva no banco.")

    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        if reaction.message.id == self.presence_message and reaction.emoji == "✅":
            member = reaction.message.guild.get_member(user.id)
            if member:
                self.users_marked.add((user.name, member.display_name))

    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return
        if reaction.message.id == self.presence_message and reaction.emoji == "✅":
            member = reaction.message.guild.get_member(user.id)
            if member:
                self.users_marked.discard((user.name, member.display_name))


async def setup(bot):
    await bot.add_cog(Presence(bot))
