# =============================================================================
# SHARED.PY — Variables globales + fonctions utilitaires
# =============================================================================

import json
import logging
import os
import re
import random
import requests
import sqlite3
import smtplib
import time
import threading
import hashlib
import hmac
import urllib.request
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from logging.handlers import RotatingFileHandler
import anthropic

from config import *

# =============================================================================
# TIMEZONE — Europe/Paris (heure d'été/hiver automatique)
# =============================================================================
import os as _tz_os
_tz_os.environ['TZ'] = 'Europe/Paris'
import time as _tz_time
_tz_time.tzset()

__all__ = [
    "ANTI_DUPLICATE_SEC",
    "AUTO_GUERISON_COOLDOWN",
    "BASELINE_ENTITIES",
    "BASE_DIR",
    "CFG",
    "COMPORTEMENT",
    "CONFIG_PATH",
    "DB_PATH",
    "DUREE_MIN_LAVE_LINGE",
    "DUREE_MIN_LAVE_VAISSELLE",
    "DUREE_MIN_SECHE_LINGE",
    "GRACE_APRES_ESSORAGE",
    "GRACE_APRES_LAVAGE",
    "GRACE_APRES_SECHAGE",
    "GRACE_APRES_VAISSELLE",
    "HA_DOMAINES_AUTORISES",
    "HA_TOOLS",
    "HEURE_BILAN_HEBDO",
    "HEURE_BILAN_SOIR",
    "HEURE_BRIEFING_TRAVAIL",
    "HEURE_BRIEFING_WEEKEND",
    "JOURS_MACHINES",
    "LOG_PATH",
    "LQI_FAIBLE",
    "MAX_MESSAGES_JOUR",
    "MODE",
    "POLL_PRISES_ACTIF",
    "POLL_PRISES_IDLE",
    "ROLES_DEFINIS",
    "SEUIL_AUTO_GUERISON",
    "SEUIL_CYCLE_W",
    "SEUIL_FIN_W",
    "TYPES_APPAREILS",
    "VERSION",
    "_ErrorCaptureHandler",
    "_alerter_si_nouveau",
    "_areas_id_to_name",
    "_coupure_edf_alertee",
    "_defroissage_detecte",
    "_derniere_phase_haute",
    "_eco_proactif_state",
    "_entites_deja_detectees",
    "_entity_areas",
    "_erreurs_buffer",
    "_erreurs_vues",
    "_est_heure_creuse_plages",
    "_est_jour_choisi",
    "_est_weekend_ou_ferie",
    "_etat_prises",
    "_grace_fin",
    "_injecter_lecons_fondatrices",
    "_install_matplotlib_bg",
    "_intelligence_compteur",
    "_is_authorized_chat",
    "_md_dernier_hash",
    "_prises_snapshot",
    "_puissances_historique",
    "_rappel_linge_envoye",
    "_snapshot_valide",
    "_watchdog",
    "_wizard_save_config",
    "_wizard_step",
    "add_historique",
    "appareil_get",
    "appareil_set",
    "appel_claude",
    "batterie_get_derniere_alerte",
    "batterie_set",
    "batterie_set_alerte",
    "canal_verrouille",
    "cartographie_get",
    "cartographie_get_par_categorie",
    "cartographie_get_toutes",
    "cartographie_get_toutes_categories",
    "charger_comportement",
    "code_auth",
    "dernier_audit",
    "en_attente_reponse",
    "enregistrer_economie",
    "entites_connues_get_toutes",
    "entites_connues_maj",
    "envoyer_code_sms",
    "envoyer_email",
    "filtre_analyser_messages",
    "filtre_apprendre_pattern",
    "generer_code_auth",
    "get_economies_mois",
    "get_historique",
    "get_token_usage",
    "ha_est_jour",
    "ha_get",
    "ha_get_etat",
    "ha_get_forecast",
    "ha_get_production_solaire_actuelle",
    "ha_post",
    "init_db",
    "load_config",
    "log",
    "log_token_usage",
    "mem_get",
    "mem_set",
    "role_decouvrir",
    "role_decouvrir_baselines",
    "role_get",
    "role_get_all",
    "role_set",
    "role_val",
    "skill_get",
    "skill_set",
    "tarif_est_heure_creuse",
    "tarif_get",
    "tarif_prix_kwh_actuel",
    "telegram_answer_callback",
    "telegram_get_updates",
    "telegram_send",
    "telegram_send_buttons",
    "telegram_send_photo",
    "verifier_budget",
    "verifier_code",
    "zigbee_absence_creer",
    "zigbee_absence_get",
    "zigbee_absence_retour",
    "zigbee_absence_statut",
]

# =============================================================================
# LOGGING
# =============================================================================
_log_level = logging.DEBUG if MODE == "DEV" else logging.WARNING
_log_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_file_handler = RotatingFileHandler(LOG_PATH, maxBytes=5*1024*1024, backupCount=3)
_file_handler.setFormatter(_log_format)
_file_handler.setLevel(_log_level)
_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_log_format)
_console_handler.setLevel(_log_level)
logging.basicConfig(level=_log_level, handlers=[_file_handler, _console_handler])
log = logging.getLogger(__name__)





# =============================================================================
# GLOBAL STATE VARIABLES
# =============================================================================

BASELINE_ENTITIES = {
    "sensor.ecojoko_consommation_temps_reel": "conso_edf_w",
    "sensor.ecu_current_power": "production_aps_w",
    "sensor.pompe_a_chaleur_air_eau_energy_current": "conso_pac_w",
    "sensor.ecojoko_temperature_interieure": "temp_interieure",
    "sensor.ecojoko_temperature_exterieure": "temp_exterieure",
}
HA_DOMAINES_AUTORISES = {"light", "switch", "lock", "cover", "climate", "fan", "vacuum", "media_player", "scene", "script"}
HA_TOOLS = [
    {
        "name": "ha_call_service",
        "description": "Appelle un service Home Assistant pour agir sur un appareil. "
                       "Domaines : lock (lock/unlock), light (turn_on/turn_off/toggle), "
                       "switch (turn_on/turn_off/toggle), cover (open_cover/close_cover), "
                       "climate (set_temperature/set_hvac_mode/turn_on/turn_off), "
                       "fan, vacuum, media_player, scene, script.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domaine HA : light, switch, lock, cover, climate, fan, vacuum, media_player, scene, script"
                },
                "service": {
                    "type": "string",
                    "description": "Service : turn_on, turn_off, toggle, lock, unlock, open_cover, close_cover, etc."
                },
                "entity_id": {
                    "type": "string",
                    "description": "Entity ID complet, ex: lock.porte_entree, light.salon"
                },
                "data": {
                    "type": "object",
                    "description": "Données optionnelles : brightness, temperature, hvac_mode, etc.",
                    "default": {}
                }
            },
            "required": ["domain", "service", "entity_id"]
        }
    },
    {
        "name": "ha_create_watch",
        "description": "Crée une alerte automatique sur un ou plusieurs appareils HA. "
                       "L'assistant vérifiera chaque minute et enverra une notification Telegram "
                       "quand la condition est remplie. "
                       "Exemples : alerter si un onduleur passe offline, si une température dépasse un seuil, "
                       "si une porte reste ouverte, si une lumière est allumée la nuit, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_pattern": {
                    "type": "string",
                    "description": "Pattern pour les entity_id à surveiller. Peut être un entity_id exact "
                                   "(sensor.ecu_lifetime_energy) ou un pattern avec * "
                                   "(sensor.ecu_*_power pour tous les micro-onduleurs APSystems). "
                                   "Utilise les entity_id visibles dans l'état HA."
                },
                "condition": {
                    "type": "string",
                    "enum": ["unavailable", "offline", "equals", "not_equals", "above", "below", "changes"],
                    "description": "Condition de déclenchement : "
                                   "unavailable/offline = entité hors ligne, "
                                   "equals/not_equals = état égal/différent de state_value, "
                                   "above/below = valeur numérique au-dessus/en-dessous de state_value, "
                                   "changes = tout changement d'état"
                },
                "state_value": {
                    "type": "string",
                    "description": "Valeur de comparaison pour equals/not_equals/above/below. Vide pour unavailable/offline/changes.",
                    "default": ""
                },
                "message": {
                    "type": "string",
                    "description": "Message d'alerte à envoyer. Utilise {entity_id}, {state}, {friendly_name} comme variables."
                },
                "cooldown_min": {
                    "type": "integer",
                    "description": "Intervalle minimum entre deux alertes identiques (en minutes). Défaut: 60.",
                    "default": 60
                }
            },
            "required": ["entity_pattern", "condition", "message"]
        }
    }
]
_areas_id_to_name = {}
_coupure_edf_alertee = False
_defroissage_detecte = {}     # {entity_id: datetime} — début du défroissage détecté
_derniere_phase_haute = {}    # {entity_id: "C"/"E"/"L"} — dernière phase > SEUIL_FIN vue
_eco_proactif_state = {}
_entites_deja_detectees = set()
_entity_areas = {}
_erreurs_buffer = []  # [(timestamp, message, source)]
_erreurs_vues = {}    # {signature: last_reported} anti-spam
_etat_prises           = {}
_grace_fin             = {}
_intelligence_compteur = 0  # Compteur de cycles pour actions périodiques
_md_dernier_hash = None
_prises_snapshot = {}       # Snapshot continu : {entity_id: "on"/"off"}
_puissances_historique = {}   # {entity_id: [(timestamp, watts), ...]}
_rappel_linge_envoye = {}     # {entity_id: True} — rappel "linge chaud" déjà envoyé
_snapshot_valide = False     # True après au moins 2 cycles normaux
_watchdog = {
    "monitoring_last_run" : datetime.now(),
    "prises_last_run"     : datetime.now(),
    "polling_last_update" : datetime.now(),
    "erreurs"             : [],
    "offset_last"         : None,
    "offset_bloque_depuis": None,
}
canal_verrouille = True
code_auth = None
dernier_audit = 0
en_attente_reponse = {}

def _install_matplotlib_bg():
    try:
        import matplotlib
    except ImportError:
        import subprocess
        subprocess.run(["pip3", "install", "matplotlib", "--break-system-packages", "-q"], timeout=300)

