-- Seal Cascade Campaign Quest Journal Entries
-- Maintained source. Merge QuestList blocks into client/System/OngoingQuestInfoList_True_EN.lub (latin1 + CRLF recommended).
-- 89 entries (20000-20234). Derived from DB + arc scripts + Obsidian vault extracts.
-- Format: Title + Description array (flavor, Location, Mob/Boss, Hunt/Return @dm warp, ^3355FFSummary...^000000).
-- Cleaned/expanded. See dm-handoff.md for merge instructions.
QuestList = QuestList or {}

QuestList[20000] = {
	Title = "Seal Cascade Session Active",
	Description = {
		"A campaign session is active for your party.",
		"Location: Prontera (fountain area)",
		"Enables DM campaign NPCs, beats, and minimap markers for the active party only.",
		"^3355FFSummary: Seal Cascade Session Active.^000000",
	},
}

QuestList[20001] = {
	Title = "Omens at the Fountain",
	Description = {
		"The village episode. Beneath the holiest city in the world, someone is painting goat-headed signs in the sewer-water — and the ground shivers at night.",
		"Location: Prontera",
		"Swear into the Adventurers' Guild with Quartermaster Wynne. Start of Arc 1. Branches set dm_arc01_* and dm_mira_lives.",
		"Return: @dm warp prontera 156 191",
		"^3355FFSummary: Omens at the Fountain.^000000",
	},
}

QuestList[20002] = {
	Title = "Contract: Cellar Vermin",
	Description = {
		"Clear Tarou from the Prontera Culvert as your first guild contract.",
		"Location: Prontera Culvert (prt_sewb2)",
		"Mob: Tarou x10",
		"Hunt: @dm warp prt_sewb2 100 100",
		"Return: @dm warp prontera 156 191",
		"Basic hunt to prove yourself to the guild.",
		"^3355FFSummary: Contract: Cellar Vermin.^000000",
	},
}

QuestList[20003] = {
	Title = "Field Contract: Rockers and Rumors",
	Description = {
		"Work the Rocker field while listening for rumors from refugees.",
		"Location: Prontera Field (prt_fild07)",
		"Turn in: Grasshopper's Leg x15, Animal Skin x10, Mushroom Spore x5",
		"Hunt: @dm warp prt_fild07 200 200",
		"Return: @dm warp prontera 156 191",
		"Field work and intel gathering.",
		"^3355FFSummary: Field Contract: Rockers and Rumors.^000000",
	},
}

QuestList[20004] = {
	Title = "The Trembling Ground",
	Description = {
		"A refugee child has gone missing following a 'gray almsman'. Investigate the south gate soup line and the ground tremors.",
		"Location: Prontera south gate + upper Culvert",
		"Introduces Mira and Deacon Holt. Branch affects dm_mira_lives and refugee flags.",
		"Return: @dm warp prontera 156 40",
		"^3355FFSummary: The Trembling Ground.^000000",
	},
}

QuestList[20005] = {
	Title = "The Goat-Headed Sign",
	Description = {
		"Follow the paintings down. Something beneath the holiest city in the world is being prayed to — and the prayer is working.",
		"Location: Prontera Culvert (prt_sewb4)",
		"Boss: Deviruchi",
		"Hunt: @dm warp prt_sewb4 103 100",
		"Return: @dm warp prontera 156 191",
		"Arc 1 climax. Cassell escapes and leaves the Sigil Ring. Holt spared/killed fork.",
		"^3355FFSummary: The Goat-Headed Sign.^000000",
	},
}

QuestList[20006] = {
	Title = "First Field Test",
	Description = {
		"Bring proof of your first field test — Jellopy, Fluff, Clover — back to Quartermaster Wynne. The guild wants to see you can follow a simple contract.",
		"Location: Prontera",
		"Hunt/turn-in near fountain or fields.",
		"^3355FFSummary: Early repeatable turn-in to simulate guild contracts and gain a small level bump between story beats.^000000",
	},
}

QuestList[20007] = {
	Title = "The Sleeping Forest",
	Description = {
		"The forest won't let its dead sleep. Payon is burying its past — and something is digging it back up under the light of the new moon.",
		"Location: Payon",
		"Start of Arc 2. Hunter Voss and ancestor disturbance. Lanterns and bone tags lead to the truth.",
		"Return: @dm warp payon 160 120",
		"^3355FFSummary: The Sleeping Forest. Main tracker for Moonlight Flower and the restless dead.^000000",
	},
}

QuestList[20008] = {
	Title = "Mushroom Ring Patrol",
	Description = {
		"Patrol the ring of mushrooms that shouldn't be growing here. The dead are listening.",
		"Location: Payon Forest (pay_fild08)",
		"Mob: Spore x20",
		"Hunt: @dm warp pay_fild08 100 100",
		"^3355FFSummary: Mushroom Ring Patrol.^000000",
	},
}

