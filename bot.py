import os
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    initial_extensions = ["cogs.presence"]
    for extension in initial_extensions:
        await bot.load_extension(extension)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

async def main():
    await load_extensions()
    await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
