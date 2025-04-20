import discord
import yt_dlp
import logging
import asyncio
from discord.ext import commands
from discord import FFmpegPCMAudio, app_commands

logger = logging.getLogger(__name__)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.current_song = None
        self.current_message = None

    async def get_audio_source(self, query):
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": False,
            "default_search": "ytsearch1",
            "extract_flat": False,
            "cookiefile": "config/cookies.txt",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if "entries" in info:
                info = info["entries"][0]
            video_url = info["webpage_url"]
            formats = [
                fmt["url"]
                for fmt in info.get("formats", [])
                if fmt.get("acodec") != "none"
            ]
            return FFmpegPCMAudio(formats[0]), info["title"], video_url

    async def play_next(self, interaction, vc):
        if self.queue:
            next_song = self.queue.pop(0)
            self.current_song = next_song
            audio_source, title, video_url = await self.get_audio_source(next_song)
            if self.current_message:
                await self.current_message.delete()
            self.current_message = await interaction.channel.send(
                f"🎶 Tocando agora: [{title}]({video_url})"
            )
            vc.play(
                audio_source,
                after=lambda e: self.bot.loop.create_task(
                    self.play_next(interaction, vc)
                ),
            )
        else:
            await interaction.channel.send("👋 Fila vazia. Desconectando em 10s...")
            await asyncio.sleep(10)
            if vc.is_connected():
                await vc.disconnect()

    @app_commands.command(name="play", description="Tocar música")
    @app_commands.describe(search="Nome ou link da música")
    async def play(self, interaction: discord.Interaction, search: str):
        if not interaction.user.voice:
            await interaction.response.send_message(
                "❌ Você precisa estar em um canal de voz!", ephemeral=True
            )
            return
        if not interaction.guild.voice_client:
            vc = await interaction.user.voice.channel.connect()
        else:
            vc = interaction.guild.voice_client
        self.queue.append(search)
        if vc.is_playing():
            await interaction.response.send_message(
                f"➕ Adicionado à fila: **{search}**"
            )
        else:
            await interaction.response.defer()
            await self.play_next(interaction, vc)

    @app_commands.command(name="skip", description="Pular música atual")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭ Música pulada.")
        else:
            await interaction.response.send_message(
                "❌ Nenhuma música tocando.", ephemeral=True
            )

    @app_commands.command(name="pause", description="Pausar música")
    async def pause(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸ Música pausada.")
        else:
            await interaction.response.send_message(
                "❌ Nenhuma música tocando.", ephemeral=True
            )

    @app_commands.command(name="resume", description="Retomar música")
    async def resume(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶ Música retomada.")
        else:
            await interaction.response.send_message(
                "❌ Nenhuma música pausada.", ephemeral=True
            )

    @app_commands.command(name="leave", description="Desconectar do canal")
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("👋 Desconectado.")
        else:
            await interaction.response.send_message(
                "❌ Não estou conectado a nenhum canal.", ephemeral=True
            )

    async def cog_load(self):
        self.bot.tree.add_command(self.play)
        self.bot.tree.add_command(self.skip)
        self.bot.tree.add_command(self.pause)
        self.bot.tree.add_command(self.resume)
        self.bot.tree.add_command(self.leave)


async def setup(bot):
    await bot.add_cog(Music(bot))
