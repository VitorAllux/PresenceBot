import os
import asyncio
from discord import Intents
from discord.ext import commands
from config.settings import load_env, BOT_PREFIX

load_env()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)


async def load_extensions():
    initial_extensions = ["cogs.presence"]
    for extension in initial_extensions:
        await bot.load_extension(extension)


@bot.event
async def on_ready():
    print(f"🤖 Bot {bot.user} está online e pronto para uso!")


async def main():
    await load_extensions()
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
