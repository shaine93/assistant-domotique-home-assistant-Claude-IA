#!/usr/bin/env python3
"""Audit Telegram complet : repérer les 2 bots, leurs usages."""
import json, requests
with open('/home/lolufe/assistant/config.json') as f:
    cfg = json.load(f)
H = {"Authorization": f"Bearer {cfg['ha_token']}"}
BASE = cfg['ha_url']

print("=" * 60)
print("AUDIT TELEGRAM — 2 bots ?")
print("=" * 60)

# 1. Token AssistantIA (vu côté VM)
tg_assistantia = cfg.get('telegram_token', '')
print(f"\n[1] Bot AssistantIA (côté VM)")
print(f"  Token: {tg_assistantia[:15]}...{tg_assistantia[-5:]}")
print(f"  Chat: {cfg.get('telegram_chat_id')}")

# 2. Services notify côté HA (chercher telegram_bot)
print(f"\n[2] Services notify HA")
r = requests.get(f"{BASE}/api/services", headers=H, timeout=15, verify=False)
services = r.json()
for d in services:
    if d['domain'] == 'notify':
        for s in d['services'].keys():
            if 'telegram' in s.lower():
                print(f"  ⭐ notify.{s} (service Telegram natif HA)")
            elif s in ('persistent_notification', 'notify', 'free'):
                pass
            else:
                pass  # ignorer autres notify
    # Chercher services telegram_bot.*
    if d['domain'] == 'telegram_bot':
        print(f"  🎯 Domain telegram_bot trouvé :")
        for s in d['services'].keys():
            print(f"      telegram_bot.{s}")

# 3. Intégrations HA
print(f"\n[3] Composants HA actifs avec 'telegram'")
r = requests.get(f"{BASE}/api/config", headers=H, timeout=15, verify=False)
components = r.json().get('components', [])
tg_comps = [c for c in components if 'telegram' in c.lower()]
for c in tg_comps:
    print(f"  ✅ {c}")
if not tg_comps:
    print("  (aucun)")

# 4. Entités HA telegram (déclencheurs / réponses)
print(f"\n[4] Entités HA liées à Telegram")
r = requests.get(f"{BASE}/api/states", headers=H, timeout=15, verify=False)
states = r.json()
tg_states = [s for s in states if 'telegram' in s['entity_id'].lower()]
print(f"  {len(tg_states)} entités")
for s in tg_states[:15]:
    print(f"    {s['entity_id']}: state={s.get('state', '?')[:50]}")

# 5. Lire automations.yaml pour repérer les automations qui utilisent telegram
print(f"\n[5] Automations HA qui utilisent Telegram")
try:
    with open('/homeassistant/automations.yaml') as f:
        autos_text = f.read()
    # Compter les utilisations
    n_telegram_bot = autos_text.count('telegram_bot.')
    n_notify_telegram = autos_text.count('notify.telegram')
    n_telegram_event = autos_text.count('telegram')
    print(f"  Mentions 'telegram_bot.' : {n_telegram_bot}")
    print(f"  Mentions 'notify.telegram' : {n_notify_telegram}")
    print(f"  Total mentions 'telegram' : {n_telegram_event}")
    
    # Extraire les noms d'automations qui touchent à telegram
    import re
    blocks = autos_text.split('\n- id:')
    matched_aliases = []
    for b in blocks:
        if 'telegram' in b.lower():
            m = re.search(r'alias:\s*(.+)', b)
            if m:
                matched_aliases.append(m.group(1).strip())
    print(f"  {len(matched_aliases)} automation(s) utilisent telegram :")
    for a in matched_aliases[:15]:
        print(f"    - {a}")
except FileNotFoundError:
    print("  ❌ /homeassistant/automations.yaml non accessible")
except Exception as e:
    print(f"  ❌ {e}")

# 6. Lire configuration.yaml pour repérer le telegram_bot intégration
print(f"\n[6] configuration.yaml — section telegram_bot")
try:
    with open('/homeassistant/configuration.yaml') as f:
        config_text = f.read()
    lines = config_text.split('\n')
    in_telegram = False
    capt = []
    for i, l in enumerate(lines):
        if 'telegram_bot:' in l or 'telegram:' in l:
            in_telegram = True
            capt.append((i+1, l))
        elif in_telegram and (l.startswith(' ') or l.startswith('\t') or l == ''):
            capt.append((i+1, l))
            if len(capt) > 30: break
        elif in_telegram and l and not l[0].isspace():
            break
    if capt:
        for ln, txt in capt:
            print(f"  L{ln}: {txt}")
    else:
        print("  (pas de section telegram trouvée)")
except FileNotFoundError:
    print("  ❌ /homeassistant/configuration.yaml non accessible directement")

# 7. Lire flows.json Node-RED si accessible
print(f"\n[7] Node-RED : flows.json")
import os
nodered_path = '/addon_configs/a0d7b954_nodered/flows.json'
if os.path.exists(nodered_path):
    try:
        with open(nodered_path) as f:
            flows_text = f.read()
        n_telegram = flows_text.count('telegram')
        print(f"  Mentions 'telegram' dans flows.json : {n_telegram}")
    except Exception as e:
        print(f"  ❌ {e}")
else:
    print(f"  ❌ {nodered_path} pas accessible depuis la VM")
