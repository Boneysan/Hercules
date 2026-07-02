# MariaDB Campaign Backup — Verification Handoff

Written 2026-07-02. Hand this to whoever (human or agent) is at the keyboard
the next time MariaDB is running. It finishes WP-13 from
`planning/dm-architecture-review.md` (finding F16: campaign state previously
had no backups at all).

## Status at handoff

**Built and committed** (commit `5ef4ecda9`):

- `tools/backup-campaign.sh` — gzipped, timestamped `mysqldump` of the whole
  `ragnarok` database into `backups/` (gitignored). Optional label argument
  (`./tools/backup-campaign.sh pre_reset`). Keeps the newest 20 dumps.
  Uses `--single-transaction --quick --routines`.
- Safety: `set -o pipefail` + a delete-and-fail if `mysqldump` errors or the
  dump is under 10 KB — a down DB can never leave a silent empty "backup".
- `tools/campaign-preflight.sh` runs it as **step 0** (non-fatal warn on
  failure so the rest of preflight still reports), meaning every game night
  gets an automatic snapshot.

**Verified:** the failure path only. MariaDB was down during the build
session; a failed dump correctly exits 1, prints
`BACKUP FAILED - is MariaDB running? Nothing was written.`, and leaves no
file behind.

**NOT yet verified:** the success path and a restore. That is this handoff.

## Environment facts (checked, not assumed)

- WSL2 Ubuntu; **systemd is `offline`** in this session, so `systemctl start`
  will not work. Use the SysV wrapper (exists at `/etc/init.d/mariadb`):
  `sudo service mariadb start`
  (needs an interactive sudo password — an agent should ask the user to run
  it via the `!` prefix if sudo prompts).
- DB credentials (from `conf/global/sql_connection.conf`, hardcoded
  identically in the script and in `tools/promote-dm.sh`):
  host `127.0.0.1`, port `3306`, user `ragnarok`, password `ragnarok`,
  database `ragnarok`.
- Liveness probe: `mysqladmin -h 127.0.0.1 -u ragnarok -pragnarok ping`
  → `mysqld is alive` when up.

## Verification procedure (run top to bottom)

```bash
cd ~/GitHub/Hercules_RO   # repo root

# 0. Ensure DB is up
mysqladmin -h 127.0.0.1 -u ragnarok -pragnarok ping   # expect: mysqld is alive

# 1. Success path
./tools/backup-campaign.sh verify
# Expect: "Backup written: backups/ragnarok_<stamp>_verify.sql.gz (<size>)"
# Size sanity: a real campaign DB dump should be at least a few hundred KB.
ls -lh backups/

# 2. Dump content spot-check (story flags + quests + globals must be present)
gunzip -c backups/ragnarok_*_verify.sql.gz | grep -c "INSERT INTO \`char_reg_num_db\`"   # >= 1 once anyone has campaign flags
gunzip -c backups/ragnarok_*_verify.sql.gz | grep -m1 "CREATE TABLE \`quest\`"
gunzip -c backups/ragnarok_*_verify.sql.gz | grep -m1 "CREATE TABLE \`mapreg\`"

# 3. Restore drill into a scratch DB (never touch `ragnarok` for this)
mysql -h 127.0.0.1 -u ragnarok -pragnarok -e "CREATE DATABASE IF NOT EXISTS ragnarok_restore_test"
gunzip -c backups/ragnarok_*_verify.sql.gz | mysql -h 127.0.0.1 -u ragnarok -pragnarok ragnarok_restore_test
mysql -h 127.0.0.1 -u ragnarok -pragnarok -e "
  SELECT (SELECT COUNT(*) FROM ragnarok.char_reg_num_db) AS live_flags,
         (SELECT COUNT(*) FROM ragnarok_restore_test.char_reg_num_db) AS restored_flags,
         (SELECT COUNT(*) FROM ragnarok.quest) AS live_quests,
         (SELECT COUNT(*) FROM ragnarok_restore_test.quest) AS restored_quests;"
# Expect: live == restored for both pairs.
mysql -h 127.0.0.1 -u ragnarok -pragnarok -e "DROP DATABASE ragnarok_restore_test"

# 4. Preflight integration
./tools/campaign-preflight.sh 2>&1 | head -12
# Expect step 0 to print a fresh "Backup written: ..." line.

# 5. Retention (optional, quick): confirm only newest 20 ragnarok_*.sql.gz remain
ls -1t backups/ragnarok_*.sql.gz | wc -l   # <= 20
```

If restoring for real one day: **stop login/char/map servers first**, then
`gunzip -c backups/<file>.sql.gz | mysql -h 127.0.0.1 -u ragnarok -pragnarok ragnarok`.

## After verification

1. Tick WP-13's remaining steps in `planning/dm-architecture-review.md`
   (mark the package fully done, note the verified dump size).
2. Delete stray `*_verify` / `*_fail_test` dumps if you want a clean
   `backups/` (or leave them; retention will age them out).
3. Remind the DM of the two habit rules (also in the crash runbook in
   `planning/dm-playtest-notes.md`):
   - labeled manual backup before `@dm reset confirm` or any bulk flag
     operation: `./tools/backup-campaign.sh pre_reset`
   - occasionally copy `backups/` off the WSL disk — it is the only copy of
     the campaign.

## Known limitations (accepted, do not "fix" without cause)

- Credentials are hardcoded in the script (matching `promote-dm.sh`'s
  existing pattern and the conf file). Fine for a localhost hobby server.
- Full-DB dump, not table-selective — the DB is small and a full dump makes
  restores trivial.
- No compression-level/threading tuning — not needed at this size.
