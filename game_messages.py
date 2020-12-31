def get_welcome_message(teams: dict) -> str:

    messages = "Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n"

    for team in teams[1]:
        messages+= f"{team}\n"

    messages += "Group 2:\n==\n"
    for team in teams[2]:
        messages+= f"{team}\n"

    messages+="\n"
    messages+="Start pressing keys on your keyboard as fast as you can!!"

    return messages


def get_end_game_message(teams:dict, team_number_of_chars:int, group_score:int, other_group_score:int, winner_id:int) -> tuple:

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
