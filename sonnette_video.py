# -*- coding: utf-8 -*-
"""
Sonnette Video — module d'envoi FCM (isole, defensif).
Surveille l'appui sonnette dans Home Assistant et envoie un push FCM HTTP v1
a l'app Sonnette Video (message DATA priorite haute => ecran d'appel CallStyle).

Concu pour ne JAMAIS faire tomber l'agent principal :
- demarre dans un thread daemon,
- tout est encapsule dans des try/except,
- ne touche a aucun etat de l'assistant, lit seulement config.json + HA.
"""
import os
import sys
import json
import time
import logging
import threading

log = logging.getLogger("sonnette_video")

# --- Constantes (specifiques a l'installation de Philippe) ---
APP_DIR        = "/home/lolufe/assistant"
VENDOR_DIR     = os.path.join(APP_DIR, "vendor")
CONFIG_JSON    = os.path.join(APP_DIR, "config.json")
SA_PATH        = "/home/lolufe/home-assistant-305916-1aeaefc37ef0.json"
PROJECT_ID     = "home-assistant-305916"
DOORBELL_EVENT = "event.doorbell_repeater_74a8_video_doorbell"
CAMERA_ENTITY  = "camera.doorbell_repeater_74a8"
TOKEN_ENTITY   = "input_text.sonnette_fcm_token"
FCM_SCOPE      = "https://www.googleapis.com/auth/firebase.messaging"
POLL_SEC       = 3

if VENDOR_DIR not in sys.path:
    sys.path.insert(0, VENDOR_DIR)


def _load_ha():
    with open(CONFIG_JSON) as f:
        cfg = json.load(f)
    return cfg.get("ha_url", "").rstrip("/"), cfg.get("ha_token", "")


def _get_access_token():
    """Mint d'un jeton OAuth2 court via le compte de service (google-auth vendored)."""
    from google.oauth2 import service_account
    import google.auth.transport.requests as gtr
    creds = service_account.Credentials.from_service_account_file(SA_PATH, scopes=[FCM_SCOPE])
    creds.refresh(gtr.Request())
    return creds.token


def _ha_state(session, ha_url, ha_tok, entity):
    r = session.get(
        ha_url + "/api/states/" + entity,
        headers={"Authorization": "Bearer " + ha_tok},
        verify=False, timeout=10,
    )
    r.raise_for_status()
    return r.json()


def _send_fcm(session, device_token, title, image_url):
    access = _get_access_token()
    payload = {
        "message": {
            "token": device_token,
            "android": {"priority": "HIGH"},
            "data": {
                "type": "ring",
                "call_id": str(int(time.time())),
                "title": title,
                "image_url": image_url or "",
            },
        }
    }
    r = session.post(
        "https://fcm.googleapis.com/v1/projects/%s/messages:send" % PROJECT_ID,
        headers={"Authorization": "Bearer " + access, "Content-Type": "application/json"},
        data=json.dumps(payload), timeout=15,
    )
    return r.status_code, r.text[:300]


def _loop():
    import requests
    try:
        requests.packages.urllib3.disable_warnings()
    except Exception:
        pass
    session = requests.Session()

    last_state = None
    errors = 0
    log.info("Sonnette Video: surveillance active (poll %ss)", POLL_SEC)

    while True:
        try:
            ha_url, ha_tok = _load_ha()
            ev = _ha_state(session, ha_url, ha_tok, DOORBELL_EVENT)
            state = ev.get("state")

            if state in (None, "", "unknown", "unavailable"):
                pass  # etat invalide transitoire : on ne touche pas a last_state
            elif last_state is None:
                last_state = state  # init : pas de declenchement au demarrage
            elif state != last_state:
                last_state = state
                _on_ring(session, ha_url, ha_tok)

            errors = 0
        except Exception as e:
            errors += 1
            if errors <= 3 or errors % 40 == 0:  # anti-spam des logs en cas de coupure reseau
                log.warning("Sonnette Video: boucle err (%d): %s", errors, str(e)[:140])
        time.sleep(POLL_SEC)


def _on_ring(session, ha_url, ha_tok):
    try:
        tok_state = _ha_state(session, ha_url, ha_tok, TOKEN_ENTITY)
        device_token = (tok_state.get("state") or "").strip()
    except Exception as e:
        log.warning("Sonnette Video: lecture token KO: %s", str(e)[:120])
        return

    if not device_token or device_token in ("unknown", "unavailable"):
        log.warning("Sonnette Video: APPUI detecte mais aucun token FCM enregistre — push ignore")
        return

    image_url = ""
    try:
        cam = _ha_state(session, ha_url, ha_tok, CAMERA_ENTITY)
        at = cam.get("attributes", {}).get("access_token", "")
        if at:
            image_url = "%s/api/camera_proxy/%s?token=%s" % (ha_url, CAMERA_ENTITY, at)
    except Exception:
        pass

    try:
        code, body = _send_fcm(session, device_token, "Quelqu'un sonne a la porte", image_url)
        if 200 <= code < 300:
            log.info("Sonnette Video: APPUI -> push FCM OK (%s)", code)
        else:
            log.warning("Sonnette Video: push FCM refuse %s: %s", code, body)
    except Exception as e:
        log.warning("Sonnette Video: envoi FCM KO: %s", str(e)[:200])


_started = False


def start():
    """Demarre la surveillance dans un thread daemon. Idempotent et sans risque."""
    global _started
    if _started:
        return
    _started = True
    t = threading.Thread(target=_loop, name="sonnette_video", daemon=True)
    t.start()
    log.info("Sonnette Video: thread demarre")
