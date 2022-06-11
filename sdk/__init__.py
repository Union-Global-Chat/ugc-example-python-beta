from websockets import connect as ws_connect
from .items import *
import discord
import asyncio
import zlib
import httpx
import orjson


class Error(Exception):
    pass


class Client:
    def __init__(self, token: str):
        self.token = token
        self.on_event = {}
        self.client = httpx.AsyncClient()

    async def close(self):
        await self.client.aclose()
        await self.ws.close()

    async def connect(self):
        self.ws = await ws_connect("wss://ugc.renorari.net/api/v1/gateway")
        while self.open:
            await self.recv()

    async def request(self, method: str, path: str, *args, **kwargs):
        kwargs["headers"] = {
            "Authorization": "Bearer {}".format(self.token)
        }
        r = await self.client.request(method, "https://ugc.renorari.net/api/v1" + path,
                                      *args, **kwargs)
        if r.status_code == 404:
            raise Error("メッセージが見つからない")
        elif r.status_code == 200:
            return r.json()
        elif response.status_code == 401:
            raise Error("認証エラー")
        elif response.status_code == 500:
            raise Error(r.json()["message"])

    @property
    def open(self) -> True:
        return self.ws.open

    async def recv(self):
        data = orjson.loads(zlib.decompress(await self.ws.recv()))
        if data["type"] == "hello":
            await self.identify()
        elif data["type"] == "identify":
            if data["success"]:
                self.dispatch("ready")
        elif data["type"] == "message":
            self.dispatch("message", Message(
                data["data"]["data"], data["data"]["from"]))

    async def identify(self):
        await self.ws_send("identify", {"token": self.token})

    def on(self, name: str):
        def deco(coro):
            if name in self.on_event:
                self.on_event[name].append(coro)
            else:
                self.on_event[name] = [coro]
            return coro
        return deco

    def dispatch(self, name: str, *args):
        if name in self.on_event:
            for coro in self.on_event[name]:
                asyncio.create_task(coro(*args))

    async def ws_send(self, type: str, data: dict):
        payload = {"type": type, "data": data}
        await self.ws.send(zlib.compress(orjson.dumps(payload)))

    async def send(self, message: discord.Message):
        payload = {
            "channel": {
                "name": message.channel.name,
                "id": str(message.channel.id)
            },
            "author": {
                "username": message.author.name,
                "discriminator": message.author.discriminator,
                "id": str(message.author.id),
                "avatarURL": getattr(message.author.avatar, "url", None),
                "bot": message.author.bot
            },
            "guild": {
                "name": message.guild.name,
                "id": str(message.guild.id),
                "iconURL": getattr(message.guild.icon, "url", None)
            },
            "message": {
                "content": message.content,
                "id": str(message.id),
                "cleanContent": message.clean_content,
                "embeds": [],
                "attachments": [
                    {
                        "url": attachment.url,
                        "name": attachment.filename,
                        "width": str(attachment.width),
                        "height": str(attachment.height),
                        "content_type": attachment.content_type
                    }
                    for attachment in message.attachments
                ],
                "reference": { 
                    "channel_id": None, 
                    "guild_id": None,
                    "message_id": None
                }
            }
        }
        await self.request("POST", "/channels", json=payload)
