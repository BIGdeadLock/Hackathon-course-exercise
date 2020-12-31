import socket
import struct
from offer import OfferPacket
import scapy.all as scapy
import time 
import sys, select
from Configurations import client_configuration


try:
    #USED FOR LINUX
    import getch
except ModuleNotFoundError:
    #USED FOR WINDOWS
    import msvcrt

class GameClient:

    def __init__(self):
        # Listen for broadcast of UDP from the server
        print('Client started, listening for offer requests...')
        self.client_offer_socket = self.start_listening()
        self.client_tcp_socket = None

    def run_game(self):
        """
        The method will run the game logic
        """
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
                    char = getch.getch()
                    self.client_tcp_socket.sendall(char.encode('utf-8'))
                ####################

                except NameError:
                    #################
                    #  USED FOR WINDOWS
                    char = msvcrt.getch()
                    self.client_tcp_socket.sendall(char)
                    ####################

            except (ConnectionResetError , TimeoutError , OSError):
                print("CONNECTION ERROR")
                #exit the game -> handler will catch in the calling function
                return None

    def start_listening(self):
        """
        The method will handle all the client port listening logic
        """
        #creating new socket for the udp connection
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 

        # Enable broadcasting mode
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        client.bind(("", client_configuration.SERVER_DEST_PORT))
        return client

    def get_game_details(self): 
            '''
            The method will retrieve the details for playing the game: port, data and address from the server
            '''
            data, addr = None, None
            while not data:
                data, addr = self.client_offer_socket.recvfrom(1024)

            if len(data) < client_configuration.PAYLOAD_SIZE:
                if not data:
                    # client closed after last message, assume all is well
                    print("Client Closed")
                    return None, 0
                else:
                    # raise IOError("Truncated message")
                    print("Truncated message")
                    return None, 0 

            #check if the data received is indeed the offer packet desired
            if not OfferPacket.validate_packet(data):
                print("Recieved a message which is not an offer message. Please try sending again")
                return None, 0

            port = OfferPacket.get_port_from_data(data)
            return port, addr
        

    def game_handler(self):
        '''
        The method will handle the connection with the server: receive, send messages and invoke the game running 
        '''
        while True:
            try:
                port, addr = self.get_game_details()
                if port == None:
                    continue
                #connect to the sever with the given port
                print(f"Received offer from {addr[0]}, attempting to connect...")
                self.client_tcp_socket = socket.socket(); 
                self.client_tcp_socket.connect((addr[0], port))
                print("Connection Established")
                
                #establish my team name and send it to the server
                self.client_tcp_socket.sendall(client_configuration.TEAM_NAME.encode('utf-8'))

                #get the welcome message from the server and print to the screen
                welcome_message = self.client_tcp_socket.recv(1024*4).decode("ASCII")
                print(welcome_message)

                self.client_tcp_socket.settimeout(client_configuration.SOCKET_TIMEOUT)
                #run the game and press as many keys as you can
                client.run_game()

                #get the end message from the server for the score outcomes and print to the screen
                while True:
                    end_messages = self.client_tcp_socket.recv(1024*4).decode("ASCII")
                    if not end_messages:
                        time.sleep(5)
                        #game has ended, server stopped sending messages -> close the connection
                        client.close_connection()
                        break
                    print(end_messages)
                
            except (ConnectionResetError , TimeoutError , OSError, ConnectionRefusedError):                
                print("Server disconnected, listening for offer requests...")
                self.client_offer_socket = self.start_listening()
                continue
        
            except socket.timeout:
                print("Connection time out, trying to reconnect..")
                continue

    def close_connection(self):
        """
        The method will close the tcp connection of the server.
        """
        self.client_tcp_socket.close()

client = GameClient()
client.game_handler()