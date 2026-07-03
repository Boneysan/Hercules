#!/bin/bash
# backup-campaign.sh — snapshot the campaign database.
#
# All Seal Cascade campaign state lives in MariaDB: story flags + inspiration
# (char_reg_num_db), quest states (quest), global $dm_* flags
# (map_reg_num_db / map_reg_str_db), and the characters themselves. One bad
# `@dm reset confirm` or `@dm flag sync`
# from the wrong source loses a 19-arc playthrough — run this before every
# session and before any risky bulk operation.
#
# Usage: ./tools/backup-campaign.sh [label]
#   ./tools/backup-campaign.sh                 -> backups/ragnarok_YYYYmmdd_HHMMSS.sql.gz
#   ./tools/backup-campaign.sh pre_session12   -> backups/ragnarok_YYYYmmdd_HHMMSS_pre_session12.sql.gz
#
# Restore (STOPS the story where the dump was taken — take servers down first):
#   gunzip -c backups/<file>.sql.gz | mysql -h 127.0.0.1 -u ragnarok -pragnarok ragnarok
#
# Keeps the newest 20 dumps; older ones are pruned automatically.

set -e
set -o pipefail

DB_HOST="127.0.0.1"
DB_PORT="3306"
DB_USER="ragnarok"
DB_PASS="ragnarok"
DB_NAME="ragnarok"
KEEP=20

cd "$(dirname "$0")/.."
mkdir -p backups

STAMP=$(date +%Y%m%d_%H%M%S)
LABEL="${1:+_$1}"
OUT="backups/${DB_NAME}_${STAMP}${LABEL}.sql.gz"

if ! mysqldump -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" \
    --single-transaction --quick --routines "$DB_NAME" | gzip > "$OUT"; then
    rm -f "$OUT"
    echo "BACKUP FAILED - is MariaDB running? Nothing was written." >&2
    exit 1
fi

# A dump of a real campaign DB is never this small; treat it as a failure.
if [ "$(stat -c %s "$OUT")" -lt 10240 ]; then
    rm -f "$OUT"
    echo "BACKUP FAILED - dump was implausibly small; nothing was kept." >&2
    exit 1
fi

# Prune old dumps beyond retention.
ls -1t backups/"${DB_NAME}"_*.sql.gz 2>/dev/null | tail -n +"$((KEEP + 1))" | xargs -r rm --

echo "Backup written: $OUT ($(du -h "$OUT" | cut -f1))"
echo "Restore with:   gunzip -c $OUT | mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p'****' $DB_NAME"