QuestList[20009] = {
	Title = "Bone Tag Turn-In",
	Description = {
		"Bone tags from old soldiers are being turned in for coin. Someone in Payon is paying well to keep the graves quiet — and the ancestors angry.",
		"Location: Payon Cave",
		"Mob: Skeleton, Familiar",
		"Hunt: @dm warp pay_dun00 50 50",
		"Return: @dm warp payon 160 120",
		"^3355FFSummary: Bone Tag Turn-In. Part of the ancestor unrest leading to Moonlight Flower.^000000",
	},
}

QuestList[20010] = {
	Title = "Lanterns for the Lost",
	Description = {
		"On the new moon, Payon floats blue lanterns down the river for the lost.",
		"Location: Payon tombs area",
		"Arc 2 support. Honors ancestors disturbed by Voss.",
		"^3355FFSummary: Lanterns for the Lost.^000000",
	},
}

QuestList[20011] = {
	Title = "The Emptied Graves",
	Description = {
		"Graves stand open. The bones that should rest are marching.",
		"Location: Payon Cave 4 area",
		"Boss hook for Moonlight Flower.",
		"Hunt: @dm warp pay_dun03 120 120",
		"^3355FFSummary: The Emptied Graves.^000000",
	},
}

QuestList[20012] = {
	Title = "What the Ancestors Won't Say",
	Description = {
		"The ancestors have a message, but they won't say it to the living who forgot them. Voss's desecration has stirred them — the lanterns and tags lead here.",
		"Location: Payon / Payon Cave",
		"^3355FFSummary: What the Ancestors Won't Say. Climactic story beat before Moonlight Flower. Choices affect ancestor respect flags.^000000",
	},
}

QuestList[20013] = {
	Title = "Sand and Whispers",
	Description = {
		"Morroc's relief mission hides a cult dig toward the oldest seal under the desert. Rashid guides through Sograt, Ant Hell, Sphinx. Mother Sabra frames the moral cost of the campaign.",
		"Location: Morroc",
		"Start Arc 3. Amon Ra and the desert seal. Branches affect cult strength later.",
		"Return: @dm warp morocc 150 100",
		"^3355FFSummary: Sand and Whispers. Main tracker for Act I desert arc and Amon Ra confrontation.^000000",
	},
}

QuestList[20014] = {
	Title = "Caravan Water Debt",
	Description = {
		"Caravans are paying water debt in blood. Something in the wells is thirsty.",
		"Location: Sograt Desert",
		"Mob: Muka, Hode",
		"Hunt: @dm warp moc_fild01 100 80",
		"^3355FFSummary: Caravan Water Debt.^000000",
	},
}

QuestList[20015] = {
	Title = "Ant Hell Survey",
	Description = {
		"Ant Hell survey. The eggs are wrong. The workers sing hymns to something below.",
		"Location: Ant Hell (anthell01)",
		"Mob: Ant Egg, Familiar",
		"Hunt: @dm warp anthell01 50 50",
		"^3355FFSummary: Ant Hell Survey.^000000",
	},
}

QuestList[20016] = {
	Title = "Sphinx Night Watch",
	Description = {
		"Sphinx night watch. The statues' eyes follow you. The old gods are not asleep.",
		"Location: Sphinx (in_sphinx2)",
		"Mob: Requiem, Zerom",
		"Hunt: @dm warp in_sphinx2 100 100",
		"^3355FFSummary: Sphinx Night Watch.^000000",
	},
}

QuestList[20017] = {
	Title = "What the Desert Spat Up",
	Description = {
		"What the desert spat up. A sealed tomb cracked open. The first symptom of the cascade walks again among the dunes.",
		"Location: Morroc area / Sograt",
		"Summary: Build to Amon Ra. The cult presence grows stronger.",
		"^3355FFSummary: What the Desert Spat Up.^000000",
	},
}

QuestList[20018] = {
	Title = "The King Beneath",
	Description = {
		"The King Beneath. Amon Ra sits on a throne of lies and old bones.",
		"Location: Sphinx deeper",
		"Boss: Amon Ra (+ Osiris, Phreeoni, Maya, Orc Hero sides)",
		"Hunt: @dm warp in_sphinx2 100 50",
		"Return: @dm warp morocc 150 100",
		"^3355FFSummary: The King Beneath.^000000",
	},
}

QuestList[20019] = {
	Title = "The City Above the Beast",
	Description = {
		"The City Above the Beast. Geffen's towers cast long shadows over something that prays in the dark.",
		"Location: Geffen",
		"Start Arc 4. Baphomet.",
		"Return: @dm warp geffen 120 60",
		"^3355FFSummary: The City Above the Beast.^000000",
	},
}

