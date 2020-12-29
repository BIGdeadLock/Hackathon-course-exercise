import socket 
import scapy.all as scapy
from threading import Thread
from offer import OfferPacket
from sender import Sender
import time


=======
# server_port = 13117
server_port = 13000
local_ip = scapy.get_if_addr("eth1")
sender = Sender(server_port)

#  Start sending offer packets
sender.start()

print("Welcome to Keyboard Spamming Battle Royale.\n Group 1:")
print("Start pressing keys on your keyboard as fast as you can!!")
=======
# Open port for tcp connection from the client
ServerSocket = socket.socket()
ServerSocket.bind((local_ip, server_port))
ServerSocket.listen()

#  Listen to incomming sockets from the clients and handle each one
while(True):
    print("St")
    (socket_for_client, client_ip) = ServerSocket.accept();
    print("client with IP address and port: %s"% client_ip);
    socket_for_client.close()





print("Game over! Group 1 typed in 104 characters. Group 2 typed in 28 characters."+
"Group 1 wins! Congratulations to the winners: =="+ "TEAMS")
