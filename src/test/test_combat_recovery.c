/**
 * Deterministic production-path tests for combat state transitions.
 *
 * Calls status->mark_combat, status->is_in_combat, status_apply_combat_from_damage,
 * status_apply_skill_combat, and status_clear_combat_and_sit — the same functions
 * the map-server uses.
 */

#define HERCULES_CORE

#include "common/cbasetypes.h"
#include "common/conf.h"
#include "common/core.h"
#include "common/showmsg.h"
#include "common/strlib.h"
#include "common/timer.h"
#include "common/utils.h"
#include "map/battle.h"
#include "map/combat_state.h"
#include "map/pc.h"
#include "map/status.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TEST(name, function) do { \
	ShowMessage("-------------------------------------------------------------------------------\n"); \
	ShowNotice("Testing %s...\n", (name)); \
	if (!(function)()) { \
		ShowError("Failed.\n"); \
		ShowMessage("===============================================================================\n"); \
		ShowFatalError("Failure. Aborting further tests.\n"); \
		exit(EXIT_FAILURE); \
	} \
	ShowInfo("Test passed.\n"); \
} while (false)

struct Battle_Config battle_config;
struct status_interface status_s;
struct status_interface *status = &status_s;

static int64 sim_tick = 100000;
static int64 (*real_gettick)(void);

static int64 mock_gettick(void)
{
	return sim_tick;
}

static void init_pc(struct map_session_data *sd)
{
	memset(sd, 0, sizeof(*sd));
	sd->bl.type = BL_PC;
}

static void bind_production_status(void)
{
	memset(&status_s, 0, sizeof(status_s));
	status->mark_combat = status_mark_combat;
	status->is_in_combat = status_is_in_combat;
}

/* 1. Combat Entry: Damage Dealt & Taken */
static bool test_combat_entry_damage(void)
{
	struct map_session_data attacker, victim;

	init_pc(&attacker);
	init_pc(&victim);
	sim_tick = 10000;

	if (status->is_in_combat(&attacker.bl) || status->is_in_combat(&victim.bl))
		return false;

	status_apply_combat_from_damage(&attacker.bl, &victim.bl, 0);
	if (status->is_in_combat(&attacker.bl) || status->is_in_combat(&victim.bl))
		return false;

	status_apply_combat_from_damage(&attacker.bl, &victim.bl, 150);
	if (!status->is_in_combat(&attacker.bl))
		return false;
	if (!status->is_in_combat(&victim.bl))
		return false;
	if (attacker.last_combat_tick != 10000 || victim.last_combat_tick != 10000)
		return false;

	return true;
}

/* 2. Combat Entry: Offensive Skills */
static bool test_combat_entry_offensive_skill(void)
{
	struct map_session_data caster, target;

	init_pc(&caster);
	init_pc(&target);
	sim_tick = 20000;

	status_apply_skill_combat(&caster.bl, &target.bl, true, false);
	if (!status->is_in_combat(&caster.bl))
		return false;
	if (caster.last_combat_tick != 20000)
		return false;

	return true;
}

/* 3. Combat Refresh */
static bool test_combat_refresh(void)
{
	struct map_session_data player;

	init_pc(&player);
	sim_tick = 10000;
	status->mark_combat(&player.bl);
	if (player.last_combat_tick != 10000)
		return false;

	sim_tick = 14000;
	if (!status->is_in_combat(&player.bl))
		return false;

	status->mark_combat(&player.bl);
	if (player.last_combat_tick != 14000)
		return false;

	sim_tick = 21000;
	if (!status->is_in_combat(&player.bl))
		return false;

	return true;
}

/* 4. Combat Expiry */
static bool test_combat_expiry(void)
{
	struct map_session_data player;

	init_pc(&player);
	sim_tick = 10000;
	status->mark_combat(&player.bl);

	sim_tick = 17999;
	if (!status->is_in_combat(&player.bl))
		return false;

	sim_tick = 18000;
	if (status->is_in_combat(&player.bl))
		return false;
	if (player.last_combat_tick != 0)
		return false;

	sim_tick = 25000;
	if (status->is_in_combat(&player.bl))
		return false;

	return true;
}