QuestList[20020] = {
	Title = "Tower Apprentice Drills",
	Description = {
		"Geffen's brilliant tower-magic is overflow from Baphomet's prison. Apprentice drills in the tower are teaching more than magic — something dark is leaking into the curriculum.",
		"Location: Geffen Tower",
		"Mob: Poison Spore x20",
		"Hunt: @dm warp gef_tower 100 100",
		"^3355FFSummary: Tower Apprentice Drills. Arc 4 support hunt leading to the Orc bounty and Baphomet seal.^000000",
	},
}

QuestList[20021] = {
	Title = "Orc Village Bounty",
	Description = {
		"Chipped orc banners from the village edge. The sigil marks are not orcish — they are bait drawing the tribes. The city is using them.",
		"Location: Orc Village (orc_village)",
		"Mob: Orc Warrior x20",
		"Hunt: @dm warp orc_village 100 100",
		"^3355FFSummary: Orc Village Bounty. Arc 4 hunt with branch choices on how to handle the evidence and villagers.^000000",
	},
}

QuestList[20022] = {
	Title = "Argiope Silk Run",
	Description = {
		"Black silk thread from the spiders. Every strand maps back to the lower vault. Gather evidence or burn the contaminated silk?",
		"Location: Mt. Mjolnir fields / Argiope areas",
		"Mob: Argiope x20",
		"Hunt: @dm warp mjolnir_06 100 100",
		"^3355FFSummary: Argiope Silk Run. Arc 4 hunt feeding into the Vault and Pilgrim choice. Branches on evidence handling.^000000",
	},
}

QuestList[20023] = {
	Title = "The Vault That Prays",
	Description = {
		"The Vault That Prays. Baphomet's seal is under the city, and the city is listening.",
		"Location: Geffen Dungeon / OD1",
		"Boss: Baphomet",
		"Hunt: @dm warp gef_dun00 100 100",
		"^3355FFSummary: The Vault That Prays.^000000",
	},
}

QuestList[20024] = {
	Title = "The Pilgrim's Offer",
	Description = {
		"At the heart of the Vault That Prays, a choice awaits. Ward the seal or break it open — the decision will echo through later arcs.",
		"Location: Baphomet seal area (Geffen Dungeon)",
		"^3355FFSummary: The Pilgrim's Offer. Key branch decision in Arc 4 (affects later seal strength/flavor).^000000",
	},
}

QuestList[20025] = {
	Title = "Tides and Trade",
	Description = {
		"The Morroc refugees reach Alberta by sea, and the same ships carry Whisperer cargo. Captain Mara and Smuggler-Baron Brode reveal the cult as a logistics network before Tao Gunka rises.",
		"Location: Alberta / Izlude",
		"Start Arc 5. Tao Gunka. Refugee flow ties back to earlier arcs.",
		"Return: @dm warp alberta 120 60",
		"^3355FFSummary: Tides and Trade. Main tracker for Act I sea arc and the deep boss.^000000",
	},
}

QuestList[20026] = {
	Title = "Refugee Ferry Rotation",
	Description = {
		"The sea takes the desperate and returns them changed. Alberta's docks are a revolving door of refugees fleeing the growing symptoms of the cascade.",
		"Location: Alberta / Izlude docks",
		"^3355FFSummary: Refugee Ferry Rotation. Arc 5 support story beat for the Tides and Trade arc.^000000",
	},
}

QuestList[20027] = {
	Title = "Byalan Tide Contract",
	Description = {
		"The currents are pulling things up from the trench that should stay down. Alberta's refugee flow and Byalan's depths are connected by more than water.",
		"Location: Byalan (iz_dun00)",
		"Mob: water monsters (various)",
		"Hunt: @dm warp iz_dun00 100 100",
		"^3355FFSummary: Byalan Tide Contract. Arc 5 hunt building toward Tao Gunka and the deep cargo of souls.^000000",
	},
}

QuestList[20028] = {
	Title = "Sunken Ship Manifest",
	Description = {
		"The pirate dead remember a debt. Byalan's sunken ships hold more than treasure — the currents are pulling things up that should stay down.",
		"Location: Sunken Ship (iz_dun01)",
		"Mob: Hydra, Pirate Skeleton",
		"Hunt: @dm warp iz_dun01 50 50",
		"^3355FFSummary: Sunken Ship Manifest. Arc 5 Byalan hunt building to Tao Gunka.^000000",
	},
}

QuestList[20029] = {
	Title = "Cargo of Souls",
	Description = {
		"Cargo of Souls. Something is trading lives for safe passage.",
		"Location: Turtle Island / Byalan deep",
		"^3355FFSummary: Cargo of Souls.^000000",
	},
}

