import datetime
import json
import os
import random
import select
import socket
import threading
import time

import paho.mqtt.client as paho
from dotenv import load_dotenv

from printer import Printer
from renderer import Renderer

load_dotenv()

lock = threading.Lock()
KEY = "70656e6973"

bt_address = os.getenv("BT_ADDRESS")
port = 1
btConnected = False

sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)


def connectBT():
    global sock
    global btConnected
    while not btConnected:
        try:
            sock = socket.socket(
                socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
            )
            sock.connect((bt_address, port))
            print("Connected")
            btConnected = True
            sendQueue()
        except Exception as e:
            btConnected = False
            print("Connection failed", e)
            time.sleep(1)


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        client.subscribe(KEY + "/all", qos=1)
        client.subscribe(str(KEY) + str(os.getenv("TOPIC")), qos=1)
        print(str(KEY) + str(os.getenv("TOPIC")))
        print("Subscribed")


def on_disconnect(client, userdata, flags, reason_code, properties=None):
    client.connect("broker.hivemq.com", 8883)


def send_confirm(type):
    print("sending repluy")
    send = {"topic": os.getenv("TOPIC"), "type": type}
    client.publish(KEY + "/acknowledge", json.dumps(send), qos=1)


def on_message(client, userdata, msg):
    msg = msg.payload.decode("utf-8")
    if len(msg) == 0:
        return
    id = random.randint(1111, 9999)
    message = json.loads(msg)

    payload = {"id": id, "msg": message}
    if not btConnected:
        send_confirm("q")
        with open("queue.json", "r") as f:
            queue = json.load(f)
            if queue == None:
                queue = []
            queue.append(payload)
        with open("queue.json", "w") as f:
            json.dump(queue, f, indent=4)
    else:
        send_confirm("p")
    renderer = Renderer()
    textImage = renderer.createBody(message)
    buf = renderer.getBuffer(textImage)
    print("Sending message", message["msg"])
    send(buf)

    with open("queue.json", "r") as f:
        queue = json.load(f)
        if queue == None:
            queue = []
        if payload in queue:
            queue = queue.remove(payload)
    with open("queue.json", "w") as f:
        json.dump(queue, f, indent=4)


client = paho.Client(paho.CallbackAPIVersion.VERSION2)
client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS)

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message


client.connect("broker.hivemq.com", 8883)


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
    global btConnected
    while True:
        time.sleep(5)
        if not btConnected:
            connectBT()
        try:
            select.select(
                [
                    sock,
                ],
                [
                    sock,
                ],
                [],
                5,
            )
            send()
        except:
            try:
                sock.shutdown(2)
                sock.close()
            except:
                print("something went wrong")

            print("Reconnecting...", datetime.datetime.now())
            btConnected = False
            connectBT()


def send(data=None):
    with lock:
        # Blocks lock while not connected
        while not btConnected:
            pass
        # Header bytes etc
        printer = Printer(sock)
        if data:
            printer.print(data)
        else:
            printer.sendHeartbeat()
        time.sleep(5)


def sendQueue():
    print("sending queue")
    renderer = Renderer()

    with open("queue.json", "r") as f:
        queue = json.load(f)
        if queue == None:
            queue = []
    if not queue:
        return
    for message in queue:
        textImage = renderer.createBody(message["msg"])
        buf = renderer.processImage(textImage)
        send(buf)

    with open("queue.json", "w") as f:
        json.dump([], f, indent=4)


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
