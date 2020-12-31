import socket
import struct
from offer import OfferPacket
import scapy.all as scapy
import time 
import sys, select
from Configurations.client_configuration import PAYLOAD_SIZE, LOCAL_IP, SERVER_DEST_PORT, TEAM_NAME

try:
    #USED FOR LINUX
    import getch
except ModuleNotFoundError:
    #USED FOR WINDOWS
    import msvcrt

def run_game():

    #Game runs for 10 seconds
    now = time.time()
    future = now + 10

    char =""
    while time.time() < future:
        #  START CATCHING KEYBOARD HIT FROM THE USER
        try:
            #################
            #  USED FOR LINUX
            try:
                char = getch.getch()#.decode('ASCII')
                client.sendall(char.encode('utf-8'))
            ####################

            except NameError:
                #################
                #  USED FOR WINDOWS
                char = msvcrt.getch()
                client.sendall(char)
                ####################

        except (ConnectionResetError , TimeoutError , OSError):
            print("CONNECTION ERROR")
            return None

# Listen for broadcast of UDP from the server
print('Client started, listening for offer requests...')
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 

# Enable broadcasting mode
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

client.bind(("", SERVER_DEST_PORT))
while True:
    try:
        data, addr = None, None
        while not data:
            data, addr = client.recvfrom(1024)

        if len(data) < PAYLOAD_SIZE:
            if not data:
                # client closed after last message, assume all is well
                print("Client Closed")
                continue
            else:
                # raise IOError("Truncated message")
                print("Truncated message")
                continue

        #check if the data received is indeed the offer packet desired
        if not OfferPacket.validate_packet(data):
            print("Recieved a message which is not an offer message. Please try sending again")
            continue

        port = OfferPacket.get_port_from_data(data)
        print(f"Received offer from {addr[0]}, attempting to connect...")
        client = socket.socket(); 
        client.connect((addr[0], port))
        print("Connection Established")
        

        #establish my team name and send it to the server
        client.sendall(TEAM_NAME.encode('utf-8'))

        #get the welcome message from the server and print to the screen
        welcome_message = client.recv(1024*4).decode("ASCII")
        print(welcome_message)

        client.settimeout(50)

        #run the game and press as many keys as you can
        run_game()

        #get the end message from the server for the score outcomes and print to the screen
        while True:
            end_messages = client.recv(1024*4).decode("ASCII")
            if not end_messages:
                time.sleep(5)
                client.close()
                break
            print(end_messages)
            
    except (ConnectionResetError , TimeoutError , OSError, ConnectionRefusedError) as e:
        print("Server disconnected, listening for offer requests...")
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
        # Enable broadcasting mode
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.bind(("", SERVER_DEST_PORT))
        continue
 
    except socket.timeout:
        print("Connection time out")
        continue