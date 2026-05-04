import socket
import threading
import time
from websockets.sync.client import connect

from printer import Printer
from renderer import Renderer

lock = threading.Lock()

bt_address = "00:00:00:04:0E:60"
port = 1

ws_address = "ws://test.sorry.horse:8765"

sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
sock.connect((bt_address, port))

renderer = Renderer
def closer():
    input()
    close()
def close():
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        # Handle cases where the socket is already disconnected
        pass
    finally:
        sock.close()
        exit()

def keepAlive():
    while True:
        try:
            send()
        except:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                # Handle cases where the socket is already disconnected
                pass
            finally:
                sock.close()
                exit()

def recMsg():
    with connect(ws_address, ping_timeout=None) as websocket:
        for x in range(3):
            msg = websocket.recv()
            send(msg)

        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            # Handle cases where the socket is already disconnected
            pass
        finally:
            sock.close()
            exit()


def send(data = None):
    with lock:
        # Header bytes etc
        printer = Printer(sock)
        if data:
            printer.print(data)
        else:
            printer.sendHeartbeat()
        time.sleep(5)

ka = threading.Thread(target=keepAlive)
ws = threading.Thread(target=recMsg)
cl = threading.Thread(target=closer)

print("Heartbeat started")
ka.start()
print("Websocket started")
ws.start()
cl.start()
ka.join()
ws.join()
cl.join()