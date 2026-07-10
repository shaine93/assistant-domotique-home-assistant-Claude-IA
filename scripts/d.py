#!/usr/bin/env python3
import json, requests, time
with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)
H = {'Authorization': 'Bearer ' + cfg['ha_token']}
BASE = cfg['ha_url']
states = None
for a in range(5):
    try:
        states = requests.get(BASE + '/api/states', headers=H, timeout=15, verify=False).json()
        break
    except Exception:
        time.sleep(4)
print('=== Sensor IMAP mails non lus ===', flush=True)
for s in states:
    eid = s.get('entity_id','')
    fn = (s.get('attributes',{}) or {}).get('friendly_name','')
    if 'imap' in eid.lower() or 'unread' in eid.lower() or 'imap' in fn.lower():
        print(f'  {eid} = {s.get("state")} mails non lus | {fn}', flush=True)
