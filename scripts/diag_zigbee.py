#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect('/home/lolufe/assistant/memory.db')
print("=== Table sensor_heartbeat ===")
rows = conn.execute("PRAGMA table_info(sensor_heartbeat)").fetchall()
if rows:
    for r in rows: print(f"  col: {r[1]} ({r[2]})")
else:
    print("absente")
print("\n=== Entrées ===")
try:
    rows = conn.execute("SELECT entity_id, learning_started, learning_complete FROM sensor_heartbeat ORDER BY entity_id").fetchall()
    print(f"  {len(rows)} entrées :")
    for r in rows: print(f"    {r[0]:55s} started={r[1][:19] if r[1] else '?':19s} complete={r[2]}")
except Exception as e:
    print(f"  err: {e}")
print("\n=== heartbeat_check (memoire) ===")
try:
    rows = conn.execute("SELECT cle, valeur FROM memoire WHERE cle = 'heartbeat_check'").fetchall()
    if rows: print(f"  ✅ {rows[0]}")
    else: print("  pas encore")
except Exception as e: print(f"  err: {e}")
conn.close()
