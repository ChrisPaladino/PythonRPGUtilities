import random

class RPGCompanionLogic:
    @staticmethod
    def roll_standard_dice(dice):
        """Rolls a standard die."""
        sides = int(dice[1:])
        return random.randint(1, sides)

    @staticmethod
    def roll_custom_formula(formula):
        """Evaluates a custom dice roll formula."""
        # Simple parser for now
        try:
            num_dice, rest = formula.split("d")
            modifier = 0
            if "+" in rest:
                sides, modifier = rest.split("+")
            elif "-" in rest:
                sides, modifier = rest.split("-")
                modifier = -int(modifier)
            else:
                sides = rest

            sides = int(sides)
            num_dice = int(num_dice)
            modifier = int(modifier)

            rolls = [random.randint(1, sides) for _ in range(num_dice)]
            return sum(rolls) + modifier
        except Exception:
            return "Invalid formula. Use NdX+/-Y (e.g., 3d6+2)"
