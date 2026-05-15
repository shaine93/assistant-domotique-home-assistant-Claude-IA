#!/usr/bin/env python3
"""Audit Telegram complet — phase 2."""
import json, requests, os, re
with open('/home/lolufe/assistant/config.json') as f:
    cfg = json.load(f)
H = {"Authorization": f"Bearer {cfg['ha_token']}"}
BASE = cfg['ha_url']

print("=" * 70)
print("AUDIT TELEGRAM COMPLET — Phase 2")
print("=" * 70)

# 1. Lire configuration.yaml via l'API HA (endpoint /api/config/core/check_config est admin only)
# On va tenter une lecture directe via le filesystem mappé /homeassistant
print("\n[1] Recherche de configuration.yaml")
candidats = [
    '/homeassistant/configuration.yaml',
    '/config/configuration.yaml',
    '/mnt/homeassistant/configuration.yaml',
]
config_path = None
for c in candidats:
    if os.path.exists(c):
        config_path = c
        print(f"  Trouvé : {c}")
        break

if not config_path:
    # Tester si la VM a un mount NFS/Samba vers HA
    for mp in ['/mnt', '/srv', '/media']:
        if os.path.exists(mp):
            for root, dirs, files in os.walk(mp):
                if 'configuration.yaml' in files:
                    config_path = os.path.join(root, 'configuration.yaml')
                    print(f"  Trouvé via walk : {config_path}")
                    break
            if config_path: break

if not config_path:
    print("  ❌ configuration.yaml inaccessible depuis la VM")
    print("  La VM AssistantIA n'a pas de mount vers le filesystem HA")
    print("  (normal — HA Green est isolé sur la box)")
else:
    # Lire et chercher la section telegram_bot
    with open(config_path) as f:
        ct = f.read()
    print(f"  Taille : {len(ct)} chars")
    # Section telegram_bot
    if 'telegram_bot:' in ct:
        idx = ct.index('telegram_bot:')
        # Lire jusqu'au prochain bloc racine
        section = ct[idx:idx+2000]
        # Tronquer aux 30 premières lignes
        section_lines = section.split('\n')[:30]
        print("\n  --- Section telegram_bot ---")
        for l in section_lines:
            # Anonymiser token éventuel
            l_safe = re.sub(r'\b\d{8,12}:[A-Za-z0-9_-]{30,}\b', '<TOKEN_BOT2_REDACTED>', l)
            print(f"  {l_safe}")
        print("  --- fin section ---")

# 2. Récupérer toutes les automatisations Telegram via API HA (états + IDs)
print("\n[2] Automatisations Telegram dans HA")
r = requests.get(f"{BASE}/api/states", headers=H, timeout=15, verify=False)
states = r.json()
autos_tg = [s for s in states if s['entity_id'].startswith('automation.') 
            and 'telegram' in s['entity_id'].lower()]
print(f"  {len(autos_tg)} automatisations Telegram trouvées :")
for a in autos_tg:
    attrs = a.get('attributes', {})
    last = attrs.get('last_triggered', '(jamais)')
    print(f"  - {a['entity_id']}")
    print(f"      state={a['state']}, last_triggered={last[:19] if last and last != '(jamais)' else last}")

# 3. Le script notify_telegram pointe-t-il toujours sur Node-RED ?
print("\n[3] Script notify_telegram — utilisé encore ?")
script_state = next((s for s in states if s['entity_id'] == 'script.notify_telegram'), None)
if script_state:
    attrs = script_state.get('attributes', {})
    print(f"  state: {script_state['state']}")
    print(f"  last_triggered: {attrs.get('last_triggered', '(jamais)')}")

# 4. Toute automation qui mentionne 'notify_telegram' ou 'telegram_bot' ?
print("\n[4] Automatisations actives référençant Telegram (non-unavailable)")
active_tg = [a for a in autos_tg if a['state'] != 'unavailable']
print(f"  {len(active_tg)} automatisation(s) ACTIVE(s) Telegram :")
for a in active_tg:
    print(f"  - {a['entity_id']} (state={a['state']})")
    last = a.get('attributes', {}).get('last_triggered', '(jamais)')
    print(f"      last_triggered: {last}")

# 5. Node-RED — Lister les addons HA et leur état
print("\n[5] Node-RED flows.json")
nodered_paths = [
    '/addon_configs/a0d7b954_nodered/flows.json',
    '/mnt/homeassistant/addon_configs/a0d7b954_nodered/flows.json',
    '/srv/nodered/data/flows.json',
]
nr_path = None
for p in nodered_paths:
    if os.path.exists(p):
        nr_path = p
        break

if nr_path:
    try:
        with open(nr_path) as f:
            flows = json.load(f)
        # Compter les nœuds telegram
        tg_nodes = [n for n in flows if 'telegram' in str(n).lower()]
        claude_nodes = [n for n in flows if 'claude' in str(n).lower() or 'anthropic' in str(n).lower()]
        print(f"  flows.json : {len(flows)} nœuds total")
        print(f"  Nœuds Telegram : {len(tg_nodes)}")
        print(f"  Nœuds Claude/Anthropic : {len(claude_nodes)}")
        # Lister les flows uniques
        flow_ids = set()
        for n in tg_nodes:
            if 'z' in n:
                flow_ids.add(n['z'])
        print(f"  Flows uniques contenant Telegram : {len(flow_ids)}")
    except Exception as e:
        print(f"  ❌ {e}")
else:
    print("  ❌ flows.json inaccessible depuis la VM")
    print("  (normal — Node-RED est un add-on sur HA Green)")

# 6. rest_command côté HA - voir si telegram_notify pointe encore sur localhost:1880 (Node-RED)
print("\n[6] rest_command.telegram_notify")
r = requests.get(f"{BASE}/api/services", headers=H, timeout=15, verify=False)
services = r.json()
for d in services:
    if d['domain'] == 'rest_command':
        for s_name in d['services'].keys():
            if 'telegram' in s_name.lower():
                print(f"  ✅ rest_command.{s_name}")

# 7. Voir le détail du flow Node-RED via l'API HA (peut-être pas accessible)
print("\n[7] Détection si Node-RED a un endpoint accessible")
try:
    rt = requests.get(f"{BASE}/api/states/sensor.nodered_status", headers=H, timeout=5, verify=False)
    if rt.status_code == 200:
        print(f"  sensor.nodered_status existe : {rt.json().get('state', '?')}")
except:
    pass
