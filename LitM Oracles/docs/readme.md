# Legends in the Mist: Oracles

A Python 3.x application with a Tkinter GUI for rolling oracles to support *Legends in the Mist* tabletop RPG campaigns.

---

## Features

This tool provides a set of oracles for quickly generating narrative prompts, challenges, and random outcomes during play:

1. **Interpretive Oracle**: Rolls a d66 and returns symbolic results for interpretation.
2. **Yes/No Oracle**: Rolls 2d6 plus a power modifier to determine answers to binary questions.
3. **Conflict Oracle**: Generates layered narrative challenges from the provided data set.
4. **Profile Builder**: A 5-step process to design enemies and challenges, with optional role overrides.
5. **Challenge Action Oracle**: Embedded within Profile Builder to provide threat and consequence generation.
6. **Consequence Oracle**: Rolls a d66 and d6 to generate nuanced outcomes for failed or complicated actions.
7. **Revelations Oracle**: Rolls a d66 to provide story-driven revelations across Acts I, II, and III.

---

## Directory Structure

LitM Oracles/
├── src/
│   └── main.py               # Tkinter GUI and core logic
├── docs/
│   └── readme.md             # This file
├── data/
│   ├── interpretive.json
│   ├── conflict.json
│   ├── revelations.json
│   ├── challenge_action.json
│   └── consequence.json

---

## 🛠 Setup

1. **Requirements**

   * Python 3.8+
   * Tkinter (bundled with most Python distributions)

2. **Run the application**

   ```bash
   python src/main.py
   ```

---

## Styling

* **Statuses**: Highlighted in **green background**
* **Tags**: Highlighted in **yellow background**
* **Limits**: Highlighted in **red background**
* **Roles**: Displayed in **bold text**

This styling mirrors the Legends in the Mist aesthetic for quick visual parsing.

---

## Future Improvements (Optional)

* Dark mode UI theme
* Copy-to-clipboard and export functions
* Modularization for larger oracle sets
