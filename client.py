import socket
import struct
from offer import OfferPacket
import scapy.all as scapy
import time 
#import getch
import msvcrt
def run_game():
    #Game runs for 10 seconds
    now = time.time()
    future = now + 10

    char =""
    hurry = True
    stop =True
    while time.time() < future:
        try:
            #char = getch.getch()#.decode('ASCII')
            #client.sendall(char.encode('utf-8'))
            char = msvcrt.getch()#.decode('ASCII')
            client.sendall(char)
            if future - time.time() <= 3 and hurry:
                hurry = False
                print("Hurry!! You have less than 3 seconds left!!")
            if future - time.time() <= 1 and stop:
                stop = False
                print("STOP TYPING!!\nCalculating scores...")
                break
        except ConnectionResetError:
            print("Connection RESET ERROR")
            return None

serverName='serverName'
#server_port = 13117
server_port = 13000

offer = OfferPacket(server_port)
# Listen for broadcast of UDP from the server
print('Client started, listening for offer requests...')
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 

# Enable broadcasting mode
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

payload_size = OfferPacket.payload_size
local_ip = scapy.get_if_addr(scapy.conf.iface)

client.bind(("", server_port))
while True:
    try:
        data, addr = None, None
        while not data:
            data, addr = client.recvfrom(1024)

        if len(data) < payload_size:
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
        print(port)
        print(f"Received offer from {addr[0]}, attempting to connect...")
        client = socket.socket(); 
        client.connect((addr[0], port))
        print("Connection Established")
        

        #establish my team name and send it to the server
        team_name ="EDEN\n"
        client.sendall(team_name.encode('utf-8'))

        #get the welcome message from the server and print to the screen
        welcome_message = client.recv(1024*4).decode("ASCII")
        print(welcome_message)

        client.settimeout(10)

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
            
    except (ConnectionResetError , TimeoutError , OSError):
        print("Server disconnected, listening for offer requests...")
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
        # Enable broadcasting mode
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.bind(("", server_port))
        continue
    # except TimeoutError:
    #     print("Connection Time out")
    #     client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
    #     # Enable broadcasting mode
    #     client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    #     client.bind(("", server_port))
    #     continue
    except socket.timeout:
        print("Connection time out")
        continue