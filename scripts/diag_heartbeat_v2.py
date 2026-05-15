#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect("/home/lolufe/assistant/memory.db")

# Tables présentes
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'heartbeat%'").fetchall()
print(f"=== Tables heartbeat* : {len(tables)} ===")
for t in tables:
    print(f"  {t[0]}")

# heartbeat_v2 contents
print("\n=== heartbeat_v2 contents ===")
try:
    rows = conn.execute("SELECT * FROM heartbeat_v2").fetchall()
    for r in rows: print(f"  {r}")
    if not rows: print("  (vide)")
except Exception as e: print(f"  {e}")

# heartbeat_v2_dryrun contents (les détections en log_only)
print("\n=== heartbeat_v2_dryrun (10 plus récentes) ===")
try:
    rows = conn.execute("SELECT * FROM heartbeat_v2_dryrun ORDER BY id DESC LIMIT 10").fetchall()
    if not rows: print("  (vide — pas encore de détection ou guard étouffe tout)")
    for r in rows: print(f"  {r}")
except Exception as e: print(f"  {e}")

# Trouver d'autres tables KV
print("\n=== Tables avec 'mem' ou 'kv' ===")
for tname in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
    name = tname[0]
    if 'mem' in name.lower() or 'kv' in name.lower():
        print(f"  {name}")
        cols = conn.execute(f"PRAGMA table_info({name})").fetchall()
        print(f"    Colonnes: {[c[1] for c in cols]}")
        # Voir les clés heartbeat
        try:
            rows = conn.execute(f"SELECT * FROM {name} WHERE key LIKE '%heartbeat%'").fetchall()
            for r in rows: print(f"    {r}")
        except: pass

conn.close()