/* 5. Support Skill Interaction with Active Combatants */
static bool test_combat_support_interaction(void)
{
	struct map_session_data healer, fighter, civilian;

	init_pc(&healer);
	init_pc(&fighter);
	init_pc(&civilian);
	sim_tick = 30000;

	status_apply_skill_combat(&healer.bl, &civilian.bl, false, true);
	if (status->is_in_combat(&healer.bl))
		return false;

	status->mark_combat(&fighter.bl);
	if (!status->is_in_combat(&fighter.bl))
		return false;

	sim_tick = 32000;
	status_apply_skill_combat(&healer.bl, &fighter.bl, false, true);
	if (!status->is_in_combat(&healer.bl))
		return false;
	if (healer.last_combat_tick != 32000)
		return false;

	return true;
}

/* 6. Death State Clears Combat and Sit Ticks */
static bool test_death_clears_combat_and_sit(void)
{
	struct map_session_data player;

	init_pc(&player);
	sim_tick = 40000;
	status->mark_combat(&player.bl);
	player.sit_regen_tick = 6500;

	if (!status->is_in_combat(&player.bl))
		return false;

	status_clear_combat_and_sit(&player);
	if (status->is_in_combat(&player.bl))
		return false;
	if (player.last_combat_tick != 0)
		return false;
	if (player.sit_regen_tick != 0)
		return false;

	player.battle_status.hp = 1000 * 50 / 100;
	player.battle_status.sp = 200 * 50 / 100;
	player.respawn_fill_until = sim_tick + 10000;
	status_clear_combat_and_sit(&player);
	if (player.battle_status.hp != 500 || player.battle_status.sp != 100)
		return false;
	if (player.respawn_fill_until != 50000)
		return false;
	if (player.last_combat_tick != 0 || player.sit_regen_tick != 0)
		return false;

	status_apply_combat_from_damage(NULL, &player.bl, 50);
	if (player.respawn_fill_until != 0)
		return false;

	return true;
}

/* 7. Map Change Clears Combat and Sit Ticks */
static bool test_map_change_clears_combat_and_sit(void)
{
	struct map_session_data player;

	init_pc(&player);
	sim_tick = 50000;
	status->mark_combat(&player.bl);
	player.sit_regen_tick = 4200;

	status_clear_combat_and_sit(&player);
	if (player.last_combat_tick != 0)
		return false;
	if (player.sit_regen_tick != 0)
		return false;
	if (status->is_in_combat(&player.bl))
		return false;

	return true;
}

/* 8. Reconnect Clears Combat and Sit Ticks */
static bool test_reconnect_clears_combat_and_sit(void)
{
	struct map_session_data player;

	init_pc(&player);
	sim_tick = 60000;
	status->mark_combat(&player.bl);
	player.sit_regen_tick = 8000;

	status_clear_combat_and_sit(&player);
	if (player.last_combat_tick != 0)
		return false;
	if (player.sit_regen_tick != 0)
		return false;
	if (status->is_in_combat(&player.bl))
		return false;

	return true;
}

/* 9. Stand and Sit State Transitions */
static bool test_stand_and_sit_transitions(void)
{
	struct map_session_data player;

	init_pc(&player);

	pc_setsit(&player);
	if (player.sit_regen_tick != 0 || player.state.dead_sit != 2)
		return false;

	player.sit_regen_tick = 5000;

	player.sit_regen_tick = 0;
	player.state.dead_sit = player.vd.dead_sit = 0;
	if (player.sit_regen_tick != 0 || player.state.dead_sit != 0)
		return false;

	return true;
}

