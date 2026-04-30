#!/usr/bin/env python3
"""Lister TOUS les services notify.* disponibles dans HA + analyser leur usage."""
import json, requests
with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)

# Récupérer les services HA
r = requests.get(f"{cfg['ha_url']}/api/services",
                 headers={"Authorization": f"Bearer {cfg['ha_token']}"},
                 timeout=15, verify=False)

services = r.json()

# Trouver le domain "notify"
print("═══ Services notify.* disponibles ═══\n")
for domain in services:
    if domain['domain'] == 'notify':
        for service_name, service_info in sorted(domain['services'].items()):
            desc = service_info.get('description', '')[:120]
            print(f"  notify.{service_name}")
            if desc:
                print(f"    └─ {desc}")
        break
else:
    print("  (aucun service notify trouvé)")

# Tester aussi : entités dont le nom contient "mobile_app" ou "notify"
print("\n═══ Entités liées aux notifications ═══")
r = requests.get(f"{cfg['ha_url']}/api/states",
                 headers={"Authorization": f"Bearer {cfg['ha_token']}"},
                 timeout=15, verify=False)
states = r.json()

# device_tracker des téléphones
print("\n--- device_tracker.* (smartphones HA Companion) ---")
for s in states:
    if s['entity_id'].startswith('device_tracker.') and 'mobile' in s['entity_id'].lower():
        print(f"  {s['entity_id']}: state={s['state']}")

# sensors mobile (batterie, version app, etc.)
print("\n--- sensor.*_battery_level (smartphones) ---")
seen = set()
for s in states:
    eid = s['entity_id']
    if eid.startswith('sensor.') and 'battery_level' in eid:
        # Extraire le nom du device
        # ex: sensor.pixel_8_battery_level → pixel_8
        device = eid.replace('sensor.', '').replace('_battery_level', '')
        if device not in seen:
            seen.add(device)
            print(f"  Device détecté: {device} (entity: {eid})")
