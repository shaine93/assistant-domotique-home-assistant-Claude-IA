#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect('/home/lolufe/assistant/memory.db')

# Table créée ?
print("=== Table sensor_heartbeat ===")
try:
    rows = conn.execute("PRAGMA table_info(sensor_heartbeat)").fetchall()
    if rows:
        print(f"✅ Schéma:")
        for r in rows: print(f"    {r}")
    else:
        print("❌ Table absente")
except Exception as e:
    print(f"err: {e}")

# Entrées créées ?
print("\n=== Entrées dans sensor_heartbeat ===")
try:
    rows = conn.execute("SELECT entity_id, learning_started, learning_complete FROM sensor_heartbeat ORDER BY entity_id").fetchall()
    print(f"  {len(rows)} entrées")
    for r in rows: print(f"    {r}")
except Exception as e:
    print(f"err: {e}")

conn.close()
