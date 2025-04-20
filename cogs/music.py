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

    async def get_audio_sources(self, query):
        logger.info(f"🔍 Buscando áudio para: {query}")
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": False,
            "quiet": True,
            "default_search": "ytsearch1",
            "extract_flat": False,
            "cookiefile": "config/cookies.txt",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(query, download=False)

                if "entries" in info:
                    entries = info["entries"]
                else:
                    entries = [info]

                sources = []
                for entry in entries:
                    formats = [
                        f["url"]
                        for f in entry.get("formats", [])
                        if f.get("acodec") != "none"
                    ]
                    if not formats:
                        continue
                    sources.append(
                        {
                            "audio": FFmpegPCMAudio(formats[0]),
                            "title": entry["title"],
                            "url": entry["webpage_url"],
                        }
                    )

                if not sources:
                    raise Exception("Nenhum áudio válido encontrado.")
                return sources
            except Exception as e:
                logger.error(f"❌ Erro ao obter áudio: {e}")
                raise

    async def play_next(self, interaction, vc):
        if self.queue:
            next_song = self.queue.pop(0)
            self.current_song = next_song
            if self.current_message:
                await self.current_message.delete()
            self.current_message = await interaction.channel.send(
                f"🎶 Tocando agora: [{next_song['title']}]({next_song['url']})"
            )
            vc.play(
                next_song["audio"],
                after=lambda e: self.bot.loop.create_task(
                    self.play_next(interaction, vc)
                ),
            )
        else:
            await interaction.channel.send("👋 Fila vazia. Desconectando em 10s...")
            await asyncio.sleep(10)
            if vc.is_connected():
                await vc.disconnect()

    @app_commands.command(name="play", description="Tocar música ou playlist")
    @app_commands.describe(search="Nome ou link da música ou playlist")
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

        await interaction.response.defer()
        try:
            songs = await self.get_audio_sources(search)
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}")
            return

        self.queue.extend(songs)
        if vc.is_playing():
            if len(songs) == 1:
                await interaction.followup.send(
                    f"➕ Adicionado à fila: **{songs[0]['title']}**"
                )
            else:
                await interaction.followup.send(
                    f"➕ {len(songs)} músicas adicionadas à fila."
                )
        else:
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

    @app_commands.command(name="queue", description="Ver fila de músicas")
    async def show_queue(self, interaction: discord.Interaction):
        if not self.queue:
            await interaction.response.send_message("📭 Fila vazia.")
            return
        lines = [
            f"{i+1}. [{song['title']}]({song['url']})"
            for i, song in enumerate(self.queue[:10])
        ]
        msg = "\n".join(lines)
        await interaction.response.send_message(f"🎵 Fila atual:\n{msg}")


async def setup(bot):
    await bot.add_cog(Music(bot))
