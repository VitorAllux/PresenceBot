import discord
import wavelink
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    async def on_ready(self):
        await asyncio.sleep(3)
        print("🤖 Bot está pronto! Conectando ao Lavalink...")

        if not wavelink.NodePool.is_connected():
            try:
                await wavelink.NodePool.create_node(
                    bot=self.bot,
                    host="lavalink_v3_no_yt.muzykant.xyz",
                    port=443,
                    password="https://discord.gg/v6sdrD9kPh",
                    https=True
                )
                print("✅ Conectado ao Lavalink com sucesso!")

            except Exception as e:
                print(f"❌ Erro ao conectar ao Lavalink: {e}")

    @commands.command(name="join")
    async def join(self, ctx):
        await ctx.message.delete()

        if ctx.author.voice:
            loading_message = await ctx.send("🤖 `BOT`: Conectando ao canal de voz... ⏳")

            try:
                vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
                await loading_message.edit(content="🎵 `BOT`: Conectado ao canal de voz!")
            except Exception as e:
                await loading_message.edit(content=f"❌ `BOT`: Erro ao conectar: `{e}`")
                print(f"❌ Erro ao conectar ao canal de voz: {e}")

        else:
            await ctx.send("❌ `BOT`: Você precisa estar em um canal de voz!")

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):
        await ctx.message.delete()
        vc: wavelink.Player = ctx.voice_client

        if not vc or not vc.is_connected():
            if ctx.author.voice:
                loading_message = await ctx.send("🎵 `BOT`: Entrando no canal de voz... ⏳")
                vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
                await loading_message.edit(content="✅ `BOT`: Conectado ao canal de voz!")
            else:
                return await ctx.send("❌ `BOT`: Você precisa estar em um canal de voz!")

        loading_message = await ctx.send("🔎 `BOT`: Buscando música... ⏳")

        try:
            tracks = await wavelink.YouTubeTrack.search(search)
        except Exception as e:
            return await loading_message.edit(content=f"❌ `BOT`: Erro ao buscar música: {e}")

        if not tracks:
            return await loading_message.edit(content="❌ `BOT`: Música não encontrada!")

        track = tracks[0]
        self.queue.append(track)

        if not vc.is_playing():
            await vc.play(self.queue.pop(0))
            await loading_message.edit(content=f"🎶 `BOT`: Tocando agora: **{track.title}**")
            print(f"🎵 Tocando: {track.title}")
        else:
            await loading_message.edit(content=f"📜 `BOT`: **{track.title}** adicionada à fila!")
            print(f"📜 Adicionada à fila: {track.title}")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track, reason):
        if self.queue:
            next_track = self.queue.pop(0)
            await player.play(next_track)
            print(f"🎶 Tocando próxima música: {next_track.title}")

    @commands.command(name="skip")
    async def skip(self, ctx):
        await ctx.message.delete()

        vc: wavelink.Player = ctx.voice_client
        if vc and vc.is_playing():
            loading_message = await ctx.send("⏭ `BOT`: Pulando música... ⏳")
            await vc.stop()
            await loading_message.edit(content="✅ `BOT`: Música pulada com sucesso!")
        else:
            await ctx.send("❌ `BOT`: Nenhuma música tocando no momento.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        await ctx.message.delete()

        vc: wavelink.Player = ctx.voice_client
        if vc and vc.is_playing():
            loading_message = await ctx.send("⏸ `BOT`: Pausando música... ⏳")
            await vc.pause()
            await loading_message.edit(content="✅ `BOT`: Música pausada!")
        else:
            await ctx.send("❌ `BOT`: Nenhuma música tocando no momento.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        await ctx.message.delete()

        vc: wavelink.Player = ctx.voice_client
        if vc and vc.paused:
            loading_message = await ctx.send("▶ `BOT`: Retomando música... ⏳")
            await vc.resume()
            await loading_message.edit(content="✅ `BOT`: Música retomada!")
        else:
            await ctx.send("❌ `BOT`: Nenhuma música está pausada.")

    @commands.command(name="queue")
    async def show_queue(self, ctx):
        await ctx.message.delete()

        if not self.queue:
            return await ctx.send("❌ `BOT`: A fila de músicas está vazia!")

        header = f"{'📜 Fila de Músicas':<25} \n{'-'*40}\n"
        queue_text = "\n".join(f"🎶 {i+1}. {track.title}" for i, track in enumerate(self.queue))
        panel = f"```{header}{queue_text}```"

        await ctx.send(f"🎵 `BOT`: {panel}")

    @commands.command(name="remove")
    async def remove(self, ctx, index: int):
        await ctx.message.delete()

        if 0 < index <= len(self.queue):
            removed_track = self.queue.pop(index - 1)
            await ctx.send(f"🗑 `BOT`: **{removed_track.title}** removida da fila!")
        else:
            await ctx.send("❌ `BOT`: Índice inválido!")

    @commands.command(name="leave")
    async def leave(self, ctx):
        await ctx.message.delete()

        vc: wavelink.Player = ctx.voice_client
        if vc:
            loading_message = await ctx.send("👋 `BOT`: Desconectando do canal de voz... ⏳")
            await vc.disconnect()
            await loading_message.edit(content="✅ `BOT`: Desconectado com sucesso!")
        else:
            await ctx.send("❌ `BOT`: O bot não está conectado a um canal de voz!")

async def setup(bot):
    await bot.add_cog(Music(bot))
