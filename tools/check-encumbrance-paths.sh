#!/bin/sh
# Verify that the audited production item-delivery paths stay on the shared
# overflow-safe encumbrance helpers (QW-075).

set -eu
cd "$(dirname "$0")/.."

require_helper() {
	file=$1
	helpers=$2
	for helper in $helpers; do
		if ! grep -q "$helper" "$file"; then
			echo "FAIL - $file no longer calls $helper."
			exit 1
		fi
	done
}

require_helper src/map/buyingstore.c 'status_encumbrance_blocks_at_percent'
require_helper src/map/npc.c 'status_encumbrance_blocks_pickup'
require_helper src/map/pc.c 'status_encumbrance_blocks_pickup status_cart_weight_blocks'
require_helper src/map/rodex.c 'status_encumbrance_blocks_pickup'
require_helper src/map/script.c 'status_encumbrance_blocks_pickup'
require_helper src/map/trade.c 'status_encumbrance_blocks_pickup'
require_helper src/map/vending.c 'status_encumbrance_blocks_pickup'

if ! grep -q 'status_encumbrance_blocks_at_percent' src/map/combat_state.c || \
	! grep -q 'status_cart_weight_blocks' src/map/combat_state.c; then
	echo "FAIL - shared overflow-safe encumbrance helpers are missing."
	exit 1
fi

echo "OK - audited item-delivery paths use shared encumbrance helpers."
