#!/usr/bin/env python3
import json, requests
with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)
H = {'Authorization': 'Bearer ' + cfg['ha_token']}
BASE = cfg['ha_url']
states = requests.get(BASE + '/api/states', headers=H, timeout=15, verify=False).json()

# Chercher TOUT ce qui touche gmail/mail/imap
print('=== Entites gmail / mail / imap ===', flush=True)
for s in states:
    eid = s.get('entity_id','')
    fn = (s.get('attributes',{}) or {}).get('friendly_name','')
    if any(k in eid.lower() or k in fn.lower() for k in ['gmail','mail','imap','courrier','inbox']):
        print(f'  {eid} = {str(s.get("state"))[:40]} | {fn[:40]}', flush=True)
