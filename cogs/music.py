import discord
import wavelink
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    async def cog_load(self):
        node = wavelink.Node(uri="http://sparkling-reverence.railway.internal:8080", password="youshallnotpass")
        await wavelink.Pool.connect(client=self.bot, nodes=[node])

    @commands.command(name="helpMusic")
    async def help_music(self, ctx):
        await ctx.message.delete()
        loading_message = await ctx.send("🤖 `BOT`: Carregando comandos de música... ⏳")

        help_text = """
        ```
        🎵 Comandos de Música
        - `!join` : Entra no canal de voz.
        - `!leave` : Sai do canal de voz.
        - `!play <nome/link>` : Toca uma música.
        - `!pause` : Pausa a música.
        - `!resume` : Retoma a música pausada.
        - `!skip` : Pula para a próxima música.
        - `!queue` : Mostra a fila de músicas.
        - `!remove <número>` : Remove uma música da fila.
        ```
        """
        await loading_message.edit(content=help_text)

    @commands.command(name="join")
    async def join(self, ctx):
        await ctx.message.delete()

        if ctx.author.voice:
            loading_message = await ctx.send("🤖 `BOT`: Conectando ao canal de voz... ⏳")
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            await loading_message.edit(content="🎵 `BOT`: Conectado ao canal de voz!")
        else:
            await ctx.send("❌ `BOT`: Você precisa estar em um canal de voz!")

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):
        await ctx.message.delete()

        vc: wavelink.Player = ctx.voice_client
        if not vc:
            loading_message = await ctx.send("🤖 `BOT`: Entrando no canal de voz... ⏳")
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            await loading_message.edit(content="🎵 `BOT`: Conectado ao canal de voz!")

        loading_message = await ctx.send("🔎 `BOT`: Buscando música... ⏳")
        tracks = await wavelink.YouTubeTrack.search(search)

        if not tracks:
            return await loading_message.edit(content="❌ `BOT`: Música não encontrada!")

        track = tracks[0]
        self.queue.append(track)

        if not vc.playing:
            await vc.play(self.queue.pop(0))
            await loading_message.edit(content=f"🎶 `BOT`: Tocando agora: **{track.title}**")
        else:
            await loading_message.edit(content=f"📜 `BOT`: **{track.title}** adicionada à fila!")

    @commands.command(name="skip")
    async def skip(self, ctx):
        await ctx.message.delete()

        vc: wavelink.Player = ctx.voice_client
        if vc and vc.playing:
            loading_message = await ctx.send("⏭ `BOT`: Pulando música... ⏳")
            await vc.stop()
            await loading_message.edit(content="✅ `BOT`: Música pulada com sucesso!")
        else:
            await ctx.send("❌ `BOT`: Nenhuma música tocando no momento.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        await ctx.message.delete()

        vc: wavelink.Player = ctx.voice_client
        if vc and vc.playing:
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
