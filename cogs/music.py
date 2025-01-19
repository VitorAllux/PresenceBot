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
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = [fmt['url'] for fmt in info['formats'] if 'audio' in fmt['format_note']]
            if not formats:
                raise Exception("Nenhum formato de áudio válido encontrado.")
            return FFmpegPCMAudio(formats[0])

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):
        print('Comando play chamado!')

        if not ctx.author.voice:
            return await ctx.send("❌ `BOT`: Você precisa estar em um canal de voz!")

        if not ctx.voice_client:
            vc = await ctx.author.voice.channel.connect()
        else:
            vc = ctx.voice_client

        url = search
        try:
            audio_source = await self.get_audio_source(url)
            vc.play(audio_source, after=lambda e: print(f'Erro na reprodução: {e}'))
            await ctx.send(f"🎶 `BOT`: Tocando agora: {url}")
        except Exception as e:
            await ctx.send(f"❌ `BOT`: Erro ao tentar reproduzir a música: {e}")

    @commands.command(name="helpMusic")
    async def help_music(self, ctx):
        await ctx.message.delete()
        help_text = """
        ```
        🎵 Comandos de Música
        - `!play <link>` : Toca uma música do YouTube.
        - `!skip` : Pula para a próxima música da fila.
        - `!pause` : Pausa a música atual.
        - `!resume` : Retoma a música pausada.
        - `!queue` : Mostra a fila de músicas.
        - `!leave` : Sai do canal de voz.
        ```
        """
        await ctx.send(help_text)

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
