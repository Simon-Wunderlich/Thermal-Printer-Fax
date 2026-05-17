import socket
import threading
import time

from websockets.sync.client import connect

from printer import Printer
from renderer import Renderer

bt_address = "00:00:00:04:01:EA"
port = 1

sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
sock.connect((bt_address, port))
