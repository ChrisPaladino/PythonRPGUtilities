# Primetime Adventures Manager

A Python 3.10+ desktop application built with **CustomTkinter** to manage a TTRPG session of *Primetime Adventures*, supporting both the original card-based resolution and an optional dice-based resolution that produces identical outcomes.

Designed as a single-user session tool: one episode tracked at a time, focused on tracking scenes, protagonists, fan mail, budget, and conflict resolution.

---

## Core Design Goals

- Preserve original PTA mechanics exactly
- Replace cards with dice as an optional equivalent system
- Support multiple protagonists per scene
- Track characters only (not real-world players)
- Provide a clean tabletop-assistant UI for live play
- Allow freeform editing — low friction, minimal enforcement
- Dark mode throughout; fully resizable window

---

## Resolution System

### Dual Mode

Two interchangeable modes are supported:

- `CARD_MODE` — uses a simulated virtual deck (shuffled by the app, drawn one at a time)
- `DICE_MODE` — uses dice rolls with the following equivalence mapping

| Cards        | Dice          |
|--------------|---------------|
| Red cards    | Even numbers  |
| Black cards  | Odd numbers   |
| Highest card | Highest die   |

Both modes produce identical outcomes using the same resolution algorithm.

---

### Card Mode — Simulated Deck

- The app maintains a shuffled virtual standard deck
- Cards are drawn automatically when resolution is triggered
- The deck state is displayed and can be manually reset or reshuffled
- Red cards (hearts, diamonds) = successes

---

### Resolution Algorithm

Applied to each protagonist in a scene independently.

**Step 1 — Determine Dice / Cards**

| Source            | Dice/Cards added             |
|-------------------|------------------------------|
| Screen Presence   | base dice (equal to SP value)|
| Trait used        | +1 die per trait             |
| Fan Mail spent    | +1 die per point             |
| Producer base     | 1 die                        |
| Producer budget   | +1 die per point (max 5, total max 6) |

**Step 2 — Count Successes**

Count EVEN dice results (or red cards in card mode).

**Step 3 — Compare protagonist vs Producer**

1. Compare number of successes (evens / red cards)
2. Compare highest value rolled / drawn

**Step 4 — Determine Outcome**

| Condition                               | Result   |
|-----------------------------------------|----------|
| More evens AND higher die               | YES AND  |
| More evens BUT lower die                | YES BUT  |
| Equal/fewer evens BUT higher die        | NO BUT   |
| Equal/fewer evens AND lower die         | NO AND   |

**Important Notes**

- Odd results are not discarded — they affect the even count by their absence
- No edge-case house rules — mechanics match original PTA exactly
- Each protagonist resolves independently against the Producer
- The Producer's dice are set and rolled manually by the user (the app does not auto-roll for the Producer)

---

## Core Data Model

### Protagonist

```python
class Protagonist:
    id: str
    name: str
    issue: str
    impulse: str
    screen_presence: int  # 1-3
    fan_mail: int
    traits: list[Trait]  # exactly 3
```

### Trait

```python
class Trait:
    name: str
    type: str  # "edge" or "connection"
    used_in_scene: bool
```

Traits are manually toggled per scene. No automatic enforcement of usage limits.

### Producer

```python
class Producer:
    budget: int
```

### Scene

```python
class Scene:
    id: str
    title: str
    scene_type: str  # "character" or "plot"
    question: str
    participants: list[Protagonist]
    producer_budget_spent: int
    results: dict[str, ResolutionResult]  # keyed by protagonist_id
```

### DieResult

```python
class DieResult:
    value: int
    source: str  # "screen_presence", "trait", "fan_mail"
```

### ResolutionResult

```python
class ResolutionResult:
    protagonist_id: str
    even_count_protagonist: int
    even_count_producer: int
    highest_die_protagonist: int
    highest_die_producer: int
    outcome: str  # "YES AND", "YES BUT", "NO BUT", "NO AND"
```

---

## Fan Mail System

- Stored per protagonist
- User manually adds or removes Fan Mail between scenes
- During resolution: each point spent adds +1 die, tagged as `fan_mail`

**Rule:** If a Fan Mail die result is EVEN, the Producer gains +1 budget after the scene.

---

## Budget System

- Stored globally on the Producer
- User manually increases or decreases budget
- During resolution: budget spent equals number of extra dice added to Producer pool (max 5 extra, total max 6)

---

## Scene Flow

1. Create scene (title, type, question)
2. Select participants from protagonist list
3. Select scene type: Character (resist impulse) or Plot (achieve goal)
4. Toggle traits used for each participant
5. Allocate fan mail spend per participant
6. User sets Producer budget spend manually
7. Trigger roll / draw and resolve

---

## UI Design (CustomTkinter)

**Framework:** CustomTkinter with dark mode as default. Fully resizable window using `grid()` layout throughout — no `pack()`.

### Root Layout — CTkTabview with two tabs

---

**Tab 1: Table (Main Play View)**

```
+--------------------------------------------------+
| Episode / Act / Scene info bar                   |
+-------------+-------------------+----------------+
| Protagonists| Scene Panel       | Producer Panel |
|             |                   |                |
| - Name      | - Scene type      | - Budget       |
| - Fan Mail  | - Question        | - Spend control|
| - SP        | - Participants    |                |
|             | - Trait toggles   |                |
|             | - Fan Mail spend  |                |
|             | - Roll button     |                |
+-------------+-------------------+----------------+
| Results Log (bottom, full width)                 |
+--------------------------------------------------+
```

---

**Tab 2: Characters**

- List of all protagonists
- Click to expand detail panel:
  - Issue / Impulse
  - Traits (name, type, edit)
  - Screen Presence
  - Fan Mail

---

### UI Requirements

- `grid()` exclusively throughout
- Frames used for layout segmentation
- Dynamic refresh on every state change
- Dark mode via `customtkinter.set_appearance_mode("dark")`

---

## Persistence

JSON save files. One episode tracked at a time (New / Save / Load / Delete).

### Save Structure

```json
{
  "protagonists": [],
  "producer": {},
  "scenes": [],
  "current_scene": "",
  "episode_info": {}
}
```

---

## Project Structure

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
        card_service.py
        resolution_service.py
        persistence_service.py

    ui/
        main_window.py
        table_view.py
        character_view.py
        scene_panel.py
        producer_panel.py
```

---

## Future Enhancements

- Scene history timeline
- Episode / Act automation
- Trait usage tracking enforcement
- Export episode summaries