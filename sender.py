from threading import Thread
from offer import OfferPacket
import socket
import time

class Sender(Thread):

    def __init__(self, Port):
        Thread.__init__(self)
        self.__port_number = Port
        self.offer_packet = OfferPacket(Port)
        self.TIME_LIMIT = 10

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.settimeout(10)
        
        now = time.time()
        future = now + 10

        while time.time() < future:
            server.sendto(self.offer_packet.getData(), ('<broadcast>', self.__port_number))
            print("message sent")
            time.sleep(1)
        