#!/bin/bash
# Reset des baselines heartbeat — appelé une seule fois après changement de la liste des sensors piliers.
DB="/home/lolufe/assistant/memory.db"
if [ ! -f "$DB" ]; then
    echo "ERROR: $DB introuvable"
    exit 1
fi
sqlite3 "$DB" <<'SQL'
DELETE FROM sensor_heartbeat;
SQL
echo "OK: sensor_heartbeat vidée"
sqlite3 "$DB" "SELECT COUNT(*) AS rows_remaining FROM sensor_heartbeat;"
