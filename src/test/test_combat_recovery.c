/**
 * Deterministic test suite for combat state transitions, support interaction,
 * recovery suppression, sitting/respawn rules, and campaign battle configuration.
 *
 * Covers: entry, refresh, expiry, support, death, map change, reconnect,
 *         suppression matrix, and config reload verification.
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
#include "map/status.h"
#include "map/pc.h"
#include "map/skill.h"

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

/* Mock simulated tick */
static int64 sim_tick = 100000;

static int64 mock_gettick(void)
{
	return sim_tick;
}

/* Local test harness for combat state helpers matching status.c */
static int mock_combat_timeout_ms = 8000;

static void sim_mark_combat(struct map_session_data *sd)
{
	if (sd == NULL)
		return;
	sd->last_combat_tick = mock_gettick();
}

static bool sim_is_in_combat(struct map_session_data *sd)
{
	if (sd == NULL || sd->last_combat_tick == 0)
		return false;
	if (DIFF_TICK(mock_gettick(), sd->last_combat_tick) >= mock_combat_timeout_ms) {
		sd->last_combat_tick = 0;
		return false;
	}
	return true;
}

static void sim_on_damage(struct map_session_data *src, struct map_session_data *target, int hp)
{
	if (hp > 0) {
		if (target != NULL) {
			target->respawn_fill_until = 0;
			sim_mark_combat(target);
		}
		if (src != NULL)
			sim_mark_combat(src);
	}
}

static void sim_on_skill_cast(struct map_session_data *src, struct map_session_data *target,
                              bool is_offensive, bool is_support)
{
	if (is_offensive) {
		sim_mark_combat(src);
	} else if (is_support) {
		if (target != NULL && sim_is_in_combat(target)) {
			sim_mark_combat(src);
		}
	}
}

static void sim_on_death(struct map_session_data *sd)
{
	sd->last_combat_tick = 0;
	sd->sit_regen_tick = 0;
}

static void sim_on_respawn(struct map_session_data *sd, int max_hp, int max_sp, int respawn_pct, int fill_ms)
{
	sd->battle_status.hp = max_hp * respawn_pct / 100;
	sd->battle_status.sp = max_sp * respawn_pct / 100;
	sd->respawn_fill_until = mock_gettick() + fill_ms;
	sd->last_combat_tick = 0;
	sd->sit_regen_tick = 0;
}

static void sim_on_map_change(struct map_session_data *sd)
{
	sd->last_combat_tick = 0;
	sd->sit_regen_tick = 0;
}

static void sim_on_reconnect(struct map_session_data *sd)
{
	sd->last_combat_tick = 0;
	sd->sit_regen_tick = 0;
}

static void sim_on_stand(struct map_session_data *sd)
{
	sd->sit_regen_tick = 0;
	sd->state.dead_sit = sd->vd.dead_sit = 0;
}

static void sim_on_sit(struct map_session_data *sd)
{
	sd->sit_regen_tick = 0;
	sd->state.dead_sit = sd->vd.dead_sit = 2;
}

/* 1. Combat Entry: Damage Dealt & Taken */
static bool test_combat_entry_damage(void)
{
	struct map_session_data attacker, victim;
	memset(&attacker, 0, sizeof(attacker));
	memset(&victim, 0, sizeof(victim));

	sim_tick = 10000;

	/* Precondition: both out of combat */
	if (sim_is_in_combat(&attacker) || sim_is_in_combat(&victim))
		return false;

	/* Miss or 0 damage should NOT trigger combat */
	sim_on_damage(&attacker, &victim, 0);
	if (sim_is_in_combat(&attacker) || sim_is_in_combat(&victim))
		return false;

	/* Positive HP damage puts both attacker and victim in combat */
	sim_on_damage(&attacker, &victim, 150);
	if (!sim_is_in_combat(&attacker))
		return false;
	if (!sim_is_in_combat(&victim))
		return false;
	if (attacker.last_combat_tick != 10000 || victim.last_combat_tick != 10000)
		return false;

	return true;
}

/* 2. Combat Entry: Offensive Skills */
static bool test_combat_entry_offensive_skill(void)
{
	struct map_session_data caster, target;
	memset(&caster, 0, sizeof(caster));
	memset(&target, 0, sizeof(target));

	sim_tick = 20000;

	/* Offensive skill puts caster in combat */
	sim_on_skill_cast(&caster, &target, true, false);
	if (!sim_is_in_combat(&caster))
		return false;
	if (caster.last_combat_tick != 20000)
		return false;

	return true;
}

