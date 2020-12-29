import socket 
from threading import Thread
from offer import OfferPacket
from sender import Sender
import time

server_port = 13117

pk = OfferPacket(server_port)
sender = Sender(server_port)

#  Start sending offer packets
sender.start()



