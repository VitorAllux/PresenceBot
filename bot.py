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
intents.voice_states = True  # NECESSÁRIO para o bot entrar em canais de voz!

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

async def connect_lavalink():
    """ Método para conectar ao Lavalink """
    await asyncio.sleep(3)  # Aguarda alguns segundos para evitar problemas de timing
    print("🔌 Tentando conectar ao Lavalink...")

    if not wavelink.NodePool.is_connected():
        try:
            await wavelink.NodePool.create_node(
                bot=bot,
                host="lavalink_v3_no_yt.muzykant.xyz",
                port=443,
                password="youshallnotpass",  # A senha correta deve ser usada aqui
                https=True
            )
            print("✅ Conectado ao Lavalink com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao conectar ao Lavalink: {e}")

@bot.event
async def setup_hook():
    """ Chamado antes do bot ficar pronto """
    print("⚙️ Configurando o bot...")
    await connect_lavalink()
    await bot.load_extension("cogs.music")
    await bot.load_extension("cogs.presence")

@bot.event
async def on_ready():
    """ Confirma que o bot está online """
    print(f"🤖 Bot {bot.user} está online e pronto para tocar músicas!")

async def main():
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
