import socket 
import scapy.all as scapy
from offer import OfferPacket
from sender import Sender
import time
import random
from threading import Thread, Lock
from termcolor import colored

lock = Lock()

class ClientThread(Thread):

    def __init__(self, connection, game_time, team_name, group_id):
        Thread.__init__(self)
        self.connection = connection
        # self.connection.setblocking(0)
        self.time_left = game_time
        self.team_name = team_name
        self.group = group_id
    
        

    def run(self):
        global teams, groups_score, teams_score
        # The servers waits for 10 seconds and than send the message to all the clients
        self.connection.settimeout(self.time_left)
        # while True:
        #     try:
        #         data = self.connection.recv(2048)
        #         if not data: break
        #         self.team_name = data.decode("ASCII").strip()
        #         #  Save the client's team name to a random group
        #         choice = random.randint(1,2)
        #         self.group = choice
        #         # with lock:
        #         #     print(self.team_name)
        #         #     self.test.append(self.team_name)
        #         #     teams[choice].append(self.test[0])
        #         #     print(teams)
        #         #     self.test.append(self.team_name)
                    


        #     except socket.timeout:
        #         break
            
            # except (ConnectionError, ConnectionResetError):
            #     print(colored(f"Clinet {self.team_name} closed the connection","red"))
            #     return None


        # teams_score[self.team_name] = 0
        try:
            self.connection.sendall(get_welcome_message().encode("utf-8"))
        except (ConnectionError, ConnectionResetError):
                print("Error occured, connection was closed")
                return None

        now = time.time()
        stop_typing = True
        while True:
            try:
                char = self.connection.recv(1024)
                if not char:
                    break

                print(char)
                char = char.decode("ASCII")
                teams_score[self.team_name] += 1
                groups_score[self.group] += 1

                # Used for bonus - statistics over each char pressed
                if char not in chars_presses:
                    chars_presses[char] = 1
                else:
                    chars_presses[char] += 1
            
                # if (time.time() - now <= 1.5) and stop_typing:
                #     self.connection.sendall("\nSTOP TYPING!!\nCALCULATING THE SCORES...".encode("utf-8"))
                #     stop_typing = False
                    
                    
            except socket.timeout:
                print("Sending end game message")
                team_message, group_message = get_end_game_message(teams_score[self.team_name],
                groups_score[self.group],groups_score[get_rival_group_number(self.group)])


                end_game_message = team_message + group_message
                self.connection.sendall(end_game_message.encode("utf-8"))
                # self.connection.sendall(group_message.encode("utf-8"))
                break
            
            except (ConnectionError, ConnectionResetError):
                print("Error occured, connection was closed")
                return None

            except KeyError:
                # Bug in the teams dictionary - some team names comes together - split them with /n
                team_names = self.team_name.split("\n")
                for team in team_names:
                    if team: # Ignore null chars
                        teams_score[team] = 1
                continue
            
        self.connection.close()


def get_welcome_message():
    global teams
    print(teams)
    messages = "Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n"

    for team in teams[1]:
        messages+= f"{team}\n"

    messages += "Group 2:\n==\n"
    for team in teams[2]:
        messages+= f"{team}\n"

    messages+="\n"
    messages+="Start pressing keys on your keyboard as fast as you can!!"

    return messages



def get_end_game_message(team_number_of_chars, group_score, other_group_score):
    global teams
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
    if group_score == other_group_score:
        group_message += "ITS A DRAW!\n\n"
    else:
        if group_score > other_group_score:
            group_message += f"YOUR group wins! \n\n"
        else:
            group_message += f"The RIVAL group wins! \n\n"

        group_message += "Congratulations to the winners:\n"
        group_message += "==\n"
        for team in teams[winner_id]:
            group_message+= f"{team}\n"

    return team_message, group_message

def get_winner():
    global groups_score
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
server_port = 2042
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
# try:
ServerSocket.bind((local_ip, server_port))
ServerSocket.listen()
# except OSError:
    # server_port += 1
    # ServerSocket.bind((local_ip, server_port))
    # ServerSocket.listen()
print(colored(f"Server Started, listening on IP address {local_ip}",'yellow'))

#  Listen to incomming sockets from the clients and handle each one
ServerSocket.settimeout(10)
future = time.time() + 10
ServerSocket.setblocking(0)

    
while True:
    #  Start sending offer packets
    Sender(server_port).start()

    #  Listen to incomming sockets from the clients and handle each one
    ServerSocket.settimeout(10)
    future = time.time() + 10
    new_game()

    # Loop for 10 seconds waiting for new clinets. Once 10 seconds have passed
    # Timeout execption will be raised and the game will begin
    while True:
        # new_game()
        try:
            (socket_for_client, client_ip) = ServerSocket.accept()
            # t = future - time.time()
            # socket_for_client.setblocking(0) # If no data recieived the .recv function will not block the program
            print(f"client with IP address and port: {client_ip}" )
            data = socket_for_client.recv(2048)
            if not data: continue
            team_name = data.decode("ASCII").strip()
            #  Save the client's team name to a random group
            choice = random.randint(1,2)
            group = choice
            teams[choice].append(team_name)
            teams_score[team_name] = 0

            thread = ClientThread(socket_for_client, 10, team_name, group)
            game_threads.append(thread)
            # thread.start()
            print(colored(f"Team {team_name} has conencted to the game","green"))
        except socket.timeout:
            print(len(game_threads))
            # 10 seconds have passed - Start the game
            for thread in game_threads:
                thread.start()
            
            # Wait for all the players to finish
            for thread in game_threads:
                print("Waiting for players to finish")
                thread.join()
                print("Waiting for players to finish")

            print(colored("Game over, sending out offer requests...",'red'))
            time.sleep(5)
            break

        except (ConnectionError, ConnectionResetError):
            print(colored("Error occured, connection to the client was closed. Waiting for the next client",'red'))
            continue

    
        


ServerSocket.close()