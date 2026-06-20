# -*- coding: utf-8 -*-
"""
Sonnette Video - module d'envoi FCM (isole, defensif).

v3 : - detection TEMPS REEL via WebSocket HA (push),
     - REGISTRE MULTI-TOKENS persistant (plusieurs telephones sonnent),
     - PURGE auto des tokens morts (404/UNREGISTERED) + ALERTE Telegram,
     - jeton OAuth Google en cache.
Repli polling si websocket-client absent. Ne doit JAMAIS faire tomber l'agent.
"""
import os
import sys
import ssl
import json
import time
import logging
import threading
from datetime import datetime, timezone

log = logging.getLogger("sonnette_video")

APP_DIR        = "/home/lolufe/assistant"
VENDOR_DIR     = os.path.join(APP_DIR, "vendor")
CONFIG_JSON    = os.path.join(APP_DIR, "config.json")
REGISTRY_PATH  = os.path.join(APP_DIR, "sonnette_tokens.json")
SA_PATH        = "/home/lolufe/home-assistant-305916-1aeaefc37ef0.json"
PROJECT_ID     = "home-assistant-305916"
DOORBELL_EVENT = "event.doorbell_repeater_74a8_video_doorbell"
CAMERA_ENTITY  = "camera.doorbell_repeater_74a8"
TOKEN_ENTITY   = "input_text.sonnette_fcm_token"
FCM_SCOPE      = "https://www.googleapis.com/auth/firebase.messaging"
POLL_SEC       = 3

if VENDOR_DIR not in sys.path:
    sys.path.insert(0, VENDOR_DIR)

_creds = None
_session = None
_reg_lock = threading.Lock()


def _load_ha():
    with open(CONFIG_JSON) as f:
        cfg = json.load(f)
    return cfg.get("ha_url", "").rstrip("/"), cfg.get("ha_token", "")


def _http():
    global _session
    if _session is None:
        import requests
        try: requests.packages.urllib3.disable_warnings()
        except Exception: pass
        _session = requests.Session()
    return _session


# ---------- Registre multi-tokens (fichier JSON persistant) ----------

def _load_registry():
    try:
        with open(REGISTRY_PATH) as f:
            d = json.load(f)
            return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def _save_registry(reg):
    try:
        tmp = REGISTRY_PATH + ".tmp"
        with open(tmp, "w") as f:
            json.dump(reg, f)
        os.replace(tmp, REGISTRY_PATH)
    except Exception as e:
        log.warning("Sonnette Video: sauvegarde registre KO: %s", str(e)[:100])


MAX_PHONES = 10
MAX_LABEL = 40
MAX_TOKEN = 4096


def _clean_label(s):
    s = "".join(ch for ch in (s or "") if ch.isprintable() and ch not in "\n\r\t")
    return s.strip()[:MAX_LABEL] or "telephone"


def _register_raw(raw):
    """raw = 'label|token' ou 'token' (retrocompat). Ajoute/maj dans le registre.
    Securise : label nettoye+borne, token borne, registre plafonne (anti-abus)."""
    if not raw or raw in ("unknown", "unavailable"):
        return
    raw = raw.strip()
    if "|" in raw:
        label, token = raw.split("|", 1)
    else:
        label, token = "telephone", raw
    label = _clean_label(label)
    token = token.strip()
    if not (20 <= len(token) <= MAX_TOKEN):
        return
    with _reg_lock:
        reg = _load_registry()
        if token not in reg and len(reg) >= MAX_PHONES:
            log.warning("Sonnette Video: registre plein (%d) - enregistrement ignore (%s)",
                        MAX_PHONES, label)
            return
        existed = token in reg
        reg[token] = {"label": label,
                      "added": reg.get(token, {}).get("added", datetime.now().isoformat()),
                      "last_seen": datetime.now().isoformat()}
        _save_registry(reg)
    if not existed:
        log.info("Sonnette Video: nouveau telephone enregistre (%s) - total %d", label, len(reg))


