from utils.dice import roll_2d6

def yes_no_oracle(power=0):
    roll = roll_2d6() + power
    if roll <= 2:
        return "Extreme No"
    elif 3 <= roll <= 6:
        return "No"
    elif 7 <= roll <= 9:
        return "Complicated"
    elif 10 <= roll <= 11:
        return "Yes"
    else:
        return "Extreme Yes"
