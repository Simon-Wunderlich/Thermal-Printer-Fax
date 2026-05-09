import websockets
from websockets import broadcast
from websockets.sync.server import serve
from renderer import Renderer
import threading

CLIENTS = set()

async def handler(websocket):
    CLIENTS.add(websocket)
    try:
        async for message in websocket:
            await broadcastMessage(message)
    finally:
        CLIENTS.remove(websocket)

def main():
    with serve(handler, host="0.0.0.0", port=8765) as server:
       server.serve_forever()  # run forever

def broadcastMessage(message):
    renderer = Renderer()
    textImage = renderer.create_text(message)
    buf = renderer.processImage(textImage)
    broadcast(CLIENTS, buf)


if __name__ == "__main__":
   main()

