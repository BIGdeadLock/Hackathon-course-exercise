import msvcrt
import time
# ...

def run_game(server_port):
    #Game runs for 10 seconds
    now = time.time()
    future = now + 10

    char =""
  #  print("Start pressing keys on your keyboard as fast as you can!!")
    hurry = True
    while time.time() < future:
        char += msvcrt.getch().decode('ASCII')
        if future - time.time() < 3 and hurry:
            hurry = False
            print("Hurry!! You have less than 3 seconds left!!")

    number_of_characters = len(char) 
    print(f"The characters pressed:\n {char}")
    print(f"You pressed {number_of_characters} characters")
    if number_of_characters <= 100:
        print("Are you even trying?")
    if number_of_characters > 100 and number_of_characters <= 150:
        print("Poor Effort! Get Better!")
    if number_of_characters > 150 and number_of_characters <= 250:
        print("Great Job!")
    if number_of_characters > 250:
        print("FANTASTIC! YOU ARE A PRO")