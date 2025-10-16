import random
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

SUIT_DOMAIN = {
    "Clubs": "Physical (appearance, existence)",
    "Diamonds": "Technical (mental, operation)",
    "Spades": "Mystical (meaning, capability)",
    "Hearts": "Social (personal, connection)"
}

RANKS = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
SUITS = ["Clubs", "Diamonds", "Spades", "Hearts"]

ACTION_FOCUS = {
    "2": "Seek",
    "3": "Oppose",
    "4": "Communicate",
    "5": "Move",
    "6": "Harm",
    "7": "Create",
    "8": "Reveal",
    "9": "Command",
    "10": "Take",
    "J": "Protect",
    "Q": "Assist",
    "K": "Transform",
    "A": "Deceive"
}

DETAIL_FOCUS = {
    "2": "Small",
    "3": "Large",
    "4": "Old",
    "5": "New",
    "6": "Mundane",
    "7": "Simple",
    "8": "Complex",
    "9": "Unsavory",
    "10": "Specialized",
    "J": "Unexpected",
    "Q": "Exotic",
    "K": "Dignified",
    "A": "Unique"
}

TOPIC_FOCUS = {
    "2": "Current Need",
    "3": "Allies",
    "4": "Community",
    "5": "History",
    "6": "Future Plans",
    "7": "Enemies",
    "8": "Knowledge",
    "9": "Rumors",
    "10": "A Plot Arc",
    "J": "Recent Events",
    "Q": "Equipment",
    "K": "A Faction",
    "A": "The PCs"
}

SCENE_COMPLICATION = {
    1: "Hostile forces oppose you",
    2: "An obstacle blocks your way",
    3: "Wouldn't it suck if…",
    4: "An NPC acts suddenly",
    5: "All is not as is seems",
    6: "Things actually go as planned"
}

ALTERED_SCENE = {
    1: "A major detail of the scene is enhanced or somehow worse",
    2: "The environment is different",
    3: "Unexpected NPCs are present",
    4: "Add a SCENE COMPLICATION",
    5: "Add a PACING MOVE",
    6: "Add a RANDOM EVENT"
}

PACING_MOVES = {
    1: "Foreshadow Trouble",
    2: "Reveal a New Detail",
    3: "An NPC Takes Action",
    4: "Advance a Threat",
    5: "Advance a Plot",
    6: "Add a RANDOM EVENT to the scene"
}

FAILURE_MOVES = {
    1: "Cause Harm",
    2: "Put Someone in a Spot",
    3: "Offer a Choice",
    4: "Advance a Threat",
    5: "Reveal an Unwelcome Truth",
    6: "Foreshadow Trouble"
}

ORACLE_HOW = {
    1: "Surprisingly lacking",
    2: "Less than expected",
    3: "About average",
    4: "About average",
    5: "More than expected",
    6: "Extraordinary"
}

YESNO_THRESH = {
    "Likely": 3,
    "Even": 4,
    "Unlikely": 5
}

def yesno_modifier(mod_die):
    if mod_die == 1:
        return "but…"
    elif mod_die == 6:
        return "and…"
    else:
        return ""

PLOT_OBJECTIVE = {
    1: "Eliminate a threat",
    2: "Learn the truth",
    3: "Recover something valuable",
    4: "Escort or deliver to safety",
    5: "Restore something broken",
    6: "Save an ally in peril"
}
PLOT_ADVERSARIES = {
    1: "A powerful organization",
    2: "Outlaws",
    3: "Guardians",
    4: "Local inhabitants",
    5: "Enemy horde or force",
    6: "A new or recurring villain"
}
PLOT_REWARDS = {
    1: "Money or valuables",
    2: "Money or valuables",
    3: "Knowledge and secrets",
    4: "Support of an ally",
    5: "Advance a plot arc",
    6: "A unique item of power"
}

NPC_IDENTITY = {
    "2": "Outlaw",
    "3": "Drifter",
    "4": "Tradesman",
    "5": "Commoner",
    "6": "Soldier",
    "7": "Merchant",
    "8": "Specialist",
    "9": "Entertainer",
    "10": "Adherent",
    "J": "Leader",
    "Q": "Mystic",
    "K": "Adventurer",
    "A": "Lord"
}

