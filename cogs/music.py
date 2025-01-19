import discord
import yt_dlp
from discord.ext import commands
from discord import FFmpegPCMAudio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []  # Fila de músicas
        self.current_song = None  # Música atual

    async def get_audio_source(self, url):
        """Baixa o áudio e retorna a fonte de áudio para tocar no Discord."""
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
            formats = [fmt['url'] for fmt in info['formats'] if 'audio' in fmt.get('format_note', '')]
            if not formats:
                raise Exception("Nenhum formato de áudio válido encontrado.")
            return FFmpegPCMAudio(formats[0])

    async def play_next(self, ctx):
        """Toca a próxima música na fila ou desconecta o bot se a fila acabar."""
        if self.queue:
            next_song = self.queue.pop(0)
            self.current_song = next_song
            vc = ctx.voice_client
            if vc:
                audio_source = await self.get_audio_source(next_song)
                vc.play(audio_source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
                await ctx.send(f"🎶 `BOT`: Tocando agora: {next_song}")
        else:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 `BOT`: Fila vazia. Saindo do canal de voz.")

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):
        """Adiciona uma música à fila e toca se não houver nenhuma em andamento."""
        await ctx.message.delete()

        if not ctx.author.voice:
            return await ctx.send("❌ `BOT`: Você precisa estar em um canal de voz!")

        if not ctx.voice_client:
            vc = await ctx.author.voice.channel.connect()
        else:
            vc = ctx.voice_client

        if vc.is_playing():
            self.queue.append(search)
            await ctx.send(f"➕ `BOT`: Música adicionada à fila: {search}")
        else:
            self.queue.append(search)
            await self.play_next(ctx)

    @commands.command(name="helpMusic")
    async def help_music(self, ctx):
        """Mostra a lista de comandos disponíveis."""
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
        """Pula a música atual e toca a próxima na fila."""
        await ctx.message.delete()
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await ctx.send("⏭ `BOT`: Pulando música...")
        else:
            await ctx.send("❌ `BOT`: Nenhuma música tocando no momento.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        """Pausa a música atual."""
        await ctx.message.delete()
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send("⏸ `BOT`: Música pausada!")
        else:
            await ctx.send("❌ `BOT`: Nenhuma música tocando no momento.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        """Retoma a música pausada."""
        await ctx.message.delete()
        vc = ctx.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send("▶ `BOT`: Música retomada!")
        else:
            await ctx.send("❌ `BOT`: Nenhuma música pausada.")

    @commands.command(name="queue")
    async def show_queue(self, ctx):
        """Mostra a fila de músicas."""
        await ctx.message.delete()
        if not self.queue:
            return await ctx.send("❌ `BOT`: A fila de músicas está vazia!")
        queue_text = "\n".join(f"🎶 {i+1}. {track}" for i, track in enumerate(self.queue))
        await ctx.send(f"🎵 `BOT`: ```📜 Fila de Músicas:\n{queue_text}```")

    @commands.command(name="leave")
    async def leave(self, ctx):
        """Faz o bot sair do canal de voz."""
        await ctx.message.delete()
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 `BOT`: Desconectado do canal de voz.")
        else:
            await ctx.send("❌ `BOT`: O bot não está conectado a um canal de voz!")

async def setup(bot):
    print("✅ Cog Music carregada com sucesso!")
    await bot.add_cog(Music(bot))