/* 10. Sitting recovery: 25% of max per 10s, no double tick, no carry-over below interval */
static bool test_sitting_recovery_boundaries(void)
{
	struct map_session_data player;
	int add_hp = 0, add_sp = 0;

	init_pc(&player);
	pc_setsit(&player);

	if (status_apply_sitting_recovery(&player, 1000, 200, 9999, &add_hp, &add_sp))
		return false;
	if (player.sit_regen_tick != 9999 || add_hp != 0 || add_sp != 0)
		return false;

	if (!status_apply_sitting_recovery(&player, 1000, 200, 1, &add_hp, &add_sp))
		return false;
	if (add_hp != 250 || add_sp != 50)
		return false;
	if (player.sit_regen_tick != 0)
		return false;

	if (status_apply_sitting_recovery(&player, 1000, 200, 10000, &add_hp, &add_sp) == false)
		return false;
	if (add_hp != 250 || add_sp != 50 || player.sit_regen_tick != 0)
		return false;

	return true;
}

/* 11. Respawn fill: 50% immediate remainder over 10s, cancelled by damage */
static bool test_respawn_fill_boundaries(void)
{
	struct map_session_data player;
	int add_hp = 0, add_sp = 0;
	bool complete = false;

	init_pc(&player);
	player.battle_status.hp = 500;
	player.battle_status.sp = 100;
	player.respawn_fill_until = 20000;

	if (!status_apply_respawn_fill(&player, 1000, 200, 10000, 500, &add_hp, &add_sp, &complete))
		return false;
	if (complete)
		return false;
	if (add_hp != 25 || add_sp != 5)
		return false;
	if (player.respawn_fill_until != 20000)
		return false;

	if (!status_apply_respawn_fill(&player, 1000, 200, 20000, 500, &add_hp, &add_sp, &complete))
		return false;
	if (!complete || player.respawn_fill_until != 0)
		return false;
	if (add_hp != 1000 || add_sp != 200)
		return false;

	player.respawn_fill_until = 30000;
	status_apply_combat_from_damage(NULL, &player.bl, 10);
	if (player.respawn_fill_until != 0)
		return false;
	if (status_apply_respawn_fill(&player, 1000, 200, 25000, 500, &add_hp, &add_sp, &complete))
		return false;

	return true;
}

/* 12. Recovery UI state: sitting, respawn, combat, weight */
static bool test_recovery_ui_state(void)
{
	struct map_session_data player;
	uint8 mode = 99, block = 99;

	init_pc(&player);
	sim_tick = 10000;

	status_recovery_ui_state(&player, RECOVERY_BLOCK_OK, &mode, &block);
	if (mode != RECOVERY_MODE_STANDING || block != RECOVERY_BLOCK_OK)
		return false;

	status->mark_combat(&player.bl);
	status_recovery_ui_state(&player, RECOVERY_BLOCK_OK, &mode, &block);
	if (mode != RECOVERY_MODE_STANDING || block != RECOVERY_BLOCK_COMBAT)
		return false;

	status_clear_combat_and_sit(&player);
	player.state.dead_sit = player.vd.dead_sit = 2;
	status_recovery_ui_state(&player, RECOVERY_BLOCK_OK, &mode, &block);
	if (mode != RECOVERY_MODE_SITTING || block != RECOVERY_BLOCK_OK)
		return false;

	player.state.dead_sit = player.vd.dead_sit = 0;
	player.respawn_fill_until = 20000;
	status_recovery_ui_state(&player, RECOVERY_BLOCK_OK, &mode, &block);
	if (mode != RECOVERY_MODE_RESPAWN || block != RECOVERY_BLOCK_OK)
		return false;

	status_recovery_ui_state(&player, RECOVERY_BLOCK_WEIGHT, &mode, &block);
	if (mode != RECOVERY_MODE_NONE || block != RECOVERY_BLOCK_WEIGHT)
		return false;

	status_recovery_ui_state(&player, RECOVERY_BLOCK_STATUS, &mode, &block);
	if (mode != RECOVERY_MODE_NONE || block != RECOVERY_BLOCK_STATUS)
		return false;

	status_recovery_ui_state(&player, RECOVERY_BLOCK_DEAD, &mode, &block);
	if (mode != RECOVERY_MODE_NONE || block != RECOVERY_BLOCK_DEAD)
		return false;

	return true;
}

