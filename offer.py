import struct

class OfferPacket:

    def __init__(self, port):
        self.tcp_port = port
        self.magic_cookie_bytes = int("0xfebedeef", 0)
        self.offer_bytes = int("0x2", 0)
        self.data = struct.pack("IBh",self.magic_cookie_bytes, self.offer_bytes, self.tcp_port)
 

    def getData(self):
        return self.data

x = OfferPacket(111)
x.data