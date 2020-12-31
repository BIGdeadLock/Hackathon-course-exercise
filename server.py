import socket 
import scapy.all as scapy
from offer import OfferPacket
from sender import Sender
import time
import random, os
import operator
from client_handler import ClientThread
from Configurations import server_configuration
try:
    from termcolor import colored
except ModuleNotFoundError:
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
        """
        The method will handle all the server port listening logic
        """
        # Open port for tcp connection from the client
        server_socket = socket.socket()

        server_socket.bind((server_configuration.LOCAL_IP, server_configuration.SERVER_PORT))
        server_socket.listen()

        print(colored(f"Server Started, listening on IP address {server_configuration.LOCAL_IP}",'yellow'))

        #  Socket configuration:
        server_socket.settimeout(server_configuration.SOCKET_TIMEOUT)
        server_socket.setblocking(server_configuration.SOCKET_NONBLOCKING)
        return server_socket

    def close_connection(self):
        """
        The method will close the tcp connection of the server.
        """
        self.__server_socket.close()

    def new_game(self):
        """
        The method will clear all the game configuration of each team
        """
        self.teams = {server_configuration.GROUP1_NUMBER: [], server_configuration.GROUP2_NUMBER: []}
        self.teams_score.clear()
        self.groups_score = {server_configuration.GROUP1_NUMBER: 0, server_configuration.GROUP2_NUMBER: 0}
        self.__game_threads.clear()        

    def send_game_offer_messages(self):
        """
        The method will start sending the configured game messages.
        """
        Sender(server_configuration.SERVER_PORT).start()

    def get_client(self) -> tuple:
        """
        The method will listen to an incoming client.
        return: Tuple. (Client socket, (client_ip, client_port), team name)
        IF the client did not give a team name - the team name will be None in the return
        """
        (socket_for_client, client_ip) = self.__server_socket.accept()
        data = socket_for_client.recv(2048)
        if not data: return (socket_for_client, client_ip, None)
        team_name = data.decode("ASCII").strip()

        return (socket_for_client, client_ip, team_name)

    def show_special_statistics(self):
        """
        The method will show some special statistics on the screen
        """
        #  Update best team in history if the team with best score scored higher
        max_current_team = max(self.teams_score.items(), key=operator.itemgetter(1))[0]
        if self.teams_score[max_current_team] > self.best_team[1]:
            self.best_team[1] = self.teams_score[max_current_team]
            self.best_team[0] = max_current_team

        #  Show most clicked character in server history
        max_charater = max(self.chars_presses.items(), key=operator.itemgetter(1))[0]
        print(colored(f"THE MOST CLICKED CHARACTER IN SERVER HISTORY: {max_charater}",'magenta', attrs=['underline']))
        print(colored(f"THE BEST TEAM IN SERVER'S HISTROY IS: {self.best_team[0]} with score of {self.best_team[1]}",'magenta', attrs=['underline']))
        print(colored("Game over, sending out offer requests...",'red'))

    def run_game(self):
        """
        The method will run the game logic
        """

        ##########################
        #  Start game algorithm:
        #     Send Offer packets for config.TIMEOUT seconds over UDP.
        #     Listen to incomming TCP packets over SERVER_PORT
        #     For each client open save the team name and create a new thread.
        #     For each client start the game in a new thread.
        #     Once every client f:inished playing start the process again
        ###########################
        while True:
            #  Start sending offer packets
            self.send_game_offer_messages()

            ######  TO AVOID BUSY WAITING ########
            time.sleep(server_configuration.BUSY_WAITING_AVOIDANCE)
            ######################################
            #  Listen to incomming sockets from the clients and handle each one
            self.__server_socket.settimeout(server_configuration.SOCKET_TIMEOUT)
            self.new_game()

            # Loop for config.TIMEOUT seconds waiting for new clinets. Once config.TIMEOUT seconds have passed
            # Timeout execption will be raised and the game will begin
            while True:
                try:
                    socket_for_client, __, team_name = self.get_client()
                    if not team_name:
                        continue
                    #  Save the client's team name to a random group
                    group = random.randint(server_configuration.GROUP1_NUMBER,server_configuration.GROUP2_NUMBER)
                    self.teams[group].append(team_name)
                    self.teams_score[team_name] = 0

                    thread = ClientThread(socket_for_client, server_configuration.SOCKET_TIMEOUT, team_name, group)
                    thread.set_game_setting(self.teams, self.groups_score, self.teams_score, self.chars_presses)
                    self.__game_threads.append(thread)

                    print(colored(f"Team {team_name} has conencted to the game","green"))

                except socket.timeout:
                    # config.TIMEOUT seconds have passed - Start the game
                    for thread in self.__game_threads:
                        thread.start()
                    
                    # Wait for all the players to finish
                    for thread in self.__game_threads:
                        thread.join()            
                    
                    self.show_special_statistics()
                    time.sleep(server_configuration.BUSY_WAITING_AVOIDANCE)
                    break

                except (ConnectionError, ConnectionResetError):
                    print(colored("Error occured, connection to the client was closed. Waiting for the next client",'red'))
                    continue


server = GameServer()
server.run_game()
server.close_connection()