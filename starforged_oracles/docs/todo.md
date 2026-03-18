# Todo Items

1. Ensure all data is downloaded, local, and ready to use. I do not want to have to download from a GitHub repo, in case that repo goes away one day. The file priority is
    1. Moves for Sundered Isles (pirates / latest version of the game engine)
    2. Moves for Starforged (space / sci-fi)
    3. Oracles for Sundered Isles
    4. Oracles for Starforged
    5. Oracles for Ironsworn (fantasy / viking times)
2. Assuming the data is downloaded and working, remove the various helper/download programs (fetch_data.py for example)
3. Include dice rolling for the moves. To start, roll Challenge Dice (2d10), and Action Roll (1d6+STAT as appropriate).
    1. If action Roll < both challenge dice then it's a Miss.
    2. If Action Roll > one of the challenge dice, that's a weak hit
    3. If Action Roll > BOTH challenge dice that's a strong hit (note, the action die must BEAT, not equal the challenge die to count)
    4. If Action Roll > BOTH challenge dice, and the challenge dice match, that's a strong hit with a match. Some moves use this in their results, othertimes it's just a bonus or "critical hit".
4. Short-term rolling is just ask the user for the STAT to add into the ACTION ROLL, longerterm we can have a character object or stats or something.