NPC_GOAL = {
    "2": "Obtain",
    "3": "Learn",
    "4": "Harm",
    "5": "Restore",
    "6": "Find",
    "7": "Travel",
    "8": "Protect",
    "9": "Enrich Self",
    "10": "Avenge",
    "J": "Fulfill Duty",
    "Q": "Escape",
    "K": "Create",
    "A": "Serve"
}

NPC_FEATURE = {
    1: "Unremarkable",
    2: "Notable nature",
    3: "Obvious physical trait",
    4: "Quirk or mannerism",
    5: "Unusual equipment",
    6: "Unexpected age or origin"
}

DUNGEON_LOCATION = {
    1: "Typical area",
    2: "Transitional area",
    3: "Living area or meeting place",
    4: "Working or utility area",
    5: "Area with a special feature",
    6: "Location for a specialized purpose"
}
DUNGEON_ENCOUNTER = {
    1: "None",
    2: "None",
    3: "Hostile enemies",
    4: "Hostile enemies",
    5: "An obstacle blocks the way",
    6: "Unique NPC or adversary"
}
DUNGEON_OBJECT = {
    1: "Nothing, or mundane objects",
    2: "Nothing, or mundane objects",
    3: "An interesting item or clue",
    4: "A useful tool, key, or device",
    5: "Something valuable",
    6: "Rare or special item"
}
DUNGEON_TOTAL_EXITS = {
    1: "Dead end",
    2: "Dead end",
    3: "1 additional exit",
    4: "1 additional exit",
    5: "2 additional exits",
    6: "2 additional exits"
}

HEX_TERRAIN = {
    1: "Same as current hex",
    2: "Same as current hex",
    3: "Common terrain",
    4: "Common terrain",
    5: "Uncommon terrain",
    6: "Rare terrain"
}
HEX_CONTENTS = {
    1: "Nothing notable",
    2: "Nothing notable",
    3: "Nothing notable",
    4: "Nothing notable",
    5: "Nothing notable",
    6: "Roll a FEATURE"
}
HEX_FEATURES = {
    1: "Notable structure",
    2: "Dangerous hazard",
    3: "A settlement",
    4: "Strange natural feature",
    5: "New region (set new terrain types)",
    6: "DUNGEON CRAWLER entrance"
}
HEX_EVENT = {
    1: "None",
    2: "None",
    3: "None",
    4: "None",
    5: "RANDOM EVENT then SET THE SCENE",
    6: "RANDOM EVENT then SET THE SCENE"
}

class Deck:
    def __init__(self):
        self.cards = []
        self.discard = []
        self._build()

    def _build(self):
        self.cards = []
        for s in SUITS:
            for r in RANKS:
                self.cards.append((r, s))
        self.cards.append(("Joker", "Black"))
        self.cards.append(("Joker", "Red"))
        random.shuffle(self.cards)
        self.discard = []

    def draw(self):
        if not self.cards:
            self._build()
        card = self.cards.pop()
        self.discard.append(card)
        return card

    def shuffle_in_discards(self):
        self.cards.extend(self.discard)
        self.discard = []
        random.shuffle(self.cards)

def d6():
    return random.randint(1, 6)

def d4():
    return random.randint(1, 4)

def d12():
    return random.randint(1, 12)

def flip_coin():
    return random.choice(["Heads", "Tails"])

def dice_to_card():
    rank_roll = d12()
    suit_roll = d4()
    if rank_roll == 12:
        return (random.choice(["Q", "K"]), SUITS[suit_roll - 1])
    else:
        mapping = {
            1: "2", 2: "3", 3: "4", 4: "5", 5: "6", 6: "7",
            7: "8", 8: "9", 9: "10", 10: "J", 11: "Q"
        }
        rank = mapping[rank_roll]
        suit = SUITS[suit_roll - 1]
        return (rank, suit)

def card_to_d6(rank):
    if rank == "A":
        return None
    val_map = {"J": 11, "Q": 12, "K": 13}
    if rank in val_map:
        val = val_map[rank]
    else:
        val = int(rank)
    res = val // 2
    if res < 1:
        res = 1
    if res > 6:
        res = 6
    return res

class OPSEApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("One Page Solo Engine (v1.6) — Tkinter")
        self.geometry("1040x720")

        self.deck = Deck()

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.log = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=20)
        self.log.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

        self._build_oracle_tab()
        self._build_scene_tab()
        self._build_gm_moves_tab()
        self._build_random_event_tab()
        self._build_npc_tab()
        self._build_plot_tab()
        self._build_generic_tab()
        self._build_dungeon_tab()
        self._build_hex_tab()
        self._build_tools_tab()

    def append_log(self, text: str):
        self.log.insert(tk.END, text + "\\n")
        self.log.see(tk.END)

    def _build_oracle_tab(self):
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        for r in range(10):
            frame.rowconfigure(r, weight=0)

        self.notebook.add(frame, text="Oracle")

        yn_box = ttk.LabelFrame(frame, text="Yes / No")
        yn_box.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        yn_box.columnconfigure(0, weight=1)
        yn_box.columnconfigure(1, weight=1)

        ttk.Label(yn_box, text="Likelihood:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.likelihood = tk.StringVar(value="Even")
        like = ttk.Combobox(yn_box, values=["Likely", "Even", "Unlikely"], textvariable=self.likelihood, state="readonly")
        like.grid(row=0, column=1, sticky="ew", padx=6, pady=4)

        ttk.Button(yn_box, text="Ask the Oracle", command=self.roll_yes_no).grid(row=1, column=0, columnspan=2, padx=6, pady=6, sticky="ew")

        how_box = ttk.LabelFrame(frame, text="How (Scale / Magnitude)")
        how_box.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        how_box.columnconfigure(0, weight=1)

        ttk.Button(how_box, text="Roll How", command=self.roll_how).grid(row=0, column=0, padx=6, pady=6, sticky="ew")

    def roll_yes_no(self):
        like = self.likelihood.get()
        threshold = YESNO_THRESH[like]
        answer_die = d6()
        mod_die = d6()
        outcome = "Yes" if answer_die >= threshold else "No"
        mod_text = yesno_modifier(mod_die)
        if mod_text:
            outcome = f"{outcome}, {mod_text}"
        self.append_log(f"[Oracle: {like}] d6={answer_die}, mod d6={mod_die} → {outcome}")

    def roll_how(self):
        roll = d6()
        desc = ORACLE_HOW[roll]
        self.append_log(f"[How] d6={roll} → {desc}")

    def _build_scene_tab(self):
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        self.notebook.add(frame, text="Scene")

        sc_box = ttk.LabelFrame(frame, text="Set the Scene")
        sc_box.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        sc_box.columnconfigure(0, weight=1)
        sc_box.columnconfigure(1, weight=1)

        ttk.Button(sc_box, text="Roll Scene Complication", command=self.roll_scene_complication).grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        ttk.Button(sc_box, text="Check Altered Scene", command=self.roll_altered_scene_check).grid(row=0, column=1, sticky="ew", padx=6, pady=6)

        ttk.Button(sc_box, text="Roll Altered Scene Table", command=self.roll_altered_scene).grid(row=1, column=0, columnspan=2, sticky="ew", padx=6, pady=6)

    def roll_scene_complication(self):
        roll = d6()
        res = SCENE_COMPLICATION[roll]
        self.append_log(f"[Scene Complication] d6={roll} → {res}")

    def roll_altered_scene_check(self):
        roll = d6()
        if roll >= 5:
            self.append_log(f"[Altered Scene Check] d6={roll} → ALTERED SCENE")
        else:
            self.append_log(f"[Altered Scene Check] d6={roll} → No change")

    def roll_altered_scene(self):
        roll = d6()
        res = ALTERED_SCENE[roll]
        self.append_log(f"[Altered Scene] d6={roll} → {res}")

    def _build_gm_moves_tab(self):
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        self.notebook.add(frame, text="GM Moves")

        pacing_box = ttk.LabelFrame(frame, text="Pacing Moves")
        pacing_box.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        ttk.Button(pacing_box, text="Roll Pacing Move", command=self.roll_pacing).grid(row=0, column=0, sticky="ew", padx=6, pady=6)

        failure_box = ttk.LabelFrame(frame, text="Failure Moves")
        failure_box.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        ttk.Button(failure_box, text="Roll Failure Move", command=self.roll_failure).grid(row=0, column=0, sticky="ew", padx=6, pady=6)

    def roll_pacing(self):
        roll = d6()
        res = PACING_MOVES[roll]
        self.append_log(f"[Pacing Move] d6={roll} → {res}")

    def roll_failure(self):
        roll = d6()
        res = FAILURE_MOVES[roll]
        self.append_log(f"[Failure Move] d6={roll} → {res}")

    def _build_random_event_tab(self):
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        self.notebook.add(frame, text="Random Event")

        re_box = ttk.LabelFrame(frame, text="Random Event")
        re_box.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        ttk.Button(re_box, text="Draw Random Event (Cards)", command=self.draw_random_event).grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        ttk.Button(re_box, text="Simulate with Dice (Optional)", command=self.dice_random_event).grid(row=0, column=1, sticky="ew", padx=6, pady=6)

    def _interpret_card(self, card):
        rank, suit = card
        if rank == "Joker":
            return "Joker", suit, "JOKER"
        return rank, suit, SUIT_DOMAIN[suit]

    def _draw_focus(self, mapping, label):
        card = self.deck.draw()
        rank, suit, domain = self._interpret_card(card)
        if rank == "Joker":
            self.deck.shuffle_in_discards()
            self.append_log(f"[{label}] Drew JOKER ({suit}). Deck reshuffled. Add a RANDOM EVENT!")
            card = self.deck.draw()
            rank, suit, domain = self._interpret_card(card)

        keyword = mapping[rank]
        return keyword, rank, suit, domain

    def draw_random_event(self):
        act, ar, asu, adom = self._draw_focus(ACTION_FOCUS, "Action Focus")
        top, tr, tsu, tdom = self._draw_focus(TOPIC_FOCUS, "Topic Focus")
        self.append_log(f"[Random Event] Action: {act} ({ar} of {asu} → {adom}); Topic: {top} ({tr} of {tsu} → {tdom})")

    def dice_random_event(self):
        act_card = dice_to_card()
        top_card = dice_to_card()
        ar, asu = act_card
        tr, tsu = top_card
        act = ACTION_FOCUS[ar]
        top = TOPIC_FOCUS[tr]
        adom = SUIT_DOMAIN[asu]
        tdom = SUIT_DOMAIN[tsu]
        self.append_log(f"[Random Event (Dice Sim)] Action: {act} ({ar} of {asu} → {adom}); Topic: {top} ({tr} of {tsu} → {tdom})")

    def _build_npc_tab(self):
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        self.notebook.add(frame, text="NPC Generator")

        npc_box = ttk.LabelFrame(frame, text="Generate NPC")
        npc_box.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)

        ttk.Button(npc_box, text="Roll NPC (Cards + d6)", command=self.roll_npc).grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=6)

    def roll_npc(self):
        ident, ir, isu, idom = self._draw_focus(NPC_IDENTITY, "NPC Identity")
        goal, gr, gsu, gdom = self._draw_focus(NPC_GOAL, "NPC Goal")
        nf_roll = d6()
        nf = NPC_FEATURE[nf_roll]
        det, dr, dsu, ddom = self._draw_focus(DETAIL_FOCUS, "NPC Detail Focus")
        att_roll = d6()
        att = ORACLE_HOW[att_roll]
        conv, cr, csu, cdom = self._draw_focus(TOPIC_FOCUS, "Conversation Topic")

        self.append_log(
            f"[NPC] Identity: {ident} ({ir} of {isu} → {idom}); Goal: {goal} ({gr} of {gsu} → {gdom}); "
            f"Feature: {nf} + {det} ({dr} of {dsu} → {ddom}); Attitude: {att}; Conversation: {conv} ({cr} of {csu} → {cdom})"
        )

    def _build_plot_tab(self):
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        self.notebook.add(frame, text="Plot Hook")

        ph_box = ttk.LabelFrame(frame, text="Generate Plot Hook")
        ph_box.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)

        ttk.Button(ph_box, text="Roll Plot Hook (d6)", command=self.roll_plot_hook).grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=6)

    def roll_plot_hook(self):
        obj = PLOT_OBJECTIVE[d6()]
        adv = PLOT_ADVERSARIES[d6()]
        rew = PLOT_REWARDS[d6()]
        self.append_log(f"[Plot Hook] Objective: {obj}; Adversaries: {adv}; Rewards: {rew}")

    def _build_generic_tab(self):
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        self.notebook.add(frame, text="Generic Generator")

        gg_box = ttk.LabelFrame(frame, text="Generic Generator")
        gg_box.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)

        ttk.Button(gg_box, text="Generate (Cards + d6)", command=self.roll_generic).grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=6)

    def roll_generic(self):
        act, ar, asu, adom = self._draw_focus(ACTION_FOCUS, "Action Focus")
        det, dr, dsu, ddom = self._draw_focus(DETAIL_FOCUS, "Detail Focus")
        how = ORACLE_HOW[d6()]
        self.append_log(f"[Generic] Does: {act} ({ar} of {asu} → {adom}); Looks: {det} ({dr} of {dsu} → {ddom}); Significance: {how}")

    def _build_dungeon_tab(self):
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        self.notebook.add(frame, text="Dungeon")

        d_box = ttk.LabelFrame(frame, text="Explore an Area")
        d_box.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)

        ttk.Button(d_box, text="Roll Area (All Tables)", command=self.roll_dungeon_area).grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=6)

    def roll_dungeon_area(self):
        loc = DUNGEON_LOCATION[d6()]
        enc = DUNGEON_ENCOUNTER[d6()]
        obj = DUNGEON_OBJECT[d6()]
        exits = DUNGEON_TOTAL_EXITS[d6()]
        self.append_log(f"[Dungeon] Location: {loc}; Encounter: {enc}; Object: {obj}; Total Exits: {exits}")

    def _build_hex_tab(self):
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        self.notebook.add(frame, text="Hex")

        h_box = ttk.LabelFrame(frame, text="Enter a Hex")
        h_box.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)

        ttk.Button(h_box, text="Roll Hex (Terrain/Contents/Event)", command=self.roll_hex).grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=6)

    def roll_hex(self):
        terr = HEX_TERRAIN[d6()]
        cont = HEX_CONTENTS[d6()]
        feat_text = ""
        if cont == "Roll a FEATURE":
            feat_text = f"; Feature: {HEX_FEATURES[d6()]}"
        event = HEX_EVENT[d6()]
        self.append_log(f"[Hex] Terrain: {terr}; Contents: {cont}{feat_text}; Event: {event}")

    def _build_tools_tab(self):
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        self.notebook.add(frame, text="Tools")

        deck_box = ttk.LabelFrame(frame, text="Deck Tools")
        deck_box.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=8, pady=8)

        ttk.Button(deck_box, text="Draw a Card", command=self.draw_card).grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        ttk.Button(deck_box, text="Shuffle Discards into Deck", command=self.shuffle_discards).grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        ttk.Button(deck_box, text="Reset Full Deck", command=self.reset_deck).grid(row=0, column=2, sticky="ew", padx=6, pady=6)

        dice_box = ttk.LabelFrame(frame, text="Dice")
        dice_box.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=8, pady=8)

        ttk.Button(dice_box, text="Roll d6", command=lambda: self.append_log(f"[Dice] d6 → {d6()}")).grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        ttk.Button(dice_box, text="Roll 2d6", command=lambda: self.append_log(f"[Dice] 2d6 → {d6() + d6()}")).grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        ttk.Button(dice_box, text="Roll d4", command=lambda: self.append_log(f"[Dice] d4 → {d4()}")).grid(row=0, column=2, sticky="ew", padx=6, pady=6)
        ttk.Button(dice_box, text="Roll d12", command=lambda: self.append_log(f"[Dice] d12 → {d12()}")).grid(row=0, column=3, sticky="ew", padx=6, pady=6)
        ttk.Button(dice_box, text="Flip Coin", command=lambda: self.append_log(f"[Dice] Coin → {flip_coin()}")).grid(row=0, column=4, sticky="ew", padx=6, pady=6)

        log_box = ttk.LabelFrame(frame, text="Log")
        log_box.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=8, pady=8)
        ttk.Button(log_box, text="Clear Log", command=lambda: self.log.delete("1.0", tk.END)).grid(row=0, column=0, sticky="ew", padx=6, pady=6)

    def draw_card(self):
        card = self.deck.draw()
        rank, suit, domain = self._interpret_card(card)
        if rank == "Joker":
            self.deck.shuffle_in_discards()
            self.append_log(f"[Deck] Drew JOKER ({suit}). Deck reshuffled. Add a RANDOM EVENT!")
        else:
            self.append_log(f"[Deck] Drew {rank} of {suit} → {domain}")

    def shuffle_discards(self):
        self.deck.shuffle_in_discards()
        self.append_log("[Deck] Shuffled discards back into deck.")

    def reset_deck(self):
        self.deck._build()
        self.append_log("[Deck] Reset and shuffled a fresh full deck (including two Jokers).")

if __name__ == "__main__":
    app = OPSEApp()
    app.mainloop()
