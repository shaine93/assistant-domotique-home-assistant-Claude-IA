#!/usr/bin/env python3
import json, requests, websocket
with open('/home/lolufe/assistant/config.json') as f:
    cfg = json.load(f)
TOKEN = cfg['ha_token']
BASE = cfg['ha_url']

# Utiliser l'API WebSocket pour avoir accès au device_registry et config_entries
WS_URL = BASE.replace('https://', 'wss://').replace('http://', 'ws://') + '/api/websocket'

try:
    ws = websocket.create_connection(WS_URL, timeout=15, sslopt={'cert_reqs': 0})
    # Auth
    ws.recv()  # auth_required
    ws.send(json.dumps({'type': 'auth', 'access_token': TOKEN}))
    auth_ok = json.loads(ws.recv())
    print('Auth:', auth_ok.get('type'))
    
    # Get config entries
    ws.send(json.dumps({'id': 1, 'type': 'config_entries/get'}))
    res = json.loads(ws.recv())
    entries = res.get('result', [])
    print('\n=== Config entries mobile_app ===')
    for e in entries:
        if e.get('domain') == 'mobile_app':
            print(f"entry_id: {e.get('entry_id')}")
            print(f"  title: {e.get('title')}")
            print(f"  state: {e.get('state')}")
            print(f"  disabled_by: {e.get('disabled_by')}")
            print()
    ws.close()
except Exception as e:
    print('ERR:', type(e).__name__, e)
