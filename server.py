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

        teams_score[self.team_name] = 0

        self.connection.sendall(get_welcome_message().encode("utf-8"))
        while True:
            try:
                char = self.connection.recv(1024)
                char = char.decode("ASCII")

                teams_score[self.team_name] += 1
                groups_score[self.group] += 1

                # Used for bonus - statistics over each char pressed
                if char not in chars_presses:
                    chars_presses[char] = 1
                else:
                    chars_presses[char] += 1


            except socket.timeout:
                team_message, group_message = get_end_game_message(teams_score[self.team_name],
                groups_score[self.group],groups_score[get_rival_group_number(self.group)])

                self.connection.sendall(team_message)
                self.connection.sendall(group_message)
                break


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
    team_message = f"You pressed {team_number_of_chars} characters"
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
    group_message += f"The other group typed {other_group_score} characters. \n"
    if winner_id == 0:
        group_message += "ITS A DRAW!\n\n"
    else:
        group_message += f"Group {winner_id} wins!. \n\n"
        group_message += "Congratulations to the winners:"
        group_message += "\n==\n"
        for team in teams[winner_id]:
            group_message+= f"{team}\n"

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

# server_port = 13117
server_port = 13000
local_ip = scapy.get_if_addr(scapy.conf.iface)
sender = Sender(server_port)

######## Game variables ########
teams = {1: [], 2: []}
teams_score = {}
groups_score = {1: 0, 2: 0}
chars_presses = {}
best_team = (0,0)
######## Game variables ########


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

#run_game()





print("Game over! Group 1 typed in 104 characters. Group 2 typed in 28 characters."+
"Group 1 wins! Congratulations to the winners: =="+ "TEAMS")