threading.Thread(target=_install_matplotlib_bg, daemon=True).start()


class _ErrorCaptureHandler(logging.Handler):
    """Capture tous les log.error() dans un buffer pour analyse périodique."""
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            try:
                msg = self.format(record)
                # Signature = message nettoyé des chiffres variables pour grouper
                import re as _re
                sig = _re.sub(r'\d+', '#', record.getMessage())[:80]
                _erreurs_buffer.append((datetime.now().isoformat(), msg[:300], sig))
                if len(_erreurs_buffer) > 200:
                    _erreurs_buffer.pop(0)
            except Exception:
                pass


def load_config():
    """Charge config.json. Si absent, lance le wizard d'installation."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        log.info("✅ Config chargée")
        return cfg

    # ═══ PREMIER DÉMARRAGE — WIZARD ═══
    print("\n" + "=" * 50)
    print("🏠 AssistantIA Domotique — Premier démarrage")
    print("=" * 50)
    print("\nCe wizard va configurer votre assistant.")
    print("Vous avez besoin de :")
    print("  1. Un bot Telegram (créé via @BotFather)")
    print("  2. Home Assistant accessible (URL + token)")
    print("  3. Une clé API Anthropic (claude.ai)\n")

    # Étape 1 : Token Telegram (seule question CLI obligatoire)
    telegram_token = input("🤖 Token bot Telegram (de @BotFather) : ").strip()
    if not telegram_token or ":" not in telegram_token:
        print("❌ Token invalide. Format attendu : 1234567890:ABCDEF...")
        raise SystemExit(1)

    # Valider le token
    try:
        r = requests.get(f"https://api.telegram.org/bot{telegram_token}/getMe", timeout=10)
        if r.status_code != 200:
            print(f"❌ Token Telegram invalide (HTTP {r.status_code})")
            raise SystemExit(1)
        bot_name = r.json().get("result", {}).get("first_name", "Bot")
        print(f"✅ Bot connecté : {bot_name}")
    except requests.RequestException as e:
        print(f"❌ Impossible de contacter Telegram : {e}")
        raise SystemExit(1)

    # Étape 2 : Détecter le chat_id
    print(f"\n📱 Envoyez un message à votre bot sur Telegram.")
    print(f"   (N'importe quel message, juste pour détecter votre chat_id)")
    print(f"   En attente...", end="", flush=True)

    chat_id = None
    for _ in range(120):  # 2 minutes max
        try:
            r = requests.get(
                f"https://api.telegram.org/bot{telegram_token}/getUpdates",
                params={"timeout": 5, "allowed_updates": json.dumps(["message"])},
                timeout=10
            )
            if r.status_code == 200:
                updates = r.json().get("result", [])
                for u in reversed(updates):
                    if "message" in u and "chat" in u["message"]:
                        chat_id = str(u["message"]["chat"]["id"])
                        break
            if chat_id:
                break
            print(".", end="", flush=True)
        except Exception:
            time.sleep(2)

    if not chat_id:
        print("\n❌ Timeout — aucun message reçu. Relancez le script et envoyez un message au bot.")
        raise SystemExit(1)

    print(f"\n✅ Chat ID détecté : {chat_id}")

    # Créer config minimale
    cfg = {
        "telegram_token": telegram_token,
        "telegram_chat_id": chat_id,
        "ha_url": "",
        "ha_token": "",
        "anthropic_api_key": "",
        "poll_interval_sec": 2,
        "audit_interval_sec": 1800,
        "anthropic_monthly_budget_usd": 10,
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
    log.info("✅ Config minimale créée")

    # Envoyer le message de bienvenue sur Telegram
    msg = (
        "🏠 BIENVENUE — AssistantIA Domotique\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Je suis votre assistant domotique IA.\n"
        "Je vais vous guider pour la configuration.\n\n"
        "📡 ÉTAPE 1/4 — Home Assistant\n"
        "Envoyez-moi l'URL de votre Home Assistant.\n\n"
        "Exemples :\n"
        "  • http://192.168.1.100:8123\n"
        "  • http://homeassistant.local:8123\n"
        "  • https://mon-ha.duckdns.org"
    )
    requests.post(
        f"https://api.telegram.org/bot{telegram_token}/sendMessage",
        json={"chat_id": chat_id, "text": msg}
    )

    # Marquer le wizard comme en cours
    cfg["_wizard_step"] = "ha_url"
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

    print("\n✅ Configuration continue sur Telegram.")
    print("   Répondez aux questions du bot pour terminer l'installation.\n")

    return cfg



CFG = load_config()

# Migration sms_method
if "sms_method" not in CFG and not CFG.get("_wizard_step"):
    if CFG.get("free_mobile_user") and CFG.get("free_mobile_pass"):
        CFG["sms_method"] = "free_mobile"
    elif CFG.get("ha_notify_service"):
        CFG["sms_method"] = "ha_notify"
    elif CFG.get("smtp_host") and CFG.get("mail_dest"):
        CFG["sms_method"] = "email"
    else:
        CFG["sms_method"] = "free_mobile"
    with open(CONFIG_PATH, "w") as f:
        json.dump(CFG, f, indent=2)
    log.info(f"Migration: sms_method={CFG['sms_method']}")

def _is_authorized_chat(chat_id):
    """Vérifie si un chat_id est autorisé — supporte multi-utilisateur.
    Config : telegram_chat_id peut être un seul ID ou une liste séparée par des virgules.
    Ex: "123456789" ou "123456789,987654321" """
    allowed = str(CFG.get("telegram_chat_id", ""))
    if "," in allowed:
        return str(chat_id) in [x.strip() for x in allowed.split(",")]
    return str(chat_id) == allowed


def init_db():
    conn = sqlite3.connect(DB_PATH)

    conn.execute('''CREATE TABLE IF NOT EXISTS memoire (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cle TEXT UNIQUE, valeur TEXT, updated_at TEXT
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mois TEXT UNIQUE, tokens_in INTEGER DEFAULT 0, tokens_out INTEGER DEFAULT 0
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS historique (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT, contenu TEXT, created_at TEXT
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS entites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_id TEXT UNIQUE, state TEXT, attributes TEXT, updated_at TEXT
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS cartographie (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_id TEXT UNIQUE, categorie TEXT, sous_categorie TEXT,
        piece TEXT, friendly_name TEXT, appris_le TEXT
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS batteries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_id TEXT UNIQUE, piece TEXT,
        derniere_valeur INTEGER, derniere_alerte TEXT, updated_at TEXT
    )''')

    # Snapshot entités connues — pour détecter nouvelles/disparues au démarrage
    conn.execute('''CREATE TABLE IF NOT EXISTS entites_connues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_id TEXT UNIQUE,
        categorie TEXT,
        vu_la_derniere_fois TEXT,
        disparu_depuis TEXT
    )''')

    # Cycles appareils (machines, sèche-linge, etc.)
    conn.execute('''CREATE TABLE IF NOT EXISTS watches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_pattern TEXT NOT NULL,
        condition TEXT NOT NULL,
        state_value TEXT DEFAULT '',
        message TEXT NOT NULL,
        cooldown_min INTEGER DEFAULT 60,
        last_triggered TEXT DEFAULT '',
        active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT ''
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS cycles_appareils (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_id TEXT,
        friendly_name TEXT,
        debut TEXT,
        fin TEXT,
        duree_min INTEGER,
        conso_kwh REAL,
        cout_eur REAL,
        production_solaire_w INTEGER,
        created_at TEXT
    )''')

    # Migration : ajouter colonnes profil + programme si absentes
    try:
        conn.execute("SELECT programme FROM cycles_appareils LIMIT 1")
    except Exception:
        conn.execute("ALTER TABLE cycles_appareils ADD COLUMN programme TEXT")
        conn.execute("ALTER TABLE cycles_appareils ADD COLUMN profil_json TEXT")
        log.info("📊 Migration: colonnes programme + profil_json ajoutées à cycles_appareils")

    # Table mesures temps réel — stocke les Watts pendant un cycle en cours
    # Survit aux restarts → plus besoin de /api/history ni de CSV
    conn.execute('''CREATE TABLE IF NOT EXISTS cycle_mesures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_id TEXT,
        watts REAL,
        ts TEXT
    )''')
    # Index pour lecture rapide par entity_id
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cycle_mesures_eid ON cycle_mesures(entity_id)")

    # ═══ TABLE APPAREILS — Association prise → type machine ═══
    # L'utilisateur dit "sur cette prise il y a le lave-linge"
    # Le script ne devine pas — il demande une seule fois.
    conn.execute('''CREATE TABLE IF NOT EXISTS appareils (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_id TEXT UNIQUE,
        type_appareil TEXT,
        nom_personnalise TEXT,
        surveiller INTEGER DEFAULT 1,
        created_at TEXT
    )''')

    # ═══ TABLE ÉCONOMIES — Le cœur du business model ═══
    # Chaque action qui économise de l'énergie est tracée ici.
    # C'est cette table qui justifie chaque token dépensé.
    conn.execute('''CREATE TABLE IF NOT EXISTS economies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        description TEXT,
        euros REAL,
        kwh_economises REAL,
        source TEXT,
        created_at TEXT
    )''')

    # Suivi absences Zigbee — boutons Normal/Anormal
    conn.execute('''CREATE TABLE IF NOT EXISTS zigbee_absences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_id TEXT UNIQUE,
        hors_ligne_depuis TEXT,
        statut TEXT,  -- 'normal', 'anormal', 'en_attente'
        alerte_envoyee TEXT,
        retour_en_ligne TEXT
    )''')

    # Baselines — construites progressivement (Étape 6)
    conn.execute('''CREATE TABLE IF NOT EXISTS entites_en_attente (
        entity_id     TEXT PRIMARY KEY,
        friendly_name TEXT,
        categorie_proposee TEXT,
        description   TEXT,
        question_posee INTEGER DEFAULT 0,
        reponse       TEXT,
        created_at    TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS baselines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_id TEXT,
        jour_semaine INTEGER,
        heure INTEGER,
        valeur_moyenne REAL,
        nb_mesures INTEGER,
        updated_at TEXT,
        UNIQUE(entity_id, jour_semaine, heure)
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT UNIQUE,
        donnees TEXT,
        nb_apprentissages INTEGER DEFAULT 0,
        updated_at TEXT
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS expertise (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categorie TEXT,
        insight TEXT,
        confiance REAL DEFAULT 0.5,
        nb_validations INTEGER DEFAULT 0,
        source TEXT,
        created_at TEXT,
        updated_at TEXT
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS decisions_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        contexte TEXT,
        resultat TEXT,
        succes INTEGER DEFAULT -1,
        created_at TEXT
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS hypotheses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        enonce TEXT,
        categorie TEXT,
        condition_test TEXT,
        predictions INTEGER DEFAULT 0,
        confirmations INTEGER DEFAULT 0,
        refutations INTEGER DEFAULT 0,
        confiance REAL DEFAULT 0.5,
        active INTEGER DEFAULT 1,
        created_at TEXT,
        updated_at TEXT
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS intelligence_score (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT UNIQUE,
        score_global REAL,
        nb_expertise INTEGER,
        nb_hypotheses_actives INTEGER,
        taux_prediction REAL,
        nb_skills INTEGER,
        nb_baselines INTEGER,
        nb_echecs_jour INTEGER,
        nb_succes_jour INTEGER,
        economie_estimee REAL DEFAULT 0,
        details TEXT
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS filtre_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern TEXT UNIQUE,
        action TEXT DEFAULT 'bloquer',
        raison TEXT,
        nb_applique INTEGER DEFAULT 0,
        nb_faux_positif INTEGER DEFAULT 0,
        actif INTEGER DEFAULT 1,
        created_at TEXT,
        updated_at TEXT
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS messages_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT,
        envoye INTEGER DEFAULT 1,
        raison_filtre TEXT,
        feedback TEXT,
        created_at TEXT
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS roles (
        role TEXT PRIMARY KEY,
        entity_id TEXT,
        confiance REAL DEFAULT 0.5,
        source TEXT,
        updated_at TEXT
    )''')

    conn.commit()
    conn.close()
    log.info("✅ Base de données initialisée")

    # Auto-déverrouillage garanti : dernier_deverrouillage en SQLite (24h)

    # ═══ PURGE EXPERTISE DUPLIQUÉE ═══
    try:
        conn_purge = sqlite3.connect(DB_PATH)
        nb_avant = conn_purge.execute("SELECT COUNT(*) FROM expertise").fetchone()[0]
        if nb_avant > 50:
            # Garder les fondatrices + les 30 meilleurs par confiance
            fondatrices = [r[0] for r in conn_purge.execute(
                "SELECT id FROM expertise WHERE source LIKE 'lecon_fondatrice%'"
            ).fetchall()]
            autres_top = [r[0] for r in conn_purge.execute(
                "SELECT id FROM expertise WHERE source NOT LIKE 'lecon_fondatrice%' ORDER BY confiance DESC LIMIT 30"
            ).fetchall()]
            a_garder = set(fondatrices + autres_top)
            if a_garder:
                placeholders = ",".join(str(i) for i in a_garder)
                conn_purge.execute(f"DELETE FROM expertise WHERE id NOT IN ({placeholders})")
                conn_purge.commit()
            nb_apres = conn_purge.execute("SELECT COUNT(*) FROM expertise").fetchone()[0]
            log.info(f"🧹 Expertise purgée : {nb_avant} → {nb_apres}")
        conn_purge.close()
    except Exception as ex_purge:
        log.error(f"⚠️ Purge expertise: {ex_purge}")

    # ═══ PURGE DIRECTE ═══
    try:
        import subprocess
        result = subprocess.run(["python3", os.path.join(BASE_DIR, "purge_expertise.py")],
                               capture_output=True, text=True, timeout=10)
        if result.stdout:
            log.info(f"🧹 {result.stdout.strip()}")
        if result.stderr:
            log.error(f"Purge: {result.stderr.strip()}")
    except Exception as ex_p:
        log.error(f"Purge: {ex_p}")

    # ═══ NETTOYAGE FICHIERS CADUQUES ═══
    import glob as _glob
    _caduques = (
        _glob.glob(os.path.join(os.path.dirname(DB_PATH), "Cahier_des_Charges_v*.md")) +
        _glob.glob(os.path.join(os.path.dirname(DB_PATH), "diag_*.txt")) +
        _glob.glob(os.path.join(os.path.dirname(DB_PATH), "diag_*.json"))
    )
    for _f in _caduques:
        try:
            os.remove(_f)
            log.info(f"🗑️ Nettoyé : {os.path.basename(_f)}")
        except Exception:
            pass

    # ═══ FIX PIÈCE PRISE LAVE-VAISSELLE (cuisine) ═══
    try:
        conn_piece = sqlite3.connect(DB_PATH)
        nb_fix = conn_piece.execute(
            "UPDATE cartographie SET piece='cuisine' WHERE entity_id LIKE '%lave_vaiselle%' AND (piece IS NULL OR piece='')"
        ).rowcount
        conn_piece.commit()
        if nb_fix > 0:
            log.info(f"🏠 Lave-vaisselle : {nb_fix} entité(s) → cuisine")
        # Diagnostic : vérifier toutes les prises
        prises_vides = conn_piece.execute(
            "SELECT entity_id, friendly_name FROM cartographie WHERE categorie='prise_connectee' AND (piece IS NULL OR piece='')"
        ).fetchall()
        if prises_vides:
            log.info(f"⚠️ {len(prises_vides)} prises sans pièce : {[r[0] for r in prises_vides]}")
        conn_piece.close()
    except Exception as ex_lv:
        log.error(f"Fix lave-vaisselle: {ex_lv}")

    # ═══ PURGE DOUBLONS ÉCHECS HISTORIQUES (fix 20/03/2026) ═══
    try:
        conn_fix = sqlite3.connect(DB_PATH)
        # Garder 1 seule copie de chaque ECHEC_ historique, supprimer les doublons
        for echec_type in ["ECHEC_nas_faux_positifs", "ECHEC_imprimante_faux_positifs",
                           "ECHEC_silent_mode_spam", "ECHEC_entites_disparues_spam",
                           "ECHEC_shell_script_vide", "ECHEC_formule_solaire",
                           "ECHEC_haiku_oublie_donnees", "ECHEC_budget_sans_alerte"]:
            ids = [r[0] for r in conn_fix.execute(
                "SELECT id FROM decisions_log WHERE action=? ORDER BY id ASC", (echec_type,)
            ).fetchall()]
            if len(ids) > 1:
                conn_fix.execute(
                    f"DELETE FROM decisions_log WHERE action=? AND id NOT IN ({ids[0]})",
                    (echec_type,)
                )
        conn_fix.commit()
        conn_fix.close()
        log.info("🧹 Doublons échecs historiques purgés")
    except Exception as ex_fix:
        log.error(f"Purge doublons: {ex_fix}")

    # ═══ INJECTION LEÇONS FONDATRICES (une seule fois) ═══
    try:
        _injecter_lecons_fondatrices(DB_PATH)
    except Exception as ex_lf:
        log.error(f"⚠️ Leçons fondatrices: {ex_lf}")


def _injecter_lecons_fondatrices(conn_or_path=None):
    """Injecte les leçons apprises par l'échec — exécuté une seule fois au premier démarrage.
    Chaque leçon est un échec documenté + la règle qui en découle."""
    import sqlite3 as _sq

    if isinstance(conn_or_path, str):
        conn = _sq.connect(conn_or_path)
    elif conn_or_path is None:
        conn = _sq.connect(DB_PATH)
    else:
        conn = conn_or_path

    # Vérifier si déjà injecté (LIKE pour matcher lecon_fondatrice:echec:...)
    deja = conn.execute("SELECT COUNT(*) FROM expertise WHERE source LIKE 'lecon_fondatrice%'").fetchone()[0]
    if deja > 0:
        if isinstance(conn_or_path, str) or conn_or_path is None:
            conn.close()
        return  # Déjà fait

    now_iso = datetime.now().isoformat()

    lecons = [
        # ═══ ÉCHEC 1 : Faux positifs NAS (13/03/2026) ═══
        ("monitoring",
         "NAS : ne JAMAIS surveiller button.*, automation.*, switch.*, update.*, binary_sensor.* — seuls les sensor.* comptent",
         0.9, "echec:28_faux_positifs_nas_13mars"),
        ("monitoring",
         "NAS : un état numérique (température, espace To) n'est PAS un volume dégradé — vérifier que c'est du texte avant d'alerter",
         0.9, "echec:temperature_26C_confondue_volume_degrade"),
        ("monitoring",
         "NAS : espace disque alerter UNIQUEMENT si unité=% ET valeur>90% — pas sur les valeurs brutes en To",
         0.9, "echec:espace_1To_faux_positif"),
        ("monitoring",
         "NAS : le statut 'attention' sur un volume Synology EST une vraie alerte — ne pas ignorer",
         0.9, "echec:vrai_positif_synology_attention"),

        # ═══ ÉCHEC 2 : Faux positifs imprimante (13/03/2026) ═══
        ("monitoring",
         "Imprimante : OctoPrint n'est PAS l'imprimante Brother — exclure octoprint/octopi/3d_print",
         0.95, "echec:octoprint_28_faux_positifs"),
        ("monitoring",
         "Imprimante : surveiller UNIQUEMENT sensor.* avec unité % contenant ink/toner/black/cyan/magenta/yellow",
         0.9, "echec:tous_domaines_imprimante_alertes"),
        ("monitoring",
         "Imprimante : automation.* et button.* ne sont JAMAIS des capteurs physiques — toujours exclure",
         0.9, "echec:automations_alertees_comme_offline"),

        # ═══ ÉCHEC 3 : silent_mode PAC (11/03/2026) ═══
        ("zigbee",
         "Zigbee : switch.*_silent_mode, *_powerful_mode, *_child_lock sont des sous-entités logiques PAC — unavailable est NORMAL",
         0.95, "echec:silent_mode_spam_permanent"),

        # ═══ ÉCHEC 4 : Entités disparues spam (13/03/2026) ═══
        ("monitoring",
         "Entités disparues : UNE seule alerte avec boutons, puis silence — jamais de spam toutes les 4h",
         0.9, "echec:spam_entites_disparues_4h"),

        # ═══ ÉCHEC 5 : cmd_claude_autonome shell script (11/03/2026) ═══
        ("code",
         "Ne JAMAIS dépendre d'un shell script externe quand Python peut lire le fichier directement",
         0.85, "echec:cmd_claude_shell_script_vide"),

        # ═══ ÉCHEC 6 : Formule solaire (11/03/2026) ═══
        ("energie",
         "Couverture solaire = production / (EDF + production) × 100 — Ecojoko = EDF seul, PAS la conso totale",
         0.95, "echec:formule_solaire_incorrecte"),

        # ═══ ÉCHEC 7 : cmd_energie dépendance Haiku (12/03/2026) ═══
        ("code",
         "Les rapports de données brutes doivent être structurés en Python — NE PAS envoyer à Haiku pour résumer, il oublie des données",
         0.9, "echec:haiku_oublie_pac_seche_linge"),

        # ═══ ÉCHEC 8 : Budget sans alerte (12/03/2026) ═══
        ("monitoring",
         "Budget API : alerter par paliers dédupliqués (50/80/90/100%) — ne pas laisser l'utilisateur découvrir un budget vide",
         0.85, "echec:budget_epuise_sans_alerte"),

        # ═══ RÈGLES ARCHITECTURALES ═══
        ("code",
         "Chaque pattern entity_id doit être testé contre les VRAIS entity_id de HA — jamais de pattern trop large",
         0.8, "principe:patterns_precis"),
        ("code",
         "Un domaine (button, automation, switch, update) n'est JAMAIS un capteur physique — toujours filtrer par domaine en premier",
         0.95, "principe:domaines_non_physiques"),
        ("general",
         "Chaque alerte doit être dédupliquée via _alerter_si_nouveau — JAMAIS d'alerte brute répétée",
         0.9, "principe:deduplication_alertes"),
        ("general",
         "Toute erreur doit être loguée dans decisions_log via apprentissage_log_echec — pas juste dans les logs fichier",
         0.8, "principe:tracer_les_echecs"),
        ("general",
         "Avant de surveiller une catégorie, vérifier les entity_id réels avec /diag_carto — ne pas deviner",
         0.85, "principe:verifier_avant_coder"),
        ("monitoring",
         "Baselines : minimum 30 mesures avant d'alerter — 10 mesures = trop de bruit, faux positifs garantis",
         0.9, "echec:baselines_10_mesures_faux_positifs_14mars"),
        ("monitoring",
         "Baselines production solaire : ignorer si baseline < 50W, seuil écart > 200% (nuages = variations normales)",
         0.9, "echec:baseline_solaire_0W_nuit_alertee"),
        ("monitoring",
         "Production solaire 0W : confirmer sur 2 cycles consécutifs avant d'alerter — un glitch capteur = faux positif",
         0.85, "echec:solaire_0W_faux_positif_14mars"),
        ("monitoring",
         "Seuil entités hors ligne : 30% minimum (pas 15%) — beaucoup d'entités sont normalement unavailable dans HA",
         0.85, "echec:21pct_entites_ko_faux_positif"),
        ("monitoring",
         "Conso EDF extrême : seuil 8000W (pas 5000W) — four + PAC + machine = facilement 5000W en usage normal",
         0.8, "principe:seuil_conso_realiste"),
        ("code",
         "La surveillance (monitoring + prises) doit tourner TOUJOURS — jamais bloquée par canal_verrouille ou code SMS",
         0.95, "echec:seche_linge_non_detecte_canal_verrouille_14mars"),
        ("code",
         "canal_verrouille ne doit bloquer QUE les commandes Telegram interactives — pas les threads de fond",
         0.95, "echec:monitoring_gele_apres_restart"),
    ]

    for cat, insight, conf, source in lecons:
        conn.execute(
            "INSERT OR IGNORE INTO expertise (categorie, insight, confiance, nb_validations, source, created_at, updated_at) "
            "VALUES (?, ?, ?, 1, ?, ?, ?)",
            (cat, insight, conf, f"lecon_fondatrice:{source}", now_iso, now_iso)
        )

    # Loguer les échecs dans decisions_log — UNE SEULE FOIS
    # Guard : vérifier si déjà injecté (évite les doublons à chaque restart)
    deja_echecs = conn.execute(
        "SELECT COUNT(*) FROM decisions_log WHERE contexte LIKE '%historique_fondateur%'"
    ).fetchone()[0]
    if deja_echecs == 0:
        echecs_historiques = [
            ("ECHEC_nas_faux_positifs", "28 faux positifs NAS : button.*, automation.*, températures et espaces bruts alertés comme 'volume dégradé'"),
            ("ECHEC_imprimante_faux_positifs", "28 faux positifs imprimante : OctoPrint + automations alertés comme 'imprimante hors ligne'"),
            ("ECHEC_silent_mode_spam", "switch.pompe_a_chaleur_air_eau_silent_mode spammait 'device Zigbee hors ligne'"),
            ("ECHEC_entites_disparues_spam", "5 entités supprimées alertées toutes les 4h sans fin"),
            ("ECHEC_shell_script_vide", "cmd_claude_autonome appelait un shell script qui retournait du vide"),
            ("ECHEC_formule_solaire", "Couverture solaire calculée sur EDF seul au lieu de EDF+production"),
            ("ECHEC_haiku_oublie_donnees", "cmd_energie envoyait tout à Haiku qui oubliait PAC et sèche-linge"),
            ("ECHEC_budget_sans_alerte", "Budget API épuisé sans aucune alerte préalable"),
        ]
        for action, description in echecs_historiques:
            conn.execute(
                "INSERT INTO decisions_log (action, contexte, resultat, succes, created_at) VALUES (?, ?, ?, 0, ?)",
                (action, '{"source": "historique_fondateur"}', description, now_iso)
            )

    conn.commit()
    log.info(f"📕 {len(lecons)} leçons fondatrices injectées + {len(echecs_historiques)} échecs historiques")


def mem_set(cle, valeur):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'INSERT OR REPLACE INTO memoire (cle, valeur, updated_at) VALUES (?, ?, ?)',
        (cle, str(valeur), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def mem_get(cle, defaut=None):
    conn = sqlite3.connect(DB_PATH)
    r = conn.execute('SELECT valeur FROM memoire WHERE cle=?', (cle,)).fetchone()
    conn.close()
    return r[0] if r else defaut


def log_token_usage(tokens_in, tokens_out):
    mois = datetime.now().strftime("%Y-%m")
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        '''INSERT INTO tokens (mois, tokens_in, tokens_out) VALUES (?, ?, ?)
           ON CONFLICT(mois) DO UPDATE SET
           tokens_in = tokens_in + ?, tokens_out = tokens_out + ?''',
        (mois, tokens_in, tokens_out, tokens_in, tokens_out)
    )
    conn.commit()
    conn.close()


def get_token_usage():
    mois = datetime.now().strftime("%Y-%m")
    conn = sqlite3.connect(DB_PATH)
    r = conn.execute('SELECT tokens_in, tokens_out FROM tokens WHERE mois=?', (mois,)).fetchone()
    conn.close()
    return r if r else (0, 0)


def add_historique(role, contenu):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'INSERT INTO historique (role, contenu, created_at) VALUES (?, ?, ?)',
        (role, contenu, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_historique(n=6):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        'SELECT role, contenu FROM historique ORDER BY id DESC LIMIT ?', (n,)
    ).fetchall()
    conn.close()
    return list(reversed(rows))


def cartographie_get(entity_id):
    conn = sqlite3.connect(DB_PATH)
    r = conn.execute(
        'SELECT categorie, sous_categorie, piece FROM cartographie WHERE entity_id=?',
        (entity_id,)
    ).fetchone()
    conn.close()
    return r


def cartographie_get_par_categorie(categorie):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        'SELECT entity_id, sous_categorie, piece FROM cartographie WHERE categorie=?',
        (categorie,)
    ).fetchall()
    conn.close()
    return rows


def cartographie_get_toutes_categories():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute('SELECT DISTINCT categorie FROM cartographie').fetchall()
    conn.close()
    return [r[0] for r in rows]


def cartographie_get_toutes():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute('SELECT entity_id, categorie FROM cartographie').fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def batterie_set(entity_id, piece, valeur):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        '''INSERT OR REPLACE INTO batteries
           (entity_id, piece, derniere_valeur, updated_at)
           VALUES (?, ?, ?, ?)''',
        (entity_id, piece, valeur, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def batterie_get_derniere_alerte(entity_id):
    conn = sqlite3.connect(DB_PATH)
    r = conn.execute(
        'SELECT derniere_alerte FROM batteries WHERE entity_id=?', (entity_id,)
    ).fetchone()
    conn.close()
    return r[0] if r else None


def batterie_set_alerte(entity_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'UPDATE batteries SET derniere_alerte=? WHERE entity_id=?',
        (datetime.now().isoformat(), entity_id)
    )
    conn.commit()
    conn.close()


def role_get(role):
    """Retourne l'entity_id assigné à un rôle, ou None"""
    conn = sqlite3.connect(DB_PATH)
    r = conn.execute("SELECT entity_id FROM roles WHERE role=?", (role,)).fetchone()
    conn.close()
    return r[0] if r else None


