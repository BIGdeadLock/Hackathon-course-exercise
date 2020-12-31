from threading import Thread
from Configurations.offer import OfferPacket
from Configurations.server_configuration import SOCKET_TIMEOUT
import socket
import time

class Sender(Thread):

    def __init__(self, Port):
        Thread.__init__(self)
        self.__port_number = Port
        self.offer_packet = OfferPacket(Port)
        self.TIME_LIMIT = SOCKET_TIMEOUT

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.settimeout(SOCKET_TIMEOUT)
        
        now = time.time()
        future = now + SOCKET_TIMEOUT

        while time.time() < future:
            server.sendto(self.offer_packet.getData(), ('<broadcast>', self.__port_number))
            print("Sending offer messages")
            time.sleep(1)
        