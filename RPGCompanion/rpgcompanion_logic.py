import random
import re

# Logic Module (rpgcompanion_logic.py)
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

    @staticmethod
    def roll_custom_formula(formula):
        """Evaluates a custom dice roll formula."""
        print(f"[DEBUG] roll_custom_formula called with: {formula}")  # Debug
        try:
            # Ensure input is cleaned
            formula = formula.strip().lower()
            print(f"[DEBUG] Processed input: {formula}")  # Debug

            # Call evaluate_single_formula
            result = RPGCompanionLogic.evaluate_single_formula(formula)
            print(f"[DEBUG] Result from evaluate_single_formula: {result}")  # Debug

            # Return result without adding "Rolled"
            return result
        except Exception as e:
            print(f"[DEBUG] Error in roll_custom_formula: {e}")  # Debug
            return f"Error in formula: {e}"

    @staticmethod
    def evaluate_single_formula(formula):
        """Evaluates a single dice roll formula."""
        print(f"[DEBUG] evaluate_single_formula called with: {formula}")  # Debug
        try:
            # Normalize case for consistency
            formula = formula.lower()

            # Handle multiple dice rolls separated by ',' or ';'
            if "," in formula or ";" in formula:
                # Split the formula into parts based on ',' or ';'
                parts = [part.strip() for part in re.split(r",|;", formula)]
                # Evaluate each part individually
                evaluated_parts = [RPGCompanionLogic.evaluate_single_formula(part) for part in parts]
                # Combine the results with line breaks, associating each input part with its result
                return "Rolled\n" + "\n".join([f"{part}: {res}" for part, res in zip(parts, evaluated_parts)])

            # Ensure the formula includes 'd'
            if "d" not in formula:
                return "Invalid format: no 'd' in formula"

            # Split the formula into number of dice and the remaining part
            num_dice, rest = formula.split("d")
            num_dice = int(num_dice) if num_dice else 1  # Default to 1 if no number provided

            if "!" in rest:  # Exploding dice
                sides = int(rest.replace("!", ""))
                return RPGCompanionLogic.exploding_dice(num_dice, sides)
            elif "k" in rest:  # Keep high/low
                sides, keep_part = rest.split("k")
                sides = int(sides)
                keep_type, keep_value = keep_part[0], int(keep_part[1:])
                if keep_type == "h":
                    return RPGCompanionLogic.keep_high(num_dice, sides, keep_value)
                elif keep_type == "l":
                    return RPGCompanionLogic.keep_low(num_dice, sides, keep_value)
                else:
                    return "Invalid keep type. Use 'h' or 'l'."
            elif "<" in rest:  # Target number (less than)
                sides, target = rest.split("<")
                sides = int(sides)
                target = int(target)
                return RPGCompanionLogic.target_number_less(num_dice, sides, target)
            elif ">" in rest:  # Target number (greater than)
                sides, target = rest.split(">")
                sides = int(sides)
                target = int(target)
                return RPGCompanionLogic.target_number(num_dice, sides, target)
            elif "f" in rest:  # Fudge/Fate dice
                return RPGCompanionLogic.fudge_dice(num_dice)
            else:  # Standard rolls with optional modifiers
                if "+" in rest:
                    sides, modifier = rest.split("+")
                    sides = int(sides)
                    modifier = int(modifier)
                elif "-" in rest:
                    sides, modifier = rest.split("-")
                    sides = int(sides)
                    modifier = -int(modifier)
                else:
                    sides = int(rest)
                    modifier = 0

                # Generate and sort rolls
                rolls = sorted([random.randint(1, sides) for _ in range(num_dice)], reverse=True)
                if num_dice == 1:
                    return f"{rolls[0] + modifier}"  # Single die result with modifier
                elif modifier != 0:
                    return f"{sum(rolls) + modifier} [{', '.join(map(str, rolls))}]"
                else:
                    return f"{sum(rolls)} [{', '.join(map(str, rolls))}]"
        except Exception as e:
            print(f"[DEBUG] Error in evaluate_single_formula: {e}")  # Debug
            return f"Error in formula: {e}"

    @staticmethod
    def exploding_dice(num_dice, sides):
        """Handles exploding dice."""
        total = 0
        rolls = []
        while num_dice > 0:
            current_rolls = [random.randint(1, sides) for _ in range(num_dice)]
            rolls.extend(current_rolls)
            num_dice = current_rolls.count(sides)
            total += sum(current_rolls)
        rolls.sort(reverse=True)
        return f"{total} [{', '.join(map(str, rolls))}]"

    @staticmethod
    def keep_high(num_dice, sides, keep):
        """Keeps the highest 'keep' number of rolls."""
        rolls = sorted([random.randint(1, sides) for _ in range(num_dice)], reverse=True)
        kept_rolls = rolls[:keep]
        return f"Rolled {num_dice}d{sides}k{keep}h: {sum(kept_rolls)} [Kept High: {', '.join(map(str, kept_rolls))} from {', '.join(map(str, rolls))}]"

    @staticmethod
    def keep_low(num_dice, sides, keep):
        """Keeps the lowest 'keep' number of rolls."""
        rolls = sorted([random.randint(1, sides) for _ in range(num_dice)])
        kept_rolls = rolls[:keep]
        return f"Rolled {num_dice}d{sides}k{keep}l: {sum(kept_rolls)} [Kept Low: {', '.join(map(str, kept_rolls))} from {', '.join(map(str, rolls))}]"

    @staticmethod
    def fudge_dice(num_dice):
        """Rolls Fudge/Fate dice."""
        rolls = [random.choice(["+", "-", "0"]) for _ in range(num_dice)]
        total = rolls.count("+") - rolls.count("-")
        return f"Rolled {num_dice}df: {total} [Fudge: {', '.join(rolls)}]"

    @staticmethod
    def target_number(num_dice, sides, target):
        """Counts successes based on a target number."""
        rolls = sorted([random.randint(1, sides) for _ in range(num_dice)], reverse=True)
        successes = sum(1 for roll in rolls if roll > target)
        return f"Rolled {num_dice}d{sides}>{target}: {successes} Successes [Rolls: {', '.join(map(str, rolls))}]"
    
    @staticmethod
    def target_number_less(num_dice, sides, target):
        """Counts successes based on a target number (less than)."""
        rolls = sorted([random.randint(1, sides) for _ in range(num_dice)], reverse=True)
        successes = sum(1 for roll in rolls if roll < target)
        return f"{successes} Successes [Rolls: {', '.join(map(str, rolls))}]"