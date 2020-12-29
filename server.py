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

print("Welcome to Keyboard Spamming Battle Royale.\n Group 1:")
print("Start pressing keys on your keyboard as fast as you can!!")

print("Game over! Group 1 typed in 104 characters. Group 2 typed in 28 characters."+
"Group 1 wins! Congratulations to the winners: =="+ "TEAMS")
