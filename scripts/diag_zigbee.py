#!/usr/bin/env python3
"""Audit post-automatisation."""
import json, requests
from datetime import datetime
with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)
H = {"Authorization": f"Bearer {cfg['ha_token']}"}
BASE = cfg['ha_url']

# 1. Quel jour sommes-nous ?
print(f"=== Jour actuel ===")
now = datetime.now()
weekday = now.weekday()
jour_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][weekday]
print(f"  {now.strftime('%Y-%m-%d %H:%M')} = {jour_fr} (weekday={weekday})")
attendu_hc = weekday in [2, 5, 6]
print(f"  Attendu : tarif {'HC' if attendu_hc else 'HP'}")

# 2. L'automatisation existe-t-elle ?
print("\n=== 1. Automatisation ZWEP ===")
r = requests.get(f"{BASE}/api/states/automation.zwep_bascule_tarif_hc_hp_selon_jour", 
                 headers=H, timeout=10, verify=False)
if r.status_code == 200:
    auto = r.json()
    print(f"  ✅ {auto['entity_id']}: state={auto['state']}")
    last = auto.get('attributes', {}).get('last_triggered')
    print(f"  last_triggered: {last}")
else:
    # Essayer un autre slug
    r = requests.get(f"{BASE}/api/states", headers=H, timeout=15, verify=False)
    states = r.json()
    autos = [s for s in states if 'zwep' in s['entity_id'].lower()]
    print(f"  Automatisations contenant 'zwep' : {len(autos)}")
    for a in autos:
        print(f"    {a['entity_id']}: state={a['state']}")
        last = a.get('attributes', {}).get('last_triggered')
        if last: print(f"      last_triggered: {last}")

# 3. État des select.conso_zwep_*
r = requests.get(f"{BASE}/api/states", headers=H, timeout=15, verify=False)
states = r.json()
print("\n=== 2. État actuel des selects de tarif ===")
selects = sorted([s for s in states if s['entity_id'].startswith('select.conso_zwep_')], key=lambda x: x['entity_id'])
for s in selects:
    state = s['state']
    icon = '✅' if state == ('hc' if attendu_hc else 'hp') else '⚠️'
    print(f"  {icon} {s['entity_id']}: {state}")

# 4. input_select.tarif_courant
ts = [s for s in states if s['entity_id'] == 'input_select.tarif_courant']
if ts:
    state = ts[0]['state']
    icon = '✅' if state == ('hc' if attendu_hc else 'hp') else '⚠️'
    print(f"\n  {icon} input_select.tarif_courant: {state}")

# 5. État des sensors conso_zwep_*_hc et _hp
print("\n=== 3. État des sensors utility_meter ===")
zwep_sensors = sorted([s for s in states if s['entity_id'].startswith('sensor.conso_zwep_')], key=lambda x: x['entity_id'])
for s in zwep_sensors:
    eid = s['entity_id']
    state = s['state']
    print(f"  {eid}: {state}")

# 6. Sensors coût mis à jour
print("\n=== 4. Sensors de coûts ===")
cout_sensors = ['cout_jour_hc', 'cout_jour_hp', 'cout_jour_total', 
                'cout_mois_total', 'cout_annee_total',
                'economie_possible_mois']
for nom in cout_sensors:
    eid = f'sensor.{nom}'
    matched = [s for s in states if s['entity_id'] == eid]
    if matched:
        print(f"  {eid}: {matched[0]['state']} €")
