#!/usr/bin/env python3
import sqlite3
from datetime import datetime, timedelta
DB = '/home/lolufe/assistant/memory.db'
conn = sqlite3.connect(DB)

# Top types d'actions
print("=== Top 20 actions dans decisions_log (7 derniers jours) ===")
rows = conn.execute(
    "SELECT action, COUNT(*) FROM decisions_log "
    "WHERE created_at >= ? "
    "GROUP BY action ORDER BY 2 DESC LIMIT 20",
    ((datetime.now() - timedelta(days=7)).isoformat(),)
).fetchall()
for r in rows: print(f"  {r[1]:>6d}  {r[0]}")

# Échantillon de 20 messages réellement envoyés (envoye=1) — diversifiés par préfixe
print("\n=== 20 messages réellement envoyés (envoye=1) — variés ===")
# On regarde les distincts en filtrant sur le 1er emoji ou le 1er mot
rows = conn.execute(
    "SELECT created_at, message FROM messages_log "
    "WHERE envoye = 1 AND length(message) > 40 "
    "ORDER BY created_at DESC LIMIT 60"
).fetchall()

# Diversifier : prendre 1 message par type de premier mot/emoji
seen = set()
diverse = []
for r in rows:
    msg = r[1].strip()
    # Premier emoji ou 3 premiers mots comme clé
    first_word = msg.split()[0] if msg.split() else ""
    if first_word in seen and len(diverse) > 5:
        continue
    seen.add(first_word)
    diverse.append(r)
    if len(diverse) >= 25:
        break

for r in diverse:
    msg = r[1].replace('\n', ' / ')[:280]
    print(f"\n  [{r[0][:19]}]")
    print(f"  {msg}")

conn.close()
