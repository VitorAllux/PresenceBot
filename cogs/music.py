import discord
import yt_dlp
from discord.ext import commands
from discord import FFmpegPCMAudio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    async def get_audio_source(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegAudioConvertor',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            return FFmpegPCMAudio(url2)

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice:
            return await ctx.send("❌ `BOT`: Você precisa estar em um canal de voz!")
        if not ctx.voice_client:
            vc = await ctx.author.voice.channel.connect(cls=discord.VoiceClient)
        else:
            vc = ctx.voice_client
        url = search
        try:
            audio_source = await self.get_audio_source(url)
            vc.play(audio_source, after=lambda e: print(f'Error: {e}'))
            await ctx.send(f"🎶 `BOT`: Tocando agora: {url}")
        except Exception as e:
            await ctx.send(f"❌ `BOT`: Erro ao tentar reproduzir a música: {e}")

    @commands.command(name="skip")
    async def skip(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await ctx.send("⏭ `BOT`: Pulando música...")
        else:
            await ctx.send("❌ `BOT`: Nenhuma música tocando no momento.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send("⏸ `BOT`: Música pausada!")
        else:
            await ctx.send("❌ `BOT`: Nenhuma música tocando no momento.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send("▶ `BOT`: Música retomada!")
        else:
            await ctx.send("❌ `BOT`: Nenhuma música pausada.")

    @commands.command(name="queue")
    async def show_queue(self, ctx):
        if not self.queue:
            return await ctx.send("❌ `BOT`: A fila de músicas está vazia!")
        queue_text = "\n".join(f"🎶 {i+1}. {track}" for i, track in enumerate(self.queue))
        await ctx.send(f"🎵 `BOT`: ```📜 Fila de Músicas:\n{queue_text}```")

    @commands.command(name="leave")
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 `BOT`: Desconectado do canal de voz.")
        else:
            await ctx.send("❌ `BOT`: O bot não está conectado a um canal de voz!")

async def setup(bot):
    print("✅ Cog Music carregada com sucesso!")
    await bot.add_cog(Music(bot))