def _seed_registry(ha_url, ha_tok):
    """Au demarrage : recupere le token courant dans HA et l'ajoute au registre."""
    try:
        raw = (_ha_state(ha_url, ha_tok, TOKEN_ENTITY).get("state") or "").strip()
        _register_raw(raw)
    except Exception:
        pass


# ---------- OAuth Google (cache) ----------

def _get_access_token():
    global _creds
    from google.oauth2 import service_account
    import google.auth.transport.requests as gtr
    if _creds is None:
        _creds = service_account.Credentials.from_service_account_file(SA_PATH, scopes=[FCM_SCOPE])
    if not _creds.valid:
        _creds.refresh(gtr.Request())
    return _creds.token


# ---------- HA + FCM ----------

def _ha_state(ha_url, ha_tok, entity):
    r = _http().get(ha_url + "/api/states/" + entity,
                    headers={"Authorization": "Bearer " + ha_tok}, verify=False, timeout=10)
    r.raise_for_status()
    return r.json()


def _send_fcm_to(token, title, image_url):
    access = _get_access_token()
    payload = {"message": {
        "token": token,
        "android": {"priority": "HIGH"},
        "data": {"type": "ring", "call_id": str(int(time.time())),
                 "title": title, "image_url": image_url or ""},
    }}
    r = _http().post(
        "https://fcm.googleapis.com/v1/projects/%s/messages:send" % PROJECT_ID,
        headers={"Authorization": "Bearer " + access, "Content-Type": "application/json"},
        data=json.dumps(payload), timeout=15)
    return r.status_code, r.text


def _is_dead_token(code, body):
    if code == 404:
        return True
    b = (body or "").upper()
    return any(s in b for s in ("UNREGISTERED", "NOT_FOUND", "INVALID_ARGUMENT",
                                "REGISTRATION-TOKEN-NOT-REGISTERED"))


def _alert(text):
    try:
        import shared
        shared.telegram_send(text, force=True)
        return
    except Exception:
        pass
    try:
        cfg = json.load(open(CONFIG_JSON))
        tok, chat = cfg.get("telegram_token"), cfg.get("telegram_chat_id")
        if tok and chat:
            _http().post("https://api.telegram.org/bot%s/sendMessage" % tok,
                         data={"chat_id": chat, "text": text}, timeout=10)
    except Exception as e:
        log.warning("Sonnette Video: alerte Telegram KO: %s", str(e)[:100])


def _is_recent(s, max_age=90):
    """Vrai si l'horodatage ISO est dans les max_age dernieres secondes."""
    try:
        dt = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - dt).total_seconds()
        return -15 <= age <= max_age
    except Exception:
        return False


def _real_press(from_s, to_s):
    """Vrai appui = transition depuis un etat VALIDE vers un horodatage RECENT et different.
    Bloque les fausses sonneries au redemarrage de HA (restauration depuis 'unavailable')."""
    if from_s in (None, "", "unknown", "unavailable"):
        return False
    if not to_s or to_s in ("unknown", "unavailable") or to_s == from_s:
        return False
    return _is_recent(to_s)


