import random

def roll_d6():
    return random.randint(1, 6)

def roll_d66():
    tens = random.randint(1, 6) * 10
    ones = random.randint(1, 6)
    return tens + ones

def roll_2d6():
    return random.randint(1, 6) + random.randint(1, 6)