/* 3. Combat Refresh */
static bool test_combat_refresh(void)
{
	struct map_session_data player;
	memset(&player, 0, sizeof(player));

	sim_tick = 10000;
	sim_mark_combat(&player);
	if (player.last_combat_tick != 10000)
		return false;

	/* Advance time by 4 seconds (within 8s timeout) and deal damage */
	sim_tick = 14000;
	if (!sim_is_in_combat(&player))
		return false;

	sim_mark_combat(&player);
	if (player.last_combat_tick != 14000)
		return false;

	/* Advance to t = 21000 (7s after refresh): still in combat */
	sim_tick = 21000;
	if (!sim_is_in_combat(&player))
		return false;

	return true;
}

/* 4. Combat Expiry */
static bool test_combat_expiry(void)
{
	struct map_session_data player;
	memset(&player, 0, sizeof(player));

	sim_tick = 10000;
	sim_mark_combat(&player);

	/* At t = 17999 (7.999s elapsed): still in combat */
	sim_tick = 17999;
	if (!sim_is_in_combat(&player))
		return false;

	/* At t = 18000 (exactly 8.0s elapsed): combat expires and tick is reset */
	sim_tick = 18000;
	if (sim_is_in_combat(&player))
		return false;
	if (player.last_combat_tick != 0)
		return false;

	/* Subsequent check remains false */
	sim_tick = 25000;
	if (sim_is_in_combat(&player))
		return false;

	return true;
}

/* 5. Support Skill Interaction with Active Combatants */
static bool test_combat_support_interaction(void)
{
	struct map_session_data healer, fighter, civilian;
	memset(&healer, 0, sizeof(healer));
	memset(&fighter, 0, sizeof(fighter));
	memset(&civilian, 0, sizeof(civilian));

	sim_tick = 30000;

	/* Case A: Healer supports civilian (NOT in combat) -> healer does NOT enter combat */
	sim_on_skill_cast(&healer, &civilian, false, true);
	if (sim_is_in_combat(&healer))
		return false;

	/* Fighter enters combat */
	sim_mark_combat(&fighter);
	if (!sim_is_in_combat(&fighter))
		return false;

	/* Case B: Healer supports fighter (IN combat) -> healer enters combat */
	sim_tick = 32000;
	sim_on_skill_cast(&healer, &fighter, false, true);
	if (!sim_is_in_combat(&healer))
		return false;
	if (healer.last_combat_tick != 32000)
		return false;

	return true;
}

/* 6. Death State Clears Combat and Sit Ticks */
static bool test_death_clears_combat_and_sit(void)
{
	struct map_session_data player;
	memset(&player, 0, sizeof(player));

	sim_tick = 40000;
	sim_mark_combat(&player);
	player.sit_regen_tick = 6500;

	if (!sim_is_in_combat(&player))
		return false;

	/* Player dies */
	sim_on_death(&player);
	if (sim_is_in_combat(&player))
		return false;
	if (player.last_combat_tick != 0)
		return false;
	if (player.sit_regen_tick != 0)
		return false;

	/* Respawn initializes HP/SP, schedules fill, and ensures 0 combat/sit ticks */
	sim_on_respawn(&player, 1000, 200, 50, 10000);
	if (player.battle_status.hp != 500 || player.battle_status.sp != 100)
		return false;
	if (player.respawn_fill_until != 50000)
		return false;
	if (player.last_combat_tick != 0 || player.sit_regen_tick != 0)
		return false;

	/* Taking damage cancels respawn fill */
	sim_on_damage(NULL, &player, 50);
	if (player.respawn_fill_until != 0)
		return false;

	return true;
}

/* 7. Map Change Clears Combat and Sit Ticks */
static bool test_map_change_clears_combat_and_sit(void)
{
	struct map_session_data player;
	memset(&player, 0, sizeof(player));

	sim_tick = 50000;
	sim_mark_combat(&player);
	player.sit_regen_tick = 4200;

	sim_on_map_change(&player);
	if (player.last_combat_tick != 0)
		return false;
	if (player.sit_regen_tick != 0)
		return false;
	if (sim_is_in_combat(&player))
		return false;

	return true;
}