def role_set(role, entity_id, source="auto", confiance=0.5):
    """Assigne un entity_id à un rôle"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO roles (role, entity_id, confiance, source, updated_at) VALUES (?, ?, ?, ?, ?)",
        (role, entity_id, confiance, source, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    log.info(f"🎯 Rôle {role} → {entity_id} (confiance {confiance:.0%}, source: {source})")


def role_get_all():
    """Retourne tous les rôles assignés"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT role, entity_id, confiance FROM roles").fetchall()
    conn.close()
    return {r[0]: {"entity_id": r[1], "confiance": r[2]} for r in rows}


def role_val(role, etats_index, default="?"):
    """Raccourci : retourne la valeur d'un rôle depuis l'index des états"""
    eid = role_get(role)
    if not eid:
        return default
    e = etats_index.get(eid)
    if e and e["state"] not in ("unavailable", "unknown"):
        return e["state"]
    return default


def role_decouvrir(etats):
    """Auto-découverte des rôles — analyse tous les entity_id de HA.
    Fonctionne sur N'IMPORTE quelle installation HA."""
    import re as _re
    index = {e["entity_id"]: e for e in etats}
    roles_actuels = role_get_all()
    nb_decouvertes = 0

    for role, definition in ROLES_DEFINIS.items():
        # Si déjà assigné avec haute confiance, ne pas écraser
        if role in roles_actuels and roles_actuels[role]["confiance"] >= 0.8:
            # Vérifier que l'entité existe encore
            if roles_actuels[role]["entity_id"] in index:
                continue

        desc = definition["description"]
        dc_cibles = definition.get("device_class", [])
        unit_cibles = definition.get("unit", [])
        patterns = definition.get("patterns", [])
        domain_cible = definition.get("domain", "sensor")

        meilleur_candidat = None
        meilleure_score = 0

        for eid, e in index.items():
            domaine = eid.split(".")[0]

            # Filtrer par domaine si spécifié
            if domain_cible and domain_cible != "sensor":
                if domaine != domain_cible:
                    continue
            elif domaine not in ("sensor",):
                continue

            attrs = e.get("attributes", {})
            dc = attrs.get("device_class", "")
            unit = attrs.get("unit_of_measurement", "")
            fname = attrs.get("friendly_name", "").lower()
            eid_low = eid.lower()

            score = 0

            # Score device_class
            if dc_cibles and dc in dc_cibles:
                score += 3

            # Score unité
            if unit_cibles and unit in unit_cibles:
                score += 2

            # Score patterns entity_id ou friendly_name
            pattern_match = False
            for pattern in patterns:
                if _re.search(pattern, eid_low) or _re.search(pattern, fname):
                    score += 4
                    pattern_match = True
                    break

            # Score domaine exact
            if domain_cible and domaine == domain_cible:
                score += 1

            # Pénalité si unavailable
            if e["state"] in ("unavailable", "unknown"):
                score -= 2

            # Si des patterns sont définis, au moins un doit matcher
            # Sinon le score seul (device_class+unit) donne des faux positifs
            # Ex: soufflant chambre (power/W) ≠ batterie puissance
            if patterns and not pattern_match:
                continue

            if score > meilleure_score:
                meilleure_score = score
                meilleur_candidat = eid

        if meilleur_candidat and meilleure_score >= 3:
            confiance = min(1.0, meilleure_score / 10)
            role_set(role, meilleur_candidat, "auto_decouverte", confiance)
            nb_decouvertes += 1

    if nb_decouvertes > 0:
        log.info(f"🎯 {nb_decouvertes} rôle(s) découvert(s)")

    return nb_decouvertes


