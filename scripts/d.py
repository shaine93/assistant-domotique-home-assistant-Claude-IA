#!/usr/bin/env python3
import json, requests
with open('/home/lolufe/assistant/config.json') as f:
    cfg = json.load(f)
H = {'Authorization': 'Bearer ' + cfg['ha_token'], 'Content-Type': 'application/json'}
BASE = cfg['ha_url']

r = requests.get(BASE + '/api/states/automation.sonnette_g410_popup_mac_notif_xiaomi',
                 headers=H, timeout=10, verify=False)
auto_id = r.json().get('attributes', {}).get('id')

# Memes parametres notif, mais pour les 2 telephones en parallele
notif_data = {
    'title': 'Sonnette - Quelqu un est a la porte',
    'message': 'Cliquez pour voir le live',
    'data': {
        'priority': 'high',
        'ttl': 0,
        'tag': 'doorbell_g410',
        'image': '/api/camera_proxy/camera.doorbell_repeater_74a8',
        'sticky': 'true',
        'color': 'red',
        'notification_icon': 'mdi:doorbell-video',
        'clickAction': '/lovelace/portail',
        'actions': [{'action': 'URI', 'title': 'Voir le live', 'uri': '/lovelace/portail'}]
    }
}

new_auto = {
    'id': auto_id,
    'alias': 'Sonnette G410 - Popup Mac + Notif Xiaomi + Redmi',
    'description': 'Popup full-screen WebRTC Mac + notif Xiaomi Philippe + notif Redmi Michele',
    'triggers': [{
        'entity_id': 'event.doorbell_repeater_74a8_video_doorbell',
        'not_from': ['unavailable', 'unknown'],
        'not_to': ['unavailable', 'unknown'],
        'trigger': 'state'
    }],
    'conditions': [{
        'condition': 'template',
        'value_template': '{{ this.attributes.last_triggered is none or (now() - this.attributes.last_triggered).total_seconds() > 30 }}'
    }],
    'actions': [
        # 1. Popup Mac full-screen
        {
            'action': 'browser_mod.popup',
            'data': {
                'browser_id': ['Mac_Philippe'],
                'title': 'Quelqu un sonne a la porte',
                'size': 'fullscreen',
                'timeout': 90000,
                'style': '--ha-card-background: black; --primary-background-color: black;',
                'content': {
                    'type': 'custom:webrtc-camera',
                    'url': 'sonnette',
                    'mode': 'webrtc',
                    'media': 'video,audio,microphone',
                    'muted': False,
                    'ui': True,
                    'intersection': 0.1,
                    'background': True,
                    'style': 'video { object-fit: contain !important; height: 100vh !important; width: 100% !important; }'
                }
            }
        },
        # 2. Notif Xiaomi Philippe (22081212ug)
        {
            'action': 'notify.mobile_app_22081212ug',
            'data': notif_data
        },
        # 3. Notif Redmi Michele (22101316g)
        {
            'action': 'notify.mobile_app_22101316g',
            'data': notif_data
        }
    ],
    'mode': 'single',
    'max_exceeded': 'silent'
}

r2 = requests.post(BASE + '/api/config/automation/config/' + auto_id,
                   headers=H, json=new_auto, timeout=15, verify=False)
print('UPDATE:', r2.status_code, flush=True)
r3 = requests.post(BASE + '/api/services/automation/reload', headers=H, json={}, timeout=10, verify=False)
print('Reload:', r3.status_code, flush=True)

import time
time.sleep(2)
r4 = requests.post(BASE + '/api/services/automation/trigger',
                   headers=H,
                   json={'entity_id': 'automation.sonnette_g410_popup_mac_notif_xiaomi', 'skip_condition': True},
                   timeout=10, verify=False)
print('Trigger:', r4.status_code, flush=True)
