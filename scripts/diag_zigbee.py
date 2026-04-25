#!/usr/bin/env python3
"""Inventaire des sensors piliers énergétiques."""
import json, requests
from datetime import datetime, timedelta, timezone

with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)
r = requests.get(f"{cfg['ha_url']}/api/states",
                 headers={"Authorization": f"Bearer {cfg['ha_token']}"},
                 timeout=15, verify=False)
states = r.json()

# Helper : âge d'un sensor en minutes
now = datetime.now(timezone.utc)
def age_min(s):
    upd = s.get('last_updated', '')
    if not upd: return None
    try:
        dt = datetime.fromisoformat(upd.replace('Z', '+00:00'))
        return (now - dt).total_seconds() / 60
    except: return None

def afficher_categorie(titre, candidats):
    print(f"\n═══ {titre} ═══")
    if not candidats:
        print("  (aucun trouvé)")
        return []
    for s in candidats:
        eid = s['entity_id']
        state = s['state']
        unit = s.get('attributes', {}).get('unit_of_measurement', '')
        fname = s.get('attributes', {}).get('friendly_name', '')[:40]
        device_class = s.get('attributes', {}).get('device_class', '')
        a = age_min(s)
        age_str = f"{a:.0f}min" if a is not None and a < 60 else f"{a/60:.1f}h" if a else "?"
        print(f"  {eid:55s} state={state:>10s}{unit:5s} age={age_str:>8s} [{device_class}] {fname}")
    return [s["entity_id"] for s in candidats]

# 1. ECOJOKO (déjà connu mais on le confirme)
ecojoko = sorted([s for s in states 
                  if 'ecojoko' in s['entity_id'].lower() 
                  and s['entity_id'].startswith('sensor.')
                  and s.get('attributes', {}).get('device_class') in ('power', 'energy', 'humidity', 'temperature', None)
                  and s.get('attributes', {}).get('unit_of_measurement') in ('W', 'kWh', '%', '°C', '€', None)
                  and s['entity_id'] != 'sensor.ecojoko'],  # exclu : c'est la version
                  key=lambda x: x['entity_id'])
afficher_categorie("ECOJOKO — sensors énergétiques candidats", ecojoko)

# 2. APSYSTEMS — production solaire (microonduleurs)
ap = sorted([s for s in states 
             if (('apsystems' in s['entity_id'].lower() 
                  or 'ecu' in s['entity_id'].lower()
                  or 'micro_onduleur' in s['entity_id'].lower()
                  or 'microonduleur' in s['entity_id'].lower()
                  or 'panneau' in s['entity_id'].lower()
                  or 'pv_' in s['entity_id'].lower())
                 and s['entity_id'].startswith('sensor.'))],
            key=lambda x: x['entity_id'])
# Filtrer pour ne garder que ceux pertinents (puissance/énergie)
ap_filt = [s for s in ap 
           if s.get('attributes', {}).get('unit_of_measurement') in ('W', 'kWh', 'V', 'A', '°C', 'Wh')
           or s.get('attributes', {}).get('device_class') in ('power', 'energy')]
afficher_categorie("APSYSTEMS — sensors solaire candidats (filtre power/energy)", ap_filt[:30])

# 3. SOLARBANK ANKER (batterie)
ank = sorted([s for s in states 
              if (('anker' in s['entity_id'].lower()
                   or 'solarbank' in s['entity_id'].lower())
                  and s['entity_id'].startswith('sensor.'))],
             key=lambda x: x['entity_id'])
ank_filt = [s for s in ank 
            if s.get('attributes', {}).get('unit_of_measurement') in ('W', 'kWh', '%', 'V', 'A')
            or s.get('attributes', {}).get('device_class') in ('power', 'energy', 'battery')]
afficher_categorie("SOLARBANK ANKER — sensors batterie/solaire candidats", ank_filt[:30])

# 4. Inventaire général : tous les sensors avec device_class=power, energy, ou battery
print("\n═══ AUTRES sensors énergétiques (device_class=power|energy|battery) ═══")
auto_elus = sorted([s for s in states 
                    if s['entity_id'].startswith('sensor.')
                    and s.get('attributes', {}).get('device_class') in ('power', 'energy')
                    and s['entity_id'] not in [c['entity_id'] for c in ecojoko + ap_filt + ank_filt]
                    and 'ecojoko' not in s['entity_id'].lower()
                    and 'anker' not in s['entity_id'].lower()
                    and 'solarbank' not in s['entity_id'].lower()
                    and 'apsystems' not in s['entity_id'].lower()],
                   key=lambda x: x['entity_id'])

print(f"  {len(auto_elus)} sensors énergétiques autres trouvés (top 25 par fraîcheur):")
auto_elus_recents = sorted(auto_elus, key=lambda x: age_min(x) if age_min(x) is not None else 999999)[:25]
for s in auto_elus_recents:
    eid = s['entity_id']
    state = s['state']
    unit = s.get('attributes', {}).get('unit_of_measurement', '')
    a = age_min(s)
    age_str = f"{a:.0f}min" if a is not None and a < 60 else f"{a/60:.1f}h" if a else "?"
    print(f"  {eid:55s} state={state:>10s}{unit:5s} age={age_str:>8s}")
