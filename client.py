import socket
import threading
import time

import paho.mqtt.client as paho

from printer import Printer
from renderer import Renderer

lock = threading.Lock()
KEY = "70656e6973"

bt_address = "00:00:00:04:01:EA"
port = 1


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        client.subscribe(KEY + "/all", qos=1)
        print("we have siubrcregewd")


def on_message(client, userdata, msg):
    print(msg.payload.decode("utf-8"))
    msg = msg.payload.decode("utf-8")
    renderer = Renderer()
    textImage = renderer.create_text(msg)
    buf = renderer.processImage(textImage)
    send(buf)


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
    client.publish(KEY + "/all", payload="I see you an i appReciae you", qos=1)


client = paho.Client(paho.CallbackAPIVersion.VERSION2)
client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS)

client.on_connect = on_connect

client.on_message = on_message

client.on_subscribe = on_subscribe


client.connect("broker.hivemq.com", 8883)


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


def loooooop():
    client.loop_forever()


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


def send(data=None):
    with lock:
        # Header bytes etc
        printer = Printer(sock)
        if data:
            printer.print(data)
        else:
            printer.sendHeartbeat()
        time.sleep(5)


ka = threading.Thread(target=keepAlive)
cl = threading.Thread(target=closer)
lf = threading.Thread(target=loooooop)

print("Heartbeat started")
lf.start()
ka.start()
cl.start()
ka.join()
cl.join()
lf.join()
