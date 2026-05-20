#!/usr/bin/env python3
"""Inspecter les triggers Telegram dans HA automations.yaml et configuration.yaml."""
import json, requests, re
with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)
H = {"Authorization": f"Bearer {cfg['ha_token']}"}
BASE = cfg['ha_url']

# Récupérer la liste de toutes les automatisations actives
r = requests.get(f"{BASE}/api/states", headers=H, timeout=15, verify=False)
states = r.json()
all_autos_active = [s for s in states if s["entity_id"].startswith("automation.") and s["state"] == "on"]
print(f"=== {len(all_autos_active)} automatisations actives ===\n")

# Récupérer le détail de chaque automatisation pour chercher "recharge nécessaire"
# via le service /api/config/automation/config/{id}
matches = []
for a in all_autos_active:
    eid = a["entity_id"]
    auto_id = a.get("attributes", {}).get("id")
    if not auto_id:
        continue
    try:
        r2 = requests.get(f"{BASE}/api/config/automation/config/{auto_id}", headers=H, timeout=10, verify=False)
        if r2.status_code == 200:
            data = r2.json()
            txt = json.dumps(data, ensure_ascii=False)
            if "recharge" in txt.lower() or "anker" in txt.lower() or "solarbank" in txt.lower():
                fname = a.get("attributes", {}).get("friendly_name", "")
                print(f"🎯 {eid}")
                print(f"   friendly_name: {fname}")
                # Extraire les actions de notification
                actions = data.get("action", [])
                if isinstance(actions, dict):
                    actions = [actions]
                for action in actions:
                    if isinstance(action, dict):
                        atxt = json.dumps(action, ensure_ascii=False)
                        if "telegram" in atxt.lower() or "notify" in atxt.lower() or "recharge" in atxt.lower():
                            # Afficher l'action
                            print(f"   ACTION: {json.dumps(action, ensure_ascii=False)[:400]}")
                matches.append(eid)
                print()
    except Exception as e:
        pass

if not matches:
    print("Aucune automatisation active ne contient 'recharge', 'anker' ou 'solarbank'.")
    print("L'alerte vient peut-être d'un script HA ou de Node-RED.")
