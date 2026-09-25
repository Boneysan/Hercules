/**
 * Production combat-state transitions.
 *
 * Kept in a dedicated compilation unit so QW-071 can link these functions
 * without the rest of the map-server object graph.
 */
#define HERCULES_CORE

#include "map/combat_state.h"

#include "map/battle.h"
#include "map/map.h"
#include "map/pc.h"
#include "common/timer.h"

void status_mark_combat(struct block_list *bl)
{
	struct map_session_data *sd = BL_CAST(BL_PC, bl);

	if (sd == NULL)
		return;
	sd->last_combat_tick = timer->gettick();
}

bool status_is_in_combat(struct block_list *bl)
{
	struct map_session_data *sd;

	if (bl == NULL)
		return false;
	sd = BL_CAST(BL_PC, bl);
	if (sd == NULL)
		return false;
	if (sd->last_combat_tick == 0)
		return false;
	if (DIFF_TICK(timer->gettick(), sd->last_combat_tick) >= battle_config.campaign_combat_timeout_ms) {
		sd->last_combat_tick = 0;
		return false;
	}
	return true;
}

void status_clear_combat_and_sit(struct map_session_data *sd)
{
	if (sd == NULL)
		return;
	sd->last_combat_tick = 0;
	sd->sit_regen_tick = 0;
}

void status_apply_combat_from_damage(struct block_list *src, struct block_list *target, int hp)
{
	if (hp <= 0)
		return;
	if (target != NULL) {
		struct map_session_data *target_sd = BL_CAST(BL_PC, target);

		if (target_sd != NULL)
			target_sd->respawn_fill_until = 0;
		status_mark_combat(target);
	}
	if (src != NULL)
		status_mark_combat(src);
}

void status_apply_skill_combat(struct block_list *src, struct block_list *target, bool offensive, bool support)
{
	if (src == NULL)
		return;
	if (offensive) {
		status_mark_combat(src);
		return;
	}
	if (support && target != NULL && status_is_in_combat(target))
		status_mark_combat(src);
}

bool status_apply_sitting_recovery(struct map_session_data *sd, int max_hp, int max_sp, int diff_tick, int *add_hp, int *add_sp)
{
	if (add_hp != NULL)
		*add_hp = 0;
	if (add_sp != NULL)
		*add_sp = 0;
	if (sd == NULL)
		return false;

	sd->sit_regen_tick += diff_tick;
	if (sd->sit_regen_tick < battle_config.campaign_sit_recovery_interval_ms)
		return false;

	sd->sit_regen_tick -= battle_config.campaign_sit_recovery_interval_ms;
	if (add_hp != NULL)
		*add_hp = max_hp * battle_config.campaign_sit_recovery_percent / 100;
	if (add_sp != NULL)
		*add_sp = max_sp * battle_config.campaign_sit_recovery_percent / 100;
	return true;
}

bool status_apply_respawn_fill(struct map_session_data *sd, int max_hp, int max_sp, int64 now, int diff_tick, int *add_hp, int *add_sp, bool *complete)
{
	if (add_hp != NULL)
		*add_hp = 0;
	if (add_sp != NULL)
		*add_sp = 0;
	if (complete != NULL)
		*complete = false;
	if (sd == NULL || sd->respawn_fill_until == 0)
		return false;

	if (now >= sd->respawn_fill_until) {
		if (add_hp != NULL)
			*add_hp = max_hp;
		if (add_sp != NULL)
			*add_sp = max_sp;
		if (complete != NULL)
			*complete = true;
		sd->respawn_fill_until = 0;
		return true;
	}

	if (add_hp != NULL) {
		*add_hp = (int)((int64)max_hp * (100 - battle_config.campaign_respawn_percent) * diff_tick
			/ (100 * (int64)battle_config.campaign_respawn_fill_ms));
		if (*add_hp < 1)
			*add_hp = 1;
	}
	if (add_sp != NULL) {
		*add_sp = (int)((int64)max_sp * (100 - battle_config.campaign_respawn_percent) * diff_tick
			/ (100 * (int64)battle_config.campaign_respawn_fill_ms));
		if (*add_sp < 1)
			*add_sp = 1;
	}
	return true;
}

void status_recovery_ui_state(struct map_session_data *sd, int block_reason, uint8 *mode, uint8 *block)
{
	if (mode == NULL || block == NULL)
		return;
	*mode = RECOVERY_MODE_NONE;
	*block = (uint8)block_reason;
	if (sd == NULL)
		return;
	if (block_reason != RECOVERY_BLOCK_OK) {
		if (*block > RECOVERY_BLOCK_WEIGHT)
			*block = RECOVERY_BLOCK_STATUS;
		return;
	}
	if (sd->respawn_fill_until != 0) {
		*mode = RECOVERY_MODE_RESPAWN;
		return;
	}
	if (sd->state.dead_sit == 2 || sd->vd.dead_sit == 2) {
		*mode = RECOVERY_MODE_SITTING;
		return;
	}
	*mode = RECOVERY_MODE_STANDING;
	if (status_is_in_combat(&sd->bl))
		*block = RECOVERY_BLOCK_COMBAT;
}

enum encumbrance_band status_encumbrance_band(const struct map_session_data *sd)
{
	unsigned int weight;
	unsigned int max_weight;

	if (sd == NULL || sd->max_weight == 0)
		return ENCUMBRANCE_NORMAL;
	weight = sd->weight;
	max_weight = sd->max_weight;
	if (weight >= max_weight)
		return ENCUMBRANCE_HARD;
	if (weight * 10 >= max_weight * 9)
		return ENCUMBRANCE_SOFT;
	if (weight * 10 >= max_weight * 7)
		return ENCUMBRANCE_WARN;
	return ENCUMBRANCE_NORMAL;
}

bool status_encumbrance_blocks_at_percent(const struct map_session_data *sd, int64 extra_weight, unsigned int percent)
{
	if (sd == NULL)
		return true;
	if (extra_weight < 0)
		extra_weight = 0;
	if (percent > 100)
		percent = 100;
	/* Calculate capacity wide, then compare by subtraction so malformed/very
	 * large stacks cannot wrap an additive weight check. */
	uint64 capacity = ((uint64)(sd->max_weight > 0 ? sd->max_weight : 0) * percent) / 100;
	uint64 current = sd->weight > 0 ? (uint64)sd->weight : 0;
	uint64 extra = (uint64)extra_weight;
	return current > capacity || extra > capacity - current;
}

bool status_encumbrance_blocks_pickup(const struct map_session_data *sd, int64 extra_weight)
{
	return status_encumbrance_blocks_at_percent(sd, extra_weight, 100);
}

bool status_cart_weight_blocks(const struct map_session_data *sd, int64 extra_weight)
{
	if (sd == NULL)
		return true;
	if (extra_weight < 0)
		extra_weight = 0;
	return sd->cart_weight > sd->cart_weight_max || (uint64)extra_weight > sd->cart_weight_max - sd->cart_weight;
}

bool status_encumbrance_blocks_attack(const struct map_session_data *sd)
{
	(void)sd;
	return false;
}

bool status_encumbrance_blocks_skill(const struct map_session_data *sd)
{
	(void)sd;
	return false;
}

bool status_encumbrance_blocks_movement(const struct map_session_data *sd)
{
	(void)sd;
	return false;
}
