from discord import Client
from sdk import connect


class MyClient(Client):
    async def setup_hook(self):
        self.ugc = await connect(
