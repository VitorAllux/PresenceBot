import discord
import wavelink
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    @commands.Cog.listener()
    async def on_ready(self):
        """ Conecta ao Lavalink ao iniciar """
        await self.connect_lavalink()

    async def connect_lavalink(self):
        """ Conexão com o servidor Lavalink """
        print("🔌 Tentando conectar ao Lavalink...")

        node = wavelink.Node(
            uri="wss://lavalink.alfari.id",
            password="catfein"
        )

        try:
            await wavelink.Pool.connect(client=self.bot, nodes=[node])
            print("✅ Conectado ao Lavalink com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao conectar ao Lavalink: {e}")

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):
        await ctx.message.delete()

        vc: wavelink.Player = ctx.voice_client

        # Se o bot não estiver no canal de voz, tenta conectar
        if not vc or not vc.is_connected():
            if not ctx.author.voice:
                return await ctx.send("❌ `BOT`: Você precisa estar em um canal de voz!")

            # Conectando automaticamente ao canal de voz
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            print(f"🎵 Conectado ao canal de voz: {ctx.author.voice.channel.name}")

        # Verificando se o Lavalink está conectado
        if not wavelink.Pool.get_nodes():
            return await ctx.send("❌ `BOT`: Lavalink não está conectado.")

        loading_message = await ctx.send("🔎 `BOT`: Buscando música... ⏳")

        try:
            tracks = await wavelink.YouTubeTrack.search(search)
            print(f"📝 Resultados da busca: {tracks}")
        except Exception as e:
            return await loading_message.edit(content=f"❌ `BOT`: Erro ao buscar música: {e}")

        if not tracks:
            return await loading_message.edit(content="❌ `BOT`: Música não encontrada!")

        track = tracks[0]
        self.queue.append(track)

        if not vc.is_playing():
            await vc.play(self.queue.pop(0))
            await loading_message.edit(content=f"🎶 `BOT`: Tocando agora: **{track.title}**")
        else:
            await loading_message.edit(content=f"📜 `BOT`: **{track.title}** adicionada à fila!")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track, reason):
        if self.queue:
            next_track = self.queue.pop(0)
            await player.play(next_track)
        else:
            await player.disconnect()

    @commands.command(name="skip")
    async def skip(self, ctx):
        await ctx.message.delete()
        vc: wavelink.Player = ctx.voice_client
        if vc and vc.is_playing():
            await ctx.send("⏭ `BOT`: Pulando música...")
            await vc.stop()

    @commands.command(name="pause")
    async def pause(self, ctx):
        await ctx.message.delete()
        vc: wavelink.Player = ctx.voice_client
        if vc and vc.is_playing():
            await ctx.send("⏸ `BOT`: Música pausada!")
            await vc.pause()

    @commands.command(name="resume")
    async def resume(self, ctx):
        await ctx.message.delete()
        vc: wavelink.Player = ctx.voice_client
        if vc and vc.paused:
            await ctx.send("▶ `BOT`: Música retomada!")
            await vc.resume()

    @commands.command(name="queue")
    async def show_queue(self, ctx):
        await ctx.message.delete()
        if not self.queue:
            return await ctx.send("❌ `BOT`: A fila de músicas está vazia!")

        queue_text = "\n".join(f"🎶 {i+1}. {track.title}" for i, track in enumerate(self.queue))
        await ctx.send(f"🎵 `BOT`: ```📜 Fila de Músicas:\n{queue_text}```")

async def setup(bot):
    await bot.add_cog(Music(bot))
