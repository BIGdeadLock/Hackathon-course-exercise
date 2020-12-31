import struct

class OfferPacket:
    '''
    The class is to create and wrap the fields making the offer packet message
    '''

    #packet size
    payload_size = struct.calcsize("Ibh")
    
    #create fields for the offer packet
    tcp_port = None
    magic_cookie_bytes = int("0xfeedbeef", 0)
    offer_bytes = int("0x2", 0)

    def __init__(self, port):
        OfferPacket.tcp_port = port
        self.data = struct.pack("Ibh",self.magic_cookie_bytes, self.offer_bytes, self.tcp_port)
 
    def getData(self):
        return self.data

    @staticmethod
    def validate_packet(payload):
        """
        The method is used to validate that a packet is indeed an offer packet 
        """
        packed_msg_size = payload[:OfferPacket.payload_size]
        magic_cookie, offer_type, _ = struct.unpack('Ibh',packed_msg_size)
        
        if magic_cookie != OfferPacket.magic_cookie_bytes:
            return False
        elif offer_type != OfferPacket.offer_bytes:
            return False
        
        return True
   
    @staticmethod
    def get_port_from_data(payload):
        packed_msg_size = payload[:OfferPacket.payload_size]
        _, _, port = struct.unpack('Ibh',packed_msg_size)
        return port