QuestList[20030] = {
	Title = "What Turned Over in the Deep",
	Description = {
		"What Turned Over in the Deep. Tao Gunka wakes. The sea floor shifts.",
		"Location: Byalan 5 / Turtle deep",
		"Boss: Tao Gunka",
		"Hunt: @dm warp iz_dun05 100 50",
		"^3355FFSummary: What Turned Over in the Deep.^000000",
	},
}

QuestList[20101] = {
	Title = "The Heart That Holds the City",
	Description = {
		"The Heart That Holds the City. Yuno's floating heart is beating wrong.",
		"Location: Yuno",
		"Start Arc 6. Norgroad / Juno floating republic.",
		"Return: @dm warp yuno 150 180",
		"^3355FFSummary: The Heart That Holds the City.^000000",
	},
}

QuestList[20102] = {
	Title = "The Number Nobody Wants",
	Description = {
		"Census data that ends in disappearances. The floating city is counting its people — and some numbers are being erased from the ledgers.",
		"Location: Yuno",
		"Summary: Arc 6 story hook leading into Harpy logs and the Norgroad heat. XP/support flavor.",
		"^3355FFSummary: The Number Nobody Wants.^000000",
	},
}

QuestList[20103] = {
	Title = "Harpy Weather Log",
	Description = {
		"Harpy Weather Log. Storms that sing. The sky is keeping records.",
		"Location: Juno fields",
		"Mob: Harpy x20",
		"Hunt: @dm warp yuno_fild01 100 100",
		"^3355FFSummary: Harpy Weather Log.^000000",
	},
}

QuestList[20104] = {
	Title = "Juperos Parts Requisition",
	Description = {
		"Juperos Parts Requisition. The ruins are selling spare parts again.",
		"Location: Juperos",
		"^3355FFSummary: Juperos Parts Requisition.^000000",
	},
}

QuestList[20105] = {
	Title = "Norgroad Heat Index",
	Description = {
		"Norgroad Heat Index. The forge under the city is running hot — on purpose.",
		"Location: Norgroad / Yuno area",
		"Boss: RSX-0806",
		"Hunt: @dm warp ein_dun02 150 150",
		"^3355FFSummary: Norgroad Heat Index.^000000",
	},
}

QuestList[20111] = {
	Title = "The Unit That Wouldn't Stay Dead",
	Description = {
		"The Unit That Wouldn't Stay Dead. Einbroch's dead workers keep reporting for shift.",
		"Location: Einbroch",
		"Start Arc 7. RSX and factory rot.",
		"Return: @dm warp einbroch 100 80",
		"^3355FFSummary: The Unit That Wouldn't Stay Dead.^000000",
	},
}

QuestList[20112] = {
	Title = "Whose Side the Smoke Is On",
	Description = {
		"The factory fog has opinions. It clings to the lungs of those who ask too many questions about the missing.",
		"Location: Einbroch fields",
		"Summary: Arc 7 atmospheric flavor. Ties into the smoke pressure hazard and RSX beat.",
		"^3355FFSummary: Whose Side the Smoke Is On.^000000",
	},
}

QuestList[20113] = {
	Title = "Factory Whistle Shift",
	Description = {
		"Factory Whistle Shift. The whistle blows for ghosts.",
		"Location: Einbroch factory",
		"Mob: Metaling, etc.",
		"^3355FFSummary: Factory Whistle Shift.^000000",
	},
}

QuestList[20114] = {
	Title = "Metaling Scrap Drive",
	Description = {
		"Metaling Scrap Drive. They are building something from the scrap of the missing.",
		"Location: Ein_fild",
		"Mob: Metaling x20",
		"^3355FFSummary: Metaling Scrap Drive.^000000",
	},
}

QuestList[20115] = {
	Title = "Mine Dust Medicine",
	Description = {
		"Mine Dust Medicine. The dust is medicine now. The patients mine more.",
		"Location: Einbroch Mine (ein_dun02)",
		"Mob: Pitman",
		"Hunt: @dm warp ein_dun02 50 50",
		"^3355FFSummary: Mine Dust Medicine.^000000",
	},
}

QuestList[20121] = {
	Title = "A Kingdom Unmade",
	Description = {
		"A Kingdom Unmade. Glast Heim's throne room is empty and listening.",
		"Location: Glast Heim",
		"Start Arc 8. Dark Lord.",
		"Return: @dm warp glast_01 100 100",
		"^3355FFSummary: A Kingdom Unmade.^000000",
	},
}

QuestList[20122] = {
	Title = "Outer Garrison",
	Description = {
		"Outer Garrison. The walls remember who they failed to keep out.",
		"Location: Glast Heim outer",
		"Mob: Orc Zombie etc",
		"^3355FFSummary: Outer Garrison.^000000",
	},
}

