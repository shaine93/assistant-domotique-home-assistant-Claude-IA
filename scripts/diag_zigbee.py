#!/usr/bin/env python3
import json, requests
with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)
try:
    r = requests.get(f"{cfg['ha_url']}/api/", 
                     headers={"Authorization": f"Bearer {cfg['ha_token']}"},
                     timeout=10, verify=False)
    print(f"GET /api/ : HTTP {r.status_code}")
    print(f"  Réponse : {r.json()}")
    
    r2 = requests.get(f"{cfg['ha_url']}/api/states",
                      headers={"Authorization": f"Bearer {cfg['ha_token']}"},
                      timeout=15, verify=False)
    states = r2.json()
    print(f"\nGET /api/states : HTTP {r2.status_code}")
    print(f"  {len(states)} entités récupérées")
    
    # Quelques entités clés pour confirmer que l'accès est bien fonctionnel
    cibles = ['sensor.ecojoko_consommation_temps_reel', 'switch.prise_ecojoko',
              'sensor.ecojoko_temperature_interieure', 'sensor.prise_anker_power']
    print("\n  Sondage entités clés :")
    for c in cibles:
        s = next((s for s in states if s['entity_id'] == c), None)
        if s:
            print(f"    ✅ {c} = {s['state']} (last_updated {s.get('last_updated','')[:19]})")
        else:
            print(f"    ⚠️ {c} : introuvable")
except Exception as e:
    print(f"❌ ERREUR : {e}")
