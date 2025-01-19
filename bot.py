import os
import asyncio
import discord
import wavelink
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

async def connect_lavalink():
    await asyncio.sleep(3)
    print("🔌 Tentando conectar ao Lavalink...")

    try:
        node = wavelink.Node(
            uri="https://ll3.myhm.space:443",
            password="d.gg/therepublic",
            secure=True
        )

        await wavelink.Pool.connect(client=bot, nodes=[node])
        print("✅ Conectado ao Lavalink com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao conectar ao Lavalink: {e}")

@bot.event
async def setup_hook():
    print("⚙️ Configurando o bot...")
    await connect_lavalink()
    await bot.load_extension("cogs.music")
    await bot.load_extension("cogs.presence")

@bot.event
async def on_ready():
    print(f"🤖 Bot {bot.user} está online e pronto para tocar músicas!")

async def main():
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
