import os
import asyncio
import discord
from discord.ext import commands
from config.settings import load_env, BOT_PREFIX

load_env()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)


@bot.event
async def setup_hook():
    await bot.load_extension("cogs.music")
    await bot.load_extension("cogs.presence")
    await bot.load_extension("cogs.poll")
    await bot.load_extension("cogs.tl_market")
    await bot.tree.sync()


@bot.event
async def on_ready():
    print(
        f"🤖 Bot {bot.user} está online e pronto para gerenciar enquetes, presenças, músicas e Lineage 2M!"
    )


async def main():
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
