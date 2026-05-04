import time


class Printer:
    def __init__(self, c):
        self.sock = c
    def initilizePrinter(self):
        self.sock.send(b"\x1b\x40")

    def getPrinterStatus(self,):
        self.sock.send(b"\x1e\x47\x03")
    
    def getPrinterSerialNumber(self):
        self.sock.send(b"\x1D\x67\x39")
        return self.sock.recv(21)
    
    def getPrinterProductInfo(self):
        self.sock.send(b"\x1d\x67\x69")
    
    def sendStartPrintSequence(self):
        self.sock.send(b"\x1d\x49\xf0\x19")
    
    def sendEndPrintSequence(self):
        self.sock.send(b"\x0a\x0a\x0a\x0a")

    def sendHeartbeat(self):
        self.sock.send(b"\x00")
        
    def print(self, buf):
        self.initilizePrinter()
        time.sleep(.5)
        self.sendStartPrintSequence()
        time.sleep(.5)
        self.sock.send(buf)
        time.sleep(.5)
        self.sendEndPrintSequence()