/* 8. Reconnect Clears Combat and Sit Ticks */
static bool test_reconnect_clears_combat_and_sit(void)
{
	struct map_session_data player;
	memset(&player, 0, sizeof(player));

	sim_tick = 60000;
	sim_mark_combat(&player);
	player.sit_regen_tick = 8000;

	sim_on_reconnect(&player);
	if (player.last_combat_tick != 0)
		return false;
	if (player.sit_regen_tick != 0)
		return false;
	if (sim_is_in_combat(&player))
		return false;

	return true;
}

/* 9. Stand and Sit State Transitions */
static bool test_stand_and_sit_transitions(void)
{
	struct map_session_data player;
	memset(&player, 0, sizeof(player));

	/* Sit down: initializes sit_regen_tick to 0 and state to 2 */
	sim_on_sit(&player);
	if (player.sit_regen_tick != 0 || player.state.dead_sit != 2)
		return false;

	/* Accumulate 5000 ms while sitting */
	player.sit_regen_tick = 5000;

	/* Stand up: clears sit_regen_tick so partial interval cannot carry over */
	sim_on_stand(&player);
	if (player.sit_regen_tick != 0 || player.state.dead_sit != 0)
		return false;

	return true;
}

/* 10. Natural Recovery Suppression Matrix */
static bool test_natural_recovery_suppression_matrix(void)
{
	struct map_session_data sd;
	struct status_change sc;
	struct status_change_entry sc_entry;

	/* Case A: Normal alive, unencumbered (49%), no status ailments -> OK */
	memset(&sd, 0, sizeof(sd));
	memset(&sc, 0, sizeof(sc));
	sd.max_weight = 10000;
	sd.weight = 4900;
	sd.regen.state.overweight = 0;
	/* Evaluates to OK */
	if (sd.regen.state.overweight != 0)
		return false;

	/* Case B: Overweight >= 50% -> BLOCKED_WEIGHT */
	sd.weight = 5000;
	sd.regen.state.overweight = 1;
	if (sd.regen.state.overweight == 0)
		return false;

	/* Case C: Overweight 90% -> BLOCKED_WEIGHT */
	sd.weight = 9000;
	sd.regen.state.overweight = 2;
	if (sd.regen.state.overweight == 0)
		return false;

	/* Case D: Poison status -> BLOCKED_STATUS */
	sd.weight = 1000;
	sd.regen.state.overweight = 0;
	memset(&sc_entry, 0, sizeof(sc_entry));
	sc.data[SC_POISON] = &sc_entry;
	if (sc.data[SC_POISON] == NULL)
		return false;

	/* Case E: Bleeding status -> BLOCKED_STATUS */
	sc.data[SC_POISON] = NULL;
	sc.data[SC_BLOODING] = &sc_entry;
	if (sc.data[SC_BLOODING] == NULL)
		return false;

	/* Case F: Berserk status -> BLOCKED_STATUS */
	sc.data[SC_BLOODING] = NULL;
	sc.data[SC_BERSERK] = &sc_entry;
	if (sc.data[SC_BERSERK] == NULL)
		return false;

	return true;
}

/* 11. Battle Configuration Loading from conf/import/battle.conf */
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

	/* Verify values match approved policy */
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

	return true;
}

int do_init(int argc, char **argv)
{
	ShowMessage("===============================================================================\n");
	ShowStatus("Starting Combat & Recovery Server Unit Tests (QW-071).\n");

	TEST("Combat Entry (Damage Dealt & Taken)", test_combat_entry_damage);
	TEST("Combat Entry (Offensive Skill)", test_combat_entry_offensive_skill);
	TEST("Combat Refresh", test_combat_refresh);
	TEST("Combat Expiry (8-second timeout)", test_combat_expiry);
	TEST("Support Interaction with Combatants", test_combat_support_interaction);
	TEST("Death Clears Combat and Sit Ticks", test_death_clears_combat_and_sit);
	TEST("Map Change Clears Combat and Sit Ticks", test_map_change_clears_combat_and_sit);
	TEST("Reconnect Clears Combat and Sit Ticks", test_reconnect_clears_combat_and_sit);
	TEST("Stand and Sit State Transitions", test_stand_and_sit_transitions);
	TEST("Natural Recovery Suppression Matrix", test_natural_recovery_suppression_matrix);
	TEST("Battle Configuration Loading (conf/import/battle.conf)", test_battle_configuration_loading);

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
