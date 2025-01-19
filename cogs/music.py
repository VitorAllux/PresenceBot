import discord
import yt_dlp
from discord.ext import commands
from discord import FFmpegPCMAudio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.current_song = None

    async def get_audio_source(self, url):
        print(f"[LOG] Obtendo fonte de áudio para URL: {url}")
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegAudioConvertor', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'quiet': False
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                formats = [fmt['url'] for fmt in info['formats'] if 'audio' in fmt.get('format_note', '')]
                if not formats:
                    raise Exception("Nenhum formato de áudio válido encontrado.")
                print(f"[LOG] Fonte de áudio obtida com sucesso.")
                return FFmpegPCMAudio(formats[0])
            except Exception as e:
                print(f"[ERRO] Erro ao obter áudio: {e}")
                raise

    async def play_next(self, ctx):
        print(f"[LOG] Tocando próxima música. Fila: {self.queue}")
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
                    print(f"[ERRO] Erro ao tocar a próxima música: {e}")
                    await ctx.send(f"❌ `BOT`: Erro ao tocar a próxima música: {e}")
        else:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 `BOT`: Fila vazia. Saindo do canal de voz.")

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):
        print(f"[LOG] Comando play chamado com parâmetro: {search}")
        await ctx.message.delete()

        if not ctx.author.voice:
            print("[LOG] Usuário não está em um canal de voz.")
            return await ctx.send("❌ `BOT`: Você precisa estar em um canal de voz!")

        if not ctx.voice_client:
            print("[LOG] Bot não está conectado. Conectando...")
            vc = await ctx.author.voice.channel.connect()
        else:
            vc = ctx.voice_client
            print(f"[LOG] Bot já conectado no canal: {vc.channel}")

        if vc.is_playing():
            print(f"[LOG] Música já tocando. Adicionando {search} à fila.")
            self.queue.append(search)
            await ctx.send(f"➕ `BOT`: Música adicionada à fila: {search}")
        else:
            print(f"[LOG] Nenhuma música tocando. Iniciando reprodução de {search}.")
            self.queue.append(search)
            await self.play_next(ctx)

    @commands.command(name="skip")
    async def skip(self, ctx):
        print("[LOG] Comando skip chamado.")
        await ctx.message.delete()
        vc = ctx.voice_client
        if vc and vc.is_playing():
            print("[LOG] Pulando música atual.")
            vc.stop()
            await ctx.send("⏭ `BOT`: Pulando música...")
        else:
            print("[LOG] Nenhuma música para pular.")
            await ctx.send("❌ `BOT`: Nenhuma música tocando no momento.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        print("[LOG] Comando pause chamado.")
        await ctx.message.delete()
        vc = ctx.voice_client
        if vc and vc.is_playing():
            print("[LOG] Música pausada.")
            vc.pause()
            await ctx.send("⏸ `BOT`: Música pausada!")
        else:
            print("[LOG] Nenhuma música para pausar.")
            await ctx.send("❌ `BOT`: Nenhuma música tocando no momento.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        print("[LOG] Comando resume chamado.")
        await ctx.message.delete()
        vc = ctx.voice_client
        if vc and vc.is_paused():
            print("[LOG] Música retomada.")
            vc.resume()
            await ctx.send("▶ `BOT`: Música retomada!")
        else:
            print("[LOG] Nenhuma música pausada para retomar.")
            await ctx.send("❌ `BOT`: Nenhuma música pausada.")

    @commands.command(name="queue")
    async def show_queue(self, ctx):
        print("[LOG] Comando queue chamado.")
        await ctx.message.delete()
        if not self.queue:
            print("[LOG] A fila de músicas está vazia.")
            return await ctx.send("❌ `BOT`: A fila de músicas está vazia!")
        queue_text = "\n".join(f"🎶 {i+1}. {track}" for i, track in enumerate(self.queue))
        print(f"[LOG] Fila de músicas: {self.queue}")
        await ctx.send(f"🎵 `BOT`: ```📜 Fila de Músicas:\n{queue_text}```")

    @commands.command(name="leave")
    async def leave(self, ctx):
        print("[LOG] Comando leave chamado.")
        await ctx.message.delete()
        if ctx.voice_client:
            print("[LOG] Bot saindo do canal de voz.")
            await ctx.voice_client.disconnect()
            await ctx.send("👋 `BOT`: Desconectado do canal de voz.")
        else:
            print("[LOG] Bot não estava conectado.")
            await ctx.send("❌ `BOT`: O bot não está conectado a um canal de voz!")

async def setup(bot):
    print("✅ Cog Music carregada com sucesso!")
    await bot.add_cog(Music(bot))
