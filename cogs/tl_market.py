import discord
from discord.ext import commands, tasks
from services.tl_market_storage import TlMarketStorage
from utils.tl_market_api import TlMarketAPI
from datetime import datetime, timezone

class TlMarket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.storage = TlMarketStorage()
        self.api = TlMarketAPI()
        self.check_items.start()

    @commands.command(name="subscribe")
    async def subscribe(self, ctx):
        servers = await self.api.get_servers()
        linhas = [f"{s['id']}: {s['name']}" for s in servers]
        await ctx.send("Servidores disponíveis:\n" + "\n".join(linhas))

    @commands.command(name="setServer")
    async def set_server(self, ctx, server_id: int):
        await self.storage.set_user_server(ctx.author.id, server_id)
        await ctx.send(f"✅ Servidor {server_id} configurado.")

    @commands.command(name="addSearch")
    async def add_search(self, ctx, *, args):
        partes = args.rsplit(" ", 1)
        nome = partes[0]
        intervalo = int(partes[1]) if len(partes) == 2 and partes[1].isdigit() else 30
        item = await self.api.search_first_item(nome)
        if not item:
            await ctx.send("❌ Item não encontrado.")
            return
        await self.storage.add_search(ctx.author.id, item['id'], intervalo)
        await ctx.send(f"🔍 {item['name']} adicionado para busca a cada {intervalo} min.")

    @tasks.loop(minutes=1)
    async def check_items(self):
        buscas = await self.storage.get_all_searches()
        for b in buscas:
            if not b['last_checked'] or (datetime.now(timezone.utc) - b['last_checked']).total_seconds() >= b['interval'] * 60:
                dados = await self.api.get_item_status(b['server_id'], b['item_id'])
                if dados:
                    user = self.bot.get_user(b['user_id'])
                    if user:
                        await user.send(f"📦 {dados['name']}\n💰 Preço: {dados['price']}\n📈 Variação: {dados['variation']}%")
                await self.storage.update_last_checked(b['user_id'], b['item_id'])

async def setup(bot):
    await bot.add_cog(TlMarket(bot))
