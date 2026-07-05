import os
import glob
import re

arc_data = {
    "Arc_01": {
        "mechanic": "**The Tremors:** Once per day while in Prontera or the Culverts, roll 1d6. On a 1, a violent tremor strikes. All creatures must succeed on a DC 12 Dexterity saving throw or fall prone. In the sewers, a failed save also results in 1d4 bludgeoning damage from falling debris.",
        "mvp": "Deviruchi",
        "mvp_read_aloud": "\"The cultists drop to their knees, chanting in a language that makes your teeth ache. In the center of the summoning circle, the shadows tear open. A creature steps out—small, winged, and wielding a pitchfork. It looks almost comical, until it opens its eyes. They are pits of pure, burning malice. The Deviruchi laughs, a sound like grinding stones, and the shadows in the room leap to do its bidding.\""
    },
    "Arc_02": {
        "mechanic": "**Restless Spirits:** While in the Payon woods or caves, resting is dangerous. Whenever the party takes a long rest, the character on watch must make a DC 13 Wisdom saving throw. On a failure, hostile spirits interrupt the rest, denying its benefits and triggering a random encounter.",
        "mvp": "Moonlight Flower",
        "mvp_read_aloud": "\"The deepest chamber of the cave is overgrown with unnatural, glowing vegetation. At the center stands a beautiful woman in traditional Payon garb—but she has the ears and tails of a spectral fox. She turns to you, her face twisted in sorrow and rage. 'Why do you disturb the sleeping earth?' Moonlight Flower whispers, her voice echoing from all directions at once. The vines around her animate, reaching for your throats.\""
    },
    "Arc_03": {
        "mechanic": "**Unnatural Heat:** The heat radiating from beneath the sand causes extreme dehydration. In the Sograt Desert or Pyramids, characters require twice as much water. Failing to drink enough requires a DC 14 Constitution saving throw each hour, gaining one level of Exhaustion on a failure.",
        "mvp": "Osiris (and Amon Ra)",
        "mvp_read_aloud": "\"The heavy stone doors to the burial chamber groan open. Inside, gold and jewels glitter in the torchlight, but the air is freezing cold. Rising from a golden sarcophagus is Osiris, his mummified body wrapped in ancient linens, wielding a staff crackling with dark energy. 'The sands belong to the dead,' he hisses, a swarm of scarabs pouring from his empty eye sockets.\""
    },
    "Arc_04": {
        "mechanic": "**Wild Magic Surges:** In Geffen and the surrounding fields, the failing seal disrupts magic. Whenever a spell of 1st level or higher is cast, roll 1d20. On a 1, a Wild Magic Surge occurs. Roll on the sorcerer Wild Magic table to determine the effect.",
        "mvp": "Baphomet",
        "mvp_read_aloud": "\"The massive seal on the floor of the guild basement shatters with the sound of breaking glass. From the abyss below rises a demon of legend. Baphomet stands twenty feet tall, his goat-like head crowned with massive, curving horns. He wields a scythe large enough to cleave a house in two. The demon doesn't roar; he merely exhales a cloud of black ash and points the scythe directly at you.\""
    },
    "Arc_05": {
        "mechanic": "**The Churning Tides:** In Alberta and the Byalan Undersea, the tides are violently unpredictable. During combat, on initiative count 20 (losing ties), a rogue wave of black water washes over the battlefield. Any creature not anchored or holding on must succeed on a DC 13 Strength saving throw or be pushed 10 feet and knocked prone.",
        "mvp": "Tao Gunka",
        "mvp_read_aloud": "\"The cavern shakes, and the stalactites above rain dust down upon you. Out of the darkness rolls a massive, stony mass, uncoiling like a living boulder. Tao Gunka rises, its rocky hide covered in glowing, ancient runes. It lets out a guttural, booming roar that reverberates through the stone, and the very ground beneath your feet begins to shift as the golem charges.\""
    },
    "Arc_06": {
        "mechanic": "**Failing Gravity:** The magic keeping Yuno afloat is fluctuating. Roll 1d6 at the start of any combat in Yuno. On a 6, gravity lessens for the encounter. Jump distances are tripled, and falling damage is halved, but any creature hit by a melee attack must make a DC 12 Dexterity saving throw or be pushed 10 feet into the air.",
        "mvp": "Mistress",
        "mvp_read_aloud": "\"The buzzing sound grows from an irritating hum to a deafening roar. Swarms of giant hornets part, revealing a colossal, humanoid queen bee wearing a mock crown. Mistress hovers above you, her wings beating so fast they are a blur. 'Pests,' she sneers, her stinger dripping with corrosive venom. 'You dare invade the hive of the sky?'\""
    },
    "Arc_07": {
        "mechanic": "**Toxic Smog:** The air in Einbroch is toxic. Characters without breathing masks or filtration must make a DC 13 Constitution saving throw every hour. On a failure, they suffer the Poisoned condition until they spend an hour in clean air.",
        "mvp": "RSX-0806",
        "mvp_read_aloud": "\"The blast doors tear open with a screech of tortured metal. Emerging from the smog is a mechanical nightmare—RSX-0806, a massive juggernaut of rusted iron, spinning saws, and blazing furnaces. Pistons pump furiously as it locks onto you with a glowing red optic sensor. 'TARGET ACQUIRED,' a synthesized, emotionless voice booms from its chassis. 'COMMENCING DISPOSAL.'\""
    },
    "Arc_08": {
        "mechanic": "**Aura of Decay:** The dark magic of Glast Heim saps vitality. Any healing magic cast within the ruins heals for half its normal amount (rounded down). Potions function normally.",
        "mvp": "Dark Lord",
        "mvp_read_aloud": "\"The temperature drops so fast your breath turns to ice. Floating above the shattered throne is the Dark Lord, an entity of pure, coalesced shadow wrapped in rotting regal robes. He holds a massive tome that bleeds black ink onto the floor. 'The living,' he whispers, a voice that sounds like a crypt closing forever. 'Such a fragile, temporary condition.'\""
    },
    "Arc_09": {
        "mechanic": "**Oppressive Holiness:** The sanctuary is saturated with hostile divine magic. Any character who does not worship Freya or Odin has disadvantage on saving throws against being Charmed or Frightened while in Rachel or the Sanctuary.",
        "mvp": "Gloom Under Night",
        "mvp_read_aloud": "\"The holy light of the sanctuary is suddenly snuffed out, replaced by a suffocating, inky blackness. A massive, formless shadow detaches itself from the ceiling, dropping to the floor with the weight of a collapsing building. Gloom Under Night is a manifestation of the fanaticism and dark secrets of the church—a swirling vortex of dark energy and agonized faces screaming in silent prayer.\""
    },
    "Arc_10": {
        "mechanic": "**Chemical Paranoia:** The chemical run-off from the Bio Labs infects the slums. Characters taking damage in the slums or Bio Labs must succeed on a DC 12 Wisdom saving throw or become paranoid for 1 minute. A paranoid character must use all their movement to move away from the nearest creature, friend or foe.",
        "mvp": "Kiel D-01",
        "mvp_read_aloud": "\"The laboratory is pristine, entirely unlike the slums above. At the center stands Kiel D-01, a perfectly crafted android wearing a gentleman's suit. He adjusts his cuffs, his mechanical joints whirring silently. 'You have trespassed in the name of morality,' Kiel says calmly, drawing a hidden blade from his sleeve. 'I will demonstrate why flesh is an obsolete technology.'\""
    },
    "Arc_11": {
        "mechanic": "**Dragon's Wrath:** The area around Abyss Lake is prone to sudden geysers of elemental energy. At the start of combat, the GM can place 1d4 geysers on the map. On initiative count 10, they erupt, dealing 2d6 fire damage to anyone within 5 feet (DC 14 Dex save for half).",
        "mvp": "Valkyrie Randgris",
        "mvp_read_aloud": "\"The clouds part, and a figure descends on wings of pure, blinding light. Valkyrie Randgris touches down, her armor immaculate, her spear humming with divine power. But her eyes are blank, her movements jerky and unnatural, as if she is a puppet pulled by unseen strings. 'The Voice commands,' she says, her tone monotone and devoid of mercy. 'The unmaking must proceed.'\""
    },
    "Arc_12": {
        "mechanic": "**Dimensional Sickness:** The New World's alien atmosphere causes disorientation. Upon entering a new area of the map, everyone must roll 1d20. On a 1-5, the character has Disadvantage on Initiative rolls for the next encounter due to vertigo.",
        "mvp": "Naght Sieger / Nidhoggr's Shadow",
        "mvp_read_aloud": "\"The dimensional rift pulses violently, and from the tear emerges Nidhoggr's Shadow. It is a dragon not made of flesh, but of raw, jagged darkness and astral energy. Its wings blot out the alien sky, and its roar creates a shockwave that flings you back. The air around it crackles with energy that threatens to rip reality itself to pieces.\""
    },
    "Arc_13": {
        "mechanic": "**The Stifling Fog:** The Nameless Island is covered in thick fog. Visibility is reduced to 15 feet. Creatures beyond that distance have total cover.",
        "mvp": "Beelzebub",
        "mvp_read_aloud": "\"The buzzing of the flies becomes a deafening roar. In the center of the desecrated abbey, a grotesque, bloated mass of flesh and insectoid limbs writhes. Beelzebub, Lord of the Flies, uncoils. Hundreds of compound eyes lock onto you. The demon speaks not with a voice, but with the synchronized buzzing of millions of wings: 'WE HUNGER.'\""
    },
    "Arc_14": {
        "mechanic": "**Volcanic Ash:** The air is thick with ash. Ranged weapon attacks have their normal range and maximum range halved.",
        "mvp": "Ifrit",
        "mvp_read_aloud": "\"The magma pool bubbles violently and explodes upward. From the pillar of fire emerges Ifrit, the lord of flame. He is a towering colossus of molten rock and raging fire, wielding a sword forged in the heart of the world. The heat is so intense your armor burns to the touch. 'Surt awakens!' Ifrit bellows, a sound like a volcanic eruption. 'Burn, and be reborn in the ash!'\""
    },
    "Arc_15": {
        "mechanic": "**Time Anomalies:** In Thanatos Tower and Aldebaran, time is unstable. Whenever a character rolls a natural 1 or 20 on an attack roll, time shifts. The combatant immediately takes another turn, but suffers 1 level of Exhaustion afterward.",
        "mvp": "Memory of Thanatos",
        "mvp_read_aloud": "\"At the pinnacle of the tower, reality is fractured. Before you stands the Memory of Thanatos—a ghostly projection of the legendary hero, trapped forever in the moment of his corruption. He wears the armor of a savior, but wields the dark energy of a demon. 'I saved them,' the phantom whispers, swinging a sword that cuts through time itself. 'Why am I the villain?'\""
    },
    "Arc_16": {
        "mechanic": "**Martial Law:** Prontera is on high alert. Any loud noise or overt use of magic in the streets instantly summons a patrol of 1d4+1 Chivalry Knights (veterans) who are hostile, believing the party to be cultists.",
        "mvp": "Bijou",
        "mvp_read_aloud": "\"The Royal Banquet hall is a slaughterhouse. Standing amidst the fallen knights is Bijou, the Whisperers' infiltrator. She wipes royal blood from her cheek and smiles—a smile completely devoid of sanity. 'It was so easy,' she giggles, raising her hands as dark, necrotic magic animates the dead knights around her. 'The King is dead! Long live the cascade!'\""
    },
    "Arc_17": {
        "mechanic": "**Rogue Leylines:** Varmundt's mansion is a magical minefield. Moving more than 20 feet in a single turn requires a DC 14 Dexterity (Acrobatics) check. On a failure, the character triggers a magical snare, reducing their speed to 0 until the end of their next turn.",
        "mvp": "Beta / Awakening Silva Papilia",
        "mvp_read_aloud": "\"The massive biosphere shatters. Beta, the mansion's rogue guardian construct, integrates with the ancient Silva Papilia. The result is a terrifying hybrid of arcane machinery and violent, mutated nature. Razor-sharp metallic vines whip through the air, and glowing cannons charge with blinding magical energy. 'UNAUTHORIZED ACCESS,' it screeches in a distorted, dual voice. 'EXTERMINATE.'\""
    },
    "Arc_18": {
        "mechanic": "**The Grasp of the Dead:** In Niflheim, the ground itself hungers for the living. Any creature knocked prone has its movement speed halved for 1 minute as spectral hands cling to their legs.",
        "mvp": "Himmelmez",
        "mvp_read_aloud": "\"The throne room of Niflheim is paved with skulls. Himmelmez, the Witch of Death, lounges on her throne of bone, flanked by undead monstrosities. She is terrifyingly beautiful, radiating the cold, inevitable certainty of the grave. 'You fought so hard to reach the end,' she says, raising a hand as the shadows in the room rise into grasping claws. 'Allow me to reward you with eternal rest.'\""
    },
    "Arc_19": {
        "mechanic": "**The Apocalypse:** The world is ending. At the end of every round of combat, every creature takes 1d6 force damage as reality itself unravels around them. There is no saving throw.",
        "mvp": "Satan Morroc / Surt",
        "mvp_read_aloud": "\"The sky tears open, revealing the infinite black of the void. Satan Morroc pulls himself from the rift, a demon lord of incomprehensible scale. But he is merely the herald. Behind him, the void burns with absolute, world-ending fire. Surt is coming. The heat vaporizes the stone beneath your feet. Morroc looks down at you, the heroes who tried to stop the inevitable. He doesn't speak. He simply raises a hand to wipe you from existence.\""
    }
}

template = """
---

## MVP Encounter & Symptom Mechanics

### Mechanizing the Symptom
> {mechanic}

### MVP Read-Aloud: The Encounter with {mvp}
> **When the party finally confronts the MVP boss of this arc, read the following:**
> 
> > {mvp_read_aloud}
"""

for file in glob.glob('Campaign/**/DM_Roleplay_Guide.md', recursive=True):
    match = re.search(r'Arc_(\d+)', file)
    if match:
        arc_key = f"Arc_{match.group(1)}"
        if arc_key in arc_data:
            data = arc_data[arc_key]
            new_content = template.format(
                mechanic=data['mechanic'],
                mvp=data['mvp'],
                mvp_read_aloud=data['mvp_read_aloud']
            )
            
            with open(file, 'a', encoding='utf-8') as f:
                f.write(new_content)

print("Boss and mechanics updates complete.")
