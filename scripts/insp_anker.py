#!/usr/bin/env python3
import json, requests
with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)
H = {"Authorization": f"Bearer {cfg['ha_token']}"}
BASE = cfg['ha_url']

# Récupérer l'état détaillé
r = requests.get(f"{BASE}/api/states/automation.delestage_anker_cycle_batterie_100_30", headers=H, timeout=10, verify=False)
print("=== State ===")
print(json.dumps(r.json(), indent=2, ensure_ascii=False)[:2000])

# Récupérer la config via /api/config/automation/config/<id>
auto_id_state = r.json().get("attributes", {}).get("id")
print(f"\n=== auto_id: {auto_id_state} ===")
if auto_id_state:
    r2 = requests.get(f"{BASE}/api/config/automation/config/{auto_id_state}", headers=H, timeout=10, verify=False)
    print(f"Status : {r2.status_code}")
    if r2.status_code == 200:
        print(json.dumps(r2.json(), indent=2, ensure_ascii=False)[:5000])
