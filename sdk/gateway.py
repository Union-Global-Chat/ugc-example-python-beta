from websockets import connect, WebSocketClientProtocol

from typing import Optional

try:
    import orjson as json
except ImportError:
    import json
import zlib


class UgcGateway:
    
    GATEWAY_URL: str = "wss://ugc.renorari.net/api/v2/gateway"
    def __init__(self):
        self.ws: Optional[WebSocketClientProtocol] = None

    async def connect(self):
        self.ws = await connect(self.GATEWAY_URL)

    async def recieve_message(self):
        payload = json.loads(zlib.decompress(await self.ws.recv()))

        if payload["type"] == "identify":
            self.heartbeat = HeartBeat(ws=self.ws)

    def close(self):
        return self.ws.close()
