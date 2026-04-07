# Todo Items

## 1. Dice rolling for moves

Roll **Challenge Dice** (2d10) and an **Action Roll** (1d6 + STAT).

Outcome rules (ties always go to the challenge dice — equal does NOT beat):

| Result | Condition |
| -------- | ----------- |
| **Strong Hit with a Match** | Action Roll > both challenge dice, AND the two challenge dice show the same number |
| **Strong Hit** | Action Roll > both challenge dice (no match) |
| **Weak Hit** | Action Roll > exactly one challenge die |
| **Miss** | Action Roll does not beat either challenge die |

Additional rule: **Action Roll total is capped at 10**, even if stat + die > 10.

Short-term implementation: prompt the user to enter their STAT value (0–5) when rolling.

Long-term: support a character sheet / stats object so the STAT is pre-filled per move.

## 2. Character stats (longer term)

Store a simple character object with the five stats used for action rolls:

- **Edge** — speed, agility, ranged combat
- **Heart** — courage, social, leadership
- **Iron** — strength, endurance, melee
- **Shadow** — stealth, deception, trickery
- **Wits** — knowledge, perception, crafting

Each stat is a value from 1–3 (occasionally 0 or 4 with assets). Let the user set these
once and have the relevant stat pre-selected when rolling a specific move.

## 1. YAML Files

- bundles.yaml
- si_assets\companion.yaml
- si_oracles\encounters.yaml
- si_oracles\other.yaml
- si_oracles\plunder.yaml
- si_oracles\ruins.yaml