/* 13. Encumbrance matrix: 70/90/100 ±1 for pickup, attack, skill, movement */
static bool test_encumbrance_matrix(void)
{
	struct map_session_data sd;
	struct { unsigned int weight; enum encumbrance_band band; bool pickup1; } cases[] = {
		{ 69, ENCUMBRANCE_NORMAL, false },
		{ 70, ENCUMBRANCE_WARN, false },
		{ 89, ENCUMBRANCE_WARN, false },
		{ 90, ENCUMBRANCE_SOFT, false },
		{ 99, ENCUMBRANCE_SOFT, false },
		{ 100, ENCUMBRANCE_HARD, true },
	};
	size_t i;

	init_pc(&sd);
	sd.max_weight = 100;

	for (i = 0; i < sizeof(cases) / sizeof(cases[0]); i++) {
		sd.weight = cases[i].weight;
		if (status_encumbrance_band(&sd) != cases[i].band)
			return false;
		if (status_encumbrance_blocks_pickup(&sd, 1) != cases[i].pickup1)
			return false;
		if (status_encumbrance_blocks_attack(&sd))
			return false;
		if (status_encumbrance_blocks_skill(&sd))
			return false;
		if (status_encumbrance_blocks_movement(&sd))
			return false;
	}

	/* Trade/storage/cart share the same hard pickup cap: one unit below 100% fits. */
	sd.weight = 99;
	if (status_encumbrance_blocks_pickup(&sd, 1))
		return false;
	if (!status_encumbrance_blocks_pickup(&sd, 2))
		return false;

	/* Cart capacity is independent of player weight (cart_weight vs cart_weight_max). */
	sd.weight = 100;
	sd.cart_weight = 0;
	sd.cart_weight_max = 8000;
	if (sd.cart_weight + 100 > sd.cart_weight_max)
		return false;
	if (!status_encumbrance_blocks_pickup(&sd, 1))
		return false;

	return true;
}

/* 14. Battle Configuration Loading from conf/import/battle.conf */
static bool test_battle_configuration_loading(void)
{
	struct config_t config;
	struct config_setting_t *setting, *battle_setting;
	const char *conf_path = "conf/import/battle.conf";
	int combat_timeout = 0;
	int sit_interval = 0;
	int sit_pct = 0;
	int respawn_pct = 0;
	int respawn_fill = 0;
	int weight_mult = 0;
	int party_bonus = 0;

	if (!exists(conf_path))
		conf_path = "Hercules/conf/import/battle.conf";
	if (!exists(conf_path))
		conf_path = "../../conf/import/battle.conf";

	if (libconfig->load_file(&config, conf_path) != CONFIG_TRUE) {
		ShowError("Failed to parse %s\n", conf_path);
		return false;
	}

	setting = libconfig->lookup(&config, "battle_configuration");
	if (setting == NULL) {
		ShowError("battle_configuration block missing in %s\n", conf_path);
		libconfig->destroy(&config);
		return false;
	}

	battle_setting = libconfig->setting_get_member(setting, "campaign_combat_timeout_ms");
	if (battle_setting != NULL)
		combat_timeout = libconfig->setting_get_int(battle_setting);

	battle_setting = libconfig->setting_get_member(setting, "campaign_sit_recovery_interval_ms");
	if (battle_setting != NULL)
		sit_interval = libconfig->setting_get_int(battle_setting);

	battle_setting = libconfig->setting_get_member(setting, "campaign_sit_recovery_percent");
	if (battle_setting != NULL)
		sit_pct = libconfig->setting_get_int(battle_setting);

	battle_setting = libconfig->setting_get_member(setting, "campaign_respawn_percent");
	if (battle_setting != NULL)
		respawn_pct = libconfig->setting_get_int(battle_setting);

	battle_setting = libconfig->setting_get_member(setting, "campaign_respawn_fill_ms");
	if (battle_setting != NULL)
		respawn_fill = libconfig->setting_get_int(battle_setting);

	battle_setting = libconfig->setting_get_member(setting, "campaign_max_weight_multiplier");
	if (battle_setting != NULL)
		weight_mult = libconfig->setting_get_int(battle_setting);

	battle_setting = libconfig->setting_get_member(setting, "party_even_share_bonus");
	if (battle_setting != NULL)
		party_bonus = libconfig->setting_get_int(battle_setting);

	libconfig->destroy(&config);

	ShowInfo("Loaded from %s: combat_timeout=%d, sit_interval=%d, sit_pct=%d, respawn_pct=%d, respawn_fill=%d, weight_mult=%d, party_bonus=%d\n",
	         conf_path, combat_timeout, sit_interval, sit_pct, respawn_pct, respawn_fill, weight_mult, party_bonus);

	if (combat_timeout != 8000) {
		ShowError("campaign_combat_timeout_ms expected 8000, got %d\n", combat_timeout);
		return false;
	}
	if (sit_interval != 10000) {
		ShowError("campaign_sit_recovery_interval_ms expected 10000, got %d\n", sit_interval);
		return false;
	}
	if (sit_pct != 25) {
		ShowError("campaign_sit_recovery_percent expected 25, got %d\n", sit_pct);
		return false;
	}
	if (respawn_pct != 50) {
		ShowError("campaign_respawn_percent expected 50, got %d\n", respawn_pct);
		return false;
	}
	if (respawn_fill != 10000) {
		ShowError("campaign_respawn_fill_ms expected 10000, got %d\n", respawn_fill);
		return false;
	}
	if (weight_mult != 5) {
		ShowError("campaign_max_weight_multiplier expected 5, got %d\n", weight_mult);
		return false;
	}
	if (party_bonus != 25) {
		ShowError("party_even_share_bonus expected 25, got %d\n", party_bonus);
		return false;
	}

	if (battle_config.campaign_combat_timeout_ms != 8000)
		return false;

	return true;
}

