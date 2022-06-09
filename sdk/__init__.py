from websockets import connect as ws_connect
import asyncio
import zlib
import orjson
    
    
class Client:
    def __init__(self, token: str):
        self.token = token
        self.on_event = {}
        
    async def connect(self):
        self.ws = await ws_connect("wss://ugc.renorari.net/api/v1/gateway")
        while self.open:
            await self.ws.recv()
    
    @property
    def open(self) -> True:
        return self.ws.open
        
    async def recv(self):
        data = orjson.loads(zlib.decompress(await self.ws.recv()))
        if data["type"] == "hello":
            await self.identify()
        elif data["type"] == "identify":
            self.dispatch("ready")
        elif data["type"] == "send":
            self.dispatch("message", data["data"])
            
    async def identify(self):
        await self.send("identify", {"token": self.token})
        
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
            for coro in self.on_event:
                asyncio.create_task(coro(*args))
        
    async def send(self, type: str, data: dict):
        payload = {"type": type, "data": data}
        await self.ws.send(zlib.compress(orjson.dumps(payload)))
