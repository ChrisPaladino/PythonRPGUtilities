## Functional Requirements

The Dice Roller application provides a user-friendly interface for rolling dice and determining results based on customizable input. Below are the functional requirements of the application:

### General Features
1. **Dice Rolling**
   - Allows users to roll two sets of dice: **Action Dice** and **Danger Dice**.
   - Processes the results to display successes, failures, and other outcomes based on the highest remaining **Action Dice**.

2. **Dice Input Options**
   - Users can input the number of dice for each type (Action and Danger) directly into input boxes.
   - **"+" and "-" Buttons**:
     - "+" button increases the number of dice in the input box by 1 (up to a maximum of 20).
     - "-" button decreases the number of dice in the input box by 1 (down to a minimum of 0).
   - Default values:
     - **Action Dice**: Starts at `1`.
     - **Danger Dice**: Starts at `0`.

3. **Result Display**
   - Results are displayed as:
     - **Success**
     - **Partial Success**
     - **Failure**
     - **BOTCH**
   - Successes may include additional **BOON(s)** for exceptional results.

4. **Dice Results Visualization**
   - Displays rolled dice in two separate sections:
     - **Action Dice**: Highlighted with:
       - Green for the highest remaining die.
       - Red for cancelled dice.
     - **Danger Dice**: Highlighted with red for cancelled dice.
   - Dice are displayed as numbered squares for clarity.
   - Labels ("Action Dice" and "Danger Dice") distinguish the results visually.

### User Interface
1. **Inputs and Controls**
   - Action and Danger dice input boxes are left-aligned.
   - "+/-" buttons for adjusting dice counts are placed to the right of the input boxes.
   - A "Roll Dice" button triggers the rolling and processing of results.

2. **Result Output**
   - Results are displayed prominently in **blue** text above the dice results area.
   - Results are left-aligned with the input labels for consistency.

3. **Dice Display Area**
   - Organized within a scrollable section labeled as **"Dice Results"**.
   - Visual separation of Action and Danger dice.
   - Proper spacing between dice rows and labels for better readability.

4. **Resizable Layout**
   - The application dynamically resizes to fit the window.
   - Dice results area expands or shrinks proportionally.

5. **Error Handling**
   - Displays an error message in **red** when invalid input is entered (e.g., non-numeric values or numbers outside the range of 0–20).

### Application Constraints
1. The maximum number of dice allowed per type (Action/Danger) is **20**.
2. The minimum number of dice allowed per type is **0**.