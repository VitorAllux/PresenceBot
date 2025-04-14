import aiohttp
import os

class TlMarketAPI:
    def __init__(self):
        self.base_url = "https://developers.plaync.com/market"
        self.key = os.getenv("TLMARKET_API_KEY")

    async def get_servers(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/servers", headers={"Authorization": f"Bearer {self.key}"}) as r:
                return await r.json()

    async def search_first_item(self, name):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/items/search?name={name}", headers={"Authorization": f"Bearer {self.key}"}) as r:
                data = await r.json()
                return data[0] if data else None

    async def get_item_status(self, server_id, item_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/servers/{server_id}/items/{item_id}", headers={"Authorization": f"Bearer {self.key}"}) as r:
                return await r.json()