def _on_ring():
    try:
        ha_url, ha_tok = _load_ha()
    except Exception as e:
        log.warning("Sonnette Video: config KO: %s", str(e)[:100]); return

    reg = _load_registry()
    if not reg:
        log.warning("Sonnette Video: APPUI mais aucun telephone enregistre - push ignore")
        _alert("\U0001F6A8 SONNETTE : quelqu'un a sonne mais AUCUN telephone n'est enregistre. "
               "Rouvre l'app Sonnette Video sur le telephone pour la reactiver.")
        return

    image_url = ""
    try:
        at = _ha_state(ha_url, ha_tok, CAMERA_ENTITY).get("attributes", {}).get("access_token", "")
        if at:
            image_url = "%s/api/camera_proxy/%s?token=%s" % (ha_url, CAMERA_ENTITY, at)
    except Exception:
        pass

    ok, dead = 0, []
    for token, meta in list(reg.items()):
        try:
            code, body = _send_fcm_to(token, "Quelqu'un sonne a la porte", image_url)
            if 200 <= code < 300:
                ok += 1
            elif _is_dead_token(code, body):
                dead.append((token, meta.get("label", "telephone")))
            else:
                log.warning("Sonnette Video: push refuse %s (%s): %s",
                            code, meta.get("label"), (body or "")[:160])
        except Exception as e:
            log.warning("Sonnette Video: envoi KO (%s): %s", meta.get("label"), str(e)[:120])

    if dead:
        with _reg_lock:
            reg2 = _load_registry()
            for token, _label in dead:
                reg2.pop(token, None)
            _save_registry(reg2)
        labels = ", ".join(sorted({l for _, l in dead}))
        _alert("⚠️ Sonnette : le(s) telephone(s) [%s] ne recoivent plus les notifications "
               "(token expire). Rouvre l'app Sonnette Video dessus pour le reactiver." % labels)
        log.warning("Sonnette Video: %d token(s) mort(s) purge(s): %s", len(dead), labels)

    if ok == 0:
        _alert("\U0001F6A8 SONNETTE : quelqu'un a sonne mais le push n'a atteint AUCUN "
               "telephone (%d enregistre(s)). Verifie l'app et la connexion du telephone." % len(reg))
    log.info("Sonnette Video: APPUI -> push envoye a %d/%d telephone(s)", ok, len(reg))


# ---------- Surveillance proactive (liveness quotidien) ----------

def _validate_token(token):
    """Test FCM 'validate_only' : verifie la validite du token SANS notifier."""
    access = _get_access_token()
    payload = {"validate_only": True,
               "message": {"token": token, "data": {"type": "ping"}}}
    r = _http().post(
        "https://fcm.googleapis.com/v1/projects/%s/messages:send" % PROJECT_ID,
        headers={"Authorization": "Bearer " + access, "Content-Type": "application/json"},
        data=json.dumps(payload), timeout=15)
    return r.status_code, r.text


def _liveness_loop():
    """Une fois par jour : verifie que chaque telephone est toujours joignable et
    ALERTE Telegram si un token est mort ou si le registre est vide. Ne purge PAS
    (pour ne jamais retirer par erreur le telephone de Michele) : la purge reelle
    reste reactive, au moment d'une vraie sonnerie."""
    time.sleep(180)
    while True:
        try:
            reg = _load_registry()
            if not reg:
                _alert("\u26A0\uFE0F Sonnette : AUCUN telephone enregistre. La sonnette ne "
                       "previendra personne. Rouvre l'app Sonnette Video sur le telephone.")
            else:
                dead = []
                for token, meta in list(reg.items()):
                    try:
                        code, body = _validate_token(token)
                        if _is_dead_token(code, body):
                            dead.append(meta.get("label", "telephone"))
                    except Exception:
                        pass  # erreur reseau ponctuelle : on n'alerte pas a tort
                if dead:
                    labels = ", ".join(sorted(set(dead)))
                    _alert("\u26A0\uFE0F Sonnette : le(s) telephone(s) [%s] ne semblent plus "
                           "joignables (token expire). Rouvre l'app Sonnette Video dessus pour "
                           "garantir la sonnerie." % labels)
                    log.warning("Sonnette Video: liveness - token(s) suspect(s): %s", labels)
                else:
                    log.info("Sonnette Video: liveness OK - %d telephone(s) joignable(s)", len(reg))
        except Exception as e:
            log.warning("Sonnette Video: liveness KO: %s", str(e)[:120])
        time.sleep(24 * 3600)


# ---------- Temps reel : WebSocket ----------

