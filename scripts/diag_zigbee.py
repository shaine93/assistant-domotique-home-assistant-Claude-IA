#!/usr/bin/env python3
"""Diag little_monkey + test direct API Ecojoko."""
import os, json, sqlite3, glob

# 1. Version installée
print("=== VERSION little_monkey ===")
manifest_paths = glob.glob("/usr/share/hassio/homeassistant/custom_components/little_monkey/manifest.json")
manifest_paths += glob.glob("/config/custom_components/little_monkey/manifest.json")
manifest_paths += glob.glob("/root/homeassistant/custom_components/little_monkey/manifest.json")

# Aussi via API HA
try:
    import requests
    with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)
    
    # Voir si on peut accéder au custom_components via SSH HA (improbable)
    # Plus simple : passer par /api/error_log ou /api/integrations
    
    # Via /api/components donne juste les domains, pas la version
    # Passer par le sensor "Ecojoko" qui contient peut-être la version
    r = requests.get(f"{cfg['ha_url']}/api/states/sensor.ecojoko",
                     headers={"Authorization": f"Bearer {cfg['ha_token']}"},
                     timeout=10, verify=False)
    if r.status_code == 200:
        data = r.json()
        print(f"  sensor.ecojoko state: {data.get('state')} (probable version)")
        for k, v in data.get('attributes', {}).items():
            print(f"    {k}: {v}")
except Exception as e:
    print(f"  err: {e}")

# 2. Update intégration disponible ?
print("\n=== UPDATE little_monkey ===")
try:
    r = requests.get(f"{cfg['ha_url']}/api/states/update.little_monkey_update",
                     headers={"Authorization": f"Bearer {cfg['ha_token']}"},
                     timeout=10, verify=False)
    if r.status_code == 200:
        data = r.json()
        attrs = data.get('attributes', {})
        print(f"  state: {data.get('state')}")
        print(f"  installed_version: {attrs.get('installed_version','?')}")
        print(f"  latest_version: {attrs.get('latest_version','?')}")
        print(f"  release_summary: {attrs.get('release_summary','')[:300]}")
        print(f"  release_url: {attrs.get('release_url','')}")
except Exception as e:
    print(f"  err: {e}")

# 3. Autres switches (pre_release etc.)
print("\n=== switch.little_monkey_pre_release ===")
try:
    r = requests.get(f"{cfg['ha_url']}/api/states/switch.little_monkey_pre_release",
                     headers={"Authorization": f"Bearer {cfg['ha_token']}"},
                     timeout=10, verify=False)
    if r.status_code == 200:
        data = r.json()
        print(f"  state: {data.get('state')}")
        for k, v in data.get('attributes', {}).items():
            print(f"    {k}: {v}")
except Exception as e:
    print(f"  err: {e}")

# 4. Voir l'historique HC/HP sur 30 jours pour comprendre quand ils ont arrêté de fonctionner
from datetime import datetime, timedelta, timezone
print("\n=== Historique HC sur 30 jours (1 sample tous les 3 jours) ===")
start = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
url = f"{cfg['ha_url']}/api/history/period/{start}?filter_entity_id=sensor.ecojoko_consommation_hc_reseau&minimal_response&no_attributes"
try:
    r = requests.get(url, headers={"Authorization": f"Bearer {cfg['ha_token']}"},
                     timeout=30, verify=False)
    data = r.json()
    if data and data[0]:
        h = data[0]
        print(f"  {len(h)} updates sur 30 jours")
        # Garder 1 sample par jour pour visualiser
        seen_dates = set()
        for entry in h:
            ts = entry.get('last_changed', entry.get('last_updated', ''))
            date = ts[:10]
            state = entry.get('state', '')
            if date not in seen_dates:
                seen_dates.add(date)
                print(f"    {date}  state={state}")
            elif state == "unknown":
                # Toujours signaler les unknown
                pass
except Exception as e:
    print(f"  err: {e}")

# 5. Tester l'API Ecojoko native (si on a les creds dans config.json)
print("\n=== Test API Ecojoko native (lecture seule) ===")
# little_monkey utilise probablement les creds Ecojoko, pas dans /home/lolufe/assistant/config.json
# Mais les creds existent dans HA, on peut juste vérifier si l'intégration tourne :
print("  (creds Ecojoko stockés dans HA, pas accessibles depuis ici)")
print("  → Conclusion via les sensors HA uniquement")
