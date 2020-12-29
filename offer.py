import struct

class OfferPacket:

    payload_size = struct.calcsize("Ibh")


    def __init__(self, port):
        self.tcp_port = port
        self.magic_cookie_bytes = int("0xfebedeef", 0)
        self.offer_bytes = int("0x2", 0)
        self.data = struct.pack("Ibh",self.magic_cookie_bytes, self.offer_bytes, self.tcp_port)
 

    def getData(self):
        return self.data

    @staticmethod
    def validatePacket(payload):
        """
        The method is used to validate that a packet is indeed an offer packet 
        """
        packed_msg_size = payload[:payload_size]
        magic_cookie, offer_type, port = struct.unpack('Ibh',packed_msg_size)

        if magic_cookie


x = OfferPacket(111)
x.data