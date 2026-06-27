#!/bin/bash
# create-account.sh — create a new player account on the Hercules RO server.
#
# Usage: ./tools/create-account.sh <username> <password> [M|F]
#
# Defaults: sex = M if not specified.
# Reads DB credentials from conf/global/sql_connection.conf (ragnarok/ragnarok).

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Database connection settings (matches conf/global/sql_connection.conf defaults).
DB_HOST="127.0.0.1"
DB_PORT="3306"
DB_USER="ragnarok"
DB_PASS="ragnarok"
DB_NAME="ragnarok"

USERNAME="$1"
PASSWORD="$2"
SEX="${3:-M}"

if [ -z "$USERNAME" ] || [ -z "$PASSWORD" ]; then
    echo "Usage: $0 <username> <password> [M|F]"
    echo "Example: $0 players3cret password123 F"
    exit 1
fi

SEX="$(echo "$SEX" | tr '[:lower:]' '[:upper:]')"
if [ "$SEX" != "M" ] && [ "$SEX" != "F" ]; then
    echo "Error: sex must be M or F (got: $SEX)"
    exit 1
fi

# Insert the account. Passwords are stored as MD5 in Hercules by default.
RESULT=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -se "
INSERT INTO login (userid, user_pass, sex, email, state, group_id)
VALUES ('$USERNAME', MD5('$PASSWORD'), '$SEX', 'a@a.com', 0, 0);
SELECT LAST_INSERT_ID();
" 2>&1)

if echo "$RESULT" | grep -q "ERROR"; then
    echo "Error creating account: $RESULT"
    exit 1
fi

ACCOUNT_ID=$(echo "$RESULT" | tail -1)
echo "Account created successfully."
echo "  Username:   $USERNAME"
echo "  Account ID: $ACCOUNT_ID"
echo "  Sex:        $SEX"
echo ""
echo "To promote to Dungeon Master (group 5), run:"
echo "  ./tools/create-account.sh ... then update in-game or via SQL:"
echo "  UPDATE login SET group_id = 5 WHERE account_id = $ACCOUNT_ID;"