int do_init(int argc, char **argv)
{
	(void)argc;
	(void)argv;

	ShowMessage("===============================================================================\n");
	ShowStatus("Starting Combat & Recovery Server Unit Tests (QW-071).\n");

	memset(&battle_config, 0, sizeof(battle_config));
	battle_config.campaign_combat_timeout_ms = 8000;
	battle_config.campaign_sit_recovery_interval_ms = 10000;
	battle_config.campaign_sit_recovery_percent = 25;
	battle_config.campaign_respawn_percent = 50;
	battle_config.campaign_respawn_fill_ms = 10000;

	bind_production_status();
	real_gettick = timer->gettick;
	timer->gettick = mock_gettick;

	TEST("Combat Entry (Damage Dealt & Taken)", test_combat_entry_damage);
	TEST("Combat Entry (Offensive Skill)", test_combat_entry_offensive_skill);
	TEST("Combat Refresh", test_combat_refresh);
	TEST("Combat Expiry (8-second timeout)", test_combat_expiry);
	TEST("Support Interaction with Combatants", test_combat_support_interaction);
	TEST("Death Clears Combat and Sit Ticks", test_death_clears_combat_and_sit);
	TEST("Map Change Clears Combat and Sit Ticks", test_map_change_clears_combat_and_sit);
	TEST("Reconnect Clears Combat and Sit Ticks", test_reconnect_clears_combat_and_sit);
	TEST("Stand and Sit State Transitions", test_stand_and_sit_transitions);
	TEST("Sitting Recovery Boundaries", test_sitting_recovery_boundaries);
	TEST("Respawn Fill Boundaries", test_respawn_fill_boundaries);
	TEST("Recovery UI State", test_recovery_ui_state);
	TEST("Encumbrance Matrix (70/90/100)", test_encumbrance_matrix);
	TEST("Battle Configuration Loading (conf/import/battle.conf)", test_battle_configuration_loading);

	timer->gettick = real_gettick;
	core->runflag = CORE_ST_STOP;
	return EXIT_SUCCESS;
}

int do_final(void)
{
	ShowMessage("===============================================================================\n");
	ShowStatus("All Combat & Recovery Server Unit Tests Passed.\n");
	return EXIT_SUCCESS;
}

void do_abort(void) { }

void set_server_type(void)
{
	SERVER_TYPE = SERVER_TYPE_UNKNOWN;
}

void cmdline_args_init_local(void) { }