QuestList[20123] = {
	Title = "Fallen Choir",
	Description = {
		"Fallen Choir. The cathedral sings without mouths.",
		"Location: Glast_02 / churchyard",
		"Mob: Fallen",
		"^3355FFSummary: Fallen Choir.^000000",
	},
}

QuestList[20124] = {
	Title = "The Weight of Faith",
	Description = {
		"The Weight of Faith. Dark Lord wears the crown he took from the dead king.",
		"Location: Glast Heim",
		"Boss: Dark Lord (+ branch adds based on Manfred)",
		"Hunt: @dm warp glast_01 150 150",
		"^3355FFSummary: The Weight of Faith.^000000",
	},
}

QuestList[20131] = {
	Title = "The Bleeding Blessing",
	Description = {
		"The Bleeding Blessing. Rachel's faith is bleeding from the inside.",
		"Location: Rachel",
		"Start Arc 9. Ice queen / temple rot.",
		"Return: @dm warp rachel 120 120",
		"^3355FFSummary: The Bleeding Blessing.^000000",
	},
}

QuestList[20132] = {
	Title = "Ice Core Samples",
	Description = {
		"Ice Core Samples. The glacier is keeping secrets in cold storage.",
		"Location: Ice dungeon / Rachel fields",
		"Mob x20",
		"^3355FFSummary: Ice Core Samples.^000000",
	},
}

QuestList[20133] = {
	Title = "Hollow Blessings",
	Description = {
		"Hollow Blessings. The priests smile with too many teeth.",
		"Location: Rachel temple",
		"^3355FFSummary: Hollow Blessings.^000000",
	},
}

QuestList[20134] = {
	Title = "The Prelate's Record",
	Description = {
		"The Prelate's Record. Someone rewrote the book.",
		"Location: Rachel",
		"Branch to frozen faith climax.",
		"^3355FFSummary: The Prelate's Record.^000000",
	},
}

QuestList[20141] = {
	Title = "The Heroes They Made",
	Description = {
		"The Heroes They Made. Lighthalzen's heroes were assembled, not born.",
		"Location: Lighthalzen",
		"Start Arc 10. Bio lab / Echo.",
		"Return: @dm warp lighthalzen 100 50",
		"^3355FFSummary: The Heroes They Made.^000000",
	},
}

QuestList[20142] = {
	Title = "Lab Infiltration",
	Description = {
		"Lab Infiltration. The lower levels remember every test subject.",
		"Location: Lighthalzen Bio Lab (lhz_dun01)",
		"Mob: Remover x20",
		"Hunt: @dm warp lhz_dun01 100 100",
		"^3355FFSummary: Lab Infiltration.^000000",
	},
}

QuestList[20143] = {
	Title = "Lower Level Sweep",
	Description = {
		"Lower Level Sweep. The prototypes are still following their last orders.",
		"Location: lhz_dun02",
		"Mob: various",
		"^3355FFSummary: Lower Level Sweep.^000000",
	},
}

QuestList[20144] = {
	Title = "Echo's Protocol",
	Description = {
		"Echo's Protocol. The one who said no. Treat it like a person or a tool.",
		"Location: Bio lab deep",
		"Echo fate branch. dm_echo_trusts_party gate.",
		"^3355FFSummary: Echo's Protocol.^000000",
	},
}

QuestList[20151] = {
	Title = "When Heaven Turns",
	Description = {
		"When Heaven Turns. The tower that reaches the gods has started reaching back.",
		"Location: Aldebaran / Thanatos approach",
		"Start Arc 11/15 tower. High tower content.",
		"Return: @dm warp aldebaran 140 140",
		"^3355FFSummary: When Heaven Turns.^000000",
	},
}

QuestList[20153] = {
	Title = "Gryphon Vigil",
	Description = {
		"Gryphon Vigil. The riders are gone but the mounts still circle.",
		"Location: Thanatos tower approach",
		"^3355FFSummary: Gryphon Vigil.^000000",
	},
}

QuestList[20154] = {
	Title = "Dragon Pack Dispersal",
	Description = {
		"Dragon Pack Dispersal. They were never tamed.",
		"Location: thana_fild / tower",
		"Mob x20",
		"^3355FFSummary: Dragon Pack Dispersal.^000000",
	},
}

QuestList[20155] = {
	Title = "The Zealot's Testimony",
	Description = {
		"The Zealot's Testimony. Thanatos did not fall. He chose.",
		"Location: thana_boss",
		"Boss encounter. Branch on Bjorn fate.",
		"Hunt: @dm warp thana_boss 100 50",
		"^3355FFSummary: The Zealot's Testimony.^000000",
	},
}

