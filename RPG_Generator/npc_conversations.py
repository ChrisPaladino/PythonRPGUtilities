import random

class NPC:
    def __init__(self, name, relationship):
        self.name = name
        self.relationship = relationship  # 1 (hated mortal enemy) to 10 (loyal lover)

class Conversation:
    def __init__(self, npc, pc_goal, importance, leverage):
        self.npc = npc
        self.pc_goal = pc_goal  # "ask" or "offer"
        self.importance = importance  # 1 to 5
        self.leverage = leverage  # 1 to 5

    def calculate_yes_chance(self):
        base_chance = 50  # Start with a 50% base chance

        # Adjust based on PC's goal
        goal_modifier = -20 if self.pc_goal == "ask" else 20

        # Adjust based on relationship
        relationship_modifier = (self.npc.relationship - 5.5) * 10

        # Adjust based on importance
        importance_modifier = (self.importance - 3) * 5

        # Adjust based on leverage
        leverage_modifier = (self.leverage - 3) * 10

        # Calculate final chance
        yes_chance = base_chance + goal_modifier + relationship_modifier + importance_modifier + leverage_modifier

        # Ensure the chance is between 0 and 100
        return max(0, min(100, yes_chance))

    def determine_attitude(self):
        attitude_score = self.npc.relationship * 10 + random.randint(-10, 10)

        if attitude_score < 20:
            return "Hostile"
        elif attitude_score < 40:
            return "Unfriendly"
        elif attitude_score < 60:
            return "Neutral"
        elif attitude_score < 80:
            return "Friendly"
        else:
            return "Very Friendly"

def simulate_conversation(npc, pc_goal, importance, leverage):
    conv = Conversation(npc, pc_goal, importance, leverage)
    yes_chance = conv.calculate_yes_chance()
    attitude = conv.determine_attitude()

    print(f"Conversation with {npc.name}")
    print(f"PC's goal: {'Asking' if pc_goal == 'ask' else 'Offering'}")
    print(f"Relationship: {npc.relationship}/10")
    print(f"Importance of the ask/offer: {importance}/5")
    print(f"PC's leverage over NPC: {leverage}/5")
    print(f"\nResults:")
    print(f"Chance to say 'yes': {yes_chance:.1f}%")
    print(f"NPC's attitude towards PC: {attitude}")

# Example usage
npc = NPC("Guard Captain", 6)  # Relationship is 6 out of 10
simulate_conversation(npc, "ask", 3, 2)  # PC is asking, importance is 3/5, leverage is 2/5

npc = NPC("Wife", 10)
simulate_conversation(npc, "want", 5, 1)

npc = NPC("Enemy", 1)
simulate_conversation(npc, "have", 5, 5)