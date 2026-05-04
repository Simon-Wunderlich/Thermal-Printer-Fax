import asyncio

import websockets
from websockets import broadcast

from renderer import Renderer

CLIENTS = set()

async def handler(websocket):
    CLIENTS.add(websocket)
    renderer = Renderer()
    while True:
        text = input("> ")
        textImage = renderer.create_text(text)
        buf = renderer.processImage(textImage)
        broadcast(CLIENTS, buf)
    # try:
    #     async for message in websocket:
    #         await websocket.send(f"Echo: {message}")
    # finally:
    #     CLIENTS.remove(websocket)

async def main():
    async with websockets.serve(handler, host="0.0.0.0", port=8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