QuestList[20161] = {
	Title = "The Wound With a Keeper",
	Description = {
		"The Wound With a Keeper. The New World is the scar that remembers how it was made.",
		"Location: Splendide / Manuk",
		"Start Arc 12. Naght Sieger. Mid-cascade reveal.",
		"Return: @dm warp splendide 150 80",
		"^3355FFSummary: The Wound With a Keeper.^000000",
	},
}

QuestList[20163] = {
	Title = "New World Cornus Survey",
	Description = {
		"New World Cornus Survey. The flowers are watching.",
		"Location: spl_fild01",
		"Mob: Cornus x20",
		"Hunt: @dm warp spl_fild01 100 100",
		"^3355FFSummary: New World Cornus Survey.^000000",
	},
}

QuestList[20164] = {
	Title = "Naga Border Patrol",
	Description = {
		"Naga Border Patrol. The border is a suggestion the snakes ignore.",
		"Location: spl_fild / man_fild",
		"Mob: Naga x20",
		"^3355FFSummary: Naga Border Patrol.^000000",
	},
}

QuestList[20165] = {
	Title = "The Vance Proposal",
	Description = {
		"The Vance Proposal. Captain Vance has a plan that might save or damn the rift.",
		"Location: New World camp",
		"Vance exposed/helped branch for Arc 12 hazard strength.",
		"^3355FFSummary: The Vance Proposal.^000000",
	},
}

QuestList[20171] = {
	Title = "The Council of the Drowned",
	Description = {
		"The Council of the Drowned. Nameless Island keeps voting on who gets to leave.",
		"Location: Nameless Island",
		"Start Arc 13. Beelzebub hosts the demon coalition in the Abbey.",
		"Return: Father Quill on Nameless Island.",
		"^3355FFSummary: The Council of the Drowned.^000000",
	},
}

QuestList[20172] = {
	Title = "A Name You Knew",
	Description = {
		"A Name You Knew. One of the dead came to the island for you.",
		"Location: Nameless Island",
		"Reckon honestly or put the familiar dead down and keep moving.",
		"^3355FFSummary: A Name You Knew.^000000",
	},
}

QuestList[20173] = {
	Title = "Abbey Bell Rotation",
	Description = {
		"Abbey Bell Rotation. Ring the Abbey routes without letting the dead organize around the sound.",
		"Location: abbey01",
		"Hunt Banshee, Zombie Slaughter, and Ragged Zombie.",
		"^3355FFSummary: Abbey Bell Rotation.^000000",
	},
}

QuestList[20174] = {
	Title = "Drowned Coin Tithe",
	Description = {
		"Drowned Coin Tithe. Recover the old payments from the lower crypt route.",
		"Location: abbey02",
		"Hunt Zombie Slaughter and Ragged Zombie.",
		"^3355FFSummary: Drowned Coin Tithe.^000000",
	},
}

QuestList[20175] = {
	Title = "Lasagna Root Wardens",
	Description = {
		"Lasagna Root Wardens. Living roots still hold one edge of the island's boundary.",
		"Location: Bifrost root route stand-in",
		"Hunt Pom Spider, Angra Mantis, and Miming until Lasagna natural spawns exist.",
		"^3355FFSummary: Lasagna Root Wardens.^000000",
	},
}

QuestList[20181] = {
	Title = "The Herald in the Magma",
	Description = {
		"The Herald in the Magma. Veins is burning and the mountain is preaching.",
		"Location: Veins",
		"Start Arc 14. Ifrit is the herald, not the god.",
		"Return: Foreman Dunmar in Veins.",
		"^3355FFSummary: The Herald in the Magma.^000000",
	},
}

QuestList[20182] = {
	Title = "The Deep Shift",
	Description = {
		"The Deep Shift. Crews are trapped below while Hesma's sealed reports burn time.",
		"Location: Veins temple office / deep galleries",
		"Expose Hesma or take the deep approach seal for silence.",
		"^3355FFSummary: The Deep Shift.^000000",
	},
}

QuestList[20183] = {
	Title = "Veins Evacuation Ledger",
	Description = {
		"Veins Evacuation Ledger. Names on paper become people moving through smoke.",
		"Location: ve_fild03",
		"Hunt Magmaring, Muscipular, and Drosera while updating the ledger.",
		"^3355FFSummary: Veins Evacuation Ledger.^000000",
	},
}

QuestList[20184] = {
	Title = "Bifrost Ash Scouting",
	Description = {
		"Bifrost Ash Scouting. The ash is fusing into glass on a breathing cycle.",
		"Location: ecl_tdun02 / ecl_tdun03",
		"Hunt Antique Book and Lichterns while mapping evacuation routes.",
		"^3355FFSummary: Bifrost Ash Scouting.^000000",
	},
}

