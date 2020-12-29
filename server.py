import socket 
import scapy.all as scapy
from offer import OfferPacket
from sender import Sender
import time
import random
from KeyboardHandler import run_game
from threading import Thread


class ClientThread(Thread):

    def __init__(self, connection, time):
        Thread.__init__(self)
        # self.ip = ip
        # self.port = port
        self.connection = connection
        self.time_left = time

    def run(self):

        # The servers waits for 10 seconds and than send the message to all the clients
        self.connection.settimeout(self.time_left)
        while True:
            try:
                data = self.connection.recv(2048)
                if not data: break
                print(data.decode("ASCII"))
                #  Save the client's team name to a random group
                choice = random.randint(1,2)
                teams[choice].append(data.decode("ASCII"))
            except socket.timeout:
                break


        self.connection.sendall(get_welcome_message().encode("utf-8"))

        self.
        self.connection.close()

def get_welcome_message():
    messages = "Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n"

    for team in teams[1]:
        messages+= f"{team}"

    messages += "Group 2:\n==\n"
    for team in teams[2]:
        messages+= f"{team}"

    messages+="\n"
    return messages


# server_port = 13117
server_port = 13000
local_ip = scapy.get_if_addr(scapy.conf.iface)
sender = Sender(server_port)

teams = {1: [], 2: []}
#  Start sending offer packets
sender.start()

# Open port for tcp connection from the client
ServerSocket = socket.socket()
ServerSocket.bind((local_ip, server_port))
ServerSocket.listen()

#  Listen to incomming sockets from the clients and handle each one
ServerSocket.settimeout(10)
future = time.time() + 10
while True:
    try:
        print(f"Server Started, listening on IP address {local_ip}")
        (socket_for_client, client_ip) = ServerSocket.accept()
        t = future - time.time()
        print(f"client with IP address and port: {client_ip}" )

        ClientThread(socket_for_client, t).start()

    except socket.timeout:
        break


ServerSocket.close()

run_game()





print("Game over! Group 1 typed in 104 characters. Group 2 typed in 28 characters."+
"Group 1 wins! Congratulations to the winners: =="+ "TEAMS")
