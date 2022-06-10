import discord
from sdk import Client as SdkClient
from json import load
try:
    import uvloop
except ImportError:
    uvloop.install()


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("config.json", "r") as f:
            self.config = load(f)
        self.sdk = SdkClient(self.config["ugc"])
    
    async def setup_hook(self):
        print("connecting to ugc gateway")
        self.loop.create_task(self.sdk.connect())
        
    def on(self, name):
        return self.sdk.on(name)
    
    async def close(self):
        await self.sdk.close()
        await super().close()
    
client = MyClient(intents=discord.Intents.all())

@client.event
async def on_ready():
    print("ready")
    
@client.on("ready")
async def ready_for_ugc():
    print("Ready for ugc")
    
@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.name != "ugc-test":
        return
    for ch in client.get_all_channels():
        if message.channel.id == ch.id:
            continue
        if ch.name == "ugc-test":
            embed = discord.Embed(description=message.content, color=0x07cff7)
            embed.set_author(name=message.author.name, icon_url=getattr(message.author.avatar, "url", None))
            embeds = [embed]
            if len(message.attachments) != 0:
                for attachment in message.attachments:
                    e = discord.Embed(color=0x07cff7)
                    e.set_image(url=attachment.url)
                    embeds.append(e)
            await ch.send(embeds=embeds)
            await client.sdk.send(message)

client.run(client.config["token"])
