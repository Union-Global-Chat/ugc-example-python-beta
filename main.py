import discord
from sdk import Client as SdkClient
from json import load


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("config.json", "r") as f:
            self.config = load(f)
        self.sdk = SdkClient()
    
    async def setup_hook(self):
        self.loop.create_task(self.sdk.connect())
        
    def on(self, name):
        return self.sdk.on(name)
    
client = MyClient(intents=discord.Intents.all())

@client.event
async def on_ready():
    print("ready")
    
@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.name != "ugc-test":
        return
    for ch in client.channels:
        if ch.name == "ugc-test":
            embed = discord.Embed(description=message.content)
            embed.set_author(name=message.author.name, url=getattr(message.author.avatar, "url", None))
            await ch.send(embed=embed)
            await client.sdk.send(message)

client.run(self.config["token"])
