import random

class NPC:
    def __init__(self, name, relationship, personality):
        self.name = name
        self.relationship = relationship # -5 to +5
        self.personality = personality # 'outgoing', 'reserved', 'logical', or 'emotional'
        
class Conversation:
    def __init__(self, npc, goal, tone):
        self.npc = npc
        self.goal = goal
        self.tone = tone
        self.exchanges = 0
        
    def initial_reaction(self):
        roll = random.randint(1, 20) + self.npc.relationship
        if roll <= 5:
            return "Hostile"
        elif roll <= 10:
            return "Guarded"
        elif roll <= 15:
            return "Neutral"
        elif roll <= 20:
            return "Friendly"
        else:
            return "Very Friendly"
        
    def exchange(self):
        self.exchanges += 1
        goal_modifier = {"gather info": 0, "persuade": -2, "threaten": -4}.get(self.goal, 0)
        tone_modifier = {"friendly": 2, "formal": 0, "aggressive": -2}.get(self.tone, 0)
        
        if (self.npc.personality == "outgoing" and self.tone == "friendly") or (self.npc.personality == "logical" and self.goal == "gather info"):
            personality_modifier = 1 
        else:
            personality_modifier = 0

        roll = random.randint(1, 20) + goal_modifier + tone_modifier + personality_modifier
        if roll <= 5:
            return "Negative"
        elif roll <= 10:
            return "Hesitant"
        elif roll <= 15:
            return "Neutral"
        elif roll <= 20:
            return "Positive"
        else:
            return "Very Positive"
        
    def outcome(self, result):
        outcomes = {
            "Negative": "NPC refuses to share information or comply.",
            "Hesitant": "NPC shares vague or partial information.",
            "Neutral": "NPC shares basic information or gives a noncommittal response.",
            "Positive": "NPC shares detailed information or is inclined to agree.",
            "Very Positive": "NPC shares detailed information and additional helpful insights, or fully agrees."
        }
        return outcomes.get(result, "Unexpected result")
    
    def adjust_relationship(self, result):
        adjustment = {"Negative": -1, "Hesitant": 0, "Neutral": 0, "Positive": 1, "Very Positive": 2}.get(result, 0)
        self.npc.relationship = max(-5, min(5, self.npc.relationship + adjustment))
        
def simulate_conversation(npc, goal, tone, max_exchanges=3):
    conv = Conversation(npc, goal, tone)
    print(f"Starting conversation with {npc.name} (Relationship: {npc.relationship}, Personality: {npc.personality})")
    print(f"Goal: {goal}, Tone: {tone}")
    print(f"Initial reaction: {conv.initial_reaction()}")
    
    for _ in range(max_exchanges):
        result = conv.exchange()
        print(f"\nExchange {conv.exchanges}:")
        print(f"Result: {result}")
        print(f"Outcome: {conv.outcome(result)}")
        conv.adjust_relationship(result)
        print(f"Updated relationship: {conv.npc.relationship}")
    
    print(f"\nFinal relationship with {npc.name}: {conv.npc.relationship}")
        
# Example usage
npc = NPC("Guard Captain", 0, "logical")
simulate_conversation(npc, "gather info", "formal")