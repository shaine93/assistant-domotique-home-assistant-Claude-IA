#!/usr/bin/env python3
"""Lister toutes les statistic_ids HA via l'API WebSocket."""
import json, asyncio, websockets, ssl

async def main():
    with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)
    
    # Construire l'URL WebSocket
    base = cfg['ha_url'].replace('https://', 'wss://').replace('http://', 'ws://')
    ws_url = f"{base}/api/websocket"
    
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    
    try:
        async with websockets.connect(ws_url, ssl=ssl_ctx) as ws:
            # Auth phase
            hello = json.loads(await ws.recv())
            print(f"Hello: {hello.get('type')}")
            
            await ws.send(json.dumps({"type": "auth", "access_token": cfg['ha_token']}))
            auth = json.loads(await ws.recv())
            print(f"Auth: {auth.get('type')}")
            
            if auth.get('type') != 'auth_ok':
                print(f"  Auth failed: {auth}")
                return
            
            # Demander la liste des statistic_ids
            await ws.send(json.dumps({
                "id": 1,
                "type": "recorder/list_statistic_ids"
            }))
            resp = json.loads(await ws.recv())
            
            if resp.get('success'):
                stats = resp.get('result', [])
                print(f"\n=== {len(stats)} statistic_ids dans HA ===\n")
                
                # Filtrer ceux liés à linky
                linky_stats = [s for s in stats if 'linky' in str(s).lower()]
                print(f"--- {len(linky_stats)} statistic_ids contenant 'linky' ---")
                for s in linky_stats:
                    print(f"\n  statistic_id: {s.get('statistic_id')}")
                    print(f"    name: {s.get('name')}")
                    print(f"    source: {s.get('source')}")
                    print(f"    statistics_unit: {s.get('statistics_unit_of_measurement')}")
                    print(f"    has_mean: {s.get('has_mean')}")
                    print(f"    has_sum: {s.get('has_sum')}")
                    print(f"    unit_class: {s.get('unit_class')}")
            else:
                print(f"Erreur: {resp}")
    except Exception as e:
        print(f"Erreur WS: {e}")

asyncio.run(main())
