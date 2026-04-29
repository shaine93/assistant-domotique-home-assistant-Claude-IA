#!/usr/bin/env python3
"""Vérifier l'état de la mémoire tarif + ce que voit le bot maintenant."""
import sqlite3
DB = '/home/lolufe/assistant/memory.db'
conn = sqlite3.connect(DB)

print("=== Memory : tout ce qui touche au tarif HC ===")
rows = conn.execute(
    "SELECT cle, valeur FROM memoire WHERE cle LIKE '%tarif%' OR cle LIKE '%hc%' OR cle LIKE '%hp%' OR cle LIKE '%heure_creuse%'"
).fetchall()
if rows:
    for r in rows:
        print(f"  {r[0]} = {r[1][:200] if r[1] else None}")
else:
    print("  (aucune entrée)")

# Aussi : tarif actuel mémorisé
print("\n=== Tarif actif (config) ===")
rows = conn.execute("SELECT cle, valeur FROM memoire WHERE cle = 'tarif_actuel' OR cle LIKE '%tarif_config%'").fetchall()
for r in rows: print(f"  {r[0]} = {r[1][:300] if r[1] else None}")
conn.close()

# Vérifier dans HA si la stat Linky HC/HP est bien présente
import json, requests
with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)
r = requests.get(f"{cfg['ha_url']}/api/states",
                 headers={"Authorization": f"Bearer {cfg['ha_token']}"},
                 timeout=15, verify=False)
states = r.json()

print("\n=== Toutes les entités liées à Linky / linky / ha-linky ===")
matched = [s for s in states if 'linky' in s['entity_id'].lower()]
for s in matched:
    eid = s['entity_id']
    state = s['state']
    fname = s.get('attributes', {}).get('friendly_name', '')
    print(f"  {eid}: state={state} fname={fname}")

if not matched:
    print("  (aucune entité Linky visible — les statistiques peuvent être invisibles via /api/states)")

# Test auto-détection HC
print("\n=== Test auto-détection HC : recherche des entités matchant les mots-clés du bot ===")
keywords = ["hchc", "hchp", "index_hc", "index_hp", "consommation_hc", "consommation_hp",
            "off_peak_hours_index", "peak_hours_index"]
for s in states:
    eid_low = s['entity_id'].lower()
    if any(k in eid_low for k in keywords):
        print(f"  ✅ {s['entity_id']}")
