#!/usr/bin/env python3
import json, requests, time
with open('/home/lolufe/assistant/config.json') as f: cfg = json.load(f)

def snap():
    r = requests.get(f"{cfg['ha_url']}/api/states",
                     headers={"Authorization": f"Bearer {cfg['ha_token']}"},
                     timeout=15, verify=False)
    states = r.json()
    # Tous les sensors/switch ecojoko
    eco = {s['entity_id']: s for s in states 
           if 'ecojoko' in s['entity_id'].lower()}
    return eco

print("═══ T=0 : snapshot initial ═══")
snap1 = snap()
for eid in sorted(snap1.keys()):
    s = snap1[eid]
    state = s['state']
    last_upd = s.get('last_updated', '')[:19]
    last_chg = s.get('last_changed', '')[:19]
    print(f"  {eid:55s} state={state:12s}  last_upd={last_upd}  last_chg={last_chg}")

print("\n⏳ Attente 60 secondes...")
time.sleep(60)

print("\n═══ T=60 : snapshot après 60s ═══")
snap2 = snap()

print("\n═══ DIFF (état figé vs frais) ═══")
all_frozen = True
for eid in sorted(snap1.keys()):
    s1 = snap1[eid]
    s2 = snap2.get(eid)
    if not s2:
        print(f"  {eid:55s}  ❌ DISPARU au T=60")
        continue
    
    upd1 = s1.get('last_updated', '')
    upd2 = s2.get('last_updated', '')
    state1 = s1['state']
    state2 = s2['state']
    
    if upd1 == upd2:
        # Pas mis à jour pendant 60s — possible mais pas concluant 
        # (ex: température ne change pas à la seconde près)
        marker = "🟡 figé"
    else:
        marker = "🟢 frais"
        all_frozen = False
    
    print(f"  {marker}  {eid:55s}  T0_upd={upd1[:19]} T60_upd={upd2[:19]}  state {state1}->{state2}")

print()
if all_frozen:
    print("⚠️  TOUS les sensors Ecojoko sont FIGÉS sur 60 secondes.")
    print("   Cela suggère que le boîtier ne pousse plus de données fraîches.")
    print("   Mais 60s peut être insuffisant pour des sensors lents (température, humidité).")
    print("   Le sensor critique 'consommation_temps_reel' DEVRAIT bouger en quelques secondes.")
else:
    print("✅ Au moins un sensor a été mis à jour. Le boîtier répond.")

# Cas critique : sensor.ecojoko_consommation_temps_reel doit bouger en quelques secondes
crit = "sensor.ecojoko_consommation_temps_reel"
if crit in snap1 and crit in snap2:
    upd1 = snap1[crit].get('last_updated', '')
    upd2 = snap2[crit].get('last_updated', '')
    if upd1 == upd2:
        print(f"\n❌ {crit} : last_updated IDENTIQUE en 60s → bo\u00eetier probablement DÉBRANCHÉ")
    else:
        from datetime import datetime
        try:
            dt1 = datetime.fromisoformat(upd1.replace("Z","+00:00"))
            dt2 = datetime.fromisoformat(upd2.replace("Z","+00:00"))
            delta = (dt2 - dt1).total_seconds()
            print(f"\n✅ {crit} : last_updated avance de {delta:.0f}s → boîtier actif")
        except Exception:
            print(f"\n✅ {crit} : changement détecté")
