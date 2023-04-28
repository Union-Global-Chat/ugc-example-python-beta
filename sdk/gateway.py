import time
import asyncio
import discord
from websockets import client
from websockets.exceptions import ConnectionClosed
from .items import Message


import aiohttp

try:
    import orjson as json
except ImportError:
    import json
import zlib


gateway_url = "wss://ugc.renorari.net/api/v2/gateway"
message_url = "https://ugc.renorari.net/api/v2/messages"



class Error(Exception):
    pass


class Client:
    def __init__(self, token: str):
        self.token = token
        self.on_event = {}

    async def close(self):
        self.ws = None
        await self.client.aclose()
        await self.ws.close()

    async def connect(self):
        async with client.connect(gateway_url) as ws:
            self.ws = ws

            while self.open:
                await self.recv()


    async def request(self, json_data):
        json_data["headers"] = {"Authorization": "Bearer {}".format(self.token),
                                "Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(message_url, data = json.dumps(json_data)) as r:
                print(r.status)
                if r.status == 404:
                    raise Error("404エラー")
                elif r.status == 200:
                    return r.json()
                elif r.status == 401:
                    raise Error("認証エラー")
                elif r.status == 400:
                    raise Error(r.json()["message"])


    async def send_message(self, message : discord.Message):
        message = json.dumps(self.discord_message_to_ugc_message(message))
        header = {"Authorization": "Bearer {}".format(self.token),
                  "Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(message_url, data = message, headers = header) as r:
                if r.status == 200:
                    return await r.json()
                else:
                    print(r.status)


    @property
    def open(self) -> bool:
        return self.ws.open

    @property
    def latency(self):
        return self._heartbeat

    async def on_close(self):
        self.dispatch("close")
        await asyncio.sleep(5)
        self.ws = None
        await self.connect()

    async def recv(self):
        try:
            data = json.loads(zlib.decompress(await self.ws.recv()))

        except ConnectionClosed:
            await self.on_close()

        else:
            if data["type"] == "hello":
                await self.identify()
            elif data["type"] == "identify":
                if data["success"]:
                    self.dispatch("ready")
            elif data["type"] == "message":
                self.dispatch("message", Message(
                    data["data"]["data"], data["data"]["source"]))
            elif data["type"] == "heartbeat":
                self._heartbeat = time.time() - data["data"]["unix_time"]

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
        await self.ws.send(zlib.compress(json.dumps(payload)))


    def discord_message_to_ugc_message(self, message : discord.Message):
        attachments = []
        for attachment in message.attachments:

            attachments_dict = {
                "url" : attachment.url,
                "name" : attachment.filename,
                "width": str(attachment.width),
                "height": str(attachment.height),
                "content_type": attachment.content_type
            }
            attachments.append(attachments_dict)

        message_dict = {
            "channel": {
                "name": message.channel.name,
                "id": str(message.channel.id)
            },
            "author": {
                "username": message.author.name,
                "discriminator": message.author.discriminator,
                "id": str(message.author.id),
                "avatarURL": message.author.display_avatar.url,
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
                "attachments": attachments,
                "reference": {
                    "channel_id": str(message.channel.id),
                    "guild_id": str(message.guild.id),
                    "message_id": str(message.id)
                }
            }
        }
        return message_dict