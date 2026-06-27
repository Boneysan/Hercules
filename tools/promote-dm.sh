#!/bin/bash
# promote-dm.sh — promote an existing account to Dungeon Master (group 5).
#
# Usage: ./tools/promote-dm.sh <username>
#
# Reads DB credentials from conf/global/sql_connection.conf defaults.

set -e

DB_HOST="127.0.0.1"
DB_PORT="3306"
DB_USER="ragnarok"
DB_PASS="ragnarok"
DB_NAME="ragnarok"
DM_GROUP=5

USERNAME="$1"

if [ -z "$USERNAME" ]; then
    echo "Usage: $0 <username>"
    echo "Example: $0 myboneysan"
    exit 1
fi

RESULT=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -se "
SELECT account_id, userid, group_id FROM login WHERE userid = '$USERNAME' AND state = 0;
" 2>&1)

if echo "$RESULT" | grep -q "ERROR"; then
    echo "Database error: $RESULT"
    exit 1
fi

if [ -z "$RESULT" ]; then
    echo "Error: account '$USERNAME' not found."
    exit 1
fi

ACCOUNT_ID=$(echo "$RESULT" | awk '{print $1}')
CURRENT_GROUP=$(echo "$RESULT" | awk '{print $3}')

if [ "$CURRENT_GROUP" = "$DM_GROUP" ]; then
    echo "Account '$USERNAME' (ID: $ACCOUNT_ID) is already in group $DM_GROUP (Dungeon Master)."
    exit 0
fi

mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "
UPDATE login SET group_id = $DM_GROUP WHERE account_id = $ACCOUNT_ID;
" 2>&1

echo "Promoted '$USERNAME' (ID: $ACCOUNT_ID) from group $CURRENT_GROUP → group $DM_GROUP (Dungeon Master)."
echo "They must log out and back in for the change to take effect."
