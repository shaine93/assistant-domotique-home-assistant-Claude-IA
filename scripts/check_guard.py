#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect("/home/lolufe/assistant/memory.db")

print("=== heartbeat_v2 (compteurs cumules) ===")
rows = conn.execute("SELECT entity_id, total_dryrun, total_alerts, last_gap_min FROM heartbeat_v2").fetchall()
for r in rows: print(f"  {r}")

print("\n=== heartbeat_v2_dryrun 12 dernieres ===")
rows = conn.execute("SELECT ts_iso, entity_id, gap_min, guard_active, would_alert FROM heartbeat_v2_dryrun ORDER BY id DESC LIMIT 12").fetchall()
for r in rows: print(f"  {r}")

conn.close()
