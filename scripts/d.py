#!/usr/bin/env python3
import json, requests
with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)
H = {'Authorization': 'Bearer ' + cfg['ha_token']}
BASE = cfg['ha_url']

# REST DELETE /api/config/config_entries/entry/{entry_id}
url = BASE + '/api/config/config_entries/entry/01KBQTSBQWM2QWFKG6612VFG90'
r = requests.delete(url, headers=H, timeout=15, verify=False)
print('DELETE:', r.status_code, r.text[:300], flush=True)

# Verification
import time; time.sleep(2)
r2 = requests.get(BASE + '/api/states/sensor.waze_travel_time', headers=H, timeout=10, verify=False)
print()
print('sensor.waze_travel_time:', r2.status_code, flush=True)
if r2.status_code == 200:
    print('  state =', r2.json().get('state'), flush=True)
else:
    print('  SUPPRIME (HTTP', r2.status_code, ')', flush=True)