QuestList[20185] = {
	Title = "Magmaring Firebreak",
	Description = {
		"Magmaring Firebreak. The clusters are drifting toward the tenement wall.",
		"Location: ve_fild03",
		"Hunt Magmaring and choose how much of the firebreak is real.",
		"^3355FFSummary: Magmaring Firebreak.^000000",
	},
}

QuestList[20191] = {
	Title = "The Five Doors of a Dead Hero",
	Description = {
		"The Five Doors of a Dead Hero. Aldebaran remembers Thanatos. The doors remember the choice.",
		"Location: Aldebaran",
		"Start Arc 15. Hero's tomb / tower.",
		"Return: @dm warp aldebaran 140 140",
		"^3355FFSummary: The Five Doors of a Dead Hero.^000000",
	},
}

QuestList[20192] = {
	Title = "What the Tower Remembers",
	Description = {
		"What the Tower Remembers. Every floor is a confession.",
		"Location: Thanatos Tower",
		"Mob: various high",
		"Hunt: @dm warp thana_tower 50 50",
		"^3355FFSummary: What the Tower Remembers.^000000",
	},
}

QuestList[20193] = {
	Title = "Aldebaran Last Letters",
	Description = {
		"Aldebaran Last Letters. The mail never reached the living.",
		"Location: Aldebaran",
		"^3355FFSummary: Aldebaran Last Letters.^000000",
	},
}

QuestList[20194] = {
	Title = "Clock Tower Daily Wounds",
	Description = {
		"Clock Tower Daily Wounds. Nightmare Clock Tower loses minutes, and every lost minute leaves something behind.",
		"Location: c_tower3_",
		"Hunt Big Bell and decide whether to witness the trapped loops.",
		"^3355FFSummary: Clock Tower Daily Wounds.^000000",
	},
}

QuestList[20195] = {
	Title = "Fragment Relief Rotation",
	Description = {
		"Fragment Relief Rotation. Sort the Thanatos fragments before turning them into experience.",
		"Location: tha_t09 through tha_t12",
		"Hunt Thanatos Tower fragment-floor mobs and read what the pouch says.",
		"^3355FFSummary: Fragment Relief Rotation.^000000",
	},
}

QuestList[20201] = {
	Title = "The Royal Banquet",
	Description = {
		"The Royal Banquet. The court smiles while the seals break. Rina watches from the wings.",
		"Location: Prontera (banquet / prison)",
		"Start Arc 16. Bijou and Rina branches. dm_arc16_rina_* + prontera_united.",
		"Return: @dm warp prontera 150 150",
		"^3355FFSummary: The Royal Banquet.^000000",
	},
}

QuestList[20202] = {
	Title = "Underground Prison Cleanup",
	Description = {
		"Bijou's network is in the cells. The prison holds more than criminals — it holds the cult's eyes and ears in the capital.",
		"Location: Prontera Underground (prt_q)",
		"Mob: Disguise x20",
		"Hunt: @dm warp prt_q 100 100",
		"Return: @dm warp prontera 156 191",
		"^3355FFSummary: Underground Prison Cleanup.^000000",
	},
}

QuestList[20203] = {
	Title = "Terra Gloria",
	Description = {
		"Terra Gloria. The bloody work of cleaning a kingdom's name.",
		"Location: Prontera area prison",
		"Mob: Bloody Murderer x20",
		"Hunt: @dm warp prt_q 120 120",
		"^3355FFSummary: Terra Gloria.^000000",
	},
}

QuestList[20204] = {
	Title = "Royal House Audience Rounds",
	Description = {
		"Royal House Audience Rounds. Matron Rina offers three paths. Exposed, rolled, or defected.",
		"Location: Prontera court",
		"Rina choice sets dm_arc16_rina_exposed/rolled/defected. Affects Bijou kill vs Maret freed.",
		"Return: @dm warp prontera 150 150",
		"^3355FFSummary: Royal House Audience Rounds.^000000",
	},
}

QuestList[20211] = {
	Title = "Illusion Investigation",
	Description = {
		"Illusion Investigation. Varmundt's mansion is running experiments on the end of the world.",
		"Location: Varmundt Mansion area",
		"Start Arc 17. Admin branches.",
		"Return: @dm warp ba_pw01 100 100",
		"^3355FFSummary: Illusion Investigation.^000000",
	},
}

QuestList[20212] = {
	Title = "Sages Legacy",
	Description = {
		"The tools that sealed the demons are being recalibrated in secret. Varmundt's old machines are waking up with new instructions from the labs.",
		"Location: Biolabs / Mansion",
		"Mob x20",
		"Summary: Arc 17. Choices here affect dm_varmundt_tools_stabilized gate for the finale.",
		"^3355FFSummary: Sages Legacy.^000000",
	},
}

