import json
import threading

import paho.mqtt.client as paho


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        client.subscribe("70656e6973/acknowledge", qos=1)
        client.subscribe("70656e6973/all", qos=1)
        print("Subscribed")


def on_disconnect(client, userdata, flags, reason_code, properties=None):
    client.connect("broker.hivemq.com", 8883)


def on_message(client, userdata, msg):
    msg = msg.payload.decode("utf-8")
    message = json.loads(msg)
    print(message)


client = paho.Client(paho.CallbackAPIVersion.VERSION2)
client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.connect("broker.hivemq.com", 8883)
print("starting")


def loooooop():
    client.loop_forever()


lf = threading.Thread(target=loooooop)
lf.start()
lf.join()
