import discord
from discord.ext import commands
import asyncpg
import os

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_url = os.getenv("DATABASE_URL")
        self.role_message_id = None

    async def fetch_role_message_id(self):
        async with asyncpg.create_pool(self.db_url) as pool:
            async with pool.acquire() as conn:
                row = await conn.fetchrow("SELECT role_message_id FROM role_manager LIMIT 1;")
                if row:
                    self.role_message_id = row["role_message_id"]

    async def save_role_message_id(self, message_id):
        async with asyncpg.create_pool(self.db_url) as pool:
            async with pool.acquire() as conn:
                await conn.execute("DELETE FROM role_manager;")
                await conn.execute("INSERT INTO role_manager (role_message_id) VALUES ($1)", message_id)
        self.role_message_id = message_id

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.find(lambda r: r.name.startswith("🦄 PÔNEI SELVAGEM"), member.guild.roles)
        if role:
            await member.add_roles(role)

    @commands.command(name="createRoleMessage")
    async def create_role_message(self, ctx):
        await self.fetch_role_message_id()
        if self.role_message_id:
            await ctx.send("A mensagem de seleção de cargos já foi criada.")
            return

        embed = discord.Embed(
            title="🎭 Escolha seu papel no servidor!",
            description=(
                "Reaja abaixo para escolher seu cargo:\n\n"
                "🛡️ - 🛡️ TANK\n"
                "⚔️ - ⚔️ DPS\n"
                "💚 - 💚 HEALER\n\n"
                "Você só pode escolher **um** cargo!"
            ),
            color=discord.Color.blue()
        )
        message = await ctx.send(embed=embed)
        for emoji in ["🛡️", "⚔️", "💚"]:
            await message.add_reaction(emoji)
        await self.save_role_message_id(message.id)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        await self.fetch_role_message_id()
        if user.bot or reaction.message.id != self.role_message_id:
            return
        guild = reaction.message.guild
        member = guild.get_member(user.id)
        role_mapping = {"🛡️": "🛡️ TANK", "⚔️": "⚔️ DPS", "💚": "💚 HEALER"}
        selected_role_name = role_mapping.get(str(reaction.emoji))
        if not selected_role_name:
            return
        selected_role = discord.utils.find(lambda r: r.name.startswith(selected_role_name), guild.roles)
        if not selected_role:
            return
        previous_roles = [role for role in member.roles if any(role.name.startswith(r) for r in role_mapping.values())]
        for role in previous_roles:
            await member.remove_roles(role)
        await member.add_roles(selected_role)
        try:
            await user.send(f"✅ Você agora faz parte do time **{selected_role_name}**!")
        except discord.Forbidden:
            pass
        for emoji, role_name in role_mapping.items():
            if emoji != reaction.emoji:
                await reaction.message.remove_reaction(emoji, user)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        await self.fetch_role_message_id()
        if user.bot or reaction.message.id != self.role_message_id:
            return
        guild = reaction.message.guild
        member = guild.get_member(user.id)
        role_mapping = {"🛡️": "🛡️ TANK", "⚔️": "⚔️ DPS", "💚": "💚 HEALER"}
        role_name = role_mapping.get(str(reaction.emoji))
        if not role_name:
            return
        role = discord.utils.find(lambda r: r.name.startswith(role_name), guild.roles)
        if role and role in member.roles:
            await member.remove_roles(role)
            try:
                await user.send(f"❌ Você **saiu** do cargo **{role_name}**.")
            except discord.Forbidden:
                pass

async def setup(bot):
    await bot.add_cog(RoleManager(bot))
