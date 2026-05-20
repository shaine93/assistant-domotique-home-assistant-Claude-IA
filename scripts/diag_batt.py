#!/usr/bin/env python3
import json, requests
with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)
H = {"Authorization": f"Bearer {cfg['ha_token']}"}
BASE = cfg['ha_url']

# 1. Lister les automatisations HA actives qui pourraient envoyer ces alertes
r = requests.get(f"{BASE}/api/states", headers=H, timeout=15, verify=False)
states = r.json()

# Chercher les automatisations dont le nom contient "batterie" ou "solarbank" ou "recharge"
print("=== Automatisations HA actives - batterie/solarbank ===")
autos = [s for s in states if s["entity_id"].startswith("automation.")]
matches = []
for a in autos:
    eid = a["entity_id"].lower()
    fname = a.get("attributes", {}).get("friendly_name", "").lower()
    if any(k in eid or k in fname for k in ["batterie", "battery", "solarbank", "recharge", "anker"]):
        matches.append(a)
        print(f"  {a['entity_id']}: state={a['state']}")
        print(f"    friendly_name: {a.get('attributes', {}).get('friendly_name')}")
        last = a.get("attributes", {}).get("last_triggered")
        if last:
            print(f"    last_triggered: {last[:19]}")

# Si rien trouvé, chercher dans les scripts
if not matches:
    print("\n=== Scripts HA - batterie/solarbank ===")
    scripts = [s for s in states if s["entity_id"].startswith("script.")]
    for s in scripts:
        eid = s["entity_id"].lower()
        if any(k in eid for k in ["batterie", "battery", "solarbank", "recharge", "anker"]):
            print(f"  {s['entity_id']}: state={s['state']}")
            last = s.get("attributes", {}).get("last_triggered")
            if last:
                print(f"    last_triggered: {last[:19]}")

# Voir aussi les triggers d'automatisations qui surveillent un seuil
# (toutes automatisations qui mentionnent Solarbank ou < 30)
print("\n=== Toutes les automatisations actives (sans filtre) - total ===")
print(f"  {len([a for a in autos if a['state'] == 'on'])} automatisations actives")
print(f"  {len([a for a in autos if a['state'] == 'unavailable'])} unavailable")

# Les 30 dernières déclenchées
print("\n=== 15 automatisations déclenchées le plus récemment ===")
with_trig = [a for a in autos if a.get("attributes", {}).get("last_triggered")]
with_trig.sort(key=lambda x: x["attributes"]["last_triggered"], reverse=True)
for a in with_trig[:15]:
    last = a["attributes"]["last_triggered"][:19]
    fname = a.get("attributes", {}).get("friendly_name", "")
    print(f"  {last} | {a['entity_id']} | {fname[:60]}")
