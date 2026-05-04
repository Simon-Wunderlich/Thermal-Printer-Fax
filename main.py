# # imgData = []
# # print(len(imgData))
# # for x in data:
# #     bits = f'{x:08b}'.replace(" ", "")
# #     uncompressedBits = bits[0] * int(bits[1:],2)
# #     print(bits)
# #     print(uncompressedBits)
# #     for bit in uncompressedBits:
# #         imgData.append(255 - int(bit) * 255)
# # width = 320
# # # while width <= 100:
# # height = math.ceil(len(imgData) / width)
# # print(height)
# # image = Image.new("L", (width, height))
# # image.putdata(imgData)
# # image.show()
# # width += 1
# #
import struct
import time

import PIL
from PIL import Image, ImageOps, ImageDraw, ImageFont
from bluedot.btcomm import BluetoothClient
from signal import pause
from time import sleep

printerWidth = 384

import subprocess

def connect_bluetooth(mac_address):
    # Piping the connect command directly to bluetoothctl
    cmd = f'echo "connect {mac_address}\nquit" | bluetoothctl'
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"Connection command sent to {mac_address}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to connect: {e}")

def pair_bluetooth(mac_address):
    # Piping the connect command directly to bluetoothctl
    cmd = f'echo "trust {mac_address}\npair {mac_address}\nquit" | bluetoothctl'
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"Connection command sent to {mac_address}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to connect: {e}")

def disconnect_bluetooth(mac_address):
    # Piping the connect command directly to bluetoothctl
    cmd = f'echo "remove {mac_address}\n" | bluetoothctl'
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"Connection command sent to {mac_address}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to connect: {e}")

def initilizePrinter(c):
    c.send(b"\x1b\x40")

def getPrinterStatus(c):
    c.send(b"\x1e\x47\x03")

def getPrinterSerialNumber(c):
    c.send(b"\x1D\x67\x39")
    return c.recv(21)

def getPrinterProductInfo(c):
    c.send(b"\x1d\x67\x69")

def sendStartPrintSequence(c):
    c.send(b"\x1d\x49\xf0\x19")

def sendEndPrintSequence(c):
    c.send(b"\x0a\x0a\x0a\x0a")


def trimImage(im):
    bg = PIL.Image.new(im.mode, im.size, (255,255,255))
    diff = PIL.ImageChops.difference(im, bg)
    diff = PIL.ImageChops.add(diff, diff, 2.0)
    bbox = diff.getbbox()
    if bbox:
        return im.crop((bbox[0],bbox[1],bbox[2],bbox[3]+10)) # don't cut off the end of the image

def create_text(text, font_name="Lucon.ttf", font_size=12):
    img = PIL.Image.new('RGB', (printerWidth, 5000), color = (255, 255, 255))
    font = ImageFont.truetype(font_name, font_size)

    d = ImageDraw.Draw(img)
    lines = []
    for line in text.splitlines():
        lines.append(get_wrapped_text(line, font, printerWidth))
    lines = "\n".join(lines)
    d.text((0,0), lines, fill=(0,0,0), font=font)
    return trimImage(img)

def get_wrapped_text(text: str, font: PIL.ImageFont.ImageFont,
                     line_length: int):
    lines = ['']
    for word in text.split():
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            lines.append(word)
    return '\n'.join(lines)


def printImage(c, im):
    if im.width > printerWidth:
        # image is wider than printer resolution; scale it down proportionately
        height = int(im.height * (printerWidth / im.width))
        im = im.resize((printerWidth, height))

    if im.width < printerWidth:
        # image is narrower than printer resolution; pad it out with white pixels
        padded_image = PIL.Image.new("1", (printerWidth, im.height), 1)
        padded_image.paste(im)
        im = padded_image

    im = im.rotate(180) #print it so it looks right when spewing out of the mouth

    # if image is not 1-bit, convert it
    if im.mode != '1':
        im = im.convert('1', dither=Image.FLOYDSTEINBERG)


    # if image width is not a multiple of 8 pixels, fix that
    if im.size[0] % 8:
        im2 = Image.new('1', (im.size[0] + 8 - im.size[0] % 8,
                              im.size[1]), 'white')
        im2.paste(im, (0, 0))
        im = im2



    # Invert image, via greyscale for compatibility
    #  (no, I don't know why I need to do this)
    im = ImageOps.invert(im.convert('L'))
    # ... and now convert back to single bit
    im = im.convert('1')

    buf = b''.join((bytearray(b'\x1d\x76\x30\x00'),
                    struct.pack('2B', int(im.size[0] / 8 % 256),
                                int(im.size[0] / 8 / 256)),
                    struct.pack('2B', int(im.size[1] % 256),
                                int(im.size[1] / 256)),
                    im.tobytes()))

    print("Printing")

    initilizePrinter(c)
    sleep(.5)
    sendStartPrintSequence(c)
    sleep(.5)
    c.send(buf)
    sleep(.5)
    sendEndPrintSequence(c)



# Callback to handle data
def data_received(data):
    print(data)
    sleep(0.5)
    c.send("X\n")

def connect():
    while True:
        try:
            c = BluetoothClient("YHK-0E60", data_received, encoding=None)
            return c
        except Exception as e:
            print(e)
            pair_bluetooth("00:00:00:04:0E:60")
            sleep(10)

# Make connection and establish serial connection
# connect_bluetooth("00:00:00:04:0E:60")
# time.sleep(20)
# c = connect()

# Send initial requests
print("Connecting to printer...")
# getPrinterStatus(c)
# sleep(0.5)
# getPrinterSerialNumber(c)
# sleep(0.5)
# getPrinterProductInfo(c)
# sleep(0.5)

img = PIL.Image.open("horse.png")
c = BluetoothClient("YHK-0E60", data_received, encoding=None)

printImage(c, img)

while True:
    text = input("> ")
    if (text == "disconnect"):
        c.disconnect()
        exit()
    printImage(c,create_text(text, font_size=32))
    # c.disconnect()
# print("Connecting")
# c = connect()
c = BluetoothClient("YHK-0E60", data_received, encoding=None)
print("Printing")
printImage(c,img)
# c.disconnect()
# input()
# print("Connecting")
# c = connect()
# print("Printing")
# printImage(c,img)
# c.disconnect()
# input()
# c = connect()
# printImage(c,img)
# disconnect_bluetooth("00:00:00:04:0E:60")