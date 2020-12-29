import socket 
import scapy.all as scapy
from offer import OfferPacket
from sender import Sender
import time
import random
from KeyboardHandler import run_game
from threading import Thread
from termcolor import colored


class ClientThread(Thread):

    def __init__(self, connection, time):
        Thread.__init__(self)
        self.connection = connection
        self.time_left = time
        self.team_name = ""
        self.group = 0

    def run(self):
        # The servers waits for 10 seconds and than send the message to all the clients
        self.connection.settimeout(self.time_left)
        while True:
            try:
                data = self.connection.recv(2048)
                if not data: break
                self.team_name = data.decode("ASCII")
                #  Save the client's team name to a random group
                choice = random.randint(1,2)
                self.group = choice
                teams[choice].append(self.team_name)

            except socket.timeout:
                break
            
            except (ConnectionError, ConnectionResetError):
                print(colored(f"Clinet {self.team_name} closed the connection","red"))
                return None

        teams_score[self.team_name] = 0

        self.connection.sendall(get_welcome_message().encode("utf-8"))
        now = time.time()
        stop_typing = True
        while True:
            try:
                char = self.connection.recv(1024)
                if not char:
                    continue

                print(char)
                char = char.decode("ASCII")

                teams_score[self.team_name] += 1
                groups_score[self.group] += 1

                # Used for bonus - statistics over each char pressed
                if char not in chars_presses:
                    chars_presses[char] = 1
                else:
                    chars_presses[char] += 1
            
                if (time.time() - now <= 1) and stop_typing:
                    self.connection.sendall("\nSTOP TYPING!!\nCALCULATING THE SCORES...".encode("utf-8"))
                    stop_typing = False
                    
            except socket.timeout:
                team_message, group_message = get_end_game_message(teams_score[self.team_name],
                groups_score[self.group],groups_score[get_rival_group_number(self.group)])

                self.connection.sendall(team_message.encode("utf-8"))
                self.connection.sendall(group_message.encode("utf-8"))
                break
            
            except (ConnectionError, ConnectionResetError):
                return None

        self.connection.close()


def get_welcome_message():
    messages = "Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n"

    for team in teams[1]:
        messages+= f"{team}"

    messages += "Group 2:\n==\n"
    for team in teams[2]:
        messages+= f"{team}"

    messages+="\n"
    messages+="Start pressing keys on your keyboard as fast as you can!!"

    return messages



def get_end_game_message(team_number_of_chars, group_score, other_group_score):
    winner_id = get_winner()
    team_message = f"\nYou pressed {team_number_of_chars} characters"
    if team_number_of_chars <= 100:
        team_message+="\nAre you even trying?\n\n"
    if team_number_of_chars > 100 and team_number_of_chars <= 150:
        team_message+="\nPoor Effort! Get Better!\n\n"
    if team_number_of_chars > 150 and team_number_of_chars <= 250:
       team_message+="\nGreat Job!\n\n"
    if team_number_of_chars > 250:
        team_message+="\nFANTASTIC! YOU ARE A PRO\n\n"

    group_message = "Game Over!\n"
    group_message += f"Your group typed {group_score} characters. \n"
    group_message += f"Your rival group typed {other_group_score} characters. \n"
    if winner_id == 0:
        group_message += "ITS A DRAW!\n\n"
    else:
        group_message += f"Group {winner_id} wins! \n\n"
        group_message += "Congratulations to the winners:\n"
        group_message += "==\n"
        for team in teams[winner_id]:
            group_message+= f"{team}"

    return team_message, group_message

def get_winner():
    first_score = groups_score[1]
    second_score = groups_score[2]

    if first_score > second_score:
        return 1
    elif first_score < second_score:
        return 2
    else:
        return 0

def get_rival_group_number(my_group):
    if my_group == 1:
        return 2
    else:
        return 1

def new_game():
    global teams, teams_score, groups_score, game_threads
    teams = {1: [], 2: []}
    teams_score.clear()
    groups_score = {1: 0, 2: 0}
    game_threads.clear()
    
# server_port = 13117
server_port = 13000
local_ip = scapy.get_if_addr(scapy.conf.iface)
#sender = Sender(server_port)
game_threads = []

######## Game variables ########
teams = {1: [], 2: []}
teams_score = {}
groups_score = {1: 0, 2: 0}
chars_presses = {}
best_team = (0,0)
######## Game variables ########


# #  Start sending offer packets
# sender.start()

# Open port for tcp connection from the client
ServerSocket = socket.socket()
ServerSocket.bind((local_ip, server_port))
ServerSocket.listen()
print(colored(f"Server Started, listening on IP address {local_ip}",'yellow'))

#  Listen to incomming sockets from the clients and handle each one
ServerSocket.settimeout(10)
future = time.time() + 10

    
while True:
    
    #  Start sending offer packets
    Sender(server_port).start()

    # # Open port for tcp connection from the client
    # ServerSocket = socket.socket()
    # ServerSocket.bind((local_ip, server_port))
    # ServerSocket.listen()

    #  Listen to incomming sockets from the clients and handle each one
    ServerSocket.settimeout(10)
    future = time.time() + 10
    while True:
        new_game()
        try:
            (socket_for_client, client_ip) = ServerSocket.accept()
            t = future - time.time()
            print(f"client with IP address and port: {client_ip}" )
            thread = ClientThread(socket_for_client, t)
            game_threads.append(thread)
            thread.start()

        except socket.timeout:
            for thread in game_threads:
                print("waiting for threads")
                thread.join()
            
            print(colored("Game over, sending out offer requests...",'red'))
            break



ServerSocket.close()