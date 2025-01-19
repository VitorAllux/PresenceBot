import discord
import wavelink
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):
        await ctx.message.delete()
        vc: wavelink.Player = ctx.voice_client

        # 🔍 Verifica se o Lavalink está conectado antes de tocar música
        if not wavelink.Pool.get_nodes():
            print("❌ ERRO: Lavalink não está conectado!")
            return await ctx.send("❌ `BOT`: Lavalink não está conectado.")

        # 🔍 Verifica se o usuário está em um canal de voz antes de conectar
        if not vc or not vc.is_connected():
            if not ctx.author.voice:
                return await ctx.send("❌ `BOT`: Você precisa estar em um canal de voz!")

            try:
                vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
                print(f"🎵 Conectado ao canal de voz: {ctx.author.voice.channel.name}")
            except Exception as e:
                print(f"❌ ERRO AO CONECTAR AO CANAL: {e}")
                return await ctx.send(f"❌ `BOT`: Erro ao conectar ao canal de voz: `{e}`")

        # 🔎 Buscando a música
        loading_message = await ctx.send("🔎 `BOT`: Buscando música... ⏳")
        try:
            tracks = await wavelink.YouTubeTrack.search(search)
            if not tracks:
                print("❌ ERRO: Nenhuma música encontrada!")
                return await loading_message.edit(content="❌ `BOT`: Música não encontrada!")

            track = tracks[0]
            print(f"🎶 Música encontrada: {track.title} | Duração: {track.length}")
            
            self.queue.append(track)

            # Se nada estiver tocando, começa a tocar
            if not vc.is_playing():
                await vc.play(self.queue.pop(0))
                await loading_message.edit(content=f"🎶 `BOT`: Tocando agora: **{track.title}**")
                print(f"▶ Tocando: {track.title}")
            else:
                await loading_message.edit(content=f"📜 `BOT`: **{track.title}** adicionada à fila!")
                print(f"📜 Adicionada à fila: {track.title}")

        except Exception as e:
            print(f"❌ ERRO AO BUSCAR MÚSICA: {e}")
            return await loading_message.edit(content=f"❌ `BOT`: Erro ao buscar música: {e}")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track, reason):
        if self.queue:
            next_track = self.queue.pop(0)
            await player.play(next_track)
            print(f"▶ Tocando próxima música: {next_track.title}")
        else:
            await player.disconnect()
            print("🚪 Desconectando do canal de voz, fila de músicas vazia.")

    @commands.command(name="skip")
    async def skip(self, ctx):
        await ctx.message.delete()
        vc: wavelink.Player = ctx.voice_client
        if vc and vc.is_playing():
            print("⏭ Pulando música...")
            await vc.stop()

    @commands.command(name="pause")
    async def pause(self, ctx):
        await ctx.message.delete()
        vc: wavelink.Player = ctx.voice_client
        if vc and vc.is_playing():
            print("⏸ Música pausada.")
            await vc.pause()

    @commands.command(name="resume")
    async def resume(self, ctx):
        await ctx.message.delete()
        vc: wavelink.Player = ctx.voice_client
        if vc and vc.paused:
            print("▶ Música retomada.")
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