def _ws_loop():
    import websocket
    backoff = 2
    log.info("Sonnette Video: mode WebSocket (push temps reel, multi-tokens)")
    while True:
        ws = None
        try:
            ha_url, ha_tok = _load_ha()
            _seed_registry(ha_url, ha_tok)
            wss = ha_url.replace("https://", "wss://").replace("http://", "ws://") + "/api/websocket"
            ws = websocket.create_connection(wss, sslopt={"cert_reqs": ssl.CERT_NONE}, timeout=20)
            ws.settimeout(75)
            ws.recv()  # auth_required
            ws.send(json.dumps({"type": "auth", "access_token": ha_tok}))
            if json.loads(ws.recv()).get("type") != "auth_ok":
                raise RuntimeError("auth refusee")
            # 1 = sonnerie, 2 = enregistrement d'un token
            ws.send(json.dumps({"id": 1, "type": "subscribe_trigger",
                                "trigger": {"platform": "state", "entity_id": DOORBELL_EVENT}}))
            ws.recv()
            ws.send(json.dumps({"id": 2, "type": "subscribe_trigger",
                                "trigger": {"platform": "state", "entity_id": TOKEN_ENTITY}}))
            ws.recv()
            log.info("Sonnette Video: WebSocket connecte + abonne (sonnerie + enregistrement)")
            backoff = 2
            ping_id = 100
            while True:
                try:
                    raw = ws.recv()
                except websocket.WebSocketTimeoutException:
                    ping_id += 1
                    ws.send(json.dumps({"id": ping_id, "type": "ping"}))
                    continue
                if not raw:
                    raise RuntimeError("connexion fermee")
                msg = json.loads(raw)
                if msg.get("type") != "event":
                    continue
                tr = msg.get("event", {}).get("variables", {}).get("trigger", {})
                to_s = (tr.get("to_state") or {}).get("state")
                from_s = (tr.get("from_state") or {}).get("state")
                if msg.get("id") == 1:
                    if _real_press(from_s, to_s):
                        _on_ring()
                    else:
                        log.info("Sonnette Video: changement ignore (pas un vrai appui: %s -> %s)",
                                 from_s, str(to_s)[:25])
                elif msg.get("id") == 2:
                    _register_raw(to_s)
        except Exception as e:
            log.warning("Sonnette Video: WS interrompu (%s) - reconnexion dans %ss", str(e)[:90], backoff)
        finally:
            try:
                if ws: ws.close()
            except Exception:
                pass
        time.sleep(backoff)
        backoff = min(backoff * 2, 30)


# ---------- Repli : polling ----------

def _poll_loop():
    log.info("Sonnette Video: repli polling %ss (multi-tokens)", POLL_SEC)
    last_ring = None
    last_tok = None
    errors = 0
    while True:
        try:
            ha_url, ha_tok = _load_ha()
            ev = _ha_state(ha_url, ha_tok, DOORBELL_EVENT).get("state")
            if ev not in (None, "", "unknown", "unavailable"):
                if last_ring is None:
                    last_ring = ev
                elif ev != last_ring:
                    last_ring = ev
                    if _is_recent(ev):
                        _on_ring()
            tok = (_ha_state(ha_url, ha_tok, TOKEN_ENTITY).get("state") or "").strip()
            if tok and tok != last_tok:
                last_tok = tok
                _register_raw(tok)
            errors = 0
        except Exception as e:
            errors += 1
            if errors <= 3 or errors % 40 == 0:
                log.warning("Sonnette Video: poll err (%d): %s", errors, str(e)[:120])
        time.sleep(POLL_SEC)


def _run():
    try:
        import websocket  # noqa: F401
    except Exception:
        log.warning("Sonnette Video: websocket-client absent -> repli polling")
        _poll_loop(); return
    try:
        _ws_loop()
    except Exception as e:
        log.warning("Sonnette Video: WS indisponible (%s) -> repli polling", str(e)[:120])
        _poll_loop()


_started = False


def start():
    global _started
    if _started:
        return
    _started = True
    threading.Thread(target=_run, name="sonnette_video", daemon=True).start()
    threading.Thread(target=_liveness_loop, name="sonnette_liveness", daemon=True).start()
    log.info("Sonnette Video: thread demarre (+ surveillance proactive)")
