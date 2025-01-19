import discord
import yt_dlp
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def get_audio_url(search_query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extractaudio': True,
        'audioquality': 1,
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'forcejson': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)
        if 'formats' in info:
            url = info['formats'][0]['url']
            return url
    return None

@bot.command(name="play")
async def play(ctx, *, search: str):
    voice_channel = ctx.author.voice.channel

    if not voice_channel:
        return await ctx.send("❌ Você precisa estar em um canal de voz.")

    # Conectando ao canal de voz
    vc = await voice_channel.connect()

    audio_url = await get_audio_url(search)
    if not audio_url:
        return await ctx.send("❌ Não foi possível encontrar o áudio.")

    # Criando o player de voz e tocando
    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options))

    await ctx.send(f"🎶 Tocando: {search}")

@bot.command(name="stop")
async def stop(ctx):
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()
        await ctx.send("✅ Desconectado do canal de voz.")
    else:
        await ctx.send("❌ Não estou conectado a nenhum canal de voz.")

bot.run('YOUR_BOT_TOKEN')