def role_decouvrir_baselines():
    """Construit BASELINE_ENTITIES dynamiquement à partir des rôles découverts."""
    roles_baseline = {
        "conso_temps_reel": "conso_w",
        "production_solaire_w": "production_w",
        "pac_conso": "conso_pac_w",
        "temp_interieure": "temp_int",
        "temp_exterieure": "temp_ext",
    }
    result = {}
    for role, label in roles_baseline.items():
        eid = role_get(role)
        if eid:
            result[eid] = label
    return result


def entites_connues_maj(entity_id, categorie):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        '''INSERT OR REPLACE INTO entites_connues
           (entity_id, categorie, vu_la_derniere_fois)
           VALUES (?, ?, ?)''',
        (entity_id, categorie, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def entites_connues_get_toutes():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute('SELECT entity_id, categorie FROM entites_connues').fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def appareil_get(entity_id):
    """Retourne le type d'appareil pour une prise, ou None si pas encore identifié."""
    try:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT type_appareil, nom_personnalise, surveiller FROM appareils WHERE entity_id=?",
            (entity_id,)
        ).fetchone()
        conn.close()
        if row:
            return {"type": row[0], "nom": row[1], "surveiller": bool(row[2])}
    except Exception:
        pass
    return None


def appareil_set(entity_id, type_appareil, nom=None):
    """Enregistre le type d'appareil pour une prise."""
    surveiller = 0 if type_appareil == "ignorer" else 1
    if not nom:
        nom = TYPES_APPAREILS.get(type_appareil, type_appareil)
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT OR REPLACE INTO appareils (entity_id, type_appareil, nom_personnalise, surveiller, created_at) VALUES (?, ?, ?, ?, ?)",
            (entity_id, type_appareil, nom, surveiller, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        log.info(f"🏷️ Appareil : {entity_id} → {type_appareil} ({nom})")
    except Exception as e:
        log.error(f"appareil_set: {e}")


def enregistrer_economie(type_eco, description, euros, kwh=0, source="auto"):
    """Enregistre une économie dans la table economies + log succès."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO economies (type, description, euros, kwh_economises, source, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (type_eco, description, round(euros, 4), round(kwh, 4), source, datetime.now().isoformat())
        )
        conn.execute(
            "INSERT INTO decisions_log (action, contexte, resultat, succes, created_at) VALUES (?, ?, ?, 1, ?)",
            ("ECONOMIE", json.dumps({"type": type_eco, "eur": round(euros, 4)}, ensure_ascii=False),
             description[:100], datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        log.error(f"économie: {e}")


def get_economies_mois(mois=None):
    """Retourne le total des économies pour un mois donné."""
    if not mois:
        mois = datetime.now().strftime("%Y-%m")
    try:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT COALESCE(SUM(euros), 0), COALESCE(SUM(kwh_economises), 0), COUNT(*) "
            "FROM economies WHERE created_at LIKE ?",
            (f"{mois}%",)
        ).fetchone()
        # Par type
        types = conn.execute(
            "SELECT type, SUM(euros), COUNT(*) FROM economies WHERE created_at LIKE ? GROUP BY type",
            (f"{mois}%",)
        ).fetchall()
        conn.close()
        return {
            "total_eur": row[0], "total_kwh": row[1], "nb_actions": row[2],
            "par_type": {t: {"eur": e, "nb": n} for t, e, n in types}
        }
    except Exception:
        return {"total_eur": 0, "total_kwh": 0, "nb_actions": 0, "par_type": {}}


def zigbee_absence_creer(entity_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        '''INSERT OR REPLACE INTO zigbee_absences
           (entity_id, hors_ligne_depuis, statut, alerte_envoyee)
           VALUES (?, ?, 'en_attente', ?)''',
        (entity_id, datetime.now().isoformat(), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def zigbee_absence_get(entity_id):
    conn = sqlite3.connect(DB_PATH)
    r = conn.execute(
        'SELECT hors_ligne_depuis, statut FROM zigbee_absences WHERE entity_id=? AND retour_en_ligne IS NULL',
        (entity_id,)
    ).fetchone()
    conn.close()
    return r


def zigbee_absence_statut(entity_id, statut):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'UPDATE zigbee_absences SET statut=? WHERE entity_id=? AND retour_en_ligne IS NULL',
        (statut, entity_id)
    )
    conn.commit()
    conn.close()


def zigbee_absence_retour(entity_id):
    conn = sqlite3.connect(DB_PATH)
    r = conn.execute(
        'SELECT statut FROM zigbee_absences WHERE entity_id=? AND retour_en_ligne IS NULL',
        (entity_id,)
    ).fetchone()
    if r and r[0] == 'anormal':
        conn.execute(
            'UPDATE zigbee_absences SET retour_en_ligne=? WHERE entity_id=? AND retour_en_ligne IS NULL',
            (datetime.now().isoformat(), entity_id)
        )
        conn.commit()
        conn.close()
        return True  # Signaler le retour
    conn.execute(
        'UPDATE zigbee_absences SET retour_en_ligne=? WHERE entity_id=? AND retour_en_ligne IS NULL',
        (datetime.now().isoformat(), entity_id)
    )
    conn.commit()
    conn.close()
    return False


def telegram_send(text, parse_mode=None, force=False):
    """Point central de TOUS les messages sortants — FILTRE APPRENANT.
    Chaque message est validé, loggé, et le filtre s'améliore avec le temps.
    force=True pour les messages système (démarrage, code SMS) qui contournent les filtres."""

    if not text or len(text.strip()) < 5:
        return None

    now_ts = datetime.now()
    text_lower = text.lower()
    raison_filtre = None

    if not force:
        # ═══ FILTRE 1 : PATTERNS APPRIS (SQLite) ═══
        try:
            conn_f = sqlite3.connect(DB_PATH)
            patterns = conn_f.execute(
                "SELECT pattern, raison FROM filtre_messages WHERE actif=1 AND action='bloquer'"
            ).fetchall()
            conn_f.close()
            for pattern, raison in patterns:
                if pattern.lower() in text_lower:
                    raison_filtre = f"pattern_appris:{raison}"
                    break
        except Exception:
            pass

        # ═══ FILTRE 2 : COHÉRENCE DONNÉES (croisement skills) ═══
        if not raison_filtre:
            # Production 0W en plein jour vs skill fenêtre solaire
            if "0 w" in text_lower or ": 0w" in text_lower:
                if any(k in text_lower for k in ["production", "solaire", "créneau", "rappel"]):
                    try:
                        h = now_ts.hour
                        if 9 <= h <= 17:
                            data_sol, nb_sol = skill_get("fenetre_solaire")
                            if data_sol and nb_sol >= 10:
                                j_str, h_str = str(now_ts.weekday()), str(h)
                                if j_str in data_sol and h_str in data_sol[j_str]:
                                    if data_sol[j_str][h_str][0] > 500:
                                        raison_filtre = f"prod_0W_vs_skill_{int(data_sol[j_str][h_str][0])}W"
                    except Exception:
                        pass

        # ═══ FILTRE 3 : ANTI-DOUBLON (5 min) ═══
        if not raison_filtre:
            if not hasattr(telegram_send, "_recent"):
                telegram_send._recent = []
            telegram_send._recent = [(t, m) for t, m in telegram_send._recent
                                      if (now_ts - t).total_seconds() < 300]
            for t, m in telegram_send._recent:
                if m == text:
                    raison_filtre = "doublon_5min"
                    break

        # ═══ FILTRE 4 : ANTI-SPAM (50/jour) ═══
        if not raison_filtre:
            today_key = now_ts.strftime("%Y-%m-%d")
            if not hasattr(telegram_send, "_daily"):
                telegram_send._daily = {"date": today_key, "count": 0}
            if telegram_send._daily["date"] != today_key:
                telegram_send._daily = {"date": today_key, "count": 0}
            telegram_send._daily["count"] += 1
            if telegram_send._daily["count"] > 50:
                raison_filtre = "limite_50_jour"

    # ═══ LOGUER (envoyé ou filtré) ═══
    try:
        conn_log = sqlite3.connect(DB_PATH)
        conn_log.execute(
            "INSERT INTO messages_log (message, envoye, raison_filtre, created_at) VALUES (?, ?, ?, ?)",
            (text[:500], 0 if raison_filtre else 1, raison_filtre, now_ts.isoformat())
        )
        # Garder max 500 entrées
        conn_log.execute("DELETE FROM messages_log WHERE id NOT IN (SELECT id FROM messages_log ORDER BY id DESC LIMIT 500)")
        conn_log.commit()
        conn_log.close()
    except Exception:
        pass

    # ═══ FILTRÉ → ne pas envoyer ═══
    if raison_filtre:
        log.warning(f"🚫 Filtré [{raison_filtre}]: {text[:80]}")
        return None

    # ═══ ENVOI ═══
    if not hasattr(telegram_send, "_recent"):
        telegram_send._recent = []
    telegram_send._recent.append((now_ts, text))

    url = f"https://api.telegram.org/bot{CFG['telegram_token']}/sendMessage"
    payload_tg = {"chat_id": CFG["telegram_chat_id"], "text": text}
    if parse_mode:
        payload_tg["parse_mode"] = parse_mode
    try:
        r = requests.post(url, json=payload_tg, timeout=10)
        if r.status_code == 200:
            count = getattr(telegram_send, "_daily", {}).get("count", "?")
            log.debug(f"📨 [{count}/50]: {text[:80]}")
            return r.json().get("result", {}).get("message_id")
        log.error(f"❌ Telegram {r.status_code}: {r.text[:100]}")
    except Exception as e:
        log.error(f"❌ Telegram: {e}")
    return None


def filtre_apprendre_pattern(pattern, raison, action="bloquer"):
    """L'IA apprend un nouveau pattern de filtrage"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT OR REPLACE INTO filtre_messages (pattern, action, raison, nb_applique, actif, created_at, updated_at) "
            "VALUES (?, ?, ?, 0, 1, ?, ?)",
            (pattern, action, raison, datetime.now().isoformat(), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        log.info(f"🧠 Filtre appris: '{pattern}' → {action} ({raison})")
    except Exception:
        pass


def filtre_analyser_messages():
    """Analyse les messages envoyés et filtrés pour apprendre de nouveaux patterns.
    Appelé toutes les 12h par le moteur d'intelligence."""
    if not verifier_budget():
        return

    conn = sqlite3.connect(DB_PATH)

    # Messages filtrés (les patterns qui marchent)
    filtres = conn.execute(
        "SELECT raison_filtre, COUNT(*) as nb FROM messages_log "
        "WHERE envoye=0 AND raison_filtre IS NOT NULL "
        "GROUP BY raison_filtre ORDER BY nb DESC LIMIT 10"
    ).fetchall()

    # Messages envoyés récents (pour détecter du bruit)
    envoyes = conn.execute(
        "SELECT message, created_at FROM messages_log "
        "WHERE envoye=1 ORDER BY id DESC LIMIT 30"
    ).fetchall()

    # Patterns existants
    patterns_actifs = conn.execute(
        "SELECT pattern, nb_applique FROM filtre_messages WHERE actif=1"
    ).fetchall()

    conn.close()

    if len(envoyes) < 10:
        return  # Pas assez de données

    # Détecter les messages répétitifs envoyés (même préfixe)
    prefixes = {}
    for msg, dt in envoyes:
        prefix = msg[:40]
        prefixes[prefix] = prefixes.get(prefix, 0) + 1

    repetitifs = [(p, n) for p, n in prefixes.items() if n >= 3]
    if repetitifs:
        prompt = (
            "Tu es le filtre anti-bruit de l'assistant domotique.\n"
            "Voici des messages Telegram envoyés fréquemment :\n"
        )
        for prefix, nb in repetitifs[:5]:
            prompt += f"  {nb}x : {prefix}...\n"
        prompt += (
            "\nCes messages sont-ils du BRUIT (répétitifs, non utiles) ou LÉGITIMES ?\n"
            "Réponds en JSON : {\"patterns_bruit\": [\"pattern à filtrer\"], "
            "\"patterns_ok\": [\"pattern légitime\"]}\n"
            "Juste le JSON, rien d'autre."
        )

        try:
            client = anthropic.Anthropic(api_key=CFG["anthropic_api_key"])
            r = client.messages.create(
                model="claude-haiku-4-5-20251001", max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            log_token_usage(r.usage.input_tokens, r.usage.output_tokens)
            texte = r.content[0].text.strip().replace("```json", "").replace("```", "").strip()
            resultat = json.loads(texte)

            for pattern in resultat.get("patterns_bruit", []):
                if pattern and len(pattern) >= 10:
                    filtre_apprendre_pattern(pattern, "detecte_auto_repetitif")

            log.info(f"🧠 Analyse filtre: {len(resultat.get('patterns_bruit', []))} nouveaux patterns")
        except Exception as ex:
            log.error(f"❌ filtre_analyser: {ex}")


def telegram_send_buttons(text, boutons, action_data=None):
    url = f"https://api.telegram.org/bot{CFG['telegram_token']}/sendMessage"
    keyboard = []
    ligne = []
    for i, b in enumerate(boutons):
        ligne.append({"text": b["text"], "callback_data": b["callback_data"]})
        if len(ligne) == 3:
            keyboard.append(ligne)
            ligne = []
    if ligne:
        keyboard.append(ligne)
    payload = {
        "chat_id": CFG["telegram_chat_id"],
        "text": text,
        "reply_markup": {"inline_keyboard": keyboard}
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            msg_id = r.json().get("result", {}).get("message_id")
            if action_data and msg_id:
                en_attente_reponse[msg_id] = action_data
            return msg_id
        log.error(f"❌ Boutons Telegram {r.status_code}")
    except Exception as e:
        log.error(f"❌ Boutons Telegram: {e}")
    return None


def telegram_send_photo(image_bytes, caption=""):
    """Envoie une image sur Telegram via sendPhoto."""
    try:
        import io
        url = f"https://api.telegram.org/bot{CFG['telegram_token']}/sendPhoto"
        files = {"photo": ("graph.png", io.BytesIO(image_bytes), "image/png")}
        data = {"chat_id": CFG["telegram_chat_id"]}
        if caption:
            data["caption"] = caption[:1024]
        r = requests.post(url, files=files, data=data, timeout=30)
        if r.status_code == 200:
            return True
        log.error(f"sendPhoto: {r.status_code}")
    except Exception as e:
        log.error(f"sendPhoto: {e}")
    return False


def telegram_answer_callback(callback_query_id, text="✅"):
    url = f"https://api.telegram.org/bot{CFG['telegram_token']}/answerCallbackQuery"
    try:
        requests.post(url, json={"callback_query_id": callback_query_id, "text": text}, timeout=5)
    except Exception:
        pass


def telegram_get_updates(offset=None):
    url = f"https://api.telegram.org/bot{CFG['telegram_token']}/getUpdates"
    params = {"timeout": 5}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return r.json().get("result", [])
    except Exception as e:
        log.error(f"❌ Polling Telegram: {e}")
    return []


def generer_code_auth():
    global code_auth
    code_auth = str(random.randint(100000, 999999))
    return code_auth


def envoyer_code_sms():
    """Envoie le code de sécurité par le canal configuré.
    Méthodes supportées (priorité) :
    1. Free Mobile API (sms_method=free_mobile)
    2. Notification HA Companion (sms_method=ha_notify)
    3. Email (sms_method=email)
    """
    global code_auth
    code = generer_code_auth()
    # Défense absolue : JAMAIS envoyer None
    if not code or code == "None" or not code.isdigit() or len(code) != 6:
        log.error(f"Code SMS invalide: '{code}' — régénération forcée")
        code = str(random.randint(100000, 999999))
        code_auth = code
    log.info(f"Code SMS généré: {code} (method={CFG.get('sms_method', '?')})")
    method = CFG.get("sms_method", "free_mobile")

    # ═══ FREE MOBILE API ═══
    if method == "free_mobile":
        user = CFG.get("free_mobile_user", "")
        passwd = CFG.get("free_mobile_pass", "")
        if user and passwd:
            try:
                url = f"https://smsapi.free-mobile.fr/sendmsg?user={user}&pass={passwd}&msg=CodeIA:{code}"
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    log.info(f"✅ SMS Free envoyé: {code}")
                    return True
                log.error(f"❌ SMS Free {r.status_code}")
            except Exception as e:
                log.error(f"❌ SMS Free: {e}")

    # ═══ NOTIFICATION HA COMPANION ═══
    elif method == "ha_notify":
        notify_service = CFG.get("ha_notify_service", "")
        if notify_service and CFG.get("ha_url") and CFG.get("ha_token"):
            try:
                url = f"{CFG['ha_url']}/api/services/notify/{notify_service}"
                headers = {"Authorization": f"Bearer {CFG['ha_token']}", "Content-Type": "application/json"}
                payload = {
                    "title": "🔐 AssistantIA — Code de sécurité",
                    "message": f"Votre code : {code}",
                    "data": {"priority": "high", "ttl": 0}
                }
                r = requests.post(url, json=payload, headers=headers, verify=False, timeout=10)
                if r.status_code == 200:
                    log.info(f"✅ Notification HA envoyée: {code}")
                    return True
                log.error(f"❌ Notify HA {r.status_code}")
            except Exception as e:
                log.error(f"❌ Notify HA: {e}")

    # ═══ EMAIL ═══
    elif method == "email":
        mail = CFG.get("mail_dest", "")
        if mail and CFG.get("smtp_host"):
            try:
                msg_mail = MIMEText(f"Votre code de sécurité AssistantIA : {code}")
                msg_mail["Subject"] = f"🔐 Code AssistantIA : {code}"
                msg_mail["From"] = CFG.get("smtp_user", "")
                msg_mail["To"] = mail
                with smtplib.SMTP(CFG["smtp_host"], CFG.get("smtp_port", 587)) as s:
                    s.starttls()
                    s.login(CFG["smtp_user"], CFG["smtp_pass"])
                    s.send_message(msg_mail)
                log.info(f"✅ Email code envoyé: {code}")
                return True
            except Exception as e:
                log.error(f"❌ Email code: {e}")

    # Aucune méthode configurée
    log.error(f"❌ Aucune méthode SMS configurée (method={method})")
    return False


def verifier_code(message):
    global canal_verrouille, code_auth
    if message.strip() == code_auth:
        canal_verrouille = False
        code_auth = None
        mem_set("dernier_deverrouillage", datetime.now().isoformat())
        log.info("✅ Canal déverrouillé + sauvegardé (24h sans SMS)")
        return True
    return False


def ha_get(endpoint):
    if not CFG.get("ha_url"):
        return None
    url = f"{CFG['ha_url']}/api/{endpoint}"
    headers = {"Authorization": f"Bearer {CFG['ha_token']}"}
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=15)
        if r.status_code == 200:
            return r.json()
        log.warning(f"⚠️ HA {endpoint}: {r.status_code}")
    except Exception as e:
        log.error(f"❌ HA {endpoint}: {e}")
    return None


def ha_post(endpoint, data):
    url = f"{CFG['ha_url']}/api/{endpoint}"
    headers = {"Authorization": f"Bearer {CFG['ha_token']}", "Content-Type": "application/json"}
    try:
        r = requests.post(url, headers=headers, json=data, verify=False, timeout=15)
        return r.json()
    except Exception as e:
        log.error(f"❌ HA POST {endpoint}: {e}")
    return None


def ha_get_forecast(entity_id=None, forecast_type="daily"):
    if entity_id is None:
        entity_id = role_get("meteo") or "weather.pavillons_sous_bois"
    """Récupère les prévisions météo via le service weather.get_forecasts (HA 2024+)"""
    try:
        # HA 2024+ exige ?return_response pour les services qui retournent des données
        url = f"{CFG['ha_url']}/api/services/weather/get_forecasts?return_response"
        headers = {"Authorization": f"Bearer {CFG['ha_token']}", "Content-Type": "application/json"}
        data = {"entity_id": entity_id, "type": forecast_type}
        r = requests.post(url, headers=headers, json=data, verify=False, timeout=15)
        if r.status_code == 200:
            result = r.json()
            # Format : {"service_response": {"weather.xxx": {"forecast": [...]}}}
            service_resp = result.get("service_response", result)
            if isinstance(service_resp, dict):
                entity_data = service_resp.get(entity_id, {})
                if isinstance(entity_data, dict):
                    return entity_data.get("forecast", [])
            # Fallback direct
            if isinstance(result, dict) and entity_id in result:
                return result[entity_id].get("forecast", [])
        else:
            log.debug(f"⚠️ Forecast HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        log.debug(f"⚠️ Forecast {entity_id}: {e}")
    return []


def ha_get_etat(entity_id):
    """Récupère l'état d'une entité spécifique"""
    return ha_get(f"states/{entity_id}")


def ha_est_jour(etats):
    """Retourne True si c'est entre lever et coucher du soleil."""
    index = {e["entity_id"]: e for e in etats}

    # Source 1 : sun.sun
    sun = index.get("sun.sun")
    if sun:
        return sun["state"] == "above_horizon"

    # Source 2 : weather.*
    for e in etats:
        if e["entity_id"].startswith("weather."):
            attrs = e.get("attributes", {})
            sunrise = attrs.get("sunrise") or attrs.get("next_rising")
            sunset  = attrs.get("sunset")  or attrs.get("next_setting")
            if sunrise and sunset:
                try:
                    now = datetime.now(timezone.utc)
                    sr = datetime.fromisoformat(sunrise.replace("Z", "+00:00"))
                    ss = datetime.fromisoformat(sunset.replace("Z", "+00:00"))
                    return sr <= now <= ss
                except Exception:
                    pass

    return True


def ha_get_production_solaire_actuelle(etats):
    """Retourne la puissance solaire instantanée totale en W.
    Sources : ECU Current Power (APSystems) + Prise Anker (injection Solarbank).
    Retourne 0 si pas de panneaux solaires installés."""
    if not role_get("production_solaire_w"):
        return 0
    if not ha_est_jour(etats):
        return 0

    index = {e["entity_id"]: e for e in etats}
    total_w = 0

    # Source 1 : APSystems via ECU (mise à jour toutes les 5 min)
    eid_aps = role_get("production_solaire_w") or "sensor.ecu_current_power"
    e_aps = index.get(eid_aps)
    if e_aps and e_aps["state"] not in ("unavailable", "unknown"):
        try:
            val = float(e_aps["state"])
            if 0 <= val <= 20000:
                total_w += val
        except Exception:
            pass

    # Source 2 : Anker Solarbank injection (prise Anker W)
    # L'Anker charge sa batterie à 100% PUIS injecte le surplus
    eid_anker = role_get("batterie_puissance")
    if eid_anker:
        e_anker = index.get(eid_anker)
        if e_anker and e_anker["state"] not in ("unavailable", "unknown"):
            try:
                val = float(e_anker["state"])
                if 0 <= val <= 5000:
                    total_w += val
            except Exception:
                pass

    return total_w


def _alerter_si_nouveau(cle, message, delai_h=2):
    """Envoie une alerte uniquement si pas déjà envoyée récemment"""
    derniere = mem_get(f"alerte_{cle}")
    if derniere:
        try:
            delta = (datetime.now() - datetime.fromisoformat(derniere)).total_seconds()
            if delta < delai_h * 3600:
                return
        except Exception:
            pass
    telegram_send(message)
    mem_set(f"alerte_{cle}", datetime.now().isoformat())
    log.warning(f"Alerte: {message[:80]}")


def skill_get(nom):
    """Lit un skill depuis SQLite"""
    conn = sqlite3.connect(DB_PATH)
    r = conn.execute("SELECT donnees, nb_apprentissages FROM skills WHERE nom=?", (nom,)).fetchone()
    conn.close()
    if r:
        return json.loads(r[0]), r[1]
    return {}, 0


def skill_set(nom, donnees, nb=None):
    """Écrit un skill dans SQLite"""
    conn = sqlite3.connect(DB_PATH)
    ancien = conn.execute("SELECT nb_apprentissages FROM skills WHERE nom=?", (nom,)).fetchone()
    nb_val = nb if nb is not None else ((ancien[0] + 1) if ancien else 1)
    conn.execute(
        "INSERT OR REPLACE INTO skills (nom, donnees, nb_apprentissages, updated_at) VALUES (?, ?, ?, ?)",
        (nom, json.dumps(donnees, ensure_ascii=False), nb_val, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def tarif_get():
    """Retourne la configuration tarifaire de l'utilisateur"""
    data, nb = skill_get("tarification")
    if data and "type" in data:
        return data
    return TARIFS_DEFAUT["base"]  # Défaut si pas configuré


def _est_heure_creuse_plages(heures_creuses):
    """Vérifie si l'heure actuelle est dans une plage HC"""
    now = datetime.now()
    heure_actuelle = now.hour * 60 + now.minute
    for plage in heures_creuses:
        try:
            debut_str, fin_str = plage.split("-")
            dh, dm = map(int, debut_str.split(":"))
            fh, fm = map(int, fin_str.split(":"))
            debut_min = dh * 60 + dm
            fin_min = fh * 60 + fm
            if debut_min > fin_min:
                if heure_actuelle >= debut_min or heure_actuelle < fin_min:
                    return True
            else:
                if debut_min <= heure_actuelle < fin_min:
                    return True
        except Exception:
            pass
    return False


def _est_weekend_ou_ferie():
    """Vérifie si on est en week-end ou jour férié"""
    now = datetime.now()
    if now.weekday() >= 5:  # Samedi=5, Dimanche=6
        return True
    # Jours fériés français
    y = now.year
    feries = [
        (1, 1), (5, 1), (5, 8), (7, 14), (8, 15),
        (11, 1), (11, 11), (12, 25),
    ]
    # Pâques (approximation — pour être exact il faudrait un calcul complet)
    if (now.month, now.day) in feries:
        return True
    return False


def _est_jour_choisi(tarif):
    """Vérifie si aujourd'hui est le jour choisi (Week-End Plus)"""
    jour_choisi = tarif.get("jour_choisi")
    if jour_choisi is not None:
        return datetime.now().weekday() == jour_choisi
    return False


def tarif_prix_kwh_actuel():
    """Retourne le prix du kWh actuel selon le type d'offre, le jour et l'heure"""
    tarif = tarif_get()
    ttype = tarif.get("type", "base")

    if ttype == "base":
        return tarif.get("prix_kwh", 0.2516)

    if ttype == "hphc":
        hc = _est_heure_creuse_plages(tarif.get("heures_creuses", []))
        return tarif.get("prix_hc" if hc else "prix_hp", 0.25)

    if ttype == "weekend":
        if _est_weekend_ou_ferie():
            return tarif.get("prix_weekend", 0.1538)
        return tarif.get("prix_semaine", 0.2038)

    if ttype == "weekend_hphc":
        if _est_weekend_ou_ferie():
            return tarif.get("prix_weekend", 0.1618)
        hc = _est_heure_creuse_plages(tarif.get("heures_creuses", []))
        return tarif.get("prix_hc" if hc else "prix_hp_semaine", 0.2153)

    if ttype == "weekend_plus":
        if _est_weekend_ou_ferie() or _est_jour_choisi(tarif):
            return tarif.get("prix_weekend_jour", 0.1604)
        return tarif.get("prix_semaine", 0.2133)

    if ttype == "weekend_plus_hphc":
        if _est_weekend_ou_ferie() or _est_jour_choisi(tarif):
            return tarif.get("prix_hc_weekend_jour", 0.166)
        hc = _est_heure_creuse_plages(tarif.get("heures_creuses", []))
        if hc:
            return tarif.get("prix_hc_weekend_jour", 0.166)
        return tarif.get("prix_hp_semaine", 0.2213)

    if ttype == "tempo":
        # Tempo simplifié — jour bleu par défaut (le plus courant)
        hc = _est_heure_creuse_plages(tarif.get("heures_creuses", []))
        return tarif.get("prix_bleu_hc" if hc else "prix_bleu_hp", 0.12)

    return 0.2516


def tarif_est_heure_creuse():
    """Retourne True si on est en heures creuses"""
    tarif = tarif_get()
    if tarif.get("type") != "hphc":
        return False
    prix_hc = tarif.get("prix_hc", 0.2068)
    return tarif_prix_kwh_actuel() == prix_hc


def envoyer_email(sujet, corps, piece_jointe=None):
    try:
        msg = MIMEMultipart()
        msg["From"] = CFG["smtp_user"]
        msg["To"]   = CFG["mail_dest"]
        msg["Subject"] = sujet
        msg.attach(MIMEText(corps, "plain", "utf-8"))
        if piece_jointe and os.path.exists(piece_jointe):
            with open(piece_jointe, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(piece_jointe)}")
            msg.attach(part)
        s = smtplib.SMTP(CFG["smtp_host"], CFG["smtp_port"])
        s.starttls()
        s.login(CFG["smtp_user"], CFG["smtp_pass"])
        s.sendmail(CFG["smtp_user"], CFG["mail_dest"], msg.as_string())
        s.quit()
        log.info(f"✅ Email: {sujet}")
        return True
    except Exception as e:
        log.error(f"❌ Email: {e}")
        return False


def _wizard_step():
    """Retourne l'étape courante du wizard, ou None si terminé."""
    return CFG.get("_wizard_step")


def _wizard_save_config():
    """Sauvegarde la config pendant le wizard."""
    with open(CONFIG_PATH, "w") as f:
        json.dump(CFG, f, indent=2)


def charger_comportement():
    if os.path.exists(COMPORTEMENT):
        with open(COMPORTEMENT) as f:
            return f.read()
    return """Tu es l'assistant domotique de l'utilisateur.
Tu réponds en français, de façon concise et professionnelle.
Tu surveilles la maison et alertes uniquement sur les vrais problèmes.
Priorités : énergie (PAC, solaire, prises), Zigbee, NAS, réseau.

ACTIONS HOME ASSISTANT :
Tu as l'outil ha_call_service pour agir sur les appareils.
Quand l'utilisateur demande une action, utilise DIRECTEMENT l'outil sans poser de question.
NE DEMANDE JAMAIS de confirmation textuelle — le système gère la confirmation par boutons.
NE DIS PAS que tu n'as pas accès à HA — tu as un accès réel via l'outil.
Utilise TOUJOURS l'entity_id exact visible dans l'état HA.
Sois CONCIS : pas de markdown, pas de blocs de code, juste l'action.

RÈGLES ABSOLUES :
- climate auto/heat/cool/fan_only = PAC EN SERVICE
- climate off = PAC ARRÊTÉE
- Onduleurs 0W la nuit = NORMAL
- Batterie Anker < 20% = signaler
- Automations unavailable = normal"""


def verifier_budget():
    tokens_in, tokens_out = get_token_usage()
    cout = (tokens_in * 0.000001) + (tokens_out * 0.000005)
    budget = CFG.get("anthropic_monthly_budget_usd", 10)
    pct = (cout / budget * 100) if budget > 0 else 0

    if pct >= 100:
        _alerter_si_nouveau(
            "budget_100",
            f"🛑 BUDGET API DÉPASSÉ — {cout:.2f}$ / {budget}$ ({pct:.0f}%)\n"
            f"Les commandes IA sont désactivées jusqu'au 1er du mois.\n"
            f"Les commandes locales (/budget /debug /logs /batteries etc.) restent actives.",
            delai_h=12
        )
        return False
    elif pct >= 90:
        _alerter_si_nouveau(
            "budget_90",
            f"🚨 BUDGET API 90% — {cout:.2f}$ / {budget}$\nIl reste ~{(budget - cout):.2f}$ pour ce mois.",
            delai_h=12
        )
    elif pct >= 80:
        _alerter_si_nouveau(
            "budget_80",
            f"⚠️ BUDGET API 80% — {cout:.2f}$ / {budget}$",
            delai_h=24
        )
    elif pct >= 50:
        _alerter_si_nouveau(
            "budget_50",
            f"📊 Budget API 50% — {cout:.2f}$ / {budget}$",
            delai_h=48
        )
    return True


def appel_claude(message_utilisateur, contexte_ha=None):
    if not verifier_budget():
        return "⚠️ Budget API mensuel atteint."

    comportement = charger_comportement()
    system_prompt = comportement
    if contexte_ha:
        system_prompt += f"\n\n=== ÉTAT HOME ASSISTANT ===\n{contexte_ha}"

    historique = get_historique(6)
    messages = [{"role": r, "content": c} for r, c in historique]
    messages.append({"role": "user", "content": message_utilisateur})

    try:
        client = anthropic.Anthropic(api_key=CFG["anthropic_api_key"])
        r = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            system=[{
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}
            }],
            messages=messages,
            tools=HA_TOOLS
        )
        t_in = r.usage.input_tokens
        t_out = r.usage.output_tokens
        t_cache_read = getattr(r.usage, "cache_read_input_tokens", 0)
        t_cache_write = getattr(r.usage, "cache_creation_input_tokens", 0)
        log_token_usage(t_in + t_cache_read + t_cache_write, t_out)
        log.debug(f"Tokens: in={t_in} out={t_out} cache_r={t_cache_read} cache_w={t_cache_write}")

        # Extraire texte + éventuel tool_use
        texte_reponse = ""
        action_demandee = None
        watch_demandee = None
        for block in r.content:
            if block.type == "text":
                texte_reponse += block.text
            elif block.type == "tool_use" and block.name == "ha_call_service":
                action_demandee = block.input
            elif block.type == "tool_use" and block.name == "ha_create_watch":
                watch_demandee = block.input

        add_historique("user", message_utilisateur)

        if action_demandee:
            domain = action_demandee.get("domain", "")
            service = action_demandee.get("service", "")
            entity_id = action_demandee.get("entity_id", "")
            data = action_demandee.get("data", {})

            # Sécurité : domaine autorisé ?
            if domain not in HA_DOMAINES_AUTORISES:
                msg = f"❌ Domaine '{domain}' non autorisé."
                add_historique("assistant", msg)
                return msg

            # Stocker l'action en attente
            action_json = json.dumps({
                "domain": domain, "service": service,
                "entity_id": entity_id, "data": data
            })
            mem_set("ha_action_pending", action_json)

            # Description humaine de l'action
            LABELS = {
                "turn_on": "Allumer", "turn_off": "Éteindre", "toggle": "Basculer",
                "lock": "Verrouiller", "unlock": "Déverrouiller",
                "open_cover": "Ouvrir", "close_cover": "Fermer", "stop_cover": "Arrêter",
                "set_temperature": "Régler température", "set_hvac_mode": "Changer mode",
                "start": "Démarrer", "stop": "Arrêter", "return_to_base": "Retour base",
                "media_play": "Lecture", "media_pause": "Pause", "volume_set": "Volume",
            }
            action_label = LABELS.get(service, service)
            entity_short = entity_id.split(".", 1)[1].replace("_", " ").title() if "." in entity_id else entity_id

            # Message + boutons confirmation (pas de texte Claude = pas de double confirmation)
            confirm_msg = f"🔧 ACTION DEMANDÉE\n━━━━━━━━━━━━━━━━━━\n"
            confirm_msg += f"{action_label} → {entity_short}\n"
            confirm_msg += f"({domain}.{service} sur {entity_id})"
            if data:
                confirm_msg += f"\nParamètres : {json.dumps(data)}"

            boutons = [
                {"text": "✅ Confirmer", "callback_data": "ha_action:confirm"},
                {"text": "❌ Annuler", "callback_data": "ha_action:cancel"},
            ]
            telegram_send_buttons(confirm_msg, boutons)
            add_historique("assistant", f"[ACTION] {action_label} {entity_short}")
            return ""  # Déjà envoyé via buttons

        # ═══ WATCH — Créer une alerte automatique ═══
        if watch_demandee:
            try:
                pattern = watch_demandee.get("entity_pattern", "")
                condition = watch_demandee.get("condition", "")
                state_value = watch_demandee.get("state_value", "")
                message = watch_demandee.get("message", "")
                cooldown = watch_demandee.get("cooldown_min", 60)

                conn = sqlite3.connect(DB_PATH)
                conn.execute(
                    "INSERT INTO watches (entity_pattern, condition, state_value, message, cooldown_min, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (pattern, condition, state_value, message, cooldown, datetime.now().isoformat())
                )
                conn.commit()
                conn.close()

                confirm = f"✅ Alerte créée\n━━━━━━━━━━━━━━━━━━\n"
                confirm += f"📡 Surveillé : {pattern}\n"
                confirm += f"🔍 Condition : {condition}"
                if state_value:
                    confirm += f" {state_value}"
                confirm += f"\n💬 Message : {message}\n"
                confirm += f"⏱️ Cooldown : {cooldown} min"
                telegram_send(confirm)
                add_historique("assistant", f"[WATCH] {pattern} → {condition}")
                log.info(f"✅ Watch créée: {pattern} {condition} {state_value}")
                return ""
            except Exception as e:
                log.error(f"❌ Watch creation: {e}")
                return f"❌ Erreur création alerte : {str(e)[:100]}"

        add_historique("assistant", texte_reponse)
        return texte_reponse
    except anthropic.AuthenticationError:
        return "❌ Clé API Anthropic invalide"
    except Exception as e:
        log.error(f"❌ Claude: {e}")
        return f"❌ Erreur Claude: {str(e)[:100]}"
