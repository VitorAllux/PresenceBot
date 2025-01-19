import discord
import wavelink
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):
        print(f"🛠 Recebido comando !play de {ctx.author} no canal {ctx.channel}")  # Log para depuração

        await ctx.message.delete()
        print("❗ Mensagem do usuário apagada.")

        vc: wavelink.Player = ctx.voice_client
        print(f"🎵 Tentando conectar ao canal de voz...")

        # Verifica se o bot já está conectado ao canal de voz
        if not vc or not vc.is_connected():
            if not ctx.author.voice:
                print("❌ O usuário não está em um canal de voz.")
                return await ctx.send("❌ `BOT`: Você precisa estar em um canal de voz!")

            # Conectando automaticamente ao canal de voz, se não estiver conectado
            try:
                vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
                print(f"🎵 Conectado ao canal de voz: {ctx.author.voice.channel.name}")
            except Exception as e:
                print(f"❌ Erro ao conectar ao canal de voz: {e}")
                return await ctx.send("❌ `BOT`: Erro ao conectar ao canal de voz.")
        else:
            print(f"⚠ O bot já está conectado ao canal de voz: {ctx.voice_client.channel.name}")

        print("aaaaaaaaaaaaaaaaaaaaa")
        if not wavelink.Pool.get_nodes():
            print("❌ Lavalink não está conectado.")
            return await ctx.send("❌ `BOT`: Lavalink não está conectado.")

        loading_message = await ctx.send("🔎 `BOT`: Buscando música... ⏳")
        print(f"🔎 Buscando música: {search}")


        tracks = await wavelink.YouTubeTrack.search(search)
        print(f"📝 Resultados da busca: {tracks}")

        if not tracks:
            print("❌ Nenhuma música encontrada.")
            return await loading_message.edit(content="❌ `BOT`: Música não encontrada!")

        track = tracks[0]
        self.queue.append(track)
        print(f"📜 Música **{track.title}** adicionada à fila!")

        if not vc.is_playing():
            print("🎶 O bot vai começar a tocar a música agora.")
            await vc.play(self.queue.pop(0))
            await loading_message.edit(content=f"🎶 `BOT`: Tocando agora: **{track.title}**")
        else:
            print("📜 Música adicionada à fila.")
            await loading_message.edit(content=f"📜 `BOT`: **{track.title}** adicionada à fila!")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track, reason):
        print(f"🎶 A música **{track.title}** terminou. Verificando a fila.")
        if self.queue:
            next_track = self.queue.pop(0)
            print(f"🎶 Tocando próxima música: {next_track.title}")
            await player.play(next_track)
        else:
            print("❌ Não há músicas na fila. Desconectando...")
            await player.disconnect()

    @commands.command(name="skip")
    async def skip(self, ctx):
        await ctx.message.delete()
        print("⏭ Pulando música...")

        vc: wavelink.Player = ctx.voice_client
        if vc and vc.is_playing():
            print("🎶 Parando música atual.")
            await ctx.send("⏭ `BOT`: Pulando música...")
            await vc.stop()
        else:
            print("❌ Nenhuma música tocando no momento.")
            await ctx.send("❌ `BOT`: Nenhuma música tocando no momento.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        await ctx.message.delete()
        print("⏸ Pausando música...")

        vc: wavelink.Player = ctx.voice_client
        if vc and vc.is_playing():
            print("🎶 Música pausada.")
            await ctx.send("⏸ `BOT`: Música pausada!")
            await vc.pause()
        else:
            print("❌ Nenhuma música tocando no momento.")
            await ctx.send("❌ `BOT`: Nenhuma música tocando no momento.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        await ctx.message.delete()
        print("▶ Retomando música...")

        vc: wavelink.Player = ctx.voice_client
        if vc and vc.paused:
            print("🎶 Retomando a música pausada.")
            await ctx.send("▶ `BOT`: Música retomada!")
            await vc.resume()
        else:
            print("❌ Nenhuma música está pausada.")
            await ctx.send("❌ `BOT`: Nenhuma música está pausada.")

    @commands.command(name="queue")
    async def show_queue(self, ctx):
        await ctx.message.delete()
        print("📜 Mostrando fila de músicas...")

        if not self.queue:
            print("❌ A fila de músicas está vazia.")
            return await ctx.send("❌ `BOT`: A fila de músicas está vazia!")

        queue_text = "\n".join(f"🎶 {i+1}. {track.title}" for i, track in enumerate(self.queue))
        await ctx.send(f"🎵 `BOT`: ```📜 Fila de Músicas:\n{queue_text}```")

async def setup(bot):
    await bot.add_cog(Music(bot))
