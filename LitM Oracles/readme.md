# Legends in the Mist: Oracles

A Python 3.x application with a Tkinter GUI for rolling oracles to support *Legends in the Mist* tabletop RPG campaigns.

---

## Features

This tool provides a set of oracles for quickly generating narrative prompts, challenges, and random outcomes during play:

1. **Interpretive Oracle**: Rolls a d66 and returns symbolic results for interpretation.
2. **Yes/No Oracle**: Rolls 2d6 plus a power modifier to determine answers to binary questions.
3. **Conflict Oracle**: Generates layered narrative challenges from the provided data set.
4. **Profile Builder**: A 5-step process to design enemies and challenges.
5. **Challenge Action Oracle** *(placeholder)*: Will eventually generate challenge-specific actions.
6. **Consequence Oracle** *(placeholder)*: Will eventually provide consequence prompts.
7. **Revelations Oracle** *(placeholder)*: Will eventually generate revelation outcomes.

---

## Directory Structure

LItM Oracles/
├── main.py               # Tkinter GUI and core logic
├── readme.md             # This file
├── data/
│   ├── interpretive.json
│   ├── conflict.json
│   ├── (other JSON files as they are added)
├── utils/
│   ├── dice.py           # d6, d66, and other roller utilities