QuestList[20213] = {
	Title = "Tartaros Dive",
	Description = {
		"Tartaros Dive. The deep labs where the last door waits.",
		"Location: ba_pw03 / lhz_dun deep",
		"^3355FFSummary: Tartaros Dive.^000000",
	},
}

QuestList[20214] = {
	Title = "Biosphere Sample Rotation",
	Description = {
		"Biosphere Sample Rotation. The admin will trade access for data — or loyalty.",
		"Location: Varmundt",
		"Admin purged/negotiated/running branches. dm_varmundt_tools_stabilized gate.",
		"^3355FFSummary: Biosphere Sample Rotation.^000000",
	},
}

QuestList[20221] = {
	Title = "The Queen the Drowned Chose",
	Description = {
		"The Queen the Drowned Chose. Niflheim's queen has a bargain for the living.",
		"Location: Niflheim",
		"Start Arc 18. Himmelmez. dm_himmelmez_bargain.",
		"Return: @dm warp nif_fild01 100 100",
		"^3355FFSummary: The Queen the Drowned Chose.^000000",
	},
}

QuestList[20222] = {
	Title = "The Dead You Failed",
	Description = {
		"The Dead You Failed. Every ghost has your name on its ledger.",
		"Location: Niflheim",
		"Mob: Khalitzburg x15",
		"Hunt: @dm warp nif_fild 100 100",
		"^3355FFSummary: The Dead You Failed.^000000",
	},
}

QuestList[20223] = {
	Title = "Banquet Hall Procession",
	Description = {
		"Banquet Hall Procession. The queen's court does not eat. It remembers.",
		"Location: Niflheim palace",
		"Boss: Himmelmez encounter",
		"Bargain choice gate for Queen's Bargain ending.",
		"^3355FFSummary: Banquet Hall Procession.^000000",
	},
}

QuestList[20230] = {
	Title = "Allied Front Muster",
	Description = {
		"Allied Front Muster. XP support for finale. Turn leveling into allied strength.",
		"Location: Endgame maps (Morroc ruins, Ash Vacuum)",
		"Finale ally turnout XP support. Affects Shared Seal gate strength. Mira/Echo/Prontera etc.",
		"^3355FFSummary: Allied Front Muster.^000000",
	},
}

QuestList[20231] = {
	Title = "Where Thanatos Stood",
	Description = {
		"Where Thanatos Stood. The sky tears open. Stand where Thanatos stood three hundred years ago. The cascade is the seal.",
		"Location: moc_fild22 / Ash Vacuum",
		"Boss: Surt",
		"Hunt: @dm warp moc_fild22 150 150",
		"Main tracker. Morroc breaks, Surt fight. Arc 19.",
		"^3355FFSummary: Where Thanatos Stood.^000000",
	},
}

QuestList[20232] = {
	Title = "Beyond the Veil",
	Description = {
		"Beyond the Veil. The rift held open long enough to walk through. On the other side is a wound that needs a keeper.",
		"Location: Morroc Ruins (moc_ruins)",
		"Mob: Khalitzburg x15 (Lv ~120)",
		"Hunt: @dm warp moc_ruins 150 150",
		"Return: @dm warp moc_fild22 150 150",
		"Hunt leading to Loki reveal and finale.",
		"^3355FFSummary: Beyond the Veil.^000000",
	},
}

QuestList[20233] = {
	Title = "The Choice He Never Had",
	Description = {
		"Everything the campaign asked, every choice tallied, every ally kept and dead failed, comes down to one room and one decision. Thanatos stood here and chose alone, and it destroyed him. The party stand here together, and they choose with sixteen arcs of who-they've-become in their hands. This is the last line of the story.",
		"Location: Morroc Ruins / Ash Vacuum (moc_fild22)",
		"Boss: Surt (after the rift opens)",
		"Hunt: @dm warp moc_fild22 150 150",
		"Return: @dm warp moc_fild22 155 150",
		"^3355FFSummary: The campaign's finale. Six possible endings (Shared Seal, Reforged, Queen's Bargain, Thanatos Road, Refusal, Unbound) based on all prior choices.^000000",
	},
}

QuestList[20234] = {
	Title = "Ragnarok Aftermath Seeds",
	Description = {
		"Ragnarok Aftermath Seeds. XP support. Hooks for what survives the choice.",
		"Location: Post-choice areas",
		"Epilogue XP support and hooks for what survives.",
		"^3355FFSummary: Ragnarok Aftermath Seeds.^000000",
	},
}

-- End of Seal Cascade campaign quest data. 89 entries.