## 2. Sundered Isles Oracles
oracles:
  - name: Beasts of the Sea
    entries:
      - range: "1–15"
        result: Predatory Shark
        rank: Various Ranks
        description: >
          Most sharks offer little threat, but certain species of large, aggressive
          sharks are properly feared and respected by seagoing folk. Mariners also
          speak of ancient sharks, relentless hunters the size of whales whose teeth
          splinter hull and bone alike.

      - range: "16–30"
        result: Great Whale
        rank: Various Ranks
        description: >
          The seas teem with whales of all sorts. Even the largest of them, the great
          whales, are generally friendly and curious. They are nevertheless under
          threat by whalers and despoilers, and some islanders sail in defense of
          these gentle creatures.

      - range: "31–35"
        result: Leviathan
        rank: Epic
        description: >
          These ancient whales are far larger and more aggressive than their common
          kin. Their bone-white hide bears the scars of harpoon strikes and hard-won
          battles with other beasts. They are keenly intelligent, have long memories,
          and do not forgive or forget.

      - range: "36–40"
        result: Rothulk
        rank: Extreme
        description: >
          Circling carrion birds and the stench of death often forewarn the appearance
          of a rothulk, a cadaverous but still animate great whale. These unfortunate
          beasts are infested by a multitude of parasites that bind grasping tendrils
          to flesh and bone. The small creatures steal the life of their host and
          puppeteer what remains.

      - range: "41–45"
        result: Giant Squid
        rank: Formidable
        description: >
          The largest of these creatures can easily crush a longboat with their
          powerful tentacles, but they only reluctantly emerge from the lightless
          depths that is their preferred hunting grounds.

      - range: "46–50"
        result: The Kraken
        rank: Epic
        description: >
          The Kraken is the singular master of the seas, a beast of horrific scale,
          cunning, and ferocity. It has the sleek form and speed of a giant whale, but
          is armed with powerful tentacles and a gaping, toothy maw. Along its flank
          are rows of luminescent eyes; doom lights, mariners call them, for they are
          a presage of certain death.

      - range: "51–55"
        result: Sea Dragon
        rank: Formidable
        description: >
          These aquatic dragons have glittering scales, toothy jaws, and long,
          bladed tails. Their winglike fins propel them through the water at amazing
          speeds, and send them leaping and gliding over the waves.

      - range: "56–60"
        result: Elder Ray
        rank: Extreme
        description: >
          Like their lesser brethren, these creatures have flattened bodies and
          broad fins. They are inherently gentle, often traveling with seafolk who
          recognize individual rays by their luminescent markings.

      - range: "61–65"
        result: Whipneck
        rank: Formidable
        description: >
          These creatures are about the length of a sloop, with long necks, broad
          bodies, and turtle-like fins. They are not overly aggressive, but often
          hound fishing boats in hopes of stealing their catch.

      - range: "66–70"
        result: Eel Swarm
        rank: Formidable
        description: >
          These masses of black-eyed, sharp-toothed eels rely on sheer numbers to
          overwhelm larger prey. Some say they are capable of chewing through a
          ship's hull, and pour into a breached vessel in a slithering, biting torrent.

      - range: "71–75"
        result: Sea Serpent
        rank: Epic
        description: >
          These titanic beasts have sinuous bodies, glittering scales, and spiny red
          fins larger than the greatest mainsail. They are largely ambivalent to the
          presence of most seagoing folk—all but the largest ship passes beneath
          their notice.

      - range: "76–80"
        result: Reefstrider
        rank: Extreme
        description: >
          The shells of these gigantic, squat crustaceans are encrusted with coral
          and sea life, camouflaging them among reef systems. They are territorial
          and protective of their habitats.

      - range: "81–85"
        result: Starlume
        rank: Dangerous
        description: >
          Hundreds of pinpoint lights shimmer within the translucent form of these
          gigantic jellyfish. According to legend, the lights of a starlume reveal
          complex celestial maps. Those who look deeply into those alluring lights
          may find themselves gifted—or cursed—with visions of lost seas and
          hidden places.

      - range: "86–90"
        result: Vortex Forge
        rank: Epic
        description: >
          From a distance, this titanic entity might be mistaken for a great whale,
          but it is a crewless metal construct that wanders the seas on an inscrutable
          mission. Its rotating maw generates powerful whirlpools to draw in prey,
          sending ship and sailor alike into an ever-burning furnace deep within
          its mechanical gullet.

      - range: "91–95"
        result: Herald
        rank: Epic
        description: >
          These colossal tortoise-like beings are the longest-lived creatures of
          the isles—perhaps as ancient as the world itself. Islanders interpret
          wondrous and grim portents from the sighting of a herald, but these
          creatures often go unseen; their craggy shell is easily mistaken for a
          small, rocky island.

      - range: "96–100"
        result: Abomination
        rank: Various Ranks
        description: >
          Generate this beast using the Starforged creature oracles (page 336 of the
          Starforged rulebook), giving it a water form.

  - name: Beasts of the Land
    entries:
      - range: "1–25"
        result: Predatory Big Cat
        rank: Various Ranks
        description: >
          Big cats are the most common land predator in the isles. Some live among
          the high branches of jungle canopies, climbing and leaping with ease.
          Others dwell within the shadows of the forest floor or amid the rocks and
          crags of highland terrain, stalking their prey with deadly skill.

      - range: "26–35"
        result: Reaper
        rank: Formidable
        description: >
          Reapers are bipedal, cunning reptiles who move in packs, striking unseen
          from the shadows and chasing prey into flanking ambushes. They dispatch
          their quarry with wicked, sickle-shaped claws.

      - range: "36–40"
        result: Great Ape
        rank: Epic
        description: >
          The towering great apes of the isles live in the most rugged and remote
          jungles. They are reclusive creatures and do not abide rivals or
          trespassers. Their long lives are marked by the innumerable scars of fights
          with other beasts.

      - range: "41–45"
        result: Thundermaw
        rank: Extreme
        description: >
          This bipedal reptile is feared for its towering size, toothy maw, and
          dreadful roar. A small circlet of bone rings the beast's skull, leading
          some to name the thundermaw a king among the isles. Despite its legendary
          reputation, the thundermaw prefers to scavenge its meals, and tires easily
          when giving chase.

      - range: "46–50"
        result: Primordial
        rank: Epic
        description: >
          This titanic, reptilian beast dwells within deep jungles and mountainous
          highlands. It is a creature of the ancient world, unconcerned with the
          petty affairs of island folk but protective of its mist-shrouded domain.
          It is taller than the highest jungle canopy, and leaves trails of
          splintered trees and sundered earth in its wake.

      - range: "51–55"
        result: Avithor
        rank: Dangerous
        description: >
          These person-sized, flightless birds are drawn to shiny things, and collect
          bits of stone, metal, and trinkets in their nests. They are jealously
          protective of this hoard. When a trespasser comes near, they use a
          chittering call and display of colorful plumage to warn them away. If that
          fails, their surprising jumping ability, razor-like claws, and sharp beak
          make quick work of any threat.

      - range: "56–60"
        result: Verdant Mammoth
        rank: Extreme
        description: >
          These majestic, nomadic creatures have prehensile trunks, long tusks, and
          spiraling horns. The largest and oldest of a herd, the matriarch, is
          covered in a layer of moss, lichen, and plant sprigs—it wears this lush
          garden like an elaborate, earthy cape. Birds roost along the matriarch's
          back and circle above while the herd travels, providing a squawking alarm
          when danger is near.

      - range: "61–65"
        result: Serrabrus
        rank: Formidable
        description: >
          The serrabrus is a large boar-like beast. It is an industrious creature,
          felling trees, gathering deadwood, and building crude barriers with its
          sweeping, sawtooth tusks. To find oneself lost within the strange,
          meandering fences of the serrabrus is to incite the rage of the builder.

      - range: "66–70"
        result: Night Weaver
        rank: Formidable
        description: >
          These enormous spiders have a sleek, obsidian exoskeleton and slender legs
          tipped with razor-sharp hooks. They lurk in shadowy places—such as grounded
          shipwrecks, deep caves, and dense woodlands—building elaborate webs as
          traps for unwary prey.

      - range: "71–75"
        result: Sylvan Strider
        rank: Extreme
        description: >
          This gargantuan, insect-like creature moves through woodlands on
          multi-jointed legs the size of tree trunks. It often stands perfectly
          still while lying in wait for prey, indiscernible from the surrounding
          wilds.

      - range: "76–80"
        result: Mimic Serpent
        rank: Extreme
        description: >
          The scales of this massive, canopy-dwelling snake can shift in hue and
          texture, allowing it to blend invisibly within its surroundings. After
          grasping its unaware prey, the mimic serpent coils around its victim,
          stealing air and crushing bones.

      - range: "81–85"
        result: Ghost Rat
        rank: Dangerous
        description: >
          These pale rats of unusual size are accustomed to life within lightless
          caves. Ghost rats are blind, and use their keen sense of smell to navigate
          the depths. They pursue potential meals with hound-like persistence.

      - range: "86–90"
        result: Gangle
        rank: Formidable
        description: >
          This large, cave-dwelling insect contorts its long limbs with uncanny
          flexibility—the joints cracking like breaking bones—to navigate the
          smallest crevices. These limbs, equipped with delicate sensory organs,
          enable the creature to perceive the subtlest vibrations and detect prey or
          threats from afar. After unfolding itself from its hiding place, the
          gangle attacks with a spray of burning saliva.

      - range: "91–95"
        result: Deep Dragon
        rank: Epic
        description: >
          These ancient dragons lair in volcanic chambers, hibernating for centuries
          amid superheated steam and gases. They are flightless, with only vestigial
          wings, but their titanic scale and molten breath mark them as the greatest
          of dragon-kind. The rare emergence of a deep dragon from its burrow is a
          catastrophic reckoning for the surface world.

      - range: "96–100"
        result: Abomination
        rank: Various Ranks
        description: >
          Generate this beast using the Starforged creature oracles (page 336 of the
          Starforged rulebook), giving it a land form.

  - name: Beasts of the Shore and River
    entries:
      - range: "1–20"
        result: Great Crocodile
        rank: Various Ranks
        description: >
          Large crocodiles dwell in waters throughout the isles, including coastal
          wetlands, rivers, and the depths of tidal caves. The greatest and fiercest
          of them are the size of a sloop—armed with dagger-like teeth, impenetrable
          hides, and powerful tails capable of shattering stone.

      - range: "21–35"
        result: Tenebrous Squid
        rank: Extreme
        description: >
          This beast dwells within shoreline hollows and sea caves. It is a cunning
          and patient creature, slumbering for months or years until hapless prey
          wanders into its dark lair. As it awakens, its orb-like eyes glimmer with a
          foul, hungry light, and its barbed tentacles prepare to strike.

      - range: "36–50"
        result: Diving Spider
        rank: Dangerous
        description: >
          These semi-aquatic arachnids trap air with their silk, enabling them to
          hunt along riverbeds and coastal shallows, or lurk along the shore in wait
          of prey. They occasionally get caught up in nets, an unlucky catch for
          fisher folk.

      - range: "51–65"
        result: Muck Toad
        rank: Formidable
        description: >
          This creature lurks within the mire of swamps and muddy rivers. What the
          muck toad lacks in speed and agility, it makes up for in strength and
          scale, grasping prey with its prehensile tongue and swallowing it whole
          with its cavernous maw.

      - range: "66–75"
        result: Sand Dragon
        rank: Formidable
        description: >
          Sand dragons are the smallest of dragon-kind, but are still a fearsome
          foe. Burrowing beneath shoreline dunes, it stirs at the telltale
          vibrations of footfalls upon its lair. It attacks with dagger-like claws,
          teeth as long and wicked as cutlasses, and breath of scalding steam.

      - range: "76–85"
        result: Keelback Crab
        rank: Extreme
        description: >
          The keelback crab uses a scavenged ship as a protective shell for its soft
          exoskeleton. Reports of ghost ships can often be attributed to keelbacks,
          scuttling along coastal waters with wrecks on their backs. As it grows, a
          keelback must commandeer vessels of increasing size.

      - range: "86–95"
        result: Jade Crab
        rank: Extreme
        description: >
          The jade crab is the largest and most aggressive of the crustaceans, able
          to snap a longboat or even a small ship in two with its vice-like pincers.
          At rest, their shell is slate gray, easily mistaken for rocks or reefs. On
          the hunt, they shimmer with an iridescent blue-green. Fiercely territorial,
          these creatures often claim a waterway, cove, or sea cave as their lair.

      - range: "96–100"
        result: Abomination
        rank: Various Ranks
        description: >
          Generate this beast using the Starforged creature oracles (page 336 of the
          Starforged rulebook), giving it a land or water form.

  - name: Beasts of the Sky
    entries:
      - range: "1–20"
        result: Great Hawk
        rank: Various Ranks
        description: >
          Various types of enormous hawks hunt among the isles, including the
          mangrove-dwelling ash hawk and the coastal wind reaver. The greatest of
          them, the fabled vastwing, is said to be capable of grasping and lifting a
          fully loaded longboat in its enormous talons.

      - range: "21–35"
        result: Iron Dragon
        rank: Extreme
        description: >
          The most common dragon of the isles, the iron dragon dwells in a variety of
          environments, from rocky coasts to deep inland jungles. They have a tough
          hide the color of weathered iron, dreadful claws, and a long, powerful
          tail. But their most potent weapon is their fiery breath, the bane of any
          wooden ship that earns their ire. Some island folk revere these creatures.
          But others harness them and ride into battle, launching from a seaside
          fort or a ship's deck to lay waste to their enemies.

      - range: "36–50"
        result: Wave Skimmer
        rank: Formidable
        description: >
          These winged reptilian beasts nest along waterside cliffs, and are adept
          at diving to spear fish with barbed beaks. Fishing boats and cargo ships
          often fall prey to wave skimmer ambushes, as the cunning predators have
          learned of the great bounties hidden within those vessels.

      - range: "51–65"
        result: Goregull
        rank: Dangerous
        description: >
          Scavengers by nature, the vulture-sized goregulls feed primarily on dead
          sea life, but are known to harass the crews of floundering ships.

      - range: "66–75"
        result: Monarch Bat
        rank: Formidable
        description: >
          These oversized bats, large enough to carry off an unlucky islander,
          dwell in caves and amid jungle canopies. As the sun sets, they leave their
          roosts to hunt. They are particularly dangerous on moonless nights when
          their swift, silent approach goes unnoticed.

      - range: "76–85"
        result: Bloodmite
        rank: Dangerous
        description: >
          Bloodmites are hound-sized, flying insects. They primarily cling to the
          hide of titanic beasts, feeding through a blade-tipped proboscis, but are
          not averse to preying upon smaller targets.

      - range: "86–95"
        result: Thanatoi
        rank: Dangerous
        description: >
          These moth-like creatures are unsettlingly large but harmless. They are
          often seen on nights when Wraith is full—they shimmer with a strange,
          ethereal glow, as if reflecting the light of the moon. Many islanders
          believe they escort souls into the world beyond. Look too long into their
          alluring glow, they say, and you suffer a glimpse of your own death.

      - range: "96–100"
        result: Abomination
        rank: Various Ranks
        description: >
          Generate this beast using the Starforged creature oracles (page 336 of the
          Starforged rulebook), giving it an air form.

