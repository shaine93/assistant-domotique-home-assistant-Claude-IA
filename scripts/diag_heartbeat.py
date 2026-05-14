#!/usr/bin/env python3
import sqlite3
DB = "/home/lolufe/assistant/memory.db"
conn = sqlite3.connect(DB)

# Lister les heartbeats actuels
print("=== Table sensor_heartbeat ===")
try:
    rows = conn.execute("SELECT entity_id, median_sec, p99_sec, samples_count, learning_complete FROM sensor_heartbeat ORDER BY entity_id").fetchall()
    print(f"  {len(rows)} entrees")
    for r in rows:
        print(f"  {r}")
except Exception as e:
    print(f"  Erreur : {e}")

conn.close()
