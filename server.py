import socket 
import scapy.all as scapy
from offer import OfferPacket
from sender import Sender
import time
import random, os
import operator
from threading import Thread, Lock
from game_messages import get_end_game_message, get_welcome_message
from client_handler import ClientThread
from server_configuration import SERVER_PORT, LOCAL_IP
try:
    from termcolor import colored
except ModuleNotFoundError as i:
    os.system("pip3 install termcolor")
finally:
    from termcolor import colored


class GameServer:

    def __init__(self):

        ######## Game variables ########
        self.teams = {1: [], 2: []}
        self.teams_score = {}
        self.groups_score = {1: 0, 2: 0}
        self.chars_presses = {}
        self.best_team = [0,0]
        ######## Game variables ########

        ####### PROTECTED ATTRIBUTES #######
        self.__game_threads = []
        self.__server_socket = self.start_listening()
        ##############################

    def start_listening(self):

        # Open port for tcp connection from the client
        server_socket = socket.socket()

        server_socket.bind((LOCAL_IP, SERVER_PORT))
        server_socket.listen()

        print(colored(f"Server Started, listening on IP address {LOCAL_IP}",'yellow'))

        #  Listen to incomming sockets from the clients and handle each one
        server_socket.settimeout(10)
        server_socket.setblocking(0)
        return server_socket

    def close_connection(self):
        self.__server_socket.close()

    def new_game(self):
        self.teams = {1: [], 2: []}
        self.teams_score.clear()
        self.groups_score = {1: 0, 2: 0}
        self.__game_threads.clear()

    def run_game(self):
        ##########################
        #  Start game algorithm 
        #     Send Offer packets for 10 seconds over UDP.
        #     Listen to incomming TCP packets over SERVER_PORT
        #      For each client open save the team name and create a new thread.
        #      For each client start the game in a new thread.
        #     Once every client finished playing start the process again
        ###########################
        while True:
            #  Start sending offer packets
            Sender(SERVER_PORT).start()

            #  Listen to incomming sockets from the clients and handle each one
            self.__server_socket.settimeout(10)
            self.new_game()

            # Loop for 10 seconds waiting for new clinets. Once 10 seconds have passed
            # Timeout execption will be raised and the game will begin
            while True:
                try:
                    (socket_for_client, client_ip) = self.__server_socket.accept()
                    print(f"client with IP address and port: {client_ip}" )
                    data = socket_for_client.recv(2048)
                    if not data: continue
                    team_name = data.decode("ASCII").strip()
                    #  Save the client's team name to a random group
                    choice = random.randint(1,2)
                    group = choice
                    self.teams[choice].append(team_name)
                    self.teams_score[team_name] = 0

                    thread = ClientThread(socket_for_client, 10, team_name, group)
                    thread.set_game_setting(self.teams, self.groups_score, self.teams_score, self.chars_presses)
                    self.__game_threads.append(thread)

                    print(colored(f"Team {team_name} has conencted to the game","green"))

                except socket.timeout:
                    # 10 seconds have passed - Start the game
                    for thread in self.__game_threads:
                        thread.start()
                    
                    # Wait for all the players to finish
                    for thread in self.__game_threads:
                        thread.join()            
                    
                    #update best team in history if the team with best score scored higher
                    max_current_team = max(self.teams_score.items(), key=operator.itemgetter(1))[0]
                    if self.teams_score[max_current_team] > self.best_team[1]:
                        self.best_team[1] = self.teams_score[max_current_team]
                        self.best_team[0] = max_current_team

                    #show most clicked character in server history
                    max_charater = max(self.chars_presses.items(), key=operator.itemgetter(1))[0]
                    print(colored(f"THE MOST CLICKED CHARACTER IN SERVER HISTORY: {max_charater}",'magenta', attrs=['underline']))
                    print(colored("Game over, sending out offer requests...",'red'))
                    time.sleep(2)
                    break

                except (ConnectionError, ConnectionResetError):
                    print(colored("Error occured, connection to the client was closed. Waiting for the next client",'red'))
                    continue


server = GameServer()
server.run_game()
server.close_connection()