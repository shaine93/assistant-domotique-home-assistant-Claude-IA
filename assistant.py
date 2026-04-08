#!/usr/bin/env python3
import shutil as _shutil, os as _os
_cache = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "__pycache__")
if _os.path.exists(_cache): _shutil.rmtree(_cache, ignore_errors=True)

# =============================================================================
# ASSISTANT.PY — main(), threads, startup, wizard
# =============================================================================

from skills import *
from skills import _lancer_questionnaire_appareils, _lancer_questionnaire_foyer, _verifier_watches
from shared import (_wizard_step, _wizard_save_config, _is_authorized_chat, transcrire_vocal,
    _etat_prises, _grace_fin, _puissances_historique, _derniere_phase_haute,
    _rappel_linge_envoye, _defroissage_detecte, _watchdog, _entites_deja_detectees,
    _prises_snapshot, _coupure_edf_alertee, _snapshot_valide)
import shared

# Stdlib AFTER wildcard
import json, os, re, requests, sqlite3, smtplib, time, threading, anthropic
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText


def backup_sqlite():
    while True:
        now = datetime.now()
        if now.hour == 2 and now.minute == 0:
            ok = envoyer_email(
                f"[AssistantIA] Backup memory.db — {now.strftime('%d/%m/%Y')}",
                f"Backup automatique. Date: {now.isoformat()}",
                piece_jointe=DB_PATH
            )
            if not ok:
                telegram_send("⚠️ BACKUP SQLite — ÉCHEC email")
            time.sleep(61)
        time.sleep(30)


