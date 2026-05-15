#!/usr/bin/env python3
import json, requests
with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)
H = {"Authorization": f"Bearer {cfg['ha_token']}"}
BASE = cfg['ha_url']

r = requests.get(f"{BASE}/api/states", headers=H, timeout=15, verify=False)
states = r.json()
idx = {s['entity_id']: s for s in states}

# Sensors critiques pour le guard solar
print("=== Pour guard solar ===")
sun = idx.get('sun.sun')
print(f"sun.sun: state={sun.get('state') if sun else 'MANQUANT'}")
if sun:
    attrs = sun.get('attributes', {})
    print(f"  elevation: {attrs.get('elevation')}")
    print(f"  azimuth: {attrs.get('azimuth')}")

# Sensors meteo
print()
weather = [s for s in states if s['entity_id'].startswith('weather.')]
print(f"weather.*: {len(weather)} entités")
for w in weather:
    print(f"  {w['entity_id']}: state={w['state']}")
    attrs = w.get('attributes', {})
    if 'cloud_coverage' in attrs:
        print(f"    cloud_coverage: {attrs['cloud_coverage']}")
    if 'humidity' in attrs:
        print(f"    humidity: {attrs['humidity']}")

# Pluie
print()
rain = [s for s in states if 'rain' in s['entity_id'].lower() or 'pluie' in s['entity_id'].lower()]
print(f"rain/pluie: {len(rain)} entités")
for r in rain[:10]:
    print(f"  {r['entity_id']}: state={r['state']} unit={r.get('attributes',{}).get('unit_of_measurement','?')}")

# Sensors ECU et Ecojoko
print()
print("=== Les sensors heartbeat v2 ===")
for eid in ['sensor.ecojoko_consommation_reseau', 'sensor.ecu_today_energy', 'sensor.ecu_current_power']:
    s = idx.get(eid)
    if s:
        print(f"  {eid}: state={s['state']} last_updated={s.get('last_updated','?')[:19]}")
