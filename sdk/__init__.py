from websockets import connect as ws_connect
import zlib
import orjson


async def connect():
    ws = await ws_connect("wss://ugc.renorari.net/api/v1/gateway")
    client = Client(ws)
    
    
class Client:
    def __init__(self, ws):
        self.ws = ws
        
    async def recv(self):
        data = orjson.loads(zlib.decompress(await self.ws.recv()))
        if data["type"] == "hello":
            pass
        
    async def send(self, type: str, data: dict):
        payload = {"type": type, "data": data}
        await self.ws.send(zlib.compress(orjson.dumps(payload)))
