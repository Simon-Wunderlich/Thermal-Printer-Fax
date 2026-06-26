from websockets.sync.server import serve

CLIENTS = set()


def handler(websocket):
    print("client joined")
    try:
        for message in websocket:
            if message == "client":
                CLIENTS.add(websocket)
            else:
                broadcastMessage(message)
    finally:
        try:
            CLIENTS.remove(websocket)
        except:
            pass


def main():
    with serve(handler, host="0.0.0.0", port=8765) as server:
        server.serve_forever()  # run forever


def broadcastMessage(message):
    print(message)
    # renderer = Renderer()
    # textImage = renderer.create_text(message)
    # buf = renderer.processImage(textImage)
    for x in CLIENTS:
        try:
            x.send(message)
        except:
            pass
    # broadcast(CLIENTS, message)


if __name__ == "__main__":
    main()