def keepalive():
    while True:
        with open(""+os.path.join(BASE_DIR,"keepalive.log", "a") as f:
            f.write(f"{datetime.now().isoformat()} keepalive\n")
        try:
            with open(""+os.path.join(BASE_DIR,"keepalive.log", "r") as f:
                lignes = f.readlines()
            if len(lignes) > 500:
                with open(""+os.path.join(BASE_DIR,"keepalive.log", "w") as f:
                    f.writelines(lignes[-200:])
        except Exception:
            pass
        time.sleep(3600)


def _wizard_handle_message(texte):
    """Traite un message pendant le wizard. Retourne True si consommé."""
    global CFG
    step = _wizard_step()
    if not step:
        return False

    texte = texte.strip()

    # ═══ ÉTAPE 1 : URL Home Assistant ═══
    if step == "ha_url":
        url = texte.rstrip("/")
        if not url.startswith("http"):
            url = "http://" + url
        if ":" not in url.split("//", 1)[-1] and "duckdns" not in url and ".local" not in url:
            url += ":8123"

        # Test de connexion
        try:
            r = requests.get(f"{url}/api/", timeout=10, verify=False)
            if r.status_code == 401:
                # HA accessible mais token requis = OK
                shared.CFG["ha_url"] = url
                shared.CFG["_wizard_step"] = "ha_token"
                _wizard_save_config()
                telegram_send(
                    f"✅ Home Assistant trouvé : {url}\n\n"
                    f"📡 ÉTAPE 2/3 — Token d'accès\n"
                    f"Créez un token longue durée dans HA :\n"
                    f"  Profil → Tokens d'accès longue durée → Créer un token\n\n"
                    f"Envoyez-moi le token (commence par eyJ...)"
                )
                return True
            elif r.status_code == 200:
                data = r.json()
                if data.get("message") == "API running.":
                    # API ouverte sans auth (rare)
                    shared.CFG["ha_url"] = url
                    shared.CFG["_wizard_step"] = "ha_token"
                    _wizard_save_config()
                    telegram_send(
                        f"✅ Home Assistant accessible : {url}\n\n"
                        f"📡 ÉTAPE 2/3 — Token d'accès\n"
                        f"Envoyez-moi votre token HA longue durée (eyJ...)"
                    )
                    return True
        except requests.exceptions.SSLError:
            # HTTPS avec certificat auto-signé
            shared.CFG["ha_url"] = url
            shared.CFG["_wizard_step"] = "ha_token"
            _wizard_save_config()
            telegram_send(
                f"✅ Home Assistant trouvé : {url} (SSL auto-signé)\n\n"
                f"📡 ÉTAPE 2/3 — Token d'accès\n"
                f"Envoyez-moi votre token HA longue durée (eyJ...)"
            )
            return True
        except Exception as e:
            telegram_send(
                f"❌ Impossible de joindre {url}\n"
                f"Erreur : {str(e)[:100]}\n\n"
                f"Vérifiez l'URL et réessayez."
            )
            return True

        telegram_send(
            f"❌ Home Assistant non trouvé à {url}\n"
            f"Vérifiez que HA est démarré et que l'URL est correcte."
        )
        return True

    # ═══ ÉTAPE 2 : Token HA ═══
    if step == "ha_token":
        token = texte.strip()
        if not token.startswith("eyJ"):
            telegram_send(
                "❌ Ce n'est pas un token HA valide.\n"
                "Le token commence par eyJ... (format JWT).\n"
                "Créez-le dans HA : Profil → Tokens d'accès longue durée"
            )
            return True

        # Test du token
        try:
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get(f"{shared.CFG['ha_url']}/api/", headers=headers, verify=False, timeout=10)
            if r.status_code == 200 and r.json().get("message") == "API running.":
                shared.CFG["ha_token"] = token
                # Compter les entités
                r2 = requests.get(f"{shared.CFG['ha_url']}/api/states", headers=headers, verify=False, timeout=15)
                nb_entites = len(r2.json()) if r2.status_code == 200 else "?"
                shared.CFG["_wizard_step"] = "anthropic_key"
                _wizard_save_config()
                telegram_send(
                    f"✅ Home Assistant connecté ! {nb_entites} entités détectées.\n\n"
                    f"🧠 ÉTAPE 3/4 — Clé API Anthropic\n"
                    f"Créez une clé sur console.anthropic.com\n"
                    f"(Plan payant requis, ~5-10€/mois)\n\n"
                    f"Envoyez-moi la clé (commence par sk-ant-...)"
                )
                return True
            else:
                telegram_send(
                    f"❌ Token refusé par Home Assistant (HTTP {r.status_code}).\n"
                    f"Vérifiez le token et réessayez."
                )
                return True
        except Exception as e:
            telegram_send(f"❌ Erreur connexion HA : {str(e)[:100]}")
            return True

    # ═══ ÉTAPE 3 : Clé Anthropic ═══
    if step == "anthropic_key":
        key = texte.strip()
        if not key.startswith("sk-ant-"):
            telegram_send(
                "❌ Ce n'est pas une clé API Anthropic valide.\n"
                "La clé commence par sk-ant-...\n"
                "Créez-la sur console.anthropic.com → API Keys"
            )
            return True

        # Test de la clé
        try:
            client = anthropic.Anthropic(api_key=key)
            r = client.messages.create(
                model="claude-haiku-4-5-20251001", max_tokens=10,
                messages=[{"role": "user", "content": "Dis bonjour"}]
            )
            shared.CFG["anthropic_api_key"] = key
            shared.CFG["_wizard_step"] = "sms_method"
            _wizard_save_config()
            telegram_send(
                "✅ Claude AI connecté !\n\n"
                "🔐 ÉTAPE 4/4 — Sécurité (code de déverrouillage)\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "L'assistant verrouille le canal au démarrage.\n"
                "Un code de sécurité vous est envoyé pour le déverrouiller.\n\n"
                "Comment voulez-vous recevoir le code ?"
            )
            telegram_send_buttons(
                "Choisissez la méthode d'envoi du code :",
                [
                    {"text": "📱 SMS Free Mobile", "callback_data": "wizard_sms:free_mobile"},
                    {"text": "🔔 Notification HA", "callback_data": "wizard_sms:ha_notify"},
                    {"text": "📧 Email", "callback_data": "wizard_sms:email"},
                ]
            )
            return True
        except Exception as e:
            telegram_send(
                f"❌ Clé API refusée par Anthropic.\n"
                f"Erreur : {str(e)[:100]}\n\n"
                f"Vérifiez la clé et réessayez."
            )
            return True

    # ═══ ÉTAPE 4a : Free Mobile credentials ═══
    if step == "sms_free_user":
        shared.CFG["free_mobile_user"] = texte.strip()
        shared.CFG["_wizard_step"] = "sms_free_pass"
        _wizard_save_config()
        telegram_send("Mot de passe API Free Mobile :\n(Espace abonné → Mes options → Notifications par SMS)")
        return True

    if step == "sms_free_pass":
        shared.CFG["free_mobile_pass"] = texte.strip()
        # Test d'envoi
        shared.CFG["sms_method"] = "free_mobile"
        _wizard_save_config()
        code_test = "TEST"
        try:
            url = f"https://smsapi.free-mobile.fr/sendmsg?user={shared.CFG['free_mobile_user']}&pass={shared.CFG['free_mobile_pass']}&msg=AssistantIA:code_test_{code_test}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                _wizard_complete()
                return True
            else:
                telegram_send(f"❌ Free Mobile a refusé (HTTP {r.status_code}).\nVérifiez identifiant et mot de passe API.")
                shared.CFG["_wizard_step"] = "sms_free_user"
                _wizard_save_config()
                telegram_send("Renvoyez votre identifiant Free Mobile (8 chiffres) :")
                return True
        except Exception as e:
            telegram_send(f"❌ Erreur Free Mobile : {str(e)[:100]}")
            shared.CFG["_wizard_step"] = "sms_free_user"
            _wizard_save_config()
            return True

    # ═══ ÉTAPE 4b : HA Notify service ═══
    if step == "sms_ha_notify_service":
        service_name = texte.strip().replace("notify.", "").replace("mobile_app_", "")
        # Si l'utilisateur a tapé le nom complet, extraire la partie utile
        if texte.strip().startswith("mobile_app_"):
            service_name = texte.strip()
        elif not texte.strip().startswith("notify."):
            service_name = f"mobile_app_{service_name}"
        shared.CFG["ha_notify_service"] = service_name
        shared.CFG["sms_method"] = "ha_notify"
        _wizard_save_config()
        # Test
        try:
            url_test = f"{shared.CFG['ha_url']}/api/services/notify/{service_name}"
            headers = {"Authorization": f"Bearer {shared.CFG['ha_token']}", "Content-Type": "application/json"}
            payload_test = {"title": "🔐 Test AssistantIA", "message": "Si vous voyez cette notification, c'est configuré !", "data": {"priority": "high"}}
            r = requests.post(url_test, json=payload_test, headers=headers, verify=False, timeout=10)
            if r.status_code == 200:
                telegram_send("✅ Notification de test envoyée ! Vérifiez votre téléphone.")
                _wizard_complete()
                return True
            else:
                # Lister les services notify disponibles
                try:
                    r2 = requests.get(f"{shared.CFG['ha_url']}/api/services", headers=headers, verify=False, timeout=10)
                    services = [s["services"] for s in r2.json() if s.get("domain") == "notify"]
                    notify_list = []
                    if services:
                        notify_list = list(services[0].keys())
                except Exception:
                    notify_list = []
                msg = f"❌ Service notify/{service_name} non trouvé.\n"
                if notify_list:
                    msg += "\nServices disponibles :\n" + "\n".join(f"  • {n}" for n in notify_list[:10])
                msg += "\n\nRenvoyez le nom du service :"
                telegram_send(msg)
                return True
        except Exception as e:
            telegram_send(f"❌ Erreur : {str(e)[:100]}\nRéessayez :")
            return True

    # ═══ ÉTAPE 4c : Email ═══
    if step == "sms_email_addr":
        email = texte.strip()
        if "@" not in email:
            telegram_send("❌ Adresse email invalide. Réessayez :")
            return True
        shared.CFG["mail_dest"] = email
        shared.CFG["smtp_user"] = email  # Par défaut = même email
        shared.CFG["_wizard_step"] = "sms_email_smtp"
        _wizard_save_config()
        telegram_send(
            f"Serveur SMTP pour {email} :\n"
            "Exemples courants :\n"
            "  • Gmail : smtp.gmail.com\n"
            "  • Outlook : smtp.office365.com\n"
            "  • Yahoo : smtp.mail.yahoo.com"
        )
        return True

    if step == "sms_email_smtp":
        shared.CFG["smtp_host"] = texte.strip()
        shared.CFG["smtp_port"] = 587
        shared.CFG["_wizard_step"] = "sms_email_pass"
        _wizard_save_config()
        telegram_send(
            "Mot de passe SMTP (ou mot de passe d'application) :\n"
            "Pour Gmail : créez un mot de passe d'application\n"
            "(Compte Google → Sécurité → Mots de passe d'application)"
        )
        return True

    if step == "sms_email_pass":
        shared.CFG["smtp_pass"] = texte.strip()
        shared.CFG["sms_method"] = "email"
        _wizard_save_config()
        # Test
        try:
            msg_test = MIMEText("Si vous recevez cet email, la configuration est correcte.")
            msg_test["Subject"] = "🔐 Test AssistantIA"
            msg_test["From"] = shared.CFG.get("smtp_user", "")
            msg_test["To"] = shared.CFG["mail_dest"]
            with smtplib.SMTP(shared.CFG["smtp_host"], shared.CFG.get("smtp_port", 587)) as s:
                s.starttls()
                s.login(shared.CFG["smtp_user"], shared.CFG["smtp_pass"])
                s.send_message(msg_test)
            telegram_send("✅ Email de test envoyé ! Vérifiez votre boîte.")
            _wizard_complete()
            return True
        except Exception as e:
            telegram_send(f"❌ Erreur SMTP : {str(e)[:100]}\nVérifiez les paramètres.")
            shared.CFG["_wizard_step"] = "sms_email_addr"
            _wizard_save_config()
            telegram_send("Renvoyez votre adresse email :")
            return True

    return False


def _wizard_complete():
    """Termine le wizard et lance le système."""
    CFG.pop("_wizard_step", None)
    _wizard_save_config()
    method_names = {"free_mobile": "SMS Free Mobile", "ha_notify": "Notification HA", "email": "Email"}
    method_name = method_names.get(shared.CFG.get("sms_method", ""), "?")
    telegram_send(
        "🎉 CONFIGURATION TERMINÉE\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"• Home Assistant : {shared.CFG['ha_url']}\n"
        f"• Telegram : connecté\n"
        f"• Claude AI : connecté\n"
        f"• Sécurité : {method_name}\n\n"
        "🚀 Premier scan en cours...\n"
        "L'assistant va scanner vos entités, découvrir vos appareils,\n"
        "et configurer la surveillance automatiquement.\n\n"
        "Tapez /aide pour voir toutes les commandes."
    )
    log.info(f"🎉 Wizard terminé — méthode SMS: {shared.CFG.get('sms_method')}")


def validation_demarrage():
    resultats = []
    try:
        r = requests.get(f"https://api.telegram.org/bot{shared.CFG['telegram_token']}/getMe", timeout=10)
        resultats.append("✅ Telegram OK" if r.status_code == 200 else f"❌ Telegram {r.status_code}")
    except Exception as e:
        resultats.append(f"❌ Telegram: {e}")

    try:
        r = ha_get("")
        resultats.append("✅ Home Assistant OK" if r and r.get("message") == "API running."
                         else "❌ Home Assistant inaccessible")
    except Exception as e:
        resultats.append(f"❌ HA: {e}")

    try:
        client = anthropic.Anthropic(api_key=shared.CFG["anthropic_api_key"])
        client.messages.create(model="claude-haiku-4-5-20251001", max_tokens=5,
                               messages=[{"role": "user", "content": "ok"}])
        resultats.append("✅ Anthropic OK")
    except Exception as e:
        resultats.append(f"❌ Anthropic: {e}")

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
        resultats.append("✅ SQLite OK")
    except Exception as e:
        resultats.append(f"❌ SQLite: {e}")

    bilan  = f"🚀 ASSISTANT IA {VERSION}\n━━━━━━━━━━━━━━━━━━━━\n"
    bilan += "\n".join(resultats)
    bilan += f"\n━━━━━━━━━━━━━━━━━━━━\nMode: {MODE}"
    log.info(bilan)
    return bilan


def est_heure_nuit():
    """Nuit = soleil sous l'horizon"""
    try:
        etats = ha_get("states")
        if etats:
            sun = next((e for e in etats if e["entity_id"] == "sun.sun"), None)
            if sun:
                return sun["state"] == "below_horizon"
    except Exception:
        pass
    h = datetime.now().hour
    return h >= 22 or h < 7


def verifier_urgences_nuit():
    alertes = []
    try:
        r = ha_get("")
        if not r or r.get("message") != "API running.":
            alertes.append("🚨 URGENCE — HA INACCESSIBLE")
    except Exception:
        alertes.append("🚨 URGENCE — HA INACCESSIBLE")

    etats = ha_get("states")
    if etats:
        index = {e["entity_id"]: e for e in etats}
        for entity_id, sous_cat, piece in cartographie_get_par_categorie("nas"):
            if "volume" in sous_cat.lower() and entity_id in index:
                v = index[entity_id]
                if v["state"] not in ["normal", "on", "unknown", "unavailable"]:
                    alertes.append(f"🚨 NAS VOLUME DÉGRADÉ : {entity_id} = {v['state']}")
    return alertes


def watchdog_interne():
    """Thread watchdog — surveille les anomalies internes"""
    time.sleep(300)
    while True:
        try:
            now = datetime.now()
            anomalies = []

            last_mon = _watchdog.get("monitoring_last_run")
            if last_mon and (now - last_mon).total_seconds() > 900:
                anomalies.append(
                    f"⚠️ Thread monitoring silencieux depuis "
                    f"{int((now-last_mon).total_seconds()//60)} min"
                )

            last_pri = _watchdog.get("prises_last_run")
            if last_pri and (now - last_pri).total_seconds() > 600:
                anomalies.append(
                    f"⚠️ Thread prises silencieux depuis "
                    f"{int((now-last_pri).total_seconds()//60)} min"
                )

            bloque = _watchdog.get("offset_bloque_depuis")
            if bloque and (now - bloque).total_seconds() > 300:
                anomalies.append(
                    f"🚨 Offset Telegram bloqué depuis "
                    f"{int((now-bloque).total_seconds()//60)} min"
                )

            erreurs = _watchdog.get("erreurs", [])
            if len(erreurs) >= 3:
                anomalies.append(
                    f"🚨 {len(erreurs)} exceptions en 1h\n"
                    f"Dernière : {erreurs[-1][1][:100]}"
                )

            if anomalies:
                # Log interne seulement — l'utilisateur ne paie pas pour voir nos bugs
                log.warning(f"Watchdog: {'; '.join(a[:60] for a in anomalies)}")

        except Exception as ex:
            log.error(f"❌ watchdog_interne: {ex}")

        time.sleep(300)


def _scan_infiltration_auto():
    """Scan d'infiltration silencieux toutes les 1h — catégorisation IA des entités inconnues."""
    while True:
        time.sleep(1 * 3600)
        try:
            etats = ha_get("states")
            if etats:
                index = {e["entity_id"]: e for e in etats}
                traiter_entites_en_attente(index)
                log.info("🔍 Scan infiltration automatique terminé")
        except Exception as ex:
            log.error(f"❌ scan_infiltration_auto: {ex}")


def audit_auto():
    global dernier_audit
    while True:
        now = time.time()
        interval = shared.CFG.get("audit_interval_sec", 1800)
        if now - dernier_audit >= interval:
            log.info("⏱️ Audit silencieux...")

            # La surveillance tourne TOUJOURS — canal_verrouille ne bloque que les commandes Telegram
            # (supprimé : skip audit si canal verrouillé)

            if est_heure_nuit():
                alertes = verifier_urgences_nuit()
                for a in alertes:
                    telegram_send(a)
                    log.warning(a)
            else:
                etats = ha_get("states")
                if etats:
                    ko = [e for e in etats if e["state"] in ["unavailable", "unknown"]]
                    mem_set("dernier_audit_ko", len(ko))
                    mem_set("dernier_audit_heure", datetime.now().strftime("%d/%m/%Y %H:%M"))
                    log.info(f"Audit silencieux : {len(ko)} entités hors ligne")

            dernier_audit = now

            bilan_jours = shared.CFG.get("bilan_jours", 4)
            dernier_bilan = mem_get("dernier_bilan")
            demarrage = mem_get("ha_scan_date")
            if demarrage and not dernier_bilan:
                try:
                    debut = datetime.fromisoformat(demarrage)
                    if (datetime.now() - debut).total_seconds() >= bilan_jours * 86400:
                        threading.Thread(target=bilan_automatique, daemon=True).start()
                except Exception:
                    pass

        time.sleep(60)


def surveillance_batteries():
    while True:
        now = datetime.now()
        if now.hour == 9 and now.minute < 5:
            log.info("🔋 Vérification batteries 9h...")
            etats = ha_get("states")
            if etats:
                alertes = []
                for e in etats:
                    eid = e["entity_id"]
                    attrs_b = e.get("attributes", {})
                    is_battery = (
                        attrs_b.get("device_class") == "battery" or
                        "etat_de_charge" in eid.lower() or
                        (("battery" in eid.lower() or "batterie" in eid.lower()) and
                         "puissance" not in eid.lower() and "power" not in eid.lower())
                    )
                    unite_b = attrs_b.get("unit_of_measurement", "")
                    if unite_b and unite_b not in ["%", ""]:
                        is_battery = False
                    if not is_battery:
                        continue
                    try:
                        val = float(e["state"])
                    except Exception:
                        continue

                    carto = cartographie_get(eid)
                    piece = carto[2] if carto else ""
                    batterie_set(eid, piece, int(val))

                    if val < 20:
                        derniere = batterie_get_derniere_alerte(eid)
                        if derniere:
                            try:
                                delta = (now - datetime.fromisoformat(derniere)).total_seconds()
                                if delta < 86400:
                                    continue
                            except Exception:
                                pass
                        piece_str = f" [{piece}]" if piece else ""
                        icone = "🚨" if val < 10 else "⚠️"
                        alertes.append(f"{icone} {eid}{piece_str} : {int(val)}%")
                        batterie_set_alerte(eid)

                if alertes:
                    telegram_send("🔋 BATTERIES FAIBLES :\n" + "\n".join(alertes))
                else:
                    log.info("✅ Batteries : toutes OK")

            time.sleep(300)
        time.sleep(60)


def main():
    # global canal_verrouille  # → shared
    log.info(f"=== AssistantIA {VERSION} démarrage ===")

    init_db()

    # ═══ MODE WIZARD : config incomplète → polling Telegram pur ═══
    if _wizard_step():
        log.info("🧙 Mode wizard — en attente de configuration via Telegram")
        # Boucle de polling minimale (pas de HA, pas de surveillance)
        offset = None
        try:
            r_off = requests.get(
                f"https://api.telegram.org/bot{shared.CFG['telegram_token']}/getUpdates",
                params={"timeout": 1, "offset": -1}, timeout=10
            )
            if r_off.status_code == 200:
                results = r_off.json().get("result", [])
                if results:
                    offset = results[-1]["update_id"] + 1
        except Exception:
            pass

        while _wizard_step():
            try:
                updates = telegram_get_updates(offset)
                for update in updates:
                    offset = update["update_id"] + 1
                    # Callbacks (boutons)
                    if "callback_query" in update:
                        cq = update["callback_query"]
                        chat_cq = str(cq.get("message", {}).get("chat", {}).get("id", ""))
                        if _is_authorized_chat(chat_cq):
                            traiter_callback(cq)
                        continue
                    # Messages texte
                    if "message" not in update:
                        continue
                    msg = update["message"]
                    chat_id = str(msg.get("chat", {}).get("id", ""))
                    texte = msg.get("text", "").strip()
                    if not texte or not _is_authorized_chat(chat_id):
                        continue
                    _wizard_handle_message(texte)
                time.sleep(2)
            except Exception as e:
                log.error(f"Wizard polling: {e}")
                time.sleep(5)

        # Wizard terminé → recharger config et continuer normalement
        log.info("🎉 Wizard terminé — démarrage normal")
        shared.CFG.update(load_config())

    # Forcer le timestamp si absent (migration v1.5.0)
    if not mem_get("canal_deverrouille_at"):
        mem_set("canal_deverrouille_at", datetime.now().isoformat())

    # Initialiser dernier_deverrouillage si premier lancement
    if not mem_get("dernier_deverrouillage"):
        mem_set("dernier_deverrouillage", datetime.now().isoformat())

    bilan = validation_demarrage()

    # ═══ SÉCURITÉ CANAL ═══
    # Dernier code < 24h → auto-déverrouillé. Sinon → SMS.
    dernier_code = mem_get("dernier_deverrouillage")
    skip_sms = False
    if dernier_code:
        try:
            dt = datetime.strptime(dernier_code[:19], "%Y-%m-%dT%H:%M:%S")
            if (datetime.now() - dt).total_seconds() < 86400:
                skip_sms = True
                shared.canal_verrouille = False
        except Exception:
            pass

    if skip_sms:
        telegram_send(bilan + "\n\n✅ Canal ouvert", force=True)
    else:
        shared.canal_verrouille = True
        envoyer_code_sms()
        telegram_send(bilan + "\n\n🔐 Entrez le code SMS", force=True)

    etats_actuels = ha_get("states")
    if etats_actuels:
        comparer_entites_au_demarrage(etats_actuels)

    conn = sqlite3.connect(DB_PATH)
    nb_carto = conn.execute('SELECT COUNT(*) FROM cartographie').fetchone()[0]
    conn.close()

    # Découverte rôles au démarrage
    if etats_actuels:
        try:
            role_decouvrir(etats_actuels)
        except Exception:
            pass

    if not mem_get("ha_scan_date") or nb_carto == 0:
        scan_ha_complet()
    else:
        threading.Thread(target=decouverte_auto, args=(etats_actuels,), daemon=True).start()

    # Threads background
    threading.Thread(target=backup_sqlite,         daemon=True).start()
    threading.Thread(target=keepalive,              daemon=True).start()
    threading.Thread(target=audit_auto,             daemon=True).start()
    threading.Thread(target=surveillance_batteries, daemon=True).start()
    threading.Thread(target=surveillance_monitoring,daemon=True).start()
    threading.Thread(target=surveillance_prises,    daemon=True).start()
    threading.Thread(target=watchdog_interne,       daemon=True).start()
    threading.Thread(target=_scan_infiltration_auto, daemon=True).start()

    # Restaurer l'état des cycles en cours depuis SQLite
    # Les mesures sont dans cycle_mesures (stockées en temps réel) — pas besoin de HA API
    try:
        conn_cycles = sqlite3.connect(DB_PATH)
        cycles_ouverts = conn_cycles.execute(
            "SELECT entity_id, debut FROM cycles_appareils WHERE fin IS NULL"
        ).fetchall()
        for eid, debut in cycles_ouverts:
            # Charger les mesures depuis SQLite
            rows = conn_cycles.execute(
                "SELECT ts, watts FROM cycle_mesures WHERE entity_id=? ORDER BY ts", (eid,)
            ).fetchall()
            _puissances_historique[eid] = [(ts, w) for ts, w in rows]
            nb = len(rows)

            app = appareil_get(eid)
            app_nom = app["nom"] if app and app.get("nom") else eid
            duree_min = 0
            try:
                duree_min = (datetime.now() - datetime.fromisoformat(debut)).total_seconds() / 60
            except Exception:
                pass

            # Lire la puissance actuelle
            puissance_now = 0
            if etats_actuels:
                e_now = {e["entity_id"]: e for e in etats_actuels}.get(eid)
                if e_now and e_now["state"] not in ("unavailable", "unknown"):
                    try:
                        puissance_now = float(e_now["state"])
                    except Exception:
                        pass

            if puissance_now > 10:
                # Machine tourne encore → restaurer en silence
                _etat_prises[eid] = "actif"
                _rappel_linge_envoye[eid] = True
                log.info(f"🔄 Cycle restauré : {app_nom} ({int(duree_min)} min, {int(puissance_now)}W)")
                try:
                    telegram_send(f"🔄 {app_nom} toujours en marche ({int(duree_min)} min, {int(puissance_now)}W)")
                except Exception:
                    pass
            else:
                # Machine à l'arrêt → demander à l'utilisateur (pas de double notification)
                _etat_prises[eid] = "attente_restart"
                telegram_send_buttons(
                    f"🔄 Restart — {app_nom} avait un cycle en cours ({int(duree_min)} min).\n"
                    f"Puissance actuelle : {int(puissance_now)}W\n\n"
                    f"Le cycle est terminé ?",
                    [
                        {"text": "✅ Oui, terminé", "callback_data": f"cycle_fin:{eid}"},
                        {"text": "🔄 Non, il tourne encore", "callback_data": f"cycle_continue:{eid}"},
                    ]
                )
                log.info(f"🔄 Cycle en attente : {app_nom} ({int(duree_min)} min, {int(puissance_now)}W) → question")
        conn_cycles.close()
    except Exception:
        pass

    log.info(f"✅ 8 threads démarrés")
    mem_set("envoyer_md_maintenant", "oui")

    # Premier démarrage : questionnaire tarif si pas encore configuré
    tarif_actuel, nb_tarif = skill_get("tarification")
    if not tarif_actuel or "type" not in tarif_actuel:
        log.info("⚡ Tarif non configuré — lancement questionnaire")
        tarif_configurer_questionnaire()

    # Identification des appareils sur les prises connectées
    try:
        conn_check = sqlite3.connect(DB_PATH)
        nb_prises_carto = conn_check.execute(
            "SELECT COUNT(*) FROM cartographie WHERE categorie='prise_connectee' AND entity_id LIKE '%_power'"
        ).fetchone()[0]
        nb_appareils = conn_check.execute("SELECT COUNT(*) FROM appareils").fetchone()[0]
        prises_sans_appareil = conn_check.execute(
            "SELECT entity_id, friendly_name FROM cartographie "
            "WHERE categorie='prise_connectee' AND entity_id LIKE '%_power' "
            "AND entity_id NOT IN (SELECT entity_id FROM appareils)"
        ).fetchall()
        log.debug(f"Appareils: {nb_prises_carto} prises, {nb_appareils} identifiés, {len(prises_sans_appareil)} restants")
        conn_check.close()
        if prises_sans_appareil:
            mem_set("appareils_configures", "")
            mem_set("appareils_queue", "")
            log.info(f"🔌 Relance questionnaire pour {len(prises_sans_appareil)} prise(s)")
            _lancer_questionnaire_appareils()
        else:
            log.info("🔌 Toutes les prises sont identifiées")
    except Exception as ex_app:
        log.error(f"🔌 Erreur diagnostic appareils: {ex_app}")
        import traceback
        log.error(traceback.format_exc())

    # Profil foyer — questions fondatrices
    if not mem_get("profil_foyer_complet"):
        log.info("👥 Profil foyer non configuré — lancement questionnaire")
        _lancer_questionnaire_foyer()
    else:
        log.info("👥 Profil foyer : configuré")







    offset = None
    try:
        url_off = f"https://api.telegram.org/bot{shared.CFG['telegram_token']}/getUpdates"
        r_off = requests.get(url_off, params={"offset": -1, "limit": 1}, timeout=10)
        if r_off.status_code == 200:
            results = r_off.json().get("result", [])
            if results:
                offset = results[-1]["update_id"] + 1
                log.info(f"📡 Offset Telegram initialisé à {offset}")
    except Exception as e_off:
        log.warning(f"⚠️ Init offset Telegram: {e_off}")
    log.info("📡 Polling démarré...")

    while True:
        try:
            updates = telegram_get_updates(offset)

            for update in updates:
                offset = update["update_id"] + 1
                _watchdog["polling_last_update"] = datetime.now()
                if _watchdog["offset_last"] == offset:
                    if _watchdog["offset_bloque_depuis"] is None:
                        _watchdog["offset_bloque_depuis"] = datetime.now()
                else:
                    _watchdog["offset_last"] = offset
                    _watchdog["offset_bloque_depuis"] = None

                if "callback_query" in update:
                    cq = update["callback_query"]
                    chat = str(cq.get("message", {}).get("chat", {}).get("id", ""))
                    if _is_authorized_chat(chat):
                        traiter_callback(cq)
                    continue

                if "message" not in update:
                    continue

                msg     = update["message"]
                chat_id = str(msg.get("chat", {}).get("id", ""))
                texte   = msg.get("text", "").strip()

                # ═══ MESSAGE VOCAL → transcription ═══
                if not texte and "voice" in msg:
                    if _is_authorized_chat(chat_id):
                        try:
                            file_id = msg["voice"].get("file_id")
                            if file_id:
                                telegram_send("🎤 Transcription en cours...")
                                texte = transcrire_vocal(file_id)
                                if texte:
                                    telegram_send(f"🎤 _{texte}_", force=True)
                                else:
                                    telegram_send("❌ Transcription impossible — tapez votre commande.")
                                    continue
                        except Exception as e_vocal:
                            log.error(f"Vocal: {e_vocal}")
                            telegram_send("❌ Erreur vocale — tapez votre commande.")
                            continue

                if not texte or not _is_authorized_chat(chat_id):
                    if texte:
                        log.warning(f"⚠️ chat_id inconnu: {chat_id}")
                    continue

                # ═══ WIZARD SETUP (premier démarrage) ═══
                if _wizard_step():
                    if _wizard_handle_message(texte):
                        # Si wizard vient de se terminer, lancer le premier scan
                        if not _wizard_step():
                            try:
                                scan_ha_complet()
                            except Exception:
                                pass
                        continue

                if shared.canal_verrouille:
                    # /sms → renvoyer un nouveau code (même si verrouillé)
                    if texte.strip().lower() in ("/sms", "sms"):
                        envoyer_code_sms()
                        telegram_send("📱 Nouveau code SMS envoyé.")
                        continue
                    if verifier_code(texte):
                        telegram_send("✅ Canal déverrouillé — Bonjour !")
                    else:
                        telegram_send("🔐 Entrez le code SMS (ou tapez /sms pour en recevoir un nouveau)")
                    continue

                reponse = traiter_message(texte)
                # L'utilisateur demande → la réponse passe TOUJOURS (force=True)
                # Les filtres ne s'appliquent qu'aux messages proactifs
                if len(reponse) > 4000:
                    for i in range(0, len(reponse), 4000):
                        telegram_send(reponse[i:i+4000], force=True)
                else:
                    telegram_send(reponse, force=True)

            time.sleep(shared.CFG.get("poll_interval_sec", 2))

        except KeyboardInterrupt:
            log.info("🛑 Arrêt manuel")
            telegram_send("🛑 AssistantIA arrêté")
            break
        except Exception as e:
            log.error(f"❌ Boucle principale: {e}")
            _watchdog["erreurs"].append((datetime.now(), str(e)))
            apprentissage_log_echec("boucle_principale", str(e))
            _watchdog["erreurs"] = [
                (dt, msg) for dt, msg in _watchdog["erreurs"]
                if (datetime.now() - dt).total_seconds() < 3600
            ]
            time.sleep(5)


if __name__ == "__main__":
    main()
