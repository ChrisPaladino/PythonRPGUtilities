import random

class RPGCompanionLogic:
    @staticmethod
    def roll_standard_dice(dice):
        """Rolls a standard die."""
        sides = int(dice[1:])
        return random.randint(1, sides)

    @staticmethod
    def roll_cortex_pool(dice_pool):
        """Rolls all dice in a Cortex dice pool."""
        rolls = [(dice, RPGCompanionLogic.roll_standard_dice(dice)) for dice in dice_pool]
        rolls.sort(key=lambda x: x[1], reverse=True)  # Sort by roll value
        return {
            "rolls": rolls,
            "hitches": [roll for roll in rolls if roll[1] == 1],
            "valid": [roll for roll in rolls if roll[1] > 1],
        }