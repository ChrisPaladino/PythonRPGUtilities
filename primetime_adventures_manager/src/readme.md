# Primetime Adventures Manager (Dice + Cards Variant)

A Python 3.10+ desktop application built with Tkinter and Grid layout to manage a TTRPG instance of *Primetime Adventures*, supporting both:

- ✅ Original card-based resolution
- ✅ Optional d20 dice-based resolution (rules-equivalent)

This tool is designed for both solo and group play, focusing on tracking scenes, protagonists, fan mail, budget, and conflict resolution.

---

# 🎯 Core Design Goals

- Preserve original PTA mechanics exactly
- Replace cards with dice as an **optional equivalent system**
- Support multiple protagonists per scene
- Avoid tracking real-world players (only characters)
- Provide a clean "tabletop view" UI for play
- Allow freeform editing (low friction, minimal constraints)

---

# 🎲 Resolution System

## ✅ Dual Mode

The system supports two interchangeable modes:

- `CARD_MODE`
- `DICE_MODE`

Both must produce identical outcomes.

---

## 🎴 Card Mode (Original)

- Count RED cards (hearts + diamonds)
- Compare against Producer
- Compare highest card to determine:
  - YES AND
  - YES BUT
  - NO BUT
  - NO AND

---

## 🎲 Dice Mode (Variant)

Dice replace cards using the following mapping:

| Cards | Dice |
|------|------|
| Red cards | Even numbers |
| Black cards | Odd numbers |
| Highest card | Highest die |

---

## 🧠 Resolution Algorithm (CRITICAL)

For EACH protagonist in a scene:

### Step 1: Roll Dice
- Screen Presence → base dice
- +1 die per Trait used
- +1 die per Fan Mail spent

Producer:
- 1 die base
- +1 die per budget spent (max +5, total max = 6)

---

### Step 2: Count Successes
- Count EVEN dice (equivalent to red cards)

---

### Step 3: Compare

For each protagonist vs Producer:

1. Compare number of EVEN results
2. Compare highest die rolled

---

### Step 4: Determine Outcome

| Condition | Result |
|----------|--------|
| More evens AND higher die | YES AND |
| More evens BUT lower die | YES BUT |
| Equal/fewer evens BUT higher die | NO BUT |
| Equal/fewer evens AND lower die | NO AND |

---

## ⚠️ Important Notes

- Odds are NOT discarded—they matter by affecting even count
- No custom edge cases — rules match original PTA exactly
- Each protagonist resolves independently

---

# 👥 Core Data Model

## Protagonist

```python
class Protagonist:
    id: str
    name: str
    issue: str
    impulse: str
    screen_presence: int  # 1-3
    fan_mail: int

    traits: list[Trait]  # exactly 3
````

***

## Trait

```python
class Trait:
    name: str
    type: str  # "edge" or "connection"
    used_in_scene: bool
```

Traits:

* Manually toggled per scene
* No automatic enforcement of usage limits

***

## Producer

```python
class Producer:
    budget: int
```

***

## Scene

```python
class Scene:
    id: str
    title: str
    scene_type: str  # "character" or "plot"
    question: str

    participants: list[Protagonist]
    producer_budget_spent: int

    results: dict[protagonist_id, ResolutionResult]
```

***

## Dice Result

```python
class DieResult:
    value: int
    source: str  # "screen_presence", "trait", "fan_mail"
```

***

## Resolution Result

```python
class ResolutionResult:
    protagonist_id: str

    even_count_protagonist: int
    even_count_producer: int

    highest_die_protagonist: int
    highest_die_producer: int

    outcome: str  # "YES AND", "YES BUT", "NO BUT", "NO AND"
```

***

# 💌 Fan Mail System

* Stored per protagonist
* Users manually:
  * Add Fan Mail
  * Remove Fan Mail

### Spending Fan Mail:

* +1 die per point
* Dice MUST be tagged as `fan_mail`

### Important Rule:

If a Fan Mail die result is EVEN:

* Producer gains +1 budget

***

# 💰 Budget System

* Stored globally on Producer
* User can manually:
  * Increase/decrease budget
* During resolution:
  * Budget spent = number of extra dice (max 5)

***

# 🎭 Scene Flow

## Guided + Editable Hybrid

### Step Flow

1. Create scene
2. Select participants
3. Select scene type:
   * Character → resist impulse
   * Plot → achieve goal
4. Define scene question
5. Assign traits (manual toggle)
6. Allocate fan mail
7. Set producer budget spend
8. Roll & resolve

***

# 🖥️ UI Design (Tkinter + Grid)

## Root Layout

Use `ttk.Notebook` (tabs):

### Tab 1: "Table" (Main Play View)

Layout grid:

```
-------------------------------------------
Top: Episode / Act / Scene Tracker
-------------------------------------------
Left: Protagonists List
      - Name
      - Fan Mail
      - Screen Presence

Center: Scene Panel
      - Scene Type
      - Question
      - Participants selector
      - Trait toggles
      - Fan Mail spend
      - Roll Button

Right: Producer Panel
      - Budget
      - Spend Budget control

Bottom: Results Log
-------------------------------------------
```

***

### Tab 2: "Characters"

* List all protagonists
* Click to open detail panel:
  * Issue / Impulse
  * Traits
  * Screen presence track
  * Fan Mail

***

### UI Requirements

* Use `grid()` exclusively (NO pack)
* Use frames for layout segmentation
* Dynamic refresh on state change

***

# 💾 Persistence

Use JSON save files.

## Save Structure

```json
{
  "protagonists": [...],
  "producer": {...},
  "scenes": [...],
  "current_scene": "...",
  "episode_info": {...}
}
```

### Required features:

* New Game
* Save Game
* Load Game
* Delete Game

***

# 🧱 Project Structure

```
pta_manager/

  main.py

  models/
    protagonist.py
    trait.py
    scene.py
    resolution.py

  services/
    dice_service.py
    resolution_service.py
    persistence_service.py

  ui/
    main_window.py
    table_view.py
    character_view.py
    scene_panel.py
    producer_panel.py
```

***

# 🎲 Dice Service (Implementation Rules)

```python
def roll_dice(num_dice: int, source: str) -> listpass
```

***

# 🧠 Resolution Service (Core Logic)

```python
def resolve_scene(protagonist_rolls, producer_rolls):
    # 1. Count evens
    # 2. Find highest
    # 3. Apply rule table
    # 4. Return structured results
```

***

# 🖼️ Future Enhancements

* Scene history timeline
* Episode / Act automation
* Trait usage tracking enforcement
* AI narrative suggestions
* Export episode summaries

***

# ✅ Copilot Prompting Guidance

To generate code effectively:

### Step 1

"Create Python classes for all models defined in README"

### Step 2

"Implement dice\_service with DieResult tracking"

### Step 3

"Implement resolution\_service using defined rules"

### Step 4

"Create Tkinter main window using ttk.Notebook and grid layout"

### Step 5

"Build Table view with left/center/right panels"

***

# 🎬 Final Notes

* Maintain fidelity to Primetime Adventures rules
* Dice system must behave identically to cards
* UI should feel like a tabletop assistant, not a rigid system
* Keep user control high, enforcement low