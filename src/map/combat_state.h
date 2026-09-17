/**
 * Isolated combat-state helpers so map-server code and deterministic tests
 * share the same implementation of mark/query/clear/apply.
 */
#ifndef MAP_COMBAT_STATE_H
#define MAP_COMBAT_STATE_H

#include "common/cbasetypes.h"
#include "common/hercules.h"

struct block_list;
struct map_session_data;

enum recovery_mode {
	RECOVERY_MODE_NONE = 0,
	RECOVERY_MODE_STANDING = 1,
	RECOVERY_MODE_SITTING = 2,
	RECOVERY_MODE_RESPAWN = 3,
};

enum recovery_block {
	RECOVERY_BLOCK_OK = 0,
	RECOVERY_BLOCK_DEAD = 1,
	RECOVERY_BLOCK_STATUS = 2,
	RECOVERY_BLOCK_WEIGHT = 3,
	RECOVERY_BLOCK_COMBAT = 4,
};

void status_mark_combat(struct block_list *bl);
bool status_is_in_combat(struct block_list *bl);
void status_clear_combat_and_sit(struct map_session_data *sd);
void status_apply_combat_from_damage(struct block_list *src, struct block_list *target, int hp);
void status_apply_skill_combat(struct block_list *src, struct block_list *target, bool offensive, bool support);
bool status_apply_sitting_recovery(struct map_session_data *sd, int max_hp, int max_sp, int diff_tick, int *add_hp, int *add_sp);
bool status_apply_respawn_fill(struct map_session_data *sd, int max_hp, int max_sp, int64 now, int diff_tick, int *add_hp, int *add_sp, bool *complete);
void status_recovery_ui_state(struct map_session_data *sd, int block_reason, uint8 *mode, uint8 *block);

enum encumbrance_band {
	ENCUMBRANCE_NORMAL = 0, /* < 70% */
	ENCUMBRANCE_WARN = 1,   /* >= 70% and < 90% */
	ENCUMBRANCE_SOFT = 2,   /* >= 90% and < 100% */
	ENCUMBRANCE_HARD = 3,   /* >= 100% */
};

enum encumbrance_band status_encumbrance_band(const struct map_session_data *sd);
bool status_encumbrance_blocks_at_percent(const struct map_session_data *sd, int64 extra_weight, unsigned int percent);
bool status_encumbrance_blocks_pickup(const struct map_session_data *sd, int64 extra_weight);
bool status_cart_weight_blocks(const struct map_session_data *sd, int64 extra_weight);
bool status_encumbrance_blocks_attack(const struct map_session_data *sd);
bool status_encumbrance_blocks_skill(const struct map_session_data *sd);
bool status_encumbrance_blocks_movement(const struct map_session_data *sd);

#endif /* MAP_COMBAT_STATE_H */