# Code
- Starting Region
- Overland waypoints (p150)

Let's continue making bundles of "these usually go together" oracles / rolls in Sundered Isles:
- Settlement
	- Settlement location: 1 roll
	- Settlement size: 1 roll
	- Settlement aesthetics: 2 rolls
	- Settlement first look: 2 rolls, curse die
	- Settlement Controlling Faction: 1 roll
	- Settlement Disposition: 1 roll
	- Settlement Authority: 1 roll
	- Settlement Focus: 2 rolls, curse die
	- Settlement Details: 2 rolls, curse die
	- Settlement Name: 1 roll, curse die
- Island
	- Island landscape
		- Size: 1 roll
		- Terrain: 1 roll
		- Vitality: 1 roll
		- Visible Habitation: 1 roll
		- Nearby Islands: 1 roll
		- Coastline aspects: 2 rolls
		- Offshore observations: 2 rolls, curse die
		- Island name: 1 roll, curse die
- Character
	- Character first look: 2 rolls, curse die
	- Character disposition: 1 roll
	- Character role: (this has a sub-table)
		- Various sub-tables for Academic, Agent, etc.
	- Trademark accessories: 2 rolls
	- Trademark weapons: 1 roll, curse die
	- Character details: 2 rolls, curse die
	- Character goals: 2 rolls, curse die
	- Character Name: need to discuss this one - the given name (first name) and family name (last name) is there twice (1-100), and Moniker uses a Curse die. My suggestion would be to combine the given names into a big 200 entry list, and combine family name into a big 200 entry list.
		- Cursed moniker has sub-tables

Future state
- Rename project to be more appropriate to what it does
- Handle Myriads, Margins, Reaches for various Tables?
- Handle Island name based on type of grouping
- Handle Settlement name based on location
- Faction grid