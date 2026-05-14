#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect("/home/lolufe/assistant/memory.db")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM sensor_heartbeat")
before = cur.fetchone()[0]
print(f"Avant purge : {before} entrees")
cur.execute("DELETE FROM sensor_heartbeat")
conn.commit()
cur.execute("SELECT COUNT(*) FROM sensor_heartbeat")
after = cur.fetchone()[0]
print(f"Apres purge : {after} entrees")
conn.close()
