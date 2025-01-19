import discord
import yt_dlp
import logging
from discord.ext import commands
from discord import FFmpegPCMAudio

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.current_song = None

async def get_audio_source(self, url):
    logger.info(f"Obtendo fonte de áudio para URL: {url}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,  # Evita pegar playlists inteiras
        'quiet': False,
        'default_search': 'ytsearch',  # Permite pesquisar mesmo sem URL direta
        'extract_flat': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            
            # Obtém a melhor URL de áudio disponível
            formats = [fmt['url'] for fmt in info.get('formats', []) if fmt.get('acodec') != 'none']
            
            if not formats:
                raise Exception("Nenhum formato de áudio válido encontrado.")

            logger.info("Fonte de áudio obtida com sucesso.")
            return FFmpegPCMAudio(formats[0])

        except Exception as e:
            logger.error(f"Erro ao obter áudio: {e}")
            raise

    async def play_next(self, ctx):
        logger.info(f"Tocando próxima música. Fila: {self.queue}")
        if self.queue:
            next_song = self.queue.pop(0)
            self.current_song = next_song
            vc = ctx.voice_client
            if vc:
                try:
                    audio_source = await self.get_audio_source(next_song)
                    vc.play(audio_source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
                    await ctx.send(f"🎶 `BOT`: Tocando agora: {next_song}")
                except Exception as e:
                    logger.error(f"Erro ao tocar a próxima música: {e}")
                    await ctx.send(f"❌ `BOT`: Erro ao tocar a próxima música: {e}")
        else:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 `BOT`: Fila vazia. Saindo do canal de voz.")

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):
        logger.info(f"Comando play chamado com parâmetro: {search}")
        await ctx.message.delete()

        if not ctx.author.voice:
            logger.warning("Usuário não está em um canal de voz.")
            return await ctx.send("❌ `BOT`: Você precisa estar em um canal de voz!")

        if not ctx.voice_client:
            logger.info("Bot não está conectado. Conectando...")
            vc = await ctx.author.voice.channel.connect()
        else:
            vc = ctx.voice_client
            logger.info(f"Bot já conectado no canal: {vc.channel}")

        if vc.is_playing():
            logger.info(f"Música já tocando. Adicionando {search} à fila.")
            self.queue.append(search)
            await ctx.send(f"➕ `BOT`: Música adicionada à fila: {search}")
        else:
            logger.info(f"Nenhuma música tocando. Iniciando reprodução de {search}.")
            self.queue.append(search)
            await self.play_next(ctx)

    @commands.command(name="skip")
    async def skip(self, ctx):
        logger.info("Comando skip chamado.")
        await ctx.message.delete()
        vc = ctx.voice_client
        if vc and vc.is_playing():
            logger.info("Pulando música atual.")
            vc.stop()
            await ctx.send("⏭ `BOT`: Pulando música...")
        else:
            logger.warning("Nenhuma música para pular.")
            await ctx.send("❌ `BOT`: Nenhuma música tocando no momento.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        logger.info("Comando pause chamado.")
        await ctx.message.delete()
        vc = ctx.voice_client
        if vc and vc.is_playing():
            logger.info("Música pausada.")
            vc.pause()
            await ctx.send("⏸ `BOT`: Música pausada!")
        else:
            logger.warning("Nenhuma música para pausar.")
            await ctx.send("❌ `BOT`: Nenhuma música tocando no momento.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        logger.info("Comando resume chamado.")
        await ctx.message.delete()
        vc = ctx.voice_client
        if vc and vc.is_paused():
            logger.info("Música retomada.")
            vc.resume()
            await ctx.send("▶ `BOT`: Música retomada!")
        else:
            logger.warning("Nenhuma música pausada para retomar.")
            await ctx.send("❌ `BOT`: Nenhuma música pausada.")

    @commands.command(name="queue")
    async def show_queue(self, ctx):
        logger.info("Comando queue chamado.")
        await ctx.message.delete()
        if not self.queue:
            logger.info("A fila de músicas está vazia.")
            return await ctx.send("❌ `BOT`: A fila de músicas está vazia!")
        queue_text = "\n".join(f"🎶 {i+1}. {track}" for i, track in enumerate(self.queue))
        logger.info(f"Fila de músicas: {self.queue}")
        await ctx.send(f"🎵 `BOT`: ```📜 Fila de Músicas:\n{queue_text}```")

    @commands.command(name="leave")
    async def leave(self, ctx):
        logger.info("Comando leave chamado.")
        await ctx.message.delete()
        if ctx.voice_client:
            logger.info("Bot saindo do canal de voz.")
            await ctx.voice_client.disconnect()
            await ctx.send("👋 `BOT`: Desconectado do canal de voz.")
        else:
            logger.warning("Bot não estava conectado.")
            await ctx.send("❌ `BOT`: O bot não está conectado a um canal de voz!")

async def setup(bot):
    logger.info("✅ Cog Music carregada com sucesso!")
    await bot.add_cog(Music(bot))
