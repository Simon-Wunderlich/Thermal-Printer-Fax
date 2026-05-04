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
            await websocket.send(f"Echo: {message}")
    finally:
        CLIENTS.remove(websocket)

def main():
    with serve(handler, host="0.0.0.0", port=8765) as server:
       server.serve_forever()  # run forever

def broadcastMessage():
    renderer = Renderer()
    while True:
        text = input("> ")
        textImage = renderer.create_text(text)
        buf = renderer.processImage(textImage)
        broadcast(CLIENTS, buf)


if __name__ == "__main__":
   ws = threading.Thread(target=main)
   bc = threading.Thread(target=broadcastMessage)
   ws.start()
   bc.start()
   ws.join()
   bc.join()

