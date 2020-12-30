import socket 
import scapy.all as scapy
from offer import OfferPacket
from sender import Sender
import time
import random, os
from threading import Thread, Lock

from server_configuration import SERVER_PORT, LOCAL_IP
try:
    from termcolor import colored
except ModuleNotFoundError as i:
    os.system("pip3 install termcolor")
finally:
    from termcolor import colored


class ClientThread(Thread):

    def __init__(self, connection, game_time, team_name, group_id):
        Thread.__init__(self)
        self.connection = connection
        self.time_left = game_time
        self.team_name = team_name
        self.group = group_id
    
        

    def run(self):
        global teams, groups_score, teams_score
        # The servers waits for 10 seconds and than send the message to all the clients
        self.connection.settimeout(self.time_left)
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
    elif team_number_of_chars > 100 and team_number_of_chars <= 150:
        team_message+="\nPoor Effort! Get Better!\n\n"
    elif team_number_of_chars > 150 and team_number_of_chars <= 250:
       team_message+="\nGreat Job!\n\n"
    elif team_number_of_chars > 250:
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
# SERVER_PORT = 2042
# local_ip = scapy.get_if_addr(scapy.conf.iface)
# LOCAL_IP = scapy.get_if_addr("eth1")
game_threads = []

######## Game variables ########
teams = {1: [], 2: []}
teams_score = {}
groups_score = {1: 0, 2: 0}
chars_presses = {}
best_team = [0,0]
######## Game variables ########

# Open port for tcp connection from the client
ServerSocket = socket.socket()

ServerSocket.bind((LOCAL_IP, SERVER_PORT))
ServerSocket.listen()

print(colored(f"Server Started, listening on IP address {LOCAL_IP}",'yellow'))

#  Listen to incomming sockets from the clients and handle each one
ServerSocket.settimeout(10)
ServerSocket.setblocking(0)

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
    ServerSocket.settimeout(10)
    new_game()

    # Loop for 10 seconds waiting for new clinets. Once 10 seconds have passed
    # Timeout execption will be raised and the game will begin
    while True:
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
            print(colored(f"Team {team_name} has conencted to the game","green"))
        except socket.timeout:
            # 10 seconds have passed - Start the game
            for thread in game_threads:
                thread.start()
            
            # Wait for all the players to finish
            for thread in game_threads:
                thread.join()            
            
            #update best team in history if the team with best score scored higher
            max_current_team = max(teams_score.items(), key=operator.itemgetter(1))[0]
            if teams_score[max_current_team] > best_team[1]:
                best_team[1] = teams_score[max_current_team]
                best_team[0] = max_current_team

            print(f"THE TEAM  SCORED HIGHEST IN SERVER HISTORY: {max_charater}")
            #show most clicked character in server history
            max_charater = max(chars_presses.items(), key=operator.itemgetter(1))[0]
            print(f"THE MOST CLICKED CHARACTER IN SERVER HISTORY: {max_charater}")
            print(colored("Game over, sending out offer requests...",'red'))
            time.sleep(2)
            break

        except (ConnectionError, ConnectionResetError):
            print(colored("Error occured, connection to the client was closed. Waiting for the next client",'red'))
            continue


ServerSocket.close()