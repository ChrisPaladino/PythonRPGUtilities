### Functional Requirements
1. **Dice Selection** 
    - **Input Field:** Allow users to input the number of six-sided dice to roll, ranging between 2 and 9.
    - **Increment/Decrement Buttons:**
        - A "+" button to increase the dice count (up to 9).
        - A "-" button to decrease the dice count (down to 2).
    - Default dice count should be 2.
2. **Difficulty Selection**
    - **Dropdown Menu:** Provide a dropdown to select one of the four difficulty levels:
        - BASIC: A quick and easy action or reaction.
        - CRITICAL: A full action or reaction (default).
        - EXTREME: A truly demanding action or reaction.
        - IMPOSSIBLE: A desperate action or reaction.
    - The default should be set to "Critical."
3. **Double Difficulty**
    - **Checkbox:** Enable users to indicate whether the Double Difficulty rule applies. Default to unchecked.
4. **Dice Rolling**
    - **Roll Button:** A button to roll the dice based on the selected number of dice.
    - **Logic:** Identify and tally successes:
        - **BASIC SUCCESS:** Two of a kind.
        - **CRITICAL SUCCESS:** Three of a kind.
        - **EXTREME SUCCESS:** Four of a kind.
        - **IMPOSSIBLE SUCCESS:** Five of a kind.
        - **JACKPOT!:** Six or more of a kind.
5. **Re-rolls**
    - Allow re-rolling all dice not part of a combination if at least one success is scored.
    - If a Free Re-roll applies, ensure it can be triggered without risk to initial successes.
    - Implement an "All In" option after a re-roll, with a warning about the potential loss of all successes.
6. **Results Display**
    - **Success Summary:** Display the tally of all success levels:
        - BASIC, CRITICAL, EXTREME, IMPOSSIBLE, JACKPOT.
    - **Outcome Assessment:** Evaluate the success level required to pass the selected difficulty:
        - Highlight if the player passed, exceeded, or failed the difficulty.
        - Provide suggestions for mitigating failures or utilizing extra successes.
7. **Extra Success Options**
    - Allow extra successes to be spent on:
        - EXTRA BASIC SUCCESS: Quick Action.
        - EXTRA CRITICAL SUCCESS: Full Action.
        - EXTRA EXTREME SUCCESS: Cool Action.
        - Lending successes to teammates.
8. **Interface Requirements**
    - Use **Tkinter** and a **Grid Layout** to organize the interface.
    - Components:
        - Input area for dice count (number field, +/– buttons).
        - Difficulty selection (dropdown menu).
        - Double Difficulty checkbox.
        - Roll button.
        - Results display (success breakdown, outcome status).
        - Re-roll and All-In options.
    - Ensure the layout is clear and user-friendly.