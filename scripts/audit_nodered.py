#!/usr/bin/env python3
"""Audit Node-RED : flows.json et processus."""
import json, requests, os, subprocess
with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)
H = {"Authorization": f"Bearer {cfg['ha_token']}"}
BASE = cfg['ha_url']

# 1. Node-RED tourne ?
print("=== Node-RED accessible via HA ? ===")
try:
    r = requests.get(f"{BASE}/api/hassio/addons/a0d7b954_nodered/info", headers=H, timeout=10, verify=False)
    print(f"  Status hassio addon: {r.status_code}")
    if r.status_code == 200:
        info = r.json()
        print(f"  state: {info.get('data', {}).get('state')}")
        print(f"  version: {info.get('data', {}).get('version')}")
except Exception as e:
    print(f"  ❌ {e}")

# 2. Tenter d'atteindre Node-RED directement
print("\n=== Node-RED interface ===")
for url in [f"{BASE}/api/hassio_ingress/nodered/", "http://192.168.1.76:1880/"]:
    try:
        r = requests.get(url, headers=H, timeout=5, verify=False)
        print(f"  {url} → status {r.status_code}")
    except Exception as e:
        print(f"  {url} → ❌ {type(e).__name__}")

# 3. Lister les notifications envoyées récemment via /api/events
# Pas possible directement, mais on peut voir les services qui ont été appelés via les logs

# 4. Vérifier que les services telegram_bot sont disponibles
print("\n=== Services telegram_bot disponibles ===")
r = requests.get(f"{BASE}/api/services", headers=H, timeout=10, verify=False)
services = r.json()
for d in services:
    if d['domain'] == 'telegram_bot':
        print(f"  domain telegram_bot trouvé : {list(d['services'].keys())[:5]}...")
        break
    if d['domain'] == 'notify':
        notifs = [s for s in d['services'].keys() if 'telegram' in s.lower()]
        if notifs:
            print(f"  notify.telegram* : {notifs}")
