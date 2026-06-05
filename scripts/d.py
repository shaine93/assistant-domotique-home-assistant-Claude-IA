#!/usr/bin/env python3
import json, requests
with open("/home/lolufe/assistant/config.json") as f:
    cfg = json.load(f)
H = {"Authorization": "Bearer " + cfg["ha_token"], "Content-Type": "application/json"}
BASE = cfg["ha_url"]

# TEST 4 : sans channel custom, juste image + actions
payload = {
    "title": "TEST 4 - Sans channel",
    "message": "Notif simple avec image",
    "data": {
        "image": "/api/camera_proxy/camera.doorbell_repeater_74a8",
        "clickAction": "/lovelace/portail",
        "actions": [
            {"action": "URI", "title": "Voir le live", "uri": "/lovelace/portail"}
        ]
    }
}
r = requests.post(BASE + "/api/services/notify/mobile_app_22081212ug",
                  headers=H, json=payload, timeout=15, verify=False)
print("TEST 4:", r.status_code, r.text[:200])
