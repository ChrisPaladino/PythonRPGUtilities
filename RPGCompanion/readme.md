# RPG Dice Rolling Program Requirements
## Overview
This Python program aims to provide a minimal, discrete, and efficient tool for RPG dice rolling, catering to office workers or individuals in constrained environments. It will focus initially on dice rolling functionality for a standard set of polyhedral dice with Cortex (Tales of Xadia), with Starforged support as the next priorities.
## Functional Requirements
### Core Features (MVP)
- **Code Layout**
   - Two distinct Python Files. GUI / Interface code should be in a separate Python File from the Logic / Processing file.
- **Dice Rolling:**
	- Support for standard RPG dice types: d4, d6, d8, d10, d12, d20, d100
	- Allow rolling odd dice (e.g., d2, Zocchi dice) and custom input formulas
	- Allow rolling of Fudge/Fate dice
	- Assume no number before the "d" to be "1", IE: d8 = 1d8; d4 = 1d4
	- Enable users to input and roll custom formulas
- **Custom Formulas: Easy:**
	- Multiple dice can be rolled without summing by separating them with a comma or semi-colon ie: 1d10, 1d10, 1d6 will roll two 10-sided, one 6-sided and show the results separately
	- XdY: rolls X number of Y-sided dice and sums them, displaying the result
	- XdY +/- Z: rolls X number of Y-sided dice, sums them and then adds or subtracts Z
	- XdYkZh: Keep High: rolls X number of Y-sided dice, and keeps the highest Z of them, then sums and displays the result. (Note Z must be <= X)
	- XdYkZl: Keep Low: rolls X number of Y-sided dice, and keeps the lowest Z of them, then sums and displays the result. (Note Z must be <= X)
	- XdY!: Exploding: rolls X number of Y-sided dice, and if all X of them show the highest value (Y), re-roll XdY and add the new total to the sum, continue until the dice no longer explode
	- Xdf: Fudge/Fate: rolls X number of Fudge Dice (a six-sided dice where two sides are "+", two sides are "-", and two sides are "0"), then sum and display
	  - XdY>Z: Target Number: rolls X number of Y-sided dice, each die with a value > Z counts as 1 success, sum the successes and show the result
- **Custom Formulas: Game-Specific:**
	- (Format TBD): Starforged/Ironsworn: rolls two 10-sided challenge dice and one 6-sided action dice +/- Z, and compares the Action result (action dice +/- Z) against each of the Challenge dice. If Action beats both Challenge dice; show all the dice results and that's a Strong Hit. If Action beats ONE Challenge die; show all the dice results and that's a Weak Hit. If Action beats none of the Challenge dice; show all dice results and that's a MISS.
	- XaYd: FU Dice: rolls X number of 6-sided Action dice and puts them in a list sorted high-roll to low-roll, and rolls Y number of 6-sided Danger dice and puts them in a list sorted high-roll to low-roll.
		- If a Danger dice result also exists in the Action dice, then both of those dice are cancelled and cannot be used in the results.
			- Note: if the Action Dice are [6, 4, 2, 2] and Danger Dice are [2, 1], then only one of the 2s is removed. The result would be: Action [6, 4, 2] and Danger [1]
		- The highest remaining Action Die determines results: 6 = Strong Hit; 4-5 = Weak Hit; 2-3 = Miss
			- Note: If 0 Action Dice remain, or if the highest Action Die is 1, then it's a BOTCH
			- Note: If you get a Strong Hit, then each additional 6 is a Boon. You can have a (theoretical) unlimited number of boons on a roll
* **Results**:
	* Results should display in a scrollable text box with two buttons:
		* **Clear** button to reset the output.
		- **Copy** button to copy results to the clipboard.
* **Graphical Interface:**
	* Minimalist design using Python's TKinter library.
	* Grid-based layout for control and scalability.
	* Buttons for each supported dice type (d4, d6, etc.), represented with clickable dice images/icons.
	* Clear and Copy buttons referenced in Results
	- Input area for manual dice formulas.
## Non-Functional Requirements
- **Performance:**
	- Load within 2 seconds on standard hardware.
	- Render dice rolls and output instantly without lag.
* **Usability:**
	- Minimalist design for discreet use.
	- No dice animations or flashy effects.
	- Results should be clear and easy to interpret. The results numbers should be surrounded by the shape of the dice rolled if appropriate (d4, d6, d8, d10, d12, d20, d100)
* **Error Handling:**
	* Basic error messages for invalid inputs
	* Handle unexpected inputs gracefully without crashing.
* **Expandability:**
	* Modular design to support additional features or systems in future updates.
* **Platform:**
	- Compatible with Python 3.x.
	- Use only core Python libraries where possible to reduce dependencies.
## Acceptance Criteria
* **MVP Delivery:**
	- Users can roll standard RPG dice (d4, d6, d8, d10, d12, d20, d100) via clickable icons or manual formulas.
	- Dice results display in a scrollable, clear text box with options to clear or copy results.
* **Error Handling:**
	- Program gracefully handles invalid dice inputs
	- Errors are logged or displayed in a non-intrusive manner.
* **UI/UX:**
	- The interface is clean, intuitive, and suitable for discreet use in an office environment.
	- Rolls and outputs are visible without unnecessary clutter.