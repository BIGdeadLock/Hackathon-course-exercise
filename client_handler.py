import socket 
import time
import random
from threading import Thread
from game_messages import get_end_game_message, get_welcome_message
from Configurations.server_configuration import SERVER_PORT, LOCAL_IP
from termcolor import colored



class ClientThread(Thread):

    def __init__(self, connection, game_time, team_name, group_id):
        Thread.__init__(self)
        self.connection = connection
        self.time_left = game_time
        self.team_name = team_name
        self.group = group_id
        self.teams = None
        self.groups_score = None
        self.teams_score = None
    
    def set_game_setting(self, teams: dict, groups_score: dict, teams_score: dict, chars_pressed: dict):
        self.teams = teams
        self.groups_score = groups_score
        self.teams_score = teams_score
        self.chars_presses = chars_pressed

    def get_winner(self):
        first_score = self.groups_score[1]
        second_score = self.groups_score[2]

        if first_score > second_score:
            return 1
        elif first_score < second_score:
            return 2
        else:
            return 0

    def get_rival_group_number(self):
        if self.group == 1:
            return 2
        else:
            return 1

    def run(self):
        # The servers waits for 10 seconds and than send the message to all the clients
        self.connection.settimeout(self.time_left)
        try:
            self.connection.sendall(get_welcome_message(self.teams).encode("utf-8"))
        except (ConnectionError, ConnectionResetError):
                print(colored("Error occured, connection was closed","red"))
                return None

        stop_typing = True
        while True:
            try:
                char = self.connection.recv(1024)
                if not char:
                    break

                print(f"{self.team_name} typed {char}")
                char = char.decode("ASCII")
                self.teams_score[self.team_name] += 1
                self.groups_score[self.group] += 1

                # Used for bonus - statistics over each char pressed
                if char not in self.chars_presses:
                    self.chars_presses[char] = 1
                else:
                    self.chars_presses[char] += 1
                    
            except socket.timeout:
                print(colored("Sending end game message","yellow"))
                team_message, group_message = get_end_game_message(
                self.teams,
                self.teams_score[self.team_name],
                self.groups_score[self.group],
                self.groups_score[self.get_rival_group_number()],
                self.get_winner()
                )


                end_game_message = team_message + group_message
                self.connection.sendall(end_game_message.encode("utf-8"))
                # self.connection.sendall(group_message.encode("utf-8"))
                break
            
            except (ConnectionError, ConnectionResetError):
                print(colored("Error occured, connection was closed","red"))
                return None

            except KeyError:
                # Bug in the teams dictionary - some team names comes together - split them with /n
                self.team_names = self.team_name.split("\n")
                for team in self.team_names:
                    if team: # Ignore null chars
                        self.teams_score[team] = 1
                continue
            
        self.connection.close()