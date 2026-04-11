# =============================================================================
# SKILLS.PY — Commandes, cycles, économies, apprentissage, surveillance
# =============================================================================

import json
import logging
import os
import re
import random
import requests
import sqlite3
import time
import threading
import hashlib
import hmac
import anthropic
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler

from shared import *
import shared

# Stdlib imports AFTER wildcard
import json, logging, os, re, random, requests, sqlite3, time, threading
import hashlib, hmac, anthropic
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler

PROFIL_QUESTIONS = [
    {
        "id": "foyer_personnes",
        "question": "👥 Combien de personnes vivent dans le foyer ?",
        "boutons": [
            {"text": "1", "value": "1"},
            {"text": "2", "value": "2"},
            {"text": "3-4", "value": "3-4"},
            {"text": "5+", "value": "5+"},
        ],
        "skill_key": "foyer",
    },
    {
        "id": "foyer_presence",
        "question": "🏠 Quand êtes-vous à la maison en semaine ?",
        "boutons": [
            {"text": "Toujours (télétravail)", "value": "teletravail"},
            {"text": "Matin + soir", "value": "matin_soir"},
            {"text": "Soir uniquement", "value": "soir"},
            {"text": "Variable", "value": "variable"},
        ],
        "skill_key": "foyer",
    },
    {
        "id": "foyer_solaire",
        "question": "☀️ Avez-vous des panneaux solaires ?",
        "boutons": [
            {"text": "Oui", "value": "oui"},
            {"text": "Non", "value": "non"},
            {"text": "En projet", "value": "projet"},
        ],
        "skill_key": "foyer",
    },
    {
        "id": "foyer_solaire_kwc",
        "question": "☀️ Quelle puissance installée (kWc) ?",
        "condition": lambda profil: profil.get("foyer_solaire") == "oui",
        "boutons": [
            {"text": "< 3 kWc", "value": "<3"},
            {"text": "3-6 kWc", "value": "3-6"},
            {"text": "6-9 kWc", "value": "6-9"},
            {"text": "> 9 kWc", "value": ">9"},
        ],
        "skill_key": "foyer",
    },
    {
        "id": "foyer_chauffage",
        "question": "🌡️ Quel est votre chauffage principal ?",
        "boutons": [
            {"text": "PAC (pompe à chaleur)", "value": "pac"},
            {"text": "Électrique (radiateurs)", "value": "electrique"},
            {"text": "Gaz", "value": "gaz"},
            {"text": "Autre (fioul, bois...)", "value": "autre"},
        ],
        "skill_key": "foyer",
    },
    {
        "id": "foyer_eau_chaude",
        "question": "🚿 Eau chaude sanitaire ?",
        "boutons": [
            {"text": "Cumulus électrique", "value": "cumulus"},
            {"text": "Thermodynamique", "value": "thermo"},
            {"text": "Chaudière (gaz/fioul)", "value": "chaudiere"},
            {"text": "Solaire / PAC", "value": "solaire_pac"},
        ],
        "skill_key": "foyer",
    },
    {
        "id": "foyer_assistant_vocal",
        "question": "🗣️ Assistant vocal / domotique ?",
        "boutons": [
            {"text": "Google Nest/Home", "value": "google"},
            {"text": "Alexa", "value": "alexa"},
            {"text": "Siri / HomeKit", "value": "siri"},
            {"text": "Aucun", "value": "aucun"},
        ],
        "skill_key": "foyer",
    },
    {
        "id": "foyer_objectif",
        "question": "🎯 Votre objectif principal ?",
        "boutons": [
            {"text": "💰 Réduire la facture", "value": "reduire_facture"},
            {"text": "☀️ Maximiser le solaire", "value": "maximiser_solaire"},
            {"text": "🔍 Comprendre ma conso", "value": "comprendre"},
            {"text": "🤖 Tout automatiser", "value": "automatiser"},
        ],
        "skill_key": "foyer",
    },
]

CATEGORIES_VALIDES = [
    "energie_solaire",    # APSystems, Anker, micro-onduleurs
    "energie_chauffage",  # PAC, thermostats
    "energie_conso",      # Ecojoko, compteurs
    "prise_connectee",    # prises avec mesure
    "meteo",              # météo
    "reseau_ip",          # device_tracker, nmap
    "reseau_zigbee",      # bridge Z2M
    "matter",             # Matter Bridge
    "nas",                # synology
    "impression",         # imprimante
    "securite",           # alarmes, caméras
    "multimedia",         # TV, enceintes
    "electromenager",     # électroménager
    "systeme_ha",         # updates, addons
    "a_ignorer",          # entités ignorées
]

PATTERNS_AUTO = [
    ("solarbank_e1600", "etat_de_charge",      "energie_batterie",   "soc",        "Batterie Anker Solarbank"),
    ("solarbank_e1600", "mode",                "energie_batterie",   "mode",       "Anker Solarbank mode"),
    ("solarbank_e1600", "puissance_solaire",   "energie_production", "production", "Panneaux Anker W"),
    ("solarbank_e1600", "puissance_de_charge", "energie_batterie",   "charge",     "Anker charge W"),
    ("solarbank_e1600", "puissance_de_sortie", "energie_production", "injection",  "Anker injection W"),
    ("solarbank_e1600", "puissance_de_decharge","energie_batterie",  "decharge",   "Anker décharge W"),
    ("system_anker",    "etat_de_charge",      "energie_batterie",   "soc",        "Système Anker SOC"),
    ("system_anker",    "energie_solaire",     "energie_production", "production", "Système Anker W"),
    ("solar", "production.*maintenant",  "energie_prevision", "temps_reel",  "Prévision solaire instantanée"),
    ("solar", "production.*demain",      "energie_prevision", "j_plus_1",    "Prévision solaire demain"),
    ("weather", "",                      "meteo",             "prevision",    "Station météo"),
]

CRITICITE_ENTITES = {
    "nas":           {"alerte_h": 2,  "label": "NAS"},
    "reseau_zigbee": {"alerte_h": 2,  "label": "Bridge Zigbee"},
    "matter":        {"alerte_h": 2,  "label": "Matter Bridge"},
    "energie_solaire":{"alerte_h": 4, "label": "Énergie solaire"},
    "prise_connectee":{"alerte_h": 24,"label": "Prise connectée"},
    "impression":    {"alerte_h": 24, "label": "Imprimante"},
    "multimedia":    {"alerte_h": 48, "label": "Multimédia"},
}

FOURNISSEURS = {
    "edf": {
        "nom": "EDF",
        "offres": {
            "base": {"nom": "Tarif Bleu Base", "type": "base", "prix_kwh": 0.2516, "abo_mois": 12.44},
            "hphc": {"nom": "Tarif Bleu HP/HC", "type": "hphc", "prix_hp": 0.27, "prix_hc": 0.2068, "abo_mois": 13.01},
            "tempo": {"nom": "Tempo", "type": "tempo", "prix_bleu_hp": 0.1369, "prix_bleu_hc": 0.1056,
                       "prix_blanc_hp": 0.1894, "prix_blanc_hc": 0.1486, "prix_rouge_hp": 0.7562, "prix_rouge_hc": 0.1568, "abo_mois": 13.01},
            "zen": {"nom": "Vert Électrique Zen", "type": "hphc", "prix_hp": 0.2676, "prix_hc": 0.2068, "abo_mois": 12.44},
            "weekend": {"nom": "Zen Week-End", "type": "weekend", "prix_semaine": 0.2038, "prix_weekend": 0.1538, "abo_mois": 14.83},
            "weekend_hphc": {"nom": "Zen Week-End HP/HC", "type": "weekend_hphc", "prix_hp_semaine": 0.2153, "prix_hc": 0.1618, "prix_weekend": 0.1618, "abo_mois": 15.08},
            "weekend_plus": {"nom": "Zen Week-End Plus (Jour choisi)", "type": "weekend_plus", "prix_semaine": 0.2133, "prix_weekend_jour": 0.1604, "abo_mois": 14.83},
            "weekend_plus_hphc": {"nom": "Zen Week-End Plus HP/HC (Jour choisi)", "type": "weekend_plus_hphc",
                "prix_hp_semaine": 0.2213, "prix_hc_weekend_jour": 0.166, "abo_mois": 15.08,
                "description": "HP semaine | HC + week-end + jour choisi + fériés = même prix réduit"},
        }
    },
    "totalenergies": {
        "nom": "TotalEnergies",
        "offres": {
            "base": {"nom": "Essentielle Base", "type": "base", "prix_kwh": 0.2516, "abo_mois": 12.44},
            "hphc": {"nom": "Essentielle HP/HC", "type": "hphc", "prix_hp": 0.27, "prix_hc": 0.2068, "abo_mois": 13.01},
            "online": {"nom": "Online Base", "type": "base", "prix_kwh": 0.2177, "abo_mois": 12.44},
        }
    },
    "engie": {
        "nom": "Engie",
        "offres": {
            "base": {"nom": "Référence Base", "type": "base", "prix_kwh": 0.2516, "abo_mois": 12.44},
            "hphc": {"nom": "Référence HP/HC", "type": "hphc", "prix_hp": 0.27, "prix_hc": 0.2068, "abo_mois": 13.01},
            "elec_adapt": {"nom": "Elec Adapt", "type": "base", "prix_kwh": 0.2346, "abo_mois": 12.44},
        }
    },
    "octopus": {
        "nom": "Octopus Energy",
        "offres": {
            "base": {"nom": "Eco-Conso Base", "type": "base", "prix_kwh": 0.1994, "abo_mois": 12.44},
            "hphc": {"nom": "Eco-Conso HP/HC", "type": "hphc", "prix_hp": 0.2252, "prix_hc": 0.1606, "abo_mois": 13.01},
        }
    },
    "ekwateur": {
        "nom": "Ekwateur",
        "offres": {
            "base": {"nom": "Électricité Base", "type": "base", "prix_kwh": 0.2364, "abo_mois": 12.44},
        }
    },
    "mint": {
        "nom": "Mint Énergie",
        "offres": {
            "base": {"nom": "Classic Base", "type": "base", "prix_kwh": 0.2041, "abo_mois": 12.44},
        }
    },
    "autre": {
        "nom": "Autre fournisseur",
        "offres": {
            "custom": {"nom": "Personnalisé", "type": "custom"}
        }
    }
}


def cmd_roles():
    """Affiche les rôles découverts"""
    roles = role_get_all()
    rapport = f"🎯 RÔLES AUTO-DÉCOUVERTS — {len(roles)}/{len(ROLES_DEFINIS)}\n━━━━━━━━━━━━━━━━━━\n"

    for role, definition in ROLES_DEFINIS.items():
        desc = definition["description"]
        if role in roles:
            eid = roles[role]["entity_id"]
            conf = roles[role]["confiance"]
            etoiles = "★" * min(5, int(conf * 5)) + "☆" * (5 - min(5, int(conf * 5)))
            rapport += f"  ✅ {role}\n    {etoiles} {eid}\n"
        else:
            rapport += f"  ❌ {role} — {desc}\n    Non découvert\n"

    non_assignes = len(ROLES_DEFINIS) - len(roles)
    if non_assignes > 0:
        rapport += f"\n⚠️ {non_assignes} rôle(s) non assigné(s) — /scan pour relancer la découverte"
    else:
        rapport += f"\n✅ Tous les rôles sont assignés"

    return rapport


def _lancer_questionnaire_foyer():
    """Lance le questionnaire de profil foyer — une question à la fois sur Telegram."""
    if mem_get("profil_foyer_complet"):
        return

    # Charger le profil en cours
    profil = {}
    try:
        data, _ = skill_get("foyer")
        if data:
            profil = data
    except Exception:
        pass

    # Trouver la prochaine question non répondue
    for q in PROFIL_QUESTIONS:
        qid = q["id"]
        if qid in profil:
            continue
        # Vérifier la condition
        if "condition" in q:
            if not q["condition"](profil):
                profil[qid] = "n/a"
                continue
        # Poser la question
        boutons = [
            {"text": b["text"], "callback_data": f"profil:{qid}:{b['value']}"}
            for b in q["boutons"]
        ]
        nb_restant = sum(1 for qq in PROFIL_QUESTIONS if qq["id"] not in profil and qq["id"] != qid)
        msg = f"{q['question']}"
        if nb_restant > 0:
            msg += f"\n({nb_restant} question(s) restante(s))"
        telegram_send_buttons(msg, boutons)
        mem_set("profil_foyer_question", qid)
        return

    # Toutes les questions répondues
    mem_set("profil_foyer_complet", "oui")
    skill_set("foyer", profil)

    # Résumé
    labels = {
        "foyer_personnes": "👥 Personnes",
        "foyer_presence": "🏠 Présence",
        "foyer_solaire": "☀️ Solaire",
        "foyer_solaire_kwc": "☀️ Puissance",
        "foyer_chauffage": "🌡️ Chauffage",
        "foyer_eau_chaude": "🚿 Eau chaude",
        "foyer_assistant_vocal": "🗣️ Assistant",
        "foyer_objectif": "🎯 Objectif",
    }
    msg = "✅ PROFIL FOYER ENREGISTRÉ\n━━━━━━━━━━━━━━━━━━\n"
    for qid, label in labels.items():
        val = profil.get(qid, "")
        if val and val != "n/a":
            msg += f"  {label} : {val}\n"
    msg += "\n🧠 Ces réponses alimentent les skills du script."
    msg += "\nPlus il en sait, mieux il vous fait économiser."
    msg += "\n💡 /profil pour revoir ou modifier"
    telegram_send(msg)
    log.info(f"✅ Profil foyer complet : {profil}")


def _lancer_questionnaire_appareils():
    """Demande à l'utilisateur d'identifier les appareils sur chaque prise connectée.
    Appelé après le premier scan. Une seule fois."""
    if mem_get("appareils_configures"):
        return

    # Trouver toutes les prises avec capteur de puissance
    try:
        conn = sqlite3.connect(DB_PATH)
        prises = conn.execute(
            "SELECT entity_id, friendly_name FROM cartographie WHERE categorie='prise_connectee' AND entity_id LIKE '%_power'"
        ).fetchall()
        conn.close()
    except Exception:
        return

    if not prises:
        return

    # Filtrer celles déjà identifiées
    a_identifier = []
    for eid, fname in prises:
        if not appareil_get(eid):
            a_identifier.append((eid, fname))

    if not a_identifier:
        mem_set("appareils_configures", "oui")
        return

    # Stocker la file d'attente
    queue = [{"entity_id": eid, "fname": fname} for eid, fname in a_identifier]
    mem_set("appareils_queue", json.dumps(queue))

    # Poser la première question
    _poser_question_appareil_suivant()


def _poser_question_appareil_suivant():
    """Pose la question pour la prochaine prise dans la file."""
    # Si on attend un nom personnalisé, ne pas avancer
    if mem_get("attente_nom_appareil"):
        return

    queue_json = mem_get("appareils_queue")
    if not queue_json:
        nb_surveilles = 0
        try:
            conn_s = sqlite3.connect(DB_PATH)
            nb_surveilles = conn_s.execute("SELECT COUNT(*) FROM appareils WHERE surveiller=1").fetchone()[0]
            conn_s.close()
        except Exception:
            pass
        mem_set("appareils_configures", "oui")
        telegram_send(
            f"✅ Configuration des appareils terminée !\n"
            f"📊 {nb_surveilles} appareils sous surveillance.\n"
            f"Tapez /surveillance pour tout voir."
        )
        return

    try:
        queue = json.loads(queue_json)
    except Exception:
        mem_set("appareils_configures", "oui")
        return

    if not queue:
        mem_set("appareils_configures", "oui")
        mem_set("appareils_queue", "")
        return

    item = queue[0]
    eid = item["entity_id"]
    fname = item["fname"]
    # Nettoyer le nom pour l'affichage
    for suffixe in [" Puissance", " Power"]:
        fname = fname.replace(suffixe, "")

    nb_restant = len(queue) - 1
    msg = f"🔌 Quel appareil est branché sur :\n**{fname}** ?\n"
    if nb_restant > 0:
        msg += f"({nb_restant} prise(s) restante(s))"

    boutons = [
        {"text": "🧺 Lave-linge", "callback_data": f"appareil:{eid}:lave_linge"},
        {"text": "👕 Sèche-linge", "callback_data": f"appareil:{eid}:seche_linge"},
        {"text": "🍽️ Lave-vaisselle", "callback_data": f"appareil:{eid}:lave_vaisselle"},
        {"text": "❄️ Congélateur", "callback_data": f"appareil:{eid}:congelateur"},
        {"text": "🔇 Coupe-veille", "callback_data": f"appareil:{eid}:coupe_veille"},
        {"text": "📊 Monitoring", "callback_data": f"appareil:{eid}:monitoring_energie"},
        {"text": "🔌 Autre", "callback_data": f"appareil:{eid}:autre"},
        {"text": "⬜ Ignorer", "callback_data": f"appareil:{eid}:ignorer"},
    ]
    telegram_send_buttons(msg, boutons)


def _moteur_economies_proactif(etats, index, now):
    """Moteur qui cherche activement des euros à gagner.
    Tourne toutes les 5 min. 0 token. 0 API externe.
    Chaque action = des euros mesurés."""
    # global _eco_proactif_state  # via shared
    heure = now.hour
    minute = now.minute

    _has_solar = role_get("production_solaire_w")
    _has_pac = role_get("pac_climate")
    production_w = ha_get_production_solaire_actuelle(etats) if _has_solar else 0
    prix_kwh = tarif_prix_kwh_actuel()

    conn = sqlite3.connect(DB_PATH)

    # ═══ 1. BRIEFING MATIN (1x/jour entre 7h00-7h05) ═══
    # Briefing : 5h lun-ven (travail), 10h sam-dim (repos)
    heure_briefing = 5 if now.weekday() < 5 else 10
    if heure == heure_briefing and minute < 5 and _eco_proactif_state.get("briefing") != now.strftime("%Y-%m-%d"):
        _eco_proactif_state["briefing"] = now.strftime("%Y-%m-%d")

        # Économies hier
        hier = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        eco_hier = conn.execute(
            "SELECT COALESCE(SUM(euros), 0) FROM economies WHERE created_at LIKE ?", (f"{hier}%",)
        ).fetchone()[0]

        # Économies ce mois
        eco_mois = conn.execute(
            "SELECT COALESCE(SUM(euros), 0), COUNT(*) FROM economies WHERE created_at LIKE ?",
            (f"{now.strftime('%Y-%m')}%",)
        ).fetchone()

        # Prédiction solaire
        solaire_prevu = ""
        if _has_solar:
            data_sol, nb_sol = skill_get("fenetre_solaire")
            if data_sol and nb_sol >= 20:
                jour_str = str(now.weekday())
                if jour_str in data_sol:
                    heures = data_sol[jour_str]
                    if heures:
                        best_h = max(heures.items(), key=lambda x: x[1][0])
                        solaire_prevu = f"\n☀️ Pic solaire prévu : {best_h[0]}h (~{int(best_h[1][0])}W)"
                        solaire_prevu += f"\n💡 Lancez une machine vers {best_h[0]}h pour du gratuit"

        # Coupe-veille : combien en standby ?
        standby_total = 0
        cv_alertes = []
        appareils_cv = conn.execute(
            "SELECT entity_id, nom_personnalise FROM appareils WHERE type_appareil='coupe_veille' AND surveiller=1"
        ).fetchall()
        for eid_cv, nom_cv in appareils_cv:
            switch_eid = eid_cv.replace("sensor.", "switch.").replace("_power", "")
            e_sw = index.get(switch_eid)
            e_se = index.get(eid_cv)
            if e_sw and e_sw.get("state") == "on" and e_se:
                try:
                    w = float(e_se.get("state", 0))
                    if 0 < w < 50:
                        standby_total += w
                        cv_alertes.append(f"{nom_cv} ({int(w)}W)")
                except (ValueError, TypeError):
                    pass

        # Adapter le briefing au profil du foyer
        profil_foyer, _ = skill_get("foyer")
        if not profil_foyer:
            profil_foyer = {}
        has_assistant = profil_foyer.get("foyer_assistant_vocal", "aucun") not in ("aucun", "n/a")
        nom_assistant = profil_foyer.get("foyer_assistant_vocal", "").title()
        objectif = profil_foyer.get("foyer_objectif", "reduire_facture")

        msg = f"💡 BRIEFING MATIN\n━━━━━━━━━━━━━━━━━━"
        if eco_hier > 0.005:
            msg += f"\n💰 Hier : +{eco_hier:.2f}€ économisés"
        msg += f"\n📈 Ce mois : {eco_mois[0]:.2f}€ ({eco_mois[1]} actions)"

        # Solaire — seulement si l'utilisateur en a
        if _has_solar:
            msg += solaire_prevu
        
        # Tarif HP/HC — conseil d'horaire
        tarif = tarif_get()
        if tarif.get("type") in ("hphc", "weekend_hphc", "weekend_plus_hphc"):
            hc_debut = tarif.get("hc_debut", 22)
            hc_fin = tarif.get("hc_fin", 6)
            prix_hp = tarif.get("prix_hp", tarif.get("prix_hp_semaine", prix_kwh))
            prix_hc = tarif.get("prix_hc", tarif.get("prix_hc_weekend_jour", prix_kwh))
            delta = prix_hp - prix_hc
            if delta > 0.01:
                msg += f"\n⚡ HC : {hc_debut}h-{hc_fin}h ({delta*100:.1f}c€/kWh moins cher)"
                if not _has_solar:
                    msg += f"\n💡 Lancez vos machines en heures creuses"

        # Weekend — tarif réduit si applicable
        if now.weekday() >= 5 and "weekend" in tarif.get("type", ""):
            msg += f"\n🗓️ Tarif weekend — c'est le bon jour pour les machines !"

        # Coupe-veille
        if cv_alertes:
            cout_standby_jour = standby_total * 24 / 1000 * prix_kwh
            msg += f"\n\n⚠️ Veille ({int(standby_total)}W = {cout_standby_jour:.2f}€/jour) :"
            for a in cv_alertes:
                msg += f"\n  🔴 {a}"
            if has_assistant:
                msg += f"\n💡 \"{nom_assistant}, éteins la télé\""
            else:
                msg += f"\n💡 Coupez les prises"

        # Objectif personnalisé
        if objectif == "comprendre" and eco_mois[1] == 0:
            msg += f"\n\n🔍 Tapez /energie pour voir votre consommation"
        elif objectif == "automatiser" and has_assistant:
            msg += f"\n\n🤖 Pensez à automatiser les coupe-veille via {nom_assistant}"

        # ═══ MÉTÉO ═══
        try:
            meteo_parts = []
            # Température
            temp_eid = role_get("meteo_temperature")
            if temp_eid:
                e_temp = index.get(temp_eid)
                if e_temp and e_temp["state"] not in ("unavailable", "unknown"):
                    meteo_parts.append(f"{e_temp['state']}°C")
            # Pluie
            pluie_eid = role_get("meteo_risque_pluie")
            if pluie_eid:
                e_pluie = index.get(pluie_eid)
                if e_pluie and e_pluie["state"] not in ("unavailable", "unknown", "0"):
                    try:
                        pct = int(float(e_pluie["state"]))
                        if pct > 30:
                            meteo_parts.append(f"🌧️ pluie {pct}%")
                    except (ValueError, TypeError):
                        pass
            # Alerte météo
            alerte_eid = role_get("alerte_meteo")
            if alerte_eid:
                e_alerte = index.get(alerte_eid)
                if e_alerte and e_alerte["state"] not in ("unavailable", "unknown", "Vert"):
                    meteo_parts.append(f"⚠️ {e_alerte['state']}")
            if meteo_parts:
                msg += f"\n\n🌤️ Météo : {' | '.join(meteo_parts)}"
        except Exception:
            pass

        # ═══ CALENDRIER / POUBELLES ═══
        try:
            headers_cal = {"Authorization": f"Bearer {CFG['ha_token']}"}
            today_start = now.strftime("%Y-%m-%dT00:00:00")
            today_end = now.strftime("%Y-%m-%dT23:59:59")
            demain_start = (now + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00")
            demain_end = (now + timedelta(days=1)).strftime("%Y-%m-%dT23:59:59")

            r_cals = requests.get(f"{CFG['ha_url']}/api/calendars", headers=headers_cal, verify=False, timeout=10)
            if r_cals.status_code == 200:
                events_today = []
                events_demain = []
                for cal_info in r_cals.json():
                    eid = cal_info.get("entity_id", "")
                    fname = cal_info.get("name", "")
                    # Aujourd'hui
                    try:
                        r_ev = requests.get(
                            f"{CFG['ha_url']}/api/calendars/{eid}?start={today_start}&end={today_end}",
                            headers=headers_cal, verify=False, timeout=5
                        )
                        if r_ev.status_code == 200:
                            for ev in r_ev.json():
                                events_today.append(f"{ev.get('summary', '?')}")
                    except Exception:
                        pass
                    # Demain (surtout pour les poubelles à sortir ce soir)
                    try:
                        r_ev2 = requests.get(
                            f"{CFG['ha_url']}/api/calendars/{eid}?start={demain_start}&end={demain_end}",
                            headers=headers_cal, verify=False, timeout=5
                        )
                        if r_ev2.status_code == 200:
                            for ev in r_ev2.json():
                                events_demain.append(f"{ev.get('summary', '?')}")
                    except Exception:
                        pass

                if events_today:
                    msg += f"\n\n📅 Aujourd'hui : {', '.join(events_today)}"
                if events_demain:
                    # Identifier les poubelles
                    poub = [e for e in events_demain if any(k in e.lower() for k in ("poubelle", "bleue", "verte", "jaune", "grise", "tri", "ordure", "recyclable"))]
                    autres = [e for e in events_demain if e not in poub]
                    if poub:
                        msg += f"\n🗑️ Poubelles demain : {', '.join(poub)} — sortez-les ce soir !"
                    if autres:
                        msg += f"\n📅 Demain : {', '.join(autres)}"
        except Exception:
            pass

        # ═══ CIRCULATION WAZE ═══
        jours_fr = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        jour_nom = jours_fr[now.weekday()]
        est_jour_travail = now.weekday() < 5  # lun-ven

        if est_jour_travail:
            waze_routes = []
            for eid in ("sensor.waze_a103", "sensor.waze_routes_locales", "sensor.waze_travel_time"):
                e_w = index.get(eid)
                if e_w and e_w["state"] not in ("unavailable", "unknown"):
                    try:
                        duree = float(e_w["state"])
                        attrs = e_w.get("attributes", {})
                        route = attrs.get("route", "")
                        distance = attrs.get("distance", "")
                        nom = attrs.get("friendly_name", eid.split(".")[-1])
                        dist_str = f" ({distance:.1f}km)" if isinstance(distance, (int, float)) else ""
                        # Trouver la route courte
                        route_courte = route.split(";")[0].strip() if route else nom
                        waze_routes.append({"nom": route_courte, "duree": duree, "dist": dist_str})
                    except (ValueError, TypeError):
                        pass

            if waze_routes:
                # Trier par durée
                waze_routes.sort(key=lambda x: x["duree"])
                best = waze_routes[0]
                msg += f"\n\n🚗 TRAJET"
                for wr in waze_routes:
                    icone = "🟢" if wr["duree"] < 30 else ("🟡" if wr["duree"] < 45 else "🔴")
                    best_marker = " ← meilleur" if wr == best and len(waze_routes) > 1 else ""
                    msg += f"\n  {icone} {wr['nom']}{wr['dist']} : {int(wr['duree'])} min{best_marker}"
                msg += f"\n\n🚗 Bonne route !"
            else:
                msg += f"\n\n🚗 Bonne journée !"
        else:
            msg += f"\n\n🏠 Bon {jour_nom} !"

        telegram_send(msg)

    # ═══ 2. ALERTE PIC SOLAIRE (si > 2000W et aucune machine en cours) ═══
    if _has_solar and production_w > 2000:
        has_cycle = any(v == "actif" for v in _etat_prises.values())
        last_solar_alert = _eco_proactif_state.get("solar_alert", "")
        if not has_cycle and last_solar_alert != now.strftime("%Y-%m-%d-%H"):
            _eco_proactif_state["solar_alert"] = now.strftime("%Y-%m-%d-%H")
            eco_potentielle = round(1.5 * prix_kwh * (production_w / 2000), 2)
            telegram_send(
                f"☀️ PIC SOLAIRE — {int(production_w)}W disponibles !\n"
                f"Aucune machine en cours.\n"
                f"💰 Lancez une machine maintenant → ~{eco_potentielle:.2f}€ d'économie"
            )

    # ═══ 3. STANDBY OUBLIÉ (toutes les 2h si switch ON + conso < 15W) ═══
    if heure >= 8 and heure <= 23:
        for eid_cv, nom_cv in (conn.execute(
            "SELECT entity_id, nom_personnalise FROM appareils WHERE type_appareil='coupe_veille' AND surveiller=1"
        ).fetchall()):
            switch_eid = eid_cv.replace("sensor.", "switch.").replace("_power", "")
            e_sw = index.get(switch_eid)
            e_se = index.get(eid_cv)

            if e_sw and e_sw.get("state") == "on" and e_se:
                try:
                    w = float(e_se.get("state", 0))
                except (ValueError, TypeError):
                    w = 0

                if 0 < w < 15:
                    key = f"standby_{eid_cv}"
                    last = _eco_proactif_state.get(key, "")
                    if last != now.strftime("%Y-%m-%d-%H") and (heure % 2 == 0):
                        _eco_proactif_state[key] = now.strftime("%Y-%m-%d-%H")
                        cout_h = w / 1000 * prix_kwh
                        cout_j = cout_h * 24
                        cout_m = cout_j * 30
                        telegram_send(
                            f"🔇 {nom_cv} en veille — {int(w)}W\n"
                            f"💸 Coût : {cout_j:.2f}€/jour | {cout_m:.1f}€/mois\n"
                            f"Couper la prise pour économiser."
                        )

    # ═══ 4. BILAN DU SOIR (1x/jour à 21h00-21h05) ═══
    if heure == 21 and minute < 5 and _eco_proactif_state.get("bilan_soir") != now.strftime("%Y-%m-%d"):
        _eco_proactif_state["bilan_soir"] = now.strftime("%Y-%m-%d")

        aujourdhui = now.strftime("%Y-%m-%d")
        eco_jour = conn.execute(
            "SELECT type, SUM(euros), COUNT(*) FROM economies WHERE created_at LIKE ? GROUP BY type",
            (f"{aujourdhui}%",)
        ).fetchall()
        total_jour = sum(row[1] for row in eco_jour)

        eco_mois_total = conn.execute(
            "SELECT COALESCE(SUM(euros), 0) FROM economies WHERE created_at LIKE ?",
            (f"{now.strftime('%Y-%m')}%",)
        ).fetchone()[0]

        if total_jour > 0.005 or eco_jour:
            type_labels = {
                "cycle_solaire": "☀️ Solaire",
                "coupe_veille": "🔇 Standby évité",
                "tarif_optimal": "⚡ Tarif",
            }
            msg = f"📊 BILAN DU JOUR — {aujourdhui}\n━━━━━━━━━━━━━━━━━━"
            for type_eco, euros, nb in eco_jour:
                label = type_labels.get(type_eco, type_eco)
                msg += f"\n  {label} : +{euros:.2f}€ ({nb}x)"
            msg += f"\n━━━\n💰 Aujourd'hui : +{total_jour:.2f}€"
            msg += f"\n📈 Ce mois : {eco_mois_total:.2f}€"
            telegram_send(msg)

    # ═══ 5. BILAN HEBDO (dimanche 20h) ═══
    if now.weekday() == 6 and heure == 20 and minute < 5 and _eco_proactif_state.get("bilan_hebdo") != now.strftime("%Y-W%W"):
        _eco_proactif_state["bilan_hebdo"] = now.strftime("%Y-W%W")

        # Bornes de la semaine (lundi 00h → dimanche 23h59)
        lundi = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
        dimanche_fin = now.strftime("%Y-%m-%d") + "T23:59:59"

        # Semaine précédente
        lundi_prec = (now - timedelta(days=now.weekday() + 7)).strftime("%Y-%m-%d")
        dimanche_prec = (now - timedelta(days=now.weekday() + 1)).strftime("%Y-%m-%d") + "T23:59:59"

        try:
            # Économies cette semaine
            eco_semaine = conn.execute(
                "SELECT COALESCE(SUM(euros), 0), COUNT(*) FROM economies WHERE created_at >= ?",
                (lundi,)
            ).fetchone()
            eco_sem_eur, eco_sem_nb = eco_semaine

            # Économies semaine précédente
            eco_prec = conn.execute(
                "SELECT COALESCE(SUM(euros), 0) FROM economies WHERE created_at >= ? AND created_at < ?",
                (lundi_prec, lundi)
            ).fetchone()[0]

            # Par type
            eco_par_type = conn.execute(
                "SELECT type, SUM(euros), COUNT(*) FROM economies WHERE created_at >= ? GROUP BY type",
                (lundi,)
            ).fetchall()

            # Cycles machines cette semaine
            cycles_sem = conn.execute(
                "SELECT COUNT(*), COALESCE(SUM(conso_kwh), 0), COALESCE(SUM(economie_eur), 0) FROM cycles_appareils "
                "WHERE fin IS NOT NULL AND created_at >= ?",
                (lundi,)
            ).fetchone()
            nb_cycles, kwh_cycles, eco_cycles = cycles_sem

            # Score intelligence
            nb_succes = conn.execute(
                "SELECT COUNT(*) FROM decisions_log WHERE succes=1 AND created_at >= ?",
                (lundi,)
            ).fetchone()[0]
            nb_echecs = conn.execute(
                "SELECT COUNT(*) FROM decisions_log WHERE succes=0 AND created_at >= ?",
                (lundi,)
            ).fetchone()[0]

            # Économies ce mois
            eco_mois = conn.execute(
                "SELECT COALESCE(SUM(euros), 0) FROM economies WHERE created_at LIKE ?",
                (f"{now.strftime('%Y-%m')}%",)
            ).fetchone()[0]

            # Construire le message
            msg = f"📊 BILAN HEBDO\n━━━━━━━━━━━━━━━━━━\n"
            msg += f"Semaine du {lundi[5:]} au {now.strftime('%d/%m')}\n\n"

            # Économies
            msg += f"💰 ÉCONOMIES\n"
            msg += f"  Cette semaine : +{eco_sem_eur:.2f}€ ({eco_sem_nb} actions)\n"
            if eco_prec > 0:
                delta_pct = ((eco_sem_eur - eco_prec) / eco_prec * 100) if eco_prec > 0.01 else 0
                tendance = "📈" if delta_pct > 5 else ("📉" if delta_pct < -5 else "➡️")
                msg += f"  Semaine précédente : {eco_prec:.2f}€ {tendance} ({delta_pct:+.0f}%)\n"
            msg += f"  Ce mois : {eco_mois:.2f}€\n"

            # Détail par type
            type_labels = {
                "cycle_solaire": "☀️ Solaire",
                "coupe_veille": "🔇 Standby",
                "tarif_optimal": "⚡ Tarif",
            }
            if eco_par_type:
                msg += f"\n📋 DÉTAIL\n"
                for t_eco, eur, nb in eco_par_type:
                    label = type_labels.get(t_eco, t_eco)
                    msg += f"  {label} : +{eur:.2f}€ ({nb}x)\n"

            # Machines
            if nb_cycles > 0:
                msg += f"\n🔌 MACHINES\n"
                msg += f"  {nb_cycles} cycles | {kwh_cycles:.1f} kWh | {eco_cycles:.2f}€ économisés\n"

            # Fiabilité
            total_decisions = nb_succes + nb_echecs
            if total_decisions > 0:
                taux = nb_succes / total_decisions * 100
                msg += f"\n🛡️ FIABILITÉ\n"
                msg += f"  {nb_succes}✅ {nb_echecs}❌ ({taux:.0f}%)\n"

            # Mot de fin
            if eco_sem_eur > eco_prec and eco_prec > 0:
                msg += f"\n🎯 Belle progression cette semaine !"
            elif eco_sem_eur > 0:
                msg += f"\n💡 Chaque euro compte."
            else:
                msg += f"\n📊 Les baselines s'accumulent — la semaine prochaine sera meilleure."

            telegram_send(msg)
        except Exception as ex:
            log.error(f"bilan_hebdo: {ex}")

    # ═══ 6. BILAN MENSUEL (1er du mois à 10h) ═══
    if now.day == 1 and heure == 10 and minute < 5 and _eco_proactif_state.get("bilan_mois") != now.strftime("%Y-%m"):
        _eco_proactif_state["bilan_mois"] = now.strftime("%Y-%m")

        mois_prec = (now.replace(day=1) - timedelta(days=1))
        mois_prec_str = mois_prec.strftime("%Y-%m")
        mois_actuel_str = now.strftime("%Y-%m")
        mois_2prec = (mois_prec.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")

        noms_mois = {1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
                     7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"}
        nom_mois = noms_mois.get(mois_prec.month, str(mois_prec.month))

        try:
            # ═══ ÉCONOMIES DU MOIS ═══
            eco_mois = conn.execute(
                "SELECT COALESCE(SUM(euros), 0), COUNT(*) FROM economies WHERE created_at LIKE ?",
                (f"{mois_prec_str}%",)
            ).fetchone()
            eco_par_type = conn.execute(
                "SELECT type, SUM(euros), COUNT(*) FROM economies WHERE created_at LIKE ? GROUP BY type",
                (f"{mois_prec_str}%",)
            ).fetchall()

            # Mois précédent (M-2) pour comparaison
            eco_m2 = conn.execute(
                "SELECT COALESCE(SUM(euros), 0) FROM economies WHERE created_at LIKE ?",
                (f"{mois_2prec}%",)
            ).fetchone()[0]

            # ═══ CYCLES MACHINES ═══
            cycles_mois = conn.execute(
                "SELECT COUNT(*), COALESCE(SUM(conso_kwh), 0), COALESCE(SUM(economie_eur), 0) "
                "FROM cycles_appareils WHERE fin IS NOT NULL AND created_at LIKE ?",
                (f"{mois_prec_str}%",)
            ).fetchone()

            # ═══ CONSO EDF — via baselines stockées ou economies ═══
            # Cumuler la dépense quotidienne depuis les baselines
            conso_eid = role_get("conso_jour_kwh")
            depense_eid = role_get("conso_jour_eur")

            # On estime via les baselines moyennes × nb jours
            nb_jours = mois_prec.day  # Dernier jour du mois précédent
            conso_kwh_mois = 0
            cout_edf_mois = 0

            # Méthode 1 : depuis les baselines
            try:
                baselines_conso = conn.execute(
                    "SELECT AVG(valeur_moyenne) FROM baselines WHERE entity_id=?",
                    (conso_eid,)
                ).fetchone()
                if baselines_conso and baselines_conso[0]:
                    conso_kwh_mois = baselines_conso[0] * nb_jours
            except Exception:
                pass

            try:
                baselines_eur = conn.execute(
                    "SELECT AVG(valeur_moyenne) FROM baselines WHERE entity_id=?",
                    (depense_eid,)
                ).fetchone()
                if baselines_eur and baselines_eur[0]:
                    cout_edf_mois = baselines_eur[0] * nb_jours
            except Exception:
                pass

            # Si pas de baselines, estimer depuis le tarif
            if cout_edf_mois == 0 and conso_kwh_mois > 0:
                cout_edf_mois = conso_kwh_mois * tarif_prix_kwh_actuel()

            # ═══ PRODUCTION SOLAIRE ═══
            prod_solaire_kwh = 0
            if _has_solar:
                try:
                    prod_eid = role_get("production_solaire_kwh")
                    baselines_sol = conn.execute(
                        "SELECT AVG(valeur_moyenne) FROM baselines WHERE entity_id=?",
                        (prod_eid,)
                    ).fetchone()
                    if baselines_sol and baselines_sol[0]:
                        prod_solaire_kwh = baselines_sol[0] * nb_jours
                except Exception:
                    pass

            # ═══ CONSTRUIRE LE MESSAGE ═══
            msg = f"📊 BILAN MENSUEL — {nom_mois} {mois_prec.year}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

            # EDF
            if conso_kwh_mois > 0 or cout_edf_mois > 0:
                msg += f"\n⚡ RÉSEAU EDF\n"
                if conso_kwh_mois > 0:
                    msg += f"  Consommation : ~{conso_kwh_mois:.0f} kWh\n"
                if cout_edf_mois > 0:
                    msg += f"  Coût estimé : ~{cout_edf_mois:.0f}€\n"

            # Solaire
            if prod_solaire_kwh > 0:
                msg += f"\n☀️ PRODUCTION SOLAIRE\n"
                msg += f"  Production : ~{prod_solaire_kwh:.0f} kWh\n"
                if conso_kwh_mois > 0:
                    conso_totale = conso_kwh_mois + prod_solaire_kwh
                    couverture = prod_solaire_kwh / conso_totale * 100 if conso_totale > 0 else 0
                    msg += f"  Couverture solaire : {couverture:.0f}%\n"
                eco_solaire = prod_solaire_kwh * tarif_prix_kwh_actuel()
                msg += f"  Valeur produite : ~{eco_solaire:.0f}€\n"

            # Économies IA
            msg += f"\n💰 ÉCONOMIES IA\n"
            msg += f"  Total : +{eco_mois[0]:.2f}€ ({eco_mois[1]} actions)\n"
            if eco_m2 > 0.01:
                delta = ((eco_mois[0] - eco_m2) / eco_m2 * 100)
                tendance = "📈" if delta > 5 else ("📉" if delta < -5 else "➡️")
                msg += f"  vs mois précédent : {tendance} ({delta:+.0f}%)\n"

            type_labels = {
                "cycle_solaire": "☀️ Solaire",
                "coupe_veille": "🔇 Standby",
                "tarif_optimal": "⚡ Tarif",
            }
            for t_eco, eur, nb in eco_par_type:
                label = type_labels.get(t_eco, t_eco)
                msg += f"  {label} : +{eur:.2f}€ ({nb}x)\n"

            # Machines
            nb_c, kwh_c, eco_c = cycles_mois
            if nb_c > 0:
                msg += f"\n🔌 MACHINES\n"
                msg += f"  {nb_c} cycles | {kwh_c:.1f} kWh | {eco_c:.2f}€ économisés\n"

            # Résumé
            if cout_edf_mois > 0 and eco_mois[0] > 0:
                pct_recup = eco_mois[0] / cout_edf_mois * 100 if cout_edf_mois > 0 else 0
                msg += f"\n🎯 L'IA a récupéré {pct_recup:.1f}% de votre facture EDF"

            telegram_send(msg)
        except Exception as ex:
            log.error(f"bilan_mensuel: {ex}")

    # ═══ 7. MACHINE EN HP ALORS QUE HC COMMENCE BIENTÔT ═══
    tarif = tarif_get()
    if tarif.get("type") in ("hphc", "weekend_hphc", "weekend_plus_hphc"):
        hc_debut = tarif.get("hc_debut", 22)
        if isinstance(hc_debut, str):
            try: hc_debut = int(hc_debut.split(":")[0])
            except: hc_debut = 22
        # Si on est 1-2h avant les HC et qu'une machine tourne
        heures_avant_hc = hc_debut - heure
        if 0 < heures_avant_hc <= 2:
            has_cycle = any(v == "actif" for v in _etat_prises.values())
            if has_cycle:
                key_hp = f"hp_alert_{now.strftime('%Y-%m-%d')}"
                if _eco_proactif_state.get(key_hp) != now.strftime("%H"):
                    _eco_proactif_state[key_hp] = now.strftime("%H")
                    prix_hp = tarif.get("prix_hp", tarif.get("prix_hp_semaine", prix_kwh))
                    prix_hc = tarif.get("prix_hc", tarif.get("prix_hc_weekend_jour", prix_kwh))
                    delta = prix_hp - prix_hc
                    if delta > 0.01:
                        eco_possible = delta * 1.5  # ~1.5 kWh par cycle moyen
                        telegram_send(
                            f"⚡ Machine en cours — tarif HP !\n"
                            f"Les heures creuses commencent à {hc_debut}h.\n"
                            f"💡 Prochain cycle : lancez après {hc_debut}h → ~{eco_possible:.2f}€ d'économie"
                        )

    conn.close()


def cycle_debut(entity_id, friendly_name, production_solaire_w=0):
    conn = sqlite3.connect(DB_PATH)
    # Supprimer cycle en cours éventuel + mesures orphelines
    conn.execute('DELETE FROM cycles_appareils WHERE entity_id=? AND fin IS NULL', (entity_id,))
    conn.execute('DELETE FROM cycle_mesures WHERE entity_id=?', (entity_id,))
    conn.execute(
        '''INSERT INTO cycles_appareils
           (entity_id, friendly_name, debut, production_solaire_w, created_at)
           VALUES (?, ?, ?, ?, ?)''',
        (entity_id, friendly_name, datetime.now().isoformat(),
         production_solaire_w, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def cycle_fin(entity_id, conso_kwh=0.0):
    conn = sqlite3.connect(DB_PATH)
    r = conn.execute(
        'SELECT id, debut, production_solaire_w FROM cycles_appareils WHERE entity_id=? AND fin IS NULL',
        (entity_id,)
    ).fetchone()
    if not r:
        conn.close()
        return None
    cycle_id, debut_str, prod_solaire_debut = r
    debut = datetime.fromisoformat(debut_str)
    duree = int((datetime.now() - debut).total_seconds() / 60)

    # Production solaire actuelle
    prod_solaire_fin = 0
    try:
        etats = ha_get("states")
        if etats:
            prod_solaire_fin = ha_get_production_solaire_actuelle(etats)
    except Exception:
        pass

    # Moyenne production solaire pendant le cycle
    prod_debut = prod_solaire_debut or 0
    prod_moy = (prod_debut + prod_solaire_fin) / 2

    # Puissance moyenne machine pendant le cycle
    puissance_moy = (conso_kwh / (duree / 60)) * 1000 if duree > 0 else 0

    # Couverture solaire : quelle part de la machine a été couverte par le solaire ?
    if puissance_moy > 0 and prod_moy > 0:
        couverture_pct = min(100, int(prod_moy / puissance_moy * 100))
    else:
        couverture_pct = 0

    # Coût : seulement la part réseau (non couverte par le solaire)
    part_reseau = max(0, 100 - couverture_pct) / 100
    prix_kwh = tarif_prix_kwh_actuel()
    cout_total = round(conso_kwh * prix_kwh, 3)
    cout_reseau = round(cout_total * part_reseau, 3)
    economie = round(cout_total - cout_reseau, 3)

    # Ajouter colonnes si absentes
    try:
        conn.execute("ALTER TABLE cycles_appareils ADD COLUMN economie_eur REAL DEFAULT 0")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE cycles_appareils ADD COLUMN couverture_pct INTEGER DEFAULT 0")
    except Exception:
        pass

    conn.execute(
        '''UPDATE cycles_appareils
           SET fin=?, duree_min=?, conso_kwh=?, cout_eur=?, economie_eur=?, couverture_pct=?, production_solaire_w=?
           WHERE id=?''',
        (datetime.now().isoformat(), duree, conso_kwh, cout_reseau, economie, couverture_pct, int(prod_moy), cycle_id)
    )
    conn.commit()
    conn.close()
    # Log succès — chaque cycle terminé = le script fonctionne
    try:
        conn2 = sqlite3.connect(DB_PATH)
        conn2.execute(
            "INSERT INTO decisions_log (action, contexte, resultat, succes, created_at) VALUES (?, ?, ?, 1, ?)",
            ("CYCLE_OK", json.dumps({"eid": entity_id, "kwh": conso_kwh}, ensure_ascii=False),
             f"{duree}min {conso_kwh}kWh", datetime.now().isoformat())
        )
        conn2.commit()
        conn2.close()
    except Exception:
        pass

    # Signature du cycle — apprentissage programme
    try:
        mesures = _puissances_historique.get(entity_id, [])
        signature = _calculer_signature_cycle(mesures)
        if signature and duree > 10:
            nom_prog = _apprentissage_cycle(entity_id, signature, duree, conso_kwh)
            # Stocker la signature dans le cycle en DB
            try:
                conn3 = sqlite3.connect(DB_PATH)
                try:
                    conn3.execute("ALTER TABLE cycles_appareils ADD COLUMN signature TEXT DEFAULT ''")
                except Exception:
                    pass
                try:
                    conn3.execute("ALTER TABLE cycles_appareils ADD COLUMN programme TEXT DEFAULT ''")
                except Exception:
                    pass
                conn3.execute(
                    "UPDATE cycles_appareils SET signature=?, programme=? WHERE id=?",
                    (signature, nom_prog or "", cycle_id)
                )
                conn3.commit()
                conn3.close()
            except Exception:
                pass
    except Exception as ex:
        log.debug(f"signature cycle: {ex}")

    return {
        "duree_min": duree, "conso_kwh": conso_kwh,
        "cout_total": cout_total, "cout_reseau": cout_reseau,
        "economie": economie, "couverture_pct": couverture_pct,
        "prod_solaire_moy": int(prod_moy)
    }


def _calculer_signature_cycle(mesures):
    """Calcule une empreinte numérique d'un cycle à partir de ses mesures de puissance.
    
    La signature encode le PROFIL du cycle : ses phases (chauffage, lavage, essorage, pause).
    Deux cycles du même programme auront des signatures très proches.
    
    Méthode : découper le cycle en tranches de 5 min, classifier chaque tranche
    en niveau de puissance (L1=0-50W, L2=50-200W, L3=200-500W, P1=>500W, C9=0W pause).
    La signature = concaténation des codes : "C9-L2-L2-P1-L3-L1-L2-P1-L1-L1-C9"
    """
    if not mesures or len(mesures) < 3:
        return ""

    # Extraire les watts (mesures = [(ts, watts), ...])
    watts = [w for _, w in mesures if isinstance(w, (int, float))]
    if len(watts) < 3:
        return ""

    # Découper en tranches de 5 min (~15 mesures à 20s)
    tranche_size = 15
    phases = []
    for i in range(0, len(watts), tranche_size):
        tranche = watts[i:i+tranche_size]
        moy = sum(tranche) / len(tranche)
        if moy < 5:
            phases.append("C9")    # Coupure / pause
        elif moy < 50:
            phases.append("L1")    # Low — veille / fin de cycle
        elif moy < 200:
            phases.append("L2")    # Moyen — lavage / rinçage
        elif moy < 500:
            phases.append("L3")    # Haut — chauffage modéré
        elif moy < 1000:
            phases.append("P1")    # Puissant — chauffage eau / essorage
        else:
            phases.append("L6")    # Très puissant — résistance max

    return "-".join(phases)


def _comparer_signatures(sig1, sig2):
    """Compare deux signatures. Retourne un score de similarité 0-100."""
    if not sig1 or not sig2:
        return 0
    p1 = sig1.split("-")
    p2 = sig2.split("-")
    # Aligner par longueur (le plus court)
    min_len = min(len(p1), len(p2))
    max_len = max(len(p1), len(p2))
    if min_len == 0:
        return 0
    matches = sum(1 for i in range(min_len) if p1[i] == p2[i])
    # Pénaliser la différence de longueur
    score = (matches / max_len) * 100
    return int(score)


def _identifier_programme(entity_id, signature, duree_min, conso_kwh):
    """Compare la signature avec les programmes connus. Retourne le nom ou None."""
    programmes, _ = skill_get("programmes_machines")
    if not programmes:
        return None

    progs = programmes.get(entity_id, {})
    meilleur_score = 0
    meilleur_nom = None

    for nom_prog, data_prog in progs.items():
        sig_connue = data_prog.get("signature", "")
        score = _comparer_signatures(signature, sig_connue)
        if score > meilleur_score:
            meilleur_score = score
            meilleur_nom = nom_prog

    if meilleur_score >= 70:
        return meilleur_nom
    return None


def _enregistrer_programme(entity_id, nom_programme, signature, duree_min, conso_kwh):
    """Enregistre un nouveau programme dans le skill."""
    programmes, _ = skill_get("programmes_machines")
    if not programmes:
        programmes = {}
    if entity_id not in programmes:
        programmes[entity_id] = {}

    programmes[entity_id][nom_programme] = {
        "signature": signature,
        "duree_moy": duree_min,
        "conso_moy": conso_kwh,
        "nb_cycles": 1,
        "derniere_utilisation": datetime.now().isoformat()
    }
    skill_set("programmes_machines", programmes)


def _apprentissage_cycle(entity_id, signature, duree_min, conso_kwh):
    """Après un cycle : identifier ou demander le nom du programme.
    
    - Programme connu → reconnaissance silencieuse, mise à jour stats
    - Programme inconnu → boutons Telegram pour nommer
    - L'utilisateur ne voit une question que pour les NOUVEAUX programmes
    """
    app = appareil_get(entity_id)
    app_nom = app["nom"] if app and app.get("nom") else entity_id

    # Identifier
    nom_reconnu = _identifier_programme(entity_id, signature, duree_min, conso_kwh)

    if nom_reconnu:
        # Programme reconnu → mise à jour silencieuse des stats
        programmes, _ = skill_get("programmes_machines")
        if programmes and entity_id in programmes and nom_reconnu in programmes[entity_id]:
            prog = programmes[entity_id][nom_reconnu]
            nb = prog.get("nb_cycles", 1)
            # Moyenne glissante
            prog["duree_moy"] = round((prog["duree_moy"] * nb + duree_min) / (nb + 1), 1)
            prog["conso_moy"] = round((prog["conso_moy"] * nb + conso_kwh) / (nb + 1), 3)
            prog["nb_cycles"] = nb + 1
            prog["derniere_utilisation"] = datetime.now().isoformat()
            skill_set("programmes_machines", programmes)
        return nom_reconnu

    # Programme inconnu → enregistrement automatique silencieux
    log.info(f"Nouveau cycle {app_nom}: {signature[:40]} | {duree_min}min | {conso_kwh:.2f}kWh")
    return None


def cmd_programmes():
    """Affiche les programmes appris pour chaque machine."""
    programmes, _ = skill_get("programmes_machines")
    if not programmes:
        return "📋 Aucun programme appris pour l'instant.\nLes programmes s'apprennent automatiquement après chaque cycle."

    rapport = "📋 PROGRAMMES APPRIS\n━━━━━━━━━━━━━━━━━━\n"
    for eid, progs in programmes.items():
        app = appareil_get(eid)
        app_nom = app["nom"] if app and app.get("nom") else eid
        rapport += f"\n🔌 {app_nom}\n"
        for nom, data in progs.items():
            rapport += f"  📊 {nom} : ~{data.get('duree_moy', '?')} min | ~{data.get('conso_moy', '?')} kWh | {data.get('nb_cycles', 0)} cycles\n"
    
    rapport += "\n💡 /appareils reset → réinitialiser si changement de machine"
    return rapport


def cycle_en_cours(entity_id):
    conn = sqlite3.connect(DB_PATH)
    r = conn.execute(
        'SELECT debut, production_solaire_w FROM cycles_appareils WHERE entity_id=? AND fin IS NULL',
        (entity_id,)
    ).fetchone()
    conn.close()
    return r


def generer_graphique_energie(etats, index):
    """Génère un graphique conso EDF + solaire du jour → bytes PNG."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        log.debug("matplotlib pas encore installé — graphique indisponible")
        return None

    now = datetime.now()
    conn = sqlite3.connect(DB_PATH)

    # Récupérer les mesures du jour depuis cycle_mesures (toutes les prises)
    today_start = now.strftime("%Y-%m-%dT00:00:00")
    mesures = conn.execute(
        "SELECT timestamp, watts FROM cycle_mesures WHERE timestamp > ? ORDER BY timestamp",
        (today_start,)
    ).fetchall()

    # Récupérer les baselines horaires pour la conso EDF
    conso_eid = role_get("conso_temps_reel")
    baselines_conso = {}
    if conso_eid:
        rows = conn.execute(
            "SELECT heure, valeur_moyenne FROM baselines WHERE entity_id=? AND jour_semaine=?",
            (conso_eid, now.weekday())
        ).fetchall()
        baselines_conso = {h: v for h, v in rows}

    conn.close()

    # Données actuelles depuis les mesures de prises (agrégées par heure)
    heures_prises = {}
    for ts, watts in mesures:
        try:
            h = int(ts[11:13])
            if h not in heures_prises:
                heures_prises[h] = []
            heures_prises[h].append(watts)
        except Exception:
            pass

    # Construire les séries
    heures = list(range(0, now.hour + 1))
    conso_baseline = [baselines_conso.get(h, 0) for h in heures]
    conso_prises = [sum(heures_prises.get(h, [0])) / max(1, len(heures_prises.get(h, [1]))) for h in heures]

    # Solaire
    solaire_data = []
    if role_get("production_solaire_w"):
        prod_eid = role_get("production_solaire_w")
        if prod_eid:
            conn2 = sqlite3.connect(DB_PATH)
            rows_sol = conn2.execute(
                "SELECT heure, valeur_moyenne FROM baselines WHERE entity_id=? AND jour_semaine=?",
                (prod_eid, now.weekday())
            ).fetchall()
            conn2.close()
            sol_dict = {h: v for h, v in rows_sol}
            solaire_data = [sol_dict.get(h, 0) for h in heures]

    # Créer le graphique
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#16213e")

    if conso_baseline and any(v > 0 for v in conso_baseline):
        ax.fill_between(heures, conso_baseline, alpha=0.3, color="#e74c3c", label="Conso EDF (baseline)")
        ax.plot(heures, conso_baseline, color="#e74c3c", linewidth=2)

    if solaire_data and any(v > 0 for v in solaire_data):
        ax.fill_between(heures, solaire_data, alpha=0.3, color="#f1c40f", label="Solaire")
        ax.plot(heures, solaire_data, color="#f1c40f", linewidth=2)

    if conso_prises and any(v > 0 for v in conso_prises):
        ax.bar(heures, conso_prises, alpha=0.5, color="#3498db", width=0.6, label="Machines (prises)")

    ax.set_xlabel("Heure", color="white", fontsize=12)
    ax.set_ylabel("Watts", color="white", fontsize=12)
    ax.set_title(f"⚡ Énergie — {now.strftime('%A %d/%m/%Y')}", color="white", fontsize=14, fontweight="bold")
    ax.tick_params(colors="white")
    ax.spines["bottom"].set_color("white")
    ax.spines["left"].set_color("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(facecolor="#16213e", edgecolor="white", labelcolor="white", fontsize=10)
    ax.set_xlim(0, 23)
    ax.set_xticks(range(0, 24, 2))

    plt.tight_layout()

    # Convertir en bytes
    import io
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def traiter_callback(callback_query):
    cqid = callback_query.get("id")
    data = callback_query.get("data", "")
    chat = str(callback_query.get("message", {}).get("chat", {}).get("id", ""))

    if not _is_authorized_chat(chat):
        return

    telegram_answer_callback(cqid)

    # ═══ SÉCURITÉ — Bloquer les boutons si canal verrouillé ═══
    if shared.canal_verrouille:
        # Seul le wizard est autorisé quand le canal est verrouillé
        if not data.startswith("wizard_"):
            telegram_send("🔐 Canal verrouillé — entrez le code SMS d'abord.")
            return

    # ═══ ACTIONS HA — Confirmation / Annulation ═══
    if data == "ha_action:confirm":
        pending = mem_get("ha_action_pending")
        if not pending:
            telegram_send("⚠️ Aucune action en attente.")
            return
        try:
            action = json.loads(pending)
            domain = action["domain"]
            service = action["service"]
            entity_id = action["entity_id"]
            extra_data = action.get("data", {})

            # Exécuter l'action
            service_data = {"entity_id": entity_id}
            service_data.update(extra_data)
            result = ha_post(f"services/{domain}/{service}", service_data)

            mem_set("ha_action_pending", "")

            if result is not None:
                entity_short = entity_id.split(".", 1)[1].replace("_", " ").title() if "." in entity_id else entity_id
                telegram_send(f"✅ Action exécutée\n{domain}.{service} → {entity_short}")
                log.info(f"✅ HA action: {domain}/{service} on {entity_id}")
            else:
                telegram_send(f"❌ Échec de l'action {domain}.{service} sur {entity_id}")
        except Exception as e:
            log.error(f"❌ HA action error: {e}")
            telegram_send(f"❌ Erreur action HA : {str(e)[:100]}")
            mem_set("ha_action_pending", "")
        return

    if data == "ha_action:cancel":
        mem_set("ha_action_pending", "")
        telegram_send("❌ Action annulée.")
        return

    # ═══ WIZARD CALLBACKS ═══
    if data.startswith("wizard_sms:"):
        method = data.split(":", 1)[1]
        if method == "free_mobile":
            CFG["_wizard_step"] = "sms_free_user"
            _wizard_save_config()
            telegram_send(
                "📱 FREE MOBILE\n"
                "━━━━━━━━━━━━━━\n"
                "Activez l'option dans votre Espace Abonné :\n"
                "Mes options → Notifications par SMS\n\n"
                "Envoyez votre identifiant Free (8 chiffres) :"
            )
        elif method == "ha_notify":
            CFG["_wizard_step"] = "sms_ha_notify_service"
            _wizard_save_config()
            # Lister les services notify disponibles
            notify_list = []
            try:
                headers = {"Authorization": f"Bearer {CFG['ha_token']}"}
                r = requests.get(f"{CFG['ha_url']}/api/services", headers=headers, verify=False, timeout=10)
                if r.status_code == 200:
                    for s in r.json():
                        if s.get("domain") == "notify":
                            notify_list = list(s.get("services", {}).keys())
            except Exception:
                pass
            msg = "🔔 NOTIFICATION HA COMPANION\n━━━━━━━━━━━━━━\n"
            msg += "L'app HA Companion sur votre téléphone recevra le code.\n\n"
            if notify_list:
                mobile_apps = [n for n in notify_list if "mobile_app" in n]
                if mobile_apps:
                    msg += "Services détectés :\n" + "\n".join(f"  • {n}" for n in mobile_apps[:5])
                else:
                    msg += "Services notify :\n" + "\n".join(f"  • {n}" for n in notify_list[:5])
                msg += "\n\nEnvoyez le nom du service :"
            else:
                msg += "Envoyez le nom du service notify (ex: mobile_app_iphone_de_jean) :"
            telegram_send(msg)
        elif method == "email":
            CFG["_wizard_step"] = "sms_email_addr"
            _wizard_save_config()
            telegram_send(
                "📧 EMAIL\n"
                "━━━━━━━━━━━━━━\n"
                "Le code sera envoyé par email.\n\n"
                "Envoyez votre adresse email :"
            )
        return

    # ═══ PROFIL FOYER — Questionnaire ═══
    if data.startswith("profil:"):
        parts = data.split(":", 2)
        if len(parts) == 3:
            _, qid, value = parts
            # Charger et mettre à jour le profil
            profil = {}
            try:
                d, _ = skill_get("foyer")
                if d:
                    profil = d
            except Exception:
                pass
            profil[qid] = value
            skill_set("foyer", profil)
            # Confirmation courte
            q_label = next((q["question"].split("\n")[0] for q in PROFIL_QUESTIONS if q["id"] == qid), qid)
            v_label = next((b["text"] for q in PROFIL_QUESTIONS if q["id"] == qid for b in q["boutons"] if b["value"] == value), value)
            telegram_send(f"✅ {v_label}")
            # Question suivante
            _lancer_questionnaire_foyer()
        return

    # ═══ CYCLES — Confirmation restart ═══
    # ═══ PROGRAMMES — Nommer un nouveau programme ═══
    if data.startswith("prog_nommer:"):
        parts = data.split(":", 4)
        if len(parts) >= 5:
            eid = parts[1]
            sig_short = parts[2]
            duree = int(parts[3]) if parts[3].isdigit() else 0
            conso = float(parts[4]) if parts[4].replace(".", "").isdigit() else 0
            # Stocker en attente et demander le nom
            mem_set("attente_nom_programme", json.dumps({
                "entity_id": eid, "signature": sig_short, "duree": duree, "conso": conso
            }))
            app = appareil_get(eid)
            app_nom = app["nom"] if app and app.get("nom") else eid
            telegram_send(
                f"📝 Tapez le nom du programme pour {app_nom}\n"
                f"Exemples : Coton 60°, Synthétique 40°, Express, Éco...",
                force=True
            )
        return

    if data.startswith("prog_ignorer:"):
        telegram_send("✅ Programme ignoré.", force=True)
        return

    if data.startswith("cycle_fin:"):
        eid = data.split(":", 1)[1]
        app = appareil_get(eid)
        app_nom = app["nom"] if app and app.get("nom") else eid
        _etat_prises.pop(eid, None)
        # Fermer le cycle en DB
        try:
            conn_cf = sqlite3.connect(DB_PATH)
            conn_cf.execute(
                "UPDATE cycles_appareils SET fin=? WHERE entity_id=? AND fin IS NULL",
                (datetime.now().isoformat(), eid)
            )
            conn_cf.execute("DELETE FROM cycle_mesures WHERE entity_id=?", (eid,))
            conn_cf.commit()
            conn_cf.close()
        except Exception:
            pass
        telegram_send(f"✅ {app_nom} — cycle fermé. Pas de double notification.", force=True)
        return

    if data.startswith("cycle_continue:"):
        eid = data.split(":", 1)[1]
        app = appareil_get(eid)
        app_nom = app["nom"] if app and app.get("nom") else eid
        _etat_prises[eid] = "actif"
        # Restaurer les mesures
        try:
            conn_cc = sqlite3.connect(DB_PATH)
            rows = conn_cc.execute(
                "SELECT ts, watts FROM cycle_mesures WHERE entity_id=? ORDER BY ts", (eid,)
            ).fetchall()
            _puissances_historique[eid] = [(ts, w) for ts, w in rows]
            conn_cc.close()
        except Exception:
            pass
        telegram_send(f"🔄 {app_nom} — cycle repris. Je continue la surveillance.", force=True)
        return

    # ═══ MENU COMMANDES — Exécuter une commande par bouton ═══
    if data.startswith("cmd:"):
        cmd_name = data.split(":", 1)[1].strip()
        try:
            reponse = traiter_message(cmd_name)
            if reponse:
                telegram_send(reponse, force=True)
        except Exception:
            pass
        return

    # ═══ APPAREILS — Identification prises ═══
    if data.startswith("appareil:"):
        parts = data.split(":", 2)
        if len(parts) == 3:
            _, eid, type_app = parts
            fname_clean = eid.replace("sensor.", "").replace("_power", "").replace("_", " ").title()

            if type_app == "autre":
                # "Autre" → demander un nom personnalisé
                mem_set("attente_nom_appareil", eid)
                telegram_send(
                    f"🔌 {fname_clean}\n"
                    f"Quel est cet appareil ? Envoyez le nom :\n"
                    f"(ex: Congélateur garage, Four, Cafetière, PC bureau...)"
                )
                # Ne pas avancer dans la queue — on attend la réponse texte
                return

            if type_app == "ignorer":
                appareil_set(eid, "ignorer", "⬜ Ignoré")
                nb_surveilles = 0
                try:
                    conn_nb = sqlite3.connect(DB_PATH)
                    nb_surveilles = conn_nb.execute("SELECT COUNT(*) FROM appareils WHERE surveiller=1").fetchone()[0]
                    conn_nb.close()
                except Exception:
                    pass
                telegram_send(
                    f"⬜ {fname_clean} — voie de garage\n"
                    f"Pas de suivi, pas de notification.\n"
                    f"(tapez /appareils reset pour reconfigurer)\n"
                    f"📊 {nb_surveilles} appareils sous surveillance"
                )
            else:
                label = TYPES_APPAREILS.get(type_app, type_app)
                appareil_set(eid, type_app, label)
                nb_surveilles = 0
                try:
                    conn_nb = sqlite3.connect(DB_PATH)
                    nb_surveilles = conn_nb.execute("SELECT COUNT(*) FROM appareils WHERE surveiller=1").fetchone()[0]
                    conn_nb.close()
                except Exception:
                    pass

                if type_app == "coupe_veille":
                    telegram_send(
                        f"🔇 {fname_clean} → Coupe-veille\n"
                        f"Économies de standby mesurées automatiquement.\n"
                        f"Chaque heure OFF = watts évités → compteur ROI.\n"
                        f"📊 {nb_surveilles} appareils sous surveillance"
                    )
                elif type_app == "monitoring_energie":
                    telegram_send(
                        f"📊 {fname_clean} → Monitoring énergie\n"
                        f"Mesure production/conso — pas de détection cycles.\n"
                        f"📊 {nb_surveilles} appareils sous surveillance"
                    )
                else:
                    telegram_send(
                        f"✅ {fname_clean} → {label}\n"
                        f"Surveillance activée — cycles, coûts, économies.\n"
                        f"📊 {nb_surveilles} appareils sous surveillance"
                    )

            # Question suivante
            try:
                queue = json.loads(mem_get("appareils_queue") or "[]")
                queue = [q for q in queue if q["entity_id"] != eid]
                mem_set("appareils_queue", json.dumps(queue))
                _poser_question_appareil_suivant()
            except Exception:
                pass
        return

    # Pièce thermostat : piece:salon:entity_id
    if data.startswith("piece:"):
        parts = data.split(":", 2)
        if len(parts) == 3:
            _, piece, entity_id = parts
            conn = sqlite3.connect(DB_PATH)
            conn.execute('UPDATE cartographie SET piece=? WHERE entity_id=?', (piece, entity_id))
            conn.commit()
            conn.close()
            telegram_send(f"✅ {entity_id}\nPièce : {piece}")
        return

    # Zigbee Normal/Anormal : zigbee_normal:entity_id ou zigbee_anormal:entity_id
    if data.startswith("zigbee_normal:"):
        entity_id = data.split(":", 1)[1]
        zigbee_absence_statut(entity_id, "normal")
        telegram_send(f"✅ Noté — {entity_id}\nPlus d'alerte pour ce device en hors ligne temporaire.")
        return

    if data.startswith("zigbee_anormal:"):
        entity_id = data.split(":", 1)[1]
        zigbee_absence_statut(entity_id, "anormal")
        telegram_send(f"🔍 Surveillance activée — {entity_id}\nAlerte dès le retour en ligne ou après 2h.")
        return

    # Entité découverte — Oui/Non
    if data.startswith("entite_oui:"):
        entity_id = data.split(":", 1)[1]
        conn = sqlite3.connect(DB_PATH)
        # Anti-doublon : vérifier si déjà traité
        already = conn.execute(
            "SELECT reponse FROM entites_en_attente WHERE entity_id=?", (entity_id,)
        ).fetchone()
        if already and already[0]:
            conn.close()
            return  # Déjà traité — callback dupliqué ignoré
        row = conn.execute(
            "SELECT categorie_proposee, friendly_name FROM entites_en_attente WHERE entity_id=?",
            (entity_id,)
        ).fetchone()
        if row:
            cat, fname = row
            piece = ha_get_area(entity_id)
            conn.execute(
                """INSERT OR REPLACE INTO cartographie
                   (entity_id, categorie, sous_categorie, piece, friendly_name, appris_le)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (entity_id, cat, "", piece, fname, datetime.now().isoformat())
            )
            conn.execute(
                "UPDATE entites_en_attente SET reponse='oui' WHERE entity_id=?",
                (entity_id,)
            )
            conn.commit()
            conn.close()
            # Intégration immédiate dans groupe Énergie si pertinent
            msg = f"✅ Intégré — **{fname}**\nCatégorie : {cat}\n"
            if cat in ("energie_batterie", "energie_production", "energie_prevision"):
                msg += "🔋 Intégré dans le groupe Énergie — j'optimiserai votre consommation EDF."
            telegram_send_buttons(msg, [
                {"text": "↩️ Annuler cette intégration", "callback_data": f"entite_annuler:{entity_id}"},
            ])
            log.info(f"✅ Entité validée par l'utilisateur : {entity_id} → {cat}")
        else:
            conn.close()
            telegram_send("✅ Noté.")
        return

    if data.startswith("entite_annuler:"):
        entity_id = data.split(":", 1)[1]
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT friendly_name, reponse FROM entites_en_attente WHERE entity_id=?",
            (entity_id,)
        ).fetchone()
        if row:
            fname, reponse_precedente = row
            # Remettre en attente
            conn.execute(
                "UPDATE entites_en_attente SET reponse=NULL, question_posee=0 WHERE entity_id=?",
                (entity_id,)
            )
            # Si était intégré en cartographie → retirer
            if reponse_precedente == "oui":
                conn.execute(
                    "DELETE FROM cartographie WHERE entity_id=?",
                    (entity_id,)
                )
                conn.commit()
                conn.close()
                telegram_send(
                    f"↩️ Annulé — **{fname}** retiré du groupe Énergie.\n"
                    f"Il sera reproposé au prochain scan."
                )
            else:
                conn.commit()
                conn.close()
                telegram_send(
                    f"↩️ Annulé — **{fname}** remis en attente.\n"
                    f"Il sera reproposé au prochain scan."
                )
            log.info(f"↩️ Entité annulée : {entity_id} (était: {reponse_precedente})")
        else:
            conn.close()
            telegram_send("↩️ Annulation impossible — entité introuvable en mémoire.")
        return

    if data.startswith("entite_non:"):
        entity_id = data.split(":", 1)[1]
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT friendly_name FROM entites_en_attente WHERE entity_id=?",
            (entity_id,)
        ).fetchone()
        fname = row[0] if row else entity_id
        conn.execute(
            "UPDATE entites_en_attente SET reponse='non' WHERE entity_id=?",
            (entity_id,)
        )
        conn.execute(
            """INSERT OR REPLACE INTO cartographie
               (entity_id, categorie, sous_categorie, piece, friendly_name, appris_le)
               VALUES (?, 'a_ignorer', '', '', ?, ?)""",
            (entity_id, fname, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        telegram_send_buttons(f"❌ Ignoré — {fname}\nJe continue la recherche.", [
                {"text": "↩️ Annuler — réintégrer", "callback_data": f"entite_annuler:{entity_id}"},
            ])
        log.info(f"❌ Entité ignorée par l'utilisateur : {entity_id}")
        return

    # Entité disparue : confirmer suppression ou signaler anormal
    if data.startswith("disparue_ok:"):
        entity_id = data.split(":", 1)[1]
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id=?",
            (entity_id,)
        )
        conn.commit()
        conn.close()
        telegram_send(f"✅ Noté — {entity_id} retiré de la surveillance.\nPlus d'alerte pour cette entité.")
        log.info(f"✅ Entité disparue confirmée supprimée : {entity_id}")
        return

    if data.startswith("disparue_ko:"):
        entity_id = data.split(":", 1)[1]
        # Reset l'alerte pour qu'elle revienne dans 4h
        mem_set(f"disparue_{entity_id}", "")
        telegram_send(
            f"🔍 Surveillance activée — {entity_id}\n"
            f"Alerte si toujours absent au prochain scan."
        )
        log.warning(f"❌ Entité disparue anormale : {entity_id}")
        return

    # Auto-correction : appliquer ou annuler le patch Sonnet
    if data.startswith("patch_appliquer:"):
        old_code = mem_get("patch_pending_old", "")
        new_code = mem_get("patch_pending_new", "")
        explication = mem_get("patch_pending_expl", "")
        if not old_code:
            telegram_send("⚠️ Pas de patch en attente")
            return
        try:
            cfg_secret = CFG.get("deploy_secret", "")
            patch_body = json.dumps({"mode": "replace", "old_str": old_code, "new_str": new_code}).encode()
            sig = hmac.new(cfg_secret.encode(), patch_body, hashlib.sha256).hexdigest()
            req_patch = urllib.request.Request("http://localhost:8501/deploy", data=patch_body, method="POST")
            req_patch.add_header("Authorization", f"HMAC {sig}")
            req_patch.add_header("Content-Type", "application/json")
            resp_patch = urllib.request.urlopen(req_patch, timeout=30)
            result = json.loads(resp_patch.read().decode())
            if result.get("status") == "ok":
                telegram_send(
                    f"✅ PATCH APPLIQUÉ + REDÉMARRÉ\n"
                    f"Correction : {explication}\n"
                    f"Backup : {result.get('patch', {}).get('backup', '?')}"
                )
            else:
                telegram_send(f"❌ Échec deploy : {result.get('message', result)}")
        except Exception as e:
            telegram_send(f"❌ Erreur deploy : {e}")
        finally:
            mem_set("patch_pending_old", "")
            mem_set("patch_pending_new", "")
        return

    if data.startswith("patch_annuler:"):
        mem_set("patch_pending_old", "")
        mem_set("patch_pending_new", "")
        telegram_send("❌ Patch annulé — aucune modification.")
        return

    # Coupure EDF : restaurer l'état exact d'avant la coupure
    if data.startswith("edf_restaurer:"):
        snapshot_json = mem_get("edf_snapshot", "{}")
        try:
            snapshot = json.loads(snapshot_json)
        except Exception:
            snapshot = {}
        if not snapshot:
            telegram_send("⚠️ Pas de snapshot disponible — restauration impossible")
            return
        rallumees = 0
        laissees_off = 0
        for eid, etat_avant in snapshot.items():
            if not eid.startswith("switch.") or "child_lock" in eid:
                continue
            try:
                if etat_avant == "on":
                    ha_post("services/switch/turn_on", {"entity_id": eid})
                    rallumees += 1
                else:
                    laissees_off += 1
            except Exception:
                pass
        telegram_send(
            f"✅ Restauration coupure EDF terminée\n"
            f"🟢 {rallumees} prise(s) remise(s) en ON\n"
            f"⚫ {laissees_off} prise(s) laissée(s) en OFF (état normal)"
        )
        log.info(f"✅ Coupure EDF restaurée : {rallumees} ON, {laissees_off} OFF")
        return

    if data.startswith("edf_laisser:"):
        telegram_send("✅ OK — prises laissées en l'état.")
        return

    # Suggestion machine : suggestion_oui, suggestion_non, suggestion_toujours
    if data.startswith("suggestion_oui:"):
        entity_id = data.split(":", 1)[1]
        telegram_send(f"✅ Compris ! Lancez la machine quand vous êtes prêt.\nJe surveille le cycle.")
        return

    if data.startswith("suggestion_non:"):
        telegram_send("✅ OK, pas de machine aujourd'hui.")
        return

    if data.startswith("suggestion_1h:"):
        telegram_send("⏰ Je vous rappelle dans 1 heure.")
        # Stocker rappel
        mem_set("rappel_machine", (datetime.now() + timedelta(hours=1)).isoformat())
        return


def ha_get_areas_mapping():
    """Récupère mapping area_id -> nom lisible via /api/template (seul endpoint fiable sur HA Green)."""
    try:
        url = f"{CFG['ha_url']}/api/template"
        headers = {"Authorization": f"Bearer {CFG['ha_token']}", "Content-Type": "application/json"}
        template = "{% for area in areas() %}AREA:::{{ area_name(area) }}:::{{ area }};;;{% endfor %}"
        r = requests.post(url, headers=headers, json={"template": template}, verify=False, timeout=10)
        if r.status_code == 200:
            mapping = {}
            for chunk in r.text.split(";;;"):
                chunk = chunk.strip()
                if chunk.startswith("AREA:::"):
                    parts = chunk.split(":::")
                    if len(parts) == 3:
                        name = parts[1].strip()
                        aid = parts[2].strip()
                        if aid:
                            mapping[aid] = name
            if mapping:
                log.info(f"\u2705 Areas HA : {len(mapping)} pièces via /api/template")
                return mapping
    except Exception as ex:
        log.debug(f"Areas template: {ex}")

    # Fallback REST classique (HA versions plus anciennes)
    for endpoint in ["/api/config/area_registry/list", "/api/areas"]:
        try:
            url = f"{CFG['ha_url']}{endpoint}"
            headers = {"Authorization": f"Bearer {CFG['ha_token']}"}
            r = requests.get(url, headers=headers, verify=False, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list) and data:
                    mapping = {}
                    for a in data:
                        aid = a.get("area_id") or a.get("id", "")
                        name = a.get("name", "") or aid
                        if aid:
                            mapping[aid] = name
                    if mapping:
                        log.info(f"✅ Areas HA : {len(mapping)} pièces via {endpoint}")
                        return mapping
        except Exception as ex:
            log.debug(f"Areas {endpoint} : {ex}")

    log.warning("⚠️ Areas HA non disponibles")
    return {}


def ha_get_entity_areas():
    """Récupère mapping entity_id -> area_id via /api/template (seul endpoint fiable sur HA Green)."""
    entity_map = {}

    # Méthode 1 : /api/template avec area_entities() — le plus fiable
    try:
        url = f"{CFG['ha_url']}/api/template"
        headers = {"Authorization": f"Bearer {CFG['ha_token']}", "Content-Type": "application/json"}
        template = '{% for area in areas() %}{% for eid in area_entities(area) %}{{ eid }}|{{ area }}\n{% endfor %}{% endfor %}'
        r = requests.post(url, headers=headers, json={"template": template}, verify=False, timeout=15)
        if r.status_code == 200:
            text = r.text.strip()
            log.debug(f"entity_areas template response: {len(text)} chars")
            for line in text.split("\n"):
                line = line.strip()
                if "|" in line:
                    eid, aid = line.split("|", 1)
                    entity_map[eid.strip()] = aid.strip()
            log.debug(f"entity_areas parsed: {len(entity_map)} entities")
            if entity_map:
                return entity_map
        else:
            log.warning(f"entity_areas template: HTTP {r.status_code}")
    except Exception as ex:
        log.warning(f"entity_areas template: {ex}")

    # Fallback : aussi chercher via device_areas (device → entités)
    try:
        url = f"{CFG['ha_url']}/api/template"
        headers = {"Authorization": f"Bearer {CFG['ha_token']}", "Content-Type": "application/json"}
        template = '{% for area in areas() %}{% for dev in area_devices(area) %}{% for eid in device_entities(dev) %}{{ eid }}|{{ area }}\n{% endfor %}{% endfor %}{% endfor %}'
        r = requests.post(url, headers=headers, json={"template": template}, verify=False, timeout=15)
        if r.status_code == 200:
            for line in r.text.strip().split("\n"):
                if "|" in line:
                    eid, aid = line.split("|", 1)
                    eid = eid.strip()
                    if eid not in entity_map:
                        entity_map[eid.strip()] = aid.strip()
    except Exception as ex:
        log.debug(f"device_areas template: {ex}")

    # Fallback REST classique
    if not entity_map:
        for endpoint in ["/api/config/entity_registry/list", "/api/entity_registry"]:
            try:
                url = f"{CFG['ha_url']}{endpoint}"
                headers = {"Authorization": f"Bearer {CFG['ha_token']}"}
                r = requests.get(url, headers=headers, verify=False, timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, list):
                        for e in data:
                            entity_map[e.get("entity_id", "")] = e.get("area_id") or ""
                        return entity_map
            except Exception as ex:
                log.debug(f"entity_areas {endpoint}: {ex}")

    return entity_map


def ha_get_entity_areas():
    """Récupère mapping entity_id -> area_id via /api/template."""
    entity_map = {}
    url = f"{CFG['ha_url']}/api/template"
    headers = {"Authorization": f"Bearer {CFG['ha_token']}", "Content-Type": "application/json"}

    # Combiner area_entities (direct) + device_entities (héritage) en un seul appel
    template = (
        "{% for area in areas() %}"
        "{% for eid in area_entities(area) %}"
        "ENTAREA:::{{ eid }}:::{{ area }};;;"
        "{% endfor %}"
        "{% for dev in area_devices(area) %}"
        "{% for eid in device_entities(dev) %}"
        "ENTAREA:::{{ eid }}:::{{ area }};;;"
        "{% endfor %}"
        "{% endfor %}"
        "{% endfor %}"
    )

    try:
        r = requests.post(url, headers=headers, json={"template": template}, verify=False, timeout=20)
        if r.status_code == 200:
            for chunk in r.text.split(";;;"):
                chunk = chunk.strip()
                if chunk.startswith("ENTAREA:::"):
                    parts = chunk.split(":::")
                    if len(parts) == 3:
                        eid = parts[1].strip()
                        aid = parts[2].strip()
                        if eid and aid and eid not in entity_map:
                            entity_map[eid] = aid
            log.info(f"entity_areas: {len(entity_map)} entités mappées via template")
        else:
            log.warning(f"entity_areas template: HTTP {r.status_code}")
    except Exception as ex:
        log.warning(f"entity_areas template: {ex}")

    return entity_map


def ha_refresh_areas():
    """Charge les areas HA et met à jour les pièces en cartographie."""
    # # global _areas_id_to_name, _entity_areas    # via shared# via shared
    shared._areas_id_to_name = ha_get_areas_mapping()
    shared._entity_areas     = ha_get_entity_areas()
    log.info(f"✅ Areas HA : {len(shared._areas_id_to_name)} pièces, {len(shared._entity_areas)} entités")

    # Mettre à jour les pièces en cartographie (API HA + fallback friendly_name)
    _PIECES_CONNUES_REFRESH = [
        "cuisine", "salon", "chambre amis", "chambre enfant", "chambre",
        "buanderie", "garage", "bureau", "salle de bain", "sdb",
        "entrée", "couloir", "jardin", "terrasse", "grenier", "cave",
    ]
    try:
        conn = sqlite3.connect(DB_PATH)
        mises_a_jour = 0
        rows = conn.execute("SELECT entity_id, piece, friendly_name FROM cartographie WHERE piece IS NULL OR piece=''").fetchall()
        for eid, piece_actuelle, fname in rows:
            nouvelle_piece = ""
            # Essai 1 : API HA
            area_id = _entity_areas.get(eid, "")
            if area_id:
                nouvelle_piece = _areas_id_to_name.get(area_id, area_id)
            # Essai 2 : extraire depuis friendly_name
            if not nouvelle_piece and fname:
                fn = fname.lower()
                for p in _PIECES_CONNUES_REFRESH:
                    if p in fn:
                        nouvelle_piece = p
                        break
            if nouvelle_piece:
                conn.execute("UPDATE cartographie SET piece=? WHERE entity_id=?", (nouvelle_piece, eid))
                mises_a_jour += 1
        if mises_a_jour > 0:
            conn.commit()
            log.info(f"🏠 {mises_a_jour} pièces mises à jour en cartographie")
        conn.close()
    except Exception as ex:
        log.error(f"Mise à jour pièces: {ex}")


def ha_get_area(entity_id):
    """Retourne le nom lisible de la pièce d'une entité"""
    area_id = _entity_areas.get(entity_id, "")
    if area_id:
        return _areas_id_to_name.get(area_id, area_id)
    return ""


def _surveiller_pac_correlee(index, etats):
    """PAC : alerte uniquement si VRAIMENT en panne (pas un cycle thermostat).
    Skip silencieux si pas de PAC.
    Le thermostat fait du on/off naturellement. On alerte seulement si :
    1. PAC en mode OFF (pas auto/heat) = désactivée manuellement
    2. Température extérieure < 3°C (vrai froid)
    3. Température intérieure < 17°C ET en baisse
    → Cela signifie que la PAC est éteinte ET la maison se refroidit."""
    if not role_get("pac_climate"):
        return
    pac_entity = None
    pac_state  = None
    for e in etats:
        eid = e["entity_id"]
        if not eid.startswith("climate."):
            continue
        carto = cartographie_get(eid)
        if carto and "chauffage" in carto[0].lower():
            pac_entity = eid
            pac_state  = e["state"]
            break

    if pac_entity is None:
        return

    # PAC en mode actif (auto, heat, etc.) → le thermostat gère, on ne dit rien
    if pac_state in ["auto", "heat", "cool", "fan_only", "heat_cool"]:
        return

    # PAC vraiment OFF — vérifier si c'est grave
    temp_ext = None
    try:
        e_ext = index.get(role_get("temp_exterieure") or "sensor.ecojoko_temperature_exterieure")
        if e_ext and e_ext["state"] not in ["unavailable", "unknown"]:
            temp_ext = float(e_ext["state"])
    except Exception:
        pass

    if temp_ext is None or temp_ext > 3:
        return  # Pas assez froid pour être critique

    # Température intérieure
    temp_int = None
    try:
        e_int = index.get(role_get("temp_interieure") or "sensor.ecojoko_temperature_interieure")
        if e_int and e_int["state"] not in ["unavailable", "unknown"]:
            temp_int = float(e_int["state"])
    except Exception:
        pass

    if temp_int is None or temp_int >= 17:
        return  # La maison est encore chaude — pas urgent

    # Vérifier que la température BAISSE (comparer avec le snapshot précédent)
    try:
        prev_json = mem_get("snapshot_precedent")
        if prev_json:
            prev = json.loads(prev_json)
            prev_int = prev.get("temp_int")
            if prev_int is not None and temp_int >= prev_int:
                return  # Température stable ou en hausse — pas de problème
    except Exception:
        pass

    # ICI c'est une vraie urgence : PAC off + gel + maison froide + temp qui baisse
    _alerter_si_nouveau(
        "pac_off_froid",
        f"🚨 PAC ÉTEINTE — Maison se refroidit\n"
        f"Ext: {temp_ext:.1f}°C | Int: {temp_int:.1f}°C (en baisse)\n"
        f"PAC {pac_entity} : {pac_state}\n"
        f"Vérifier : thermostat / disjoncteur / mode",
        delai_h=6
    )


def ha_get_contexte_intelligent(question, etats=None):
    if etats is None:
        etats = ha_get("states")
    if not etats:
        return "HA inaccessible"

    index = {e["entity_id"]: e for e in etats}
    categories_disponibles = cartographie_get_toutes_categories()

    if not categories_disponibles:
        return _ha_resume_generique(etats)

    prompt_detection = (
        f"Question : \"{question}\"\n"
        f"Catégories disponibles : {', '.join(categories_disponibles)}\n"
        "Liste UNIQUEMENT les catégories pertinentes, séparées par des virgules."
    )

    try:
        client = anthropic.Anthropic(api_key=CFG["anthropic_api_key"])
        r = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=80,
            messages=[{"role": "user", "content": prompt_detection}]
        )
        log_token_usage(r.usage.input_tokens, r.usage.output_tokens)
        categories_cibles = [c.strip() for c in r.content[0].text.strip().split(",") if c.strip()]
    except Exception as e:
        log.error(f"❌ Détection catégorie: {e}")
        return _ha_resume_generique(etats)

    lignes = []
    for cat in categories_cibles:
        entites_cat = cartographie_get_par_categorie(cat)
        for entity_id, sous_cat, piece in entites_cat:
            if entity_id in index:
                e = index[entity_id]
                unite = e.get("attributes", {}).get("unit_of_measurement", "")
                piece_str = f" [{piece}]" if piece else ""
                lignes.append(f"{entity_id}{piece_str} = {e['state']} {unite}".strip())

    # ═══ CALENDRIERS HA — événements des 72 prochaines heures ═══
    try:
        now_dt = datetime.now()
        start_dt = now_dt.strftime("%Y-%m-%dT00:00:00")
        end_dt = (now_dt + timedelta(hours=72)).strftime("%Y-%m-%dT23:59:59")
        headers_cal = {"Authorization": f"Bearer {CFG['ha_token']}"}
        url_cals = f"{CFG['ha_url']}/api/calendars"

        r_list = requests.get(url_cals, headers=headers_cal, verify=False, timeout=15)
        log.debug(f"Calendars API: {r_list.status_code} | {len(r_list.json()) if r_list.status_code == 200 else r_list.text[:100]}")

        if r_list.status_code == 200:
            for cal_info in r_list.json():
                eid = cal_info.get("entity_id", "")
                fname = cal_info.get("name", eid)
                url_ev = f"{CFG['ha_url']}/api/calendars/{eid}?start={start_dt}&end={end_dt}"
                try:
                    r_ev = requests.get(url_ev, headers=headers_cal, verify=False, timeout=15)
                    if r_ev.status_code == 200:
                        events = r_ev.json()
                        for ev in events[:5]:
                            summary = ev.get("summary", "?")
                            ev_start = ev.get("start", {})
                            date_str = ev_start.get("dateTime", ev_start.get("date", "?"))
                            try:
                                if "T" in str(date_str):
                                    dt_ev = datetime.fromisoformat(date_str.replace("Z", "+00:00")[:19])
                                    jours_fr = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
                                    date_lisible = f"{jours_fr[dt_ev.weekday()]} {dt_ev.day}/{dt_ev.month} à {dt_ev.hour}h{dt_ev.minute:02d}"
                                else:
                                    date_lisible = str(date_str)
                            except Exception:
                                date_lisible = str(date_str)
                            lignes.append(f"📅 CALENDRIER {fname}: {summary} — {date_lisible}")
                        if not events:
                            lignes.append(f"📅 CALENDRIER {fname}: rien dans les 72h")
                except Exception as ex_ev:
                    log.debug(f"Calendar events {eid}: {ex_ev}")
    except Exception as ex_cal:
        log.debug(f"Calendars API error: {ex_cal}")

    # ═══ CONSTRUIRE LE CONTEXTE ═══
    # Calendriers EN PREMIER (prioritaires pour les questions du quotidien)
    cal_lignes = [l for l in lignes if l.startswith("📅")]
    autres_lignes = [l for l in lignes if not l.startswith("📅")]
    lignes_ordonnees = cal_lignes + autres_lignes
    contexte = "Données disponibles :\n" + "\n".join(lignes_ordonnees[:80]) if lignes_ordonnees else _ha_resume_generique(etats)

    # ═══ ENRICHIR AVEC LA MÉMOIRE SQLITE ═══
    memoire_extra = []

    # Baselines : comparer les valeurs actuelles aux habitudes
    now = datetime.now()
    jour = now.weekday()
    heure = now.hour
    try:
        conn = sqlite3.connect(DB_PATH)
        for eid in list(BASELINE_ENTITIES.keys()):
            row = conn.execute(
                "SELECT valeur_moyenne, nb_mesures FROM baselines WHERE entity_id=? AND jour_semaine=? AND heure=?",
                (eid, jour, heure)
            ).fetchone()
            if row and row[1] >= 5:
                e = index.get(eid)
                if e and e["state"] not in ("unavailable", "unknown"):
                    try:
                        val = float(e["state"])
                        moy = row[0]
                        ecart = abs(val - moy) / moy * 100 if moy > 0 else 0
                        label = BASELINE_ENTITIES[eid]
                        memoire_extra.append(
                            f"BASELINE {label}: actuel={val:.0f}, habituel={moy:.0f} "
                            f"(écart {ecart:.0f}%, {row[1]} mesures)"
                        )
                    except Exception:
                        pass
        conn.close()
    except Exception:
        pass

    # Derniers cycles machines
    try:
        conn = sqlite3.connect(DB_PATH)
        cycles = conn.execute(
            "SELECT friendly_name, debut, duree_min, conso_kwh FROM cycles_appareils "
            "WHERE fin IS NOT NULL ORDER BY created_at DESC LIMIT 5"
        ).fetchall()
        conn.close()
        if cycles:
            memoire_extra.append("DERNIERS CYCLES MACHINES :")
            for fname, debut, duree, conso in cycles:
                date = debut[:10] if debut else "?"
                memoire_extra.append(f"  {fname} — {date} | {duree}min | {conso:.2f}kWh")
    except Exception:
        pass

    # Mémoire clés importantes
    try:
        cles_utiles = ["dernier_bilan", "ha_scan_date", "ha_entites_count", "decouverte_count"]
        for cle in cles_utiles:
            val = mem_get(cle)
            if val:
                memoire_extra.append(f"MEM {cle} = {val}")
    except Exception:
        pass

    # Tarif électricité (pour répondre aux questions coût/économie)
    try:
        tarif = tarif_get()
        prix_now = tarif_prix_kwh_actuel()
        ttype = tarif.get("type", "base")
        fournisseur = tarif.get("fournisseur", "?")
        est_we = _est_weekend_ou_ferie()
        info_tarif = f"TARIF: {fournisseur} {ttype} | Prix actuel: {prix_now}€/kWh"
        if ttype in ("hphc", "weekend_hphc", "weekend_plus_hphc"):
            hc = _est_heure_creuse_plages(tarif.get("heures_creuses", []))
            info_tarif += f" ({'HC' if hc else 'HP'})"
        if est_we:
            info_tarif += " (week-end/férié)"
        jour_choisi = tarif.get("jour_choisi")
        if jour_choisi is not None:
            jours = ['lun', 'mar', 'mer', 'jeu', 'ven', 'sam', 'dim']
            info_tarif += f" | Jour choisi: {jours[jour_choisi]}"
        memoire_extra.append(info_tarif)
        # Bilan tarif du mois
        data_tarif, nb_tarif = skill_get("optimisation_tarif")
        if data_tarif and data_tarif.get("total_kwh", 0) > 1:
            periodes = data_tarif.get("periodes", {})
            resume = " | ".join(f"{p}:{v['kwh']:.0f}kWh/{v['eur']:.1f}€" for p, v in periodes.items())
            memoire_extra.append(f"BILAN TARIF MOIS: {data_tarif['total_kwh']:.0f}kWh {data_tarif['total_eur']:.1f}€ | {resume}")
    except Exception:
        pass

    # Expertise accumulée (les règles que l'IA a apprises)
    try:
        conn_exp = sqlite3.connect(DB_PATH)
        expertise = conn_exp.execute(
            "SELECT categorie, insight, confiance FROM expertise "
            "WHERE confiance >= 0.4 ORDER BY confiance DESC LIMIT 10"
        ).fetchall()
        conn_exp.close()
        if expertise:
            memoire_extra.append("EXPERTISE ACQUISE (règles apprises par l'IA) :")
            for cat, insight, conf in expertise:
                etoiles = "★" * min(5, int(conf * 5))
                memoire_extra.append(f"  [{cat}] {etoiles} {insight}")
    except Exception:
        pass

    # Hypothèses validées (prédictions fiables)
    try:
        conn_hyp = sqlite3.connect(DB_PATH)
        hyps = conn_hyp.execute(
            "SELECT enonce, confiance, confirmations, predictions FROM hypotheses "
            "WHERE active=1 AND confiance >= 0.6 AND predictions >= 3 ORDER BY confiance DESC LIMIT 5"
        ).fetchall()
        if hyps:
            memoire_extra.append("HYPOTHÈSES VALIDÉES (prédictions fiables) :")
            for enonce, conf, confirm, pred in hyps:
                memoire_extra.append(f"  [{conf:.0%}] {enonce} ({confirm}/{pred} confirmées)")

        # Score intelligence
        score_row = conn_hyp.execute(
            "SELECT score_global, details FROM intelligence_score ORDER BY date DESC LIMIT 1"
        ).fetchone()
        if score_row:
            details = json.loads(score_row[1]) if score_row[1] else {}
            memoire_extra.append(f"SCORE INTELLIGENCE: {score_row[0]}/100 ({details.get('niveau', '?')})")
        conn_hyp.close()
    except Exception:
        pass

    # Santé hôte (pour que Haiku sache si la machine souffre)
    try:
        data_hote, nb_hote = skill_get("sante_hote")
        if data_hote and data_hote.get("historique"):
            dernier = data_hote["historique"][-1].get("metriques", {})
            ram = dernier.get("ram_mb", "?")
            disque = dernier.get("disque_libre_mb", "?")
            latence = dernier.get("latence_ha_ms", "?")
            memoire_extra.append(f"HÔTE: RAM={ram}MB | Disque libre={disque}MB | Latence HA={latence}ms")
    except Exception:
        pass

    # Santé hôte (si problème)
    try:
        data_hote, nb_hote = skill_get("hote")
        if data_hote and "derniere_mesure" in data_hote:
            m = data_hote["derniere_mesure"]
            ram = m.get("ram_pct", 0)
            disque = m.get("disque_pct", 0)
            if ram > 70 or disque > 80:
                memoire_extra.append(
                    f"HÔTE: RAM {ram:.0f}% | Disque {disque:.0f}% | "
                    f"DB {m.get('db_kb', '?')}KB | Load {m.get('cpu_load5', '?')}"
                )
    except Exception:
        pass

    # Dernière analyse IA
    try:
        derniere_analyse = mem_get("derniere_analyse_ia")
        derniere_date = mem_get("derniere_analyse_ia_date")
        if derniere_analyse and derniere_date:
            memoire_extra.append(f"DERNIÈRE ANALYSE ({derniere_date[:16]}) : {derniere_analyse[:300]}")
    except Exception:
        pass

    # Économies du mois (et mois précédent pour comparaison)
    try:
        eco_mois = get_economies_mois()
        if eco_mois["nb_actions"] > 0:
            memoire_extra.append(
                f"ÉCONOMIES MOIS EN COURS: {eco_mois['total_eur']:.2f}€ | "
                f"{eco_mois['total_kwh']:.1f} kWh | {eco_mois['nb_actions']} actions"
            )
            for t, d in eco_mois["par_type"].items():
                memoire_extra.append(f"  {t}: {d['eur']:.2f}€ ({d['nb']} actions)")
        # Mois précédent
        mois_prec = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
        eco_prec = get_economies_mois(mois_prec)
        if eco_prec["nb_actions"] > 0:
            memoire_extra.append(
                f"ÉCONOMIES MOIS PRÉCÉDENT ({mois_prec}): {eco_prec['total_eur']:.2f}€ | "
                f"{eco_prec['total_kwh']:.1f} kWh | {eco_prec['nb_actions']} actions"
            )
    except Exception:
        pass

    # Projection facture EDF fin de mois
    try:
        import calendar as _cal
        data_tarif, nb_tarif = skill_get("optimisation_tarif")
        if data_tarif and data_tarif.get("total_kwh", 0) > 1:
            now_proj = datetime.now()
            jour_actuel = now_proj.day
            jours_mois = _cal.monthrange(now_proj.year, now_proj.month)[1]
            jours_restants = jours_mois - jour_actuel

            conso_kwh = data_tarif["total_kwh"]
            conso_eur = data_tarif["total_eur"]

            # Projection linéaire
            if jour_actuel > 0:
                kwh_par_jour = conso_kwh / jour_actuel
                eur_par_jour = conso_eur / jour_actuel
                proj_kwh = kwh_par_jour * jours_mois
                proj_eur = eur_par_jour * jours_mois

                # Abonnement EDF (~16€/mois pour 9kVA, ajustable)
                abo_mensuel = CFG.get("edf_abonnement_mensuel", 16.0)
                proj_total = proj_eur + abo_mensuel

                memoire_extra.append(
                    f"FACTURE EDF PROJECTION: "
                    f"Conso {jour_actuel}j = {conso_kwh:.0f} kWh / {conso_eur:.1f}€ | "
                    f"Projection mois = {proj_kwh:.0f} kWh / {proj_eur:.1f}€ conso + {abo_mensuel:.0f}€ abo = ~{proj_total:.0f}€ TTC | "
                    f"Moyenne {kwh_par_jour:.1f} kWh/j / {eur_par_jour:.2f}€/j"
                )

                # Détail par période
                periodes = data_tarif.get("periodes", {})
                noms_p = {"hp": "HP", "hc": "HC", "base": "Base", "semaine": "Semaine", "weekend_jour": "WE/Jour choisi"}
                for p, vals in periodes.items():
                    pct = vals["kwh"] / conso_kwh * 100 if conso_kwh > 0 else 0
                    memoire_extra.append(f"  {noms_p.get(p, p)}: {vals['kwh']:.0f} kWh ({pct:.0f}%) / {vals['eur']:.1f}€")

                # Solaire
                solaire_kwh = data_tarif.get("solaire_kwh", 0)
                if solaire_kwh > 0:
                    eco_sol = solaire_kwh * (conso_eur / conso_kwh if conso_kwh > 0 else 0.20)
                    memoire_extra.append(f"  Solaire autoconsommé: {solaire_kwh:.0f} kWh → ~{eco_sol:.1f}€ économisés (non facturé)")
    except Exception:
        pass

    # Skills appris
    try:
        data_sol, nb_sol = skill_get("fenetre_solaire")
        if data_sol and nb_sol >= 10:
            jour_str = str(datetime.now().weekday())
            if jour_str in data_sol:
                best = max(data_sol[jour_str].items(), key=lambda x: x[1][0])
                memoire_extra.append(f"SKILL fenetre_solaire: pic {best[0]}h → {int(best[1][0])} W ({nb_sol} apprentissages)")

        data_cyc, nb_cyc = skill_get("cycle_signatures")
        if data_cyc:
            for eid, info in list(data_cyc.items())[:3]:
                memoire_extra.append(
                    f"SKILL machine {info['nom']}: ~{info['duree_moy']:.0f}min, "
                    f"~{info['conso_moy']:.2f}kWh, {info['nb_cycles']} cycles"
                )

        data_pac, nb_pac = skill_get("comportement_pac")
        if data_pac and nb_pac >= 10:
            memoire_extra.append(f"SKILL comportement_pac: {nb_pac} observations")
    except Exception:
        pass

    if memoire_extra:
        contexte += "\n\n=== MÉMOIRE / HISTORIQUE ===\n" + "\n".join(memoire_extra)

    return contexte


def _ha_resume_generique(etats):
    resume = []
    cats = {"sensor": [], "binary_sensor": [], "switch": [], "climate": [], "automation": []}
    for e in etats:
        d = e["entity_id"].split(".")[0]
        if d in cats:
            cats[d].append(f"{e['entity_id']}={e['state']}")
    for d, items in cats.items():
        if items:
            resume.append(f"[{d}] {', '.join(items[:8])}")
    return "\n".join(resume[:40])


def _match_pattern(entity_id, fname):
    """Tente de catégoriser une entité via les patterns."""
    import re
    eid_low = entity_id.lower()
    fname_low = (fname or "").lower()
    combined = eid_low + " " + fname_low
    for p_id, p_nom, cat, sous, desc in PATTERNS_AUTO:
        if p_id in combined:
            if not p_nom or re.search(p_nom, combined):
                return cat, sous, desc
    return None, None, None


def _construire_question_intelligente(entity_id, fname, etat, attrs):
    """Utilise Claude pour construire une question précise"""
    unite = attrs.get("unit_of_measurement", "")
    device_class = attrs.get("device_class", "")
    prompt = (
        f"Tu es l'assistant domotique de l'utilisateur.\n"
        f"entity_id: {entity_id}\n"
        f"friendly_name: {fname}\n"
        f"état: {etat} {unite}\n"
        f"device_class: {device_class}\n\n"
        f"Propose UNE phrase : ce que fait cette entité et sa catégorie.\n"
        f"Catégories : energie_batterie, energie_production, energie_prevision, meteo, prise_connectee, chauffage, a_ignorer\n\n"
        f"Réponds UNIQUEMENT en JSON: {{\"categorie\": \"...\", \"description\": \"...\"}}"
    )
    try:
        client = anthropic.Anthropic(api_key=CFG["anthropic_api_key"])
        r = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )
        import json as _json
        txt = r.content[0].text.strip()
        txt = txt.replace("```json", "").replace("```", "").strip()
        data = _json.loads(txt)
        log_token_usage(r.usage.input_tokens, r.usage.output_tokens)
        return data.get("categorie", "inconnu"), data.get("description", fname)
    except Exception as ex:
        log.warning(f"⚠️ Question intelligente {entity_id}: {ex}")
        return "inconnu", fname


def poser_question_entite(entity_id, fname, categorie, description):
    """Envoie une question Telegram avec boutons Oui/Non"""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT question_posee, reponse FROM entites_en_attente WHERE entity_id=?",
        (entity_id,)
    ).fetchone()
    conn.close()

    if row and row[0] == 1 and not row[1]:
        log.debug(f"Question déjà posée sans réponse : {entity_id}")
        return

    if row and row[1]:
        log.debug(f"Entité déjà répondue : {entity_id} → {row[1]}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT OR REPLACE INTO entites_en_attente
           (entity_id, friendly_name, categorie_proposee, description, question_posee, created_at)
           VALUES (?, ?, ?, ?, 1, ?)""",
        (entity_id, fname, categorie, description, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    msg = (
        f"🔍 Nouvelle entité découverte\n"
        f"**{fname}**\n"
        f"Catégorie proposée : {categorie}\n"
        f"Rôle supposé : {description}\n\n"
        f"Est-ce correct ?"
    )
    telegram_send_buttons(msg, [
        {"text": "✅ Oui",   "callback_data": f"entite_oui:{entity_id}"},
        {"text": "❌ Non",   "callback_data": f"entite_non:{entity_id}"},
        {"text": "↩️ Annuler","callback_data": f"entite_annuler:{entity_id}"},
    ])
    log.info(f"❓ Question posée : {fname} ({entity_id})")


def _verifier_coherence_cartographie(index):
    """Vérifie que les entités déjà en mémoire sont toujours cohérentes"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT entity_id, categorie, friendly_name FROM cartographie"
    ).fetchall()
    conn.close()

    for entity_id, categorie, fname in rows:
        if "prise" in entity_id and categorie in ("energie_batterie", "energie_production", "energie_prevision"):
            log.warning(f"🔧 Correction : {entity_id} mal classifié")
            conn2 = sqlite3.connect(DB_PATH)
            conn2.execute(
                "UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id=?",
                (entity_id,)
            )
            conn2.commit()
            conn2.close()
            continue

        if entity_id not in index:
            if categorie in ("a_ignorer", "disparu_confirme"):
                continue

            # Vérifier si on a déjà alerté pour cette entité
            cle_alerte = f"disparue_{entity_id}"
            deja_alertee = mem_get(cle_alerte)
            if deja_alertee:
                continue

            # Première détection : alerte avec boutons
            mem_set(cle_alerte, datetime.now().isoformat())
            piece_str = f" [{fname}]" if fname else ""
            telegram_send_buttons(
                f"⚠️ Entité disparue de HA\n{entity_id}{piece_str}\nCatégorie : {categorie}",
                [
                    {"text": "✅ Supprimé (normal)", "callback_data": f"disparue_ok:{entity_id}"},
                    {"text": "❌ Anormal", "callback_data": f"disparue_ko:{entity_id}"},
                ]
            )
            log.warning(f"⚠️ Entité disparue : {entity_id}")


def traiter_entites_en_attente(index):
    """Scan d'infiltration — détecte toutes les nouvelles entités"""
    conn = sqlite3.connect(DB_PATH)
    connus = set(
        r[0] for r in conn.execute(
            "SELECT entity_id FROM cartographie WHERE categorie != 'a_ignorer'"
        ).fetchall()
    )
    en_attente = set(r[0] for r in conn.execute(
        "SELECT entity_id FROM entites_en_attente WHERE reponse IS NULL OR reponse = ''"
    ).fetchall())
    conn.close()

    domaines_ignores = {
        "persistent_notification", "group", "zone", "sun",
        "input_boolean", "input_number", "input_select",
        "input_text", "input_datetime", "timer", "counter",
        "script", "scene", "tag", "device_tracker",
        "automation", "button", "select", "update", "number"
    }

    nb_questions = 0
    for entity_id, e in index.items():
        if entity_id in connus or entity_id in en_attente:
            continue
        domaine = entity_id.split(".")[0]
        if domaine in domaines_ignores:
            continue
        if "prise" in entity_id:
            continue

        attrs = e.get("attributes", {})
        fname = attrs.get("friendly_name", entity_id)
        etat  = e.get("state", "")

        cat, sous, desc = _match_pattern(entity_id, fname)
        if cat:
            if cat in ("energie_batterie", "energie_production", "energie_prevision"):
                conn = sqlite3.connect(DB_PATH)
                piece = ha_get_area(entity_id)
                conn.execute(
                    """INSERT OR REPLACE INTO cartographie
                       (entity_id, categorie, sous_categorie, piece, friendly_name, appris_le)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (entity_id, cat, sous, piece, fname, datetime.now().isoformat())
                )
                conn.commit()
                conn.close()
                log.info(f"✅ Auto-catégorisé : {fname} → {cat}")
                poser_question_entite(entity_id, fname, cat, desc)
                nb_questions += 1
                if nb_questions >= 3:
                    break
                continue

        if nb_questions < 3:
            cat_claude, desc_claude = _construire_question_intelligente(entity_id, fname, etat, attrs)
            poser_question_entite(entity_id, fname, cat_claude, desc_claude)
            nb_questions += 1

    if nb_questions > 0:
        log.info(f"❓ {nb_questions} question(s) posée(s)")

    _verifier_coherence_cartographie(index)


def _forcer_reclassification_anker(index):
    """Force la reclassification des entités Anker"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT entity_id, categorie, friendly_name FROM cartographie WHERE categorie='a_ignorer'"
    ).fetchall()
    conn.close()
    
    reclassifiees = 0
    
    for entity_id, categorie, fname in rows:
        if "solarbank_e1600" not in entity_id and "system_anker" not in entity_id:
            continue
        
        if entity_id not in index:
            continue
        
        attrs = index[entity_id].get("attributes", {})
        fname_ha = attrs.get("friendly_name", entity_id)
        
        cat, sous, desc = _match_pattern(entity_id, fname_ha)
        
        if not cat:
            if "solarbank_e1600" in entity_id:
                cat, sous, desc = "energie_batterie", "autre", "Anker Solarbank E1600"
            elif "system_anker" in entity_id:
                cat, sous, desc = "energie_production", "autre", "Système Anker"
            else:
                continue
        
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE cartographie SET categorie=?, sous_categorie=?, friendly_name=? WHERE entity_id=?",
            (cat, sous, fname_ha, entity_id)
        )
        conn.commit()
        conn.close()
        
        log.info(f"🔴→⚡ Force Anker : {fname_ha} ({entity_id}) → {cat}")
        reclassifiees += 1
    
    if reclassifiees > 0:
        log.info(f"🔴→⚡ {reclassifiees} entité(s) Anker reclassifiée(s)")


def decouverte_auto(etats=None):
    ha_refresh_areas()
    _maj_baseline_entities()
    log.info("🧠 Découverte automatique...")

    if etats is None:
        etats = ha_get("states")
        if not etats:
            log.error("❌ Découverte : HA inaccessible")
            return

    conn = sqlite3.connect(DB_PATH)
    connus = set(r[0] for r in conn.execute('SELECT entity_id FROM cartographie').fetchall())
    conn.close()

    domaines_ignores = {
        "persistent_notification", "group", "zone", "sun",
        "input_boolean", "input_number", "input_select",
        "input_text", "input_datetime", "timer", "counter",
        "script", "scene", "tag", "device_tracker"
    }

    nouvelles = [
        e for e in etats
        if e["entity_id"] not in connus
        and e["entity_id"].split(".")[0] not in domaines_ignores
    ]

    if not nouvelles:
        log.info("✅ Toutes les entités déjà cartographiées")
        mem_set("decouverte_date", datetime.now().isoformat())
        _maj_entites_connues()
        return

    auto_categorisees = []
    a_envoyer_claude  = []

    # Pièces connues pour extraction depuis friendly_name
    _PIECES_CONNUES = [
        "cuisine", "salon", "chambre", "buanderie", "garage", "bureau",
        "salle de bain", "sdb", "entrée", "couloir", "jardin", "terrasse",
        "grenier", "cave", "wc", "toilettes", "chambre amis", "chambre enfant",
    ]

    def _extraire_piece(fname):
        """Extrait la pièce depuis le friendly_name quand l'API HA ne répond pas."""
        fn = fname.lower()
        for p in _PIECES_CONNUES:
            if p in fn:
                return p
        return ""

    for e in nouvelles:
        eid    = e["entity_id"]
        attrs  = e.get("attributes", {})
        fname  = attrs.get("friendly_name", eid)
        piece  = ha_get_area(eid) or _extraire_piece(fname)
        domaine = eid.split(".")[0]
        nom_bas = eid.lower()

        if "prise" in nom_bas:
            if domaine == "sensor" and nom_bas.endswith("_power"):
                auto_categorisees.append((eid, "prise_connectee", "puissance", piece, fname))
            elif domaine == "switch" and not nom_bas.endswith("_child_lock"):
                auto_categorisees.append((eid, "prise_connectee", "commande", piece, fname))
            else:
                auto_categorisees.append((eid, "a_ignorer", "", piece, fname))
        else:
            a_envoyer_claude.append(e)

    if auto_categorisees:
        conn = sqlite3.connect(DB_PATH)
        for eid, cat, sous, pc, fn in auto_categorisees:
            conn.execute(
                '''INSERT OR REPLACE INTO cartographie
                   (entity_id, categorie, sous_categorie, piece, friendly_name, appris_le)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (eid, cat, sous, pc, fn, datetime.now().isoformat())
            )
        nb_prises = sum(1 for _, cat, _, _, _ in auto_categorisees if cat == "prise_connectee")
        conn.commit()
        conn.close()
        if nb_prises > 0:
            noms = [fn for _, cat, _, _, fn in auto_categorisees if cat == "prise_connectee"]
            telegram_send(
                f"🔌 {nb_prises} nouvelle(s) prise(s) détectée(s) :\n"
                + "\n".join(f"  • {n}" for n in noms) +
                "\n\n📡 Surveillance activée — cycles machines détectés automatiquement."
            )
        log.info(f"✅ Prises : {nb_prises} utiles catégorisées")

    nouvelles = a_envoyer_claude
    batch_size = 40
    total = 0

    for i in range(0, len(nouvelles), batch_size):
        batch = nouvelles[i:i + batch_size]
        liste = []
        for e in batch:
            attrs = e.get("attributes", {})
            friendly = attrs.get("friendly_name", "")
            unite = attrs.get("unit_of_measurement", "")
            device_class = attrs.get("device_class", "")
            liste.append(
                f"{e['entity_id']} | état:{e['state']} | unité:{unite} | "
                f"device_class:{device_class} | nom:{friendly}"
            )

        prompt = (
            f"Tu es l'assistant domotique de l'utilisateur.\n"
            f"Catégorise chaque entité dans UNE des catégories :\n"
            f"{', '.join(CATEGORIES_VALIDES)}\n\n"
            f"Les prises connectées avec mesure de consommation = 'prise_connectee'\n"
            f"Réponds UNIQUEMENT en JSON valide :\n"
            f'[{{"entity_id":"...", "categorie":"...", "sous_categorie":"...", "piece":""}}]\n\n'
            f"Entités :\n" + "\n".join(liste)
        )

        try:
            client = anthropic.Anthropic(api_key=CFG["anthropic_api_key"])
            r = client.messages.create(
                model="claude-haiku-4-5-20251001", max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            log_token_usage(r.usage.input_tokens, r.usage.output_tokens)
            texte = r.content[0].text.strip()
            match = re.search(r'\[.*\]', texte, re.DOTALL)
            if not match:
                continue
            resultats = json.loads(match.group())
            conn = sqlite3.connect(DB_PATH)
            for item in resultats:
                eid = item.get("entity_id", "")
                cat = item.get("categorie", "a_ignorer")
                sous = item.get("sous_categorie", "")
                e_orig = next((e for e in batch if e["entity_id"] == eid), None)
                fname = e_orig.get("attributes", {}).get("friendly_name", "") if e_orig else ""
                piece_ha = ha_get_area(eid)
                piece = piece_ha if piece_ha else item.get("piece", "")
                conn.execute(
                    '''INSERT OR REPLACE INTO cartographie
                       (entity_id, categorie, sous_categorie, piece, friendly_name, appris_le)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (eid, cat, sous, piece, fname, datetime.now().isoformat())
                )
                total += 1
            conn.commit()
            conn.close()
            log.info(f"✅ Batch {i//batch_size+1}: {len(resultats)} catégorisées")
        except Exception as ex:
            log.error(f"❌ Batch {i//batch_size+1}: {ex}")
        time.sleep(1)

    mem_set("decouverte_date", datetime.now().isoformat())
    mem_set("decouverte_count", total)
    _maj_entites_connues()


def _maj_entites_connues():
    """Met à jour le snapshot des entités connues"""
    carto = cartographie_get_toutes()
    for eid, cat in carto.items():
        entites_connues_maj(eid, cat)


def comparer_entites_au_demarrage(etats):
    """Compare les entités actuelles avec la mémoire"""
    connues = entites_connues_get_toutes()
    if not connues:
        log.info("Première comparaison — pas d'historique encore")
        return

    actuelles = set(e["entity_id"] for e in etats)
    connues_set = set(connues.keys())

    # Entités disparues
    disparues = connues_set - actuelles
    for eid in disparues:
        cat = connues.get(eid, "")
        criticite = CRITICITE_ENTITES.get(cat, {})
        alerte_h = criticite.get("alerte_h", 48)
        label = criticite.get("label", cat)
        if alerte_h <= 4:
            telegram_send(
                f"🚨 ENTITÉ DISPARUE — {label}\n{eid}\n"
                f"Non trouvée dans Home Assistant au démarrage."
            )
            log.warning(f"Entité disparue critique: {eid}")

    carto_connues = set(cartographie_get_toutes().keys())
    nouvelles = actuelles - carto_connues
    if nouvelles:
        log.info(f"🆕 {len(nouvelles)} nouvelles entités à catégoriser")

    log.info(f"Comparaison démarrage : {len(actuelles)} actuelles, {len(disparues)} disparues, {len(nouvelles)} nouvelles")


def scan_ha_complet():
    ha_refresh_areas()
    log.info("🔍 Scan HA...")

    etats = ha_get("states")
    if not etats:
        telegram_send("❌ SCAN — HA inaccessible")
        return False

    conn = sqlite3.connect(DB_PATH)
    for e in etats:
        conn.execute(
            '''INSERT OR REPLACE INTO entites (entity_id, state, attributes, updated_at)
               VALUES (?, ?, ?, ?)''',
            (e["entity_id"], e["state"],
             json.dumps(e.get("attributes", {})), datetime.now().isoformat())
        )
    conn.commit()
    conn.close()

    mem_set("ha_scan_date", datetime.now().isoformat())
    mem_set("ha_entites_count", len(etats))

    threading.Thread(target=decouverte_auto, args=(etats,), daemon=True).start()

    # Découverte des rôles (universel)
    try:
        nb_roles = role_decouvrir(etats)
        if nb_roles > 0:
            log.info(f"🎯 {nb_roles} rôle(s) auto-découvert(s) au scan")
    except Exception as ex_r:
        log.error(f"❌ role_decouvrir: {ex_r}")

    return True


def _detecter_nouvelles_entites(index):
    """Détection antivirus — repère les nouvelles entités en < 1ms, 0 token.
    Les prises et capteurs de puissance sont auto-catégorisés immédiatement.
    Les autres sont signalés pour le prochain scan d'infiltration."""
    # global _entites_deja_detectees  # via shared

    conn = sqlite3.connect(DB_PATH)
    carto_set = set(r[0] for r in conn.execute("SELECT entity_id FROM cartographie").fetchall())

    domaines_ignores = {
        "persistent_notification", "group", "zone", "sun",
        "input_boolean", "input_number", "input_select",
        "input_text", "input_datetime", "timer", "counter",
        "script", "scene", "tag", "device_tracker",
        "automation", "button", "select", "update", "number"
    }

    _PIECES_DETECT = [
        "cuisine", "salon", "chambre amis", "chambre enfant", "chambre",
        "buanderie", "garage", "bureau", "salle de bain", "sdb",
    ]

    nouvelles_prises = []
    nouvelles_autres = []

    for eid, e in index.items():
        if eid in carto_set or eid in _entites_deja_detectees:
            continue
        domaine = eid.split(".")[0]
        if domaine in domaines_ignores:
            continue

        attrs = e.get("attributes", {})
        fname = attrs.get("friendly_name", eid)
        nom_bas = eid.lower()

        # Pièce depuis friendly_name
        piece = ha_get_area(eid)
        if not piece:
            fn_low = fname.lower()
            for p in _PIECES_DETECT:
                if p in fn_low:
                    piece = p
                    break

        # Auto-catégoriser les prises — PAS de supposition sur la marque.
        # Une prise = un capteur de puissance (W) + un switch on/off sur le même device.
        # On ne devine pas : on vérifie les FAITS dans HA.
        dc = attrs.get("device_class", "")
        unit = attrs.get("unit_of_measurement", "")

        # Méthode 1 : nom explicite (l'utilisateur a nommé sa prise)
        _is_prise_par_nom = ("prise" in nom_bas or "plug" in nom_bas
                             or "outlet" in nom_bas or "socket" in nom_bas)

        # Méthode 2 : capteur de puissance (W) avec switch associé = prise avec mesure
        _is_prise_par_structure = False
        if domaine == "sensor" and (dc == "power" or unit == "W"):
            # Chercher un switch associé (même préfixe sans _power)
            base = eid.replace("sensor.", "").replace("_power", "").replace("_puissance", "")
            for candidate in index:
                if candidate.startswith("switch.") and base in candidate:
                    _is_prise_par_structure = True
                    break

        _is_prise = _is_prise_par_nom or _is_prise_par_structure
        if _is_prise:
            if domaine == "sensor" and (dc == "power" or unit == "W" or nom_bas.endswith("_power")):
                conn.execute(
                    "INSERT OR REPLACE INTO cartographie (entity_id, categorie, sous_categorie, piece, friendly_name, appris_le) VALUES (?, ?, ?, ?, ?, ?)",
                    (eid, "prise_connectee", "puissance", piece, fname, datetime.now().isoformat())
                )
                nouvelles_prises.append(fname)
            elif domaine == "switch" and not nom_bas.endswith("_child_lock"):
                conn.execute(
                    "INSERT OR REPLACE INTO cartographie (entity_id, categorie, sous_categorie, piece, friendly_name, appris_le) VALUES (?, ?, ?, ?, ?, ?)",
                    (eid, "prise_connectee", "commande", piece, fname, datetime.now().isoformat())
                )
                nouvelles_prises.append(fname)
            # Les autres (energy, voltage, current, number, select) → ignorer
            _entites_deja_detectees.add(eid)
            continue

        # Auto-catégoriser les capteurs de puissance (device_class=power)
        dc = attrs.get("device_class", "")
        unit = attrs.get("unit_of_measurement", "")
        if domaine == "sensor" and (dc == "power" or unit == "W"):
            cat_auto = "energie_conso"
            if any(k in nom_bas for k in ["solar", "solaire", "ecu", "inverter", "onduleur"]):
                cat_auto = "energie_solaire"
            elif any(k in nom_bas for k in ["battery", "batterie", "solarbank", "anker"]):
                cat_auto = "energie_batterie"
            conn.execute(
                "INSERT OR REPLACE INTO cartographie (entity_id, categorie, sous_categorie, piece, friendly_name, appris_le) VALUES (?, ?, ?, ?, ?, ?)",
                (eid, cat_auto, "puissance", piece, fname, datetime.now().isoformat())
            )
            _entites_deja_detectees.add(eid)
            nouvelles_autres.append(f"{fname} → {cat_auto}")
            continue

        # Nouvelle entité non auto-catégorisée → détecter le protocole + notifier
        _entites_deja_detectees.add(eid)
        dc = attrs.get("device_class", "")
        unit = attrs.get("unit_of_measurement", "")
        state = e.get("state", "?")

        # Détection protocole par les indices dans l'entity_id et les attributs
        _proto = "inconnu"
        _eid_low = eid.lower()
        _fname_low = fname.lower()
        if any(k in _eid_low for k in ("zigbee", "z2m", "zha", "zbee")):
            _proto = "Zigbee"
        elif any(k in _eid_low for k in ("matter", "mtr")):
            _proto = "Matter"
        elif any(k in _eid_low for k in ("zwave", "zw_")):
            _proto = "Z-Wave"
        elif any(k in _eid_low for k in ("esphome", "esp32", "esp8266")):
            _proto = "ESPHome"
        elif any(k in _eid_low for k in ("tapo", "shelly", "tuya", "sonoff", "meross", "wemo", "kasa")):
            _proto = "WiFi"
        elif domaine in ("light", "climate", "cover", "fan", "lock", "vacuum"):
            _proto = "HA"
        elif any(k in _eid_low for k in ("hue", "ikea", "tradfri", "aqara", "xiaomi")):
            _proto = "Zigbee"

        # Construire la description factuelle
        desc_facts = f"{fname}"
        infos = []
        if _proto != "inconnu":
            infos.append(_proto)
        if dc:
            infos.append(dc)
        if unit and state not in ("unavailable", "unknown"):
            infos.append(f"{state}{unit}")
        elif state not in ("unavailable", "unknown", ""):
            infos.append(state)
        if piece:
            infos.append(f"📍{piece}")
        if infos:
            desc_facts += f" ({', '.join(infos)})"

        nouvelles_autres.append(desc_facts)

    if nouvelles_prises:
        conn.commit()
        nb_total = conn.execute("SELECT COUNT(*) FROM cartographie").fetchone()[0]
        nb_surveilles = conn.execute("SELECT COUNT(*) FROM appareils WHERE surveiller=1").fetchone()[0]
        telegram_send(
            f"🔌 DÉTECTION — {len(nouvelles_prises)} nouvelle(s) prise(s)\n━━━━━━━━━━━━━━━━━━\n"
            + "\n".join(f"  • {n}" for n in nouvelles_prises)
            + f"\n\n📡 Surveillance activée — mode sniper 20s"
            + f"\n📊 {nb_total} entités | {nb_surveilles} appareils surveillés"
        )
        log.info(f"🔌 Nouvelles prises: {nouvelles_prises}")

        # Demander à l'utilisateur d'identifier les nouveaux appareils
        # (seulement les prises avec capteur de puissance pas encore dans table appareils)
        try:
            new_power = conn.execute(
                "SELECT entity_id, friendly_name FROM cartographie "
                "WHERE categorie='prise_connectee' AND sous_categorie='puissance' "
                "AND entity_id NOT IN (SELECT entity_id FROM appareils)"
            ).fetchall()
            if new_power:
                queue = [{"entity_id": eid, "fname": fn} for eid, fn in new_power]
                existing_queue = mem_get("appareils_queue")
                if existing_queue:
                    try:
                        existing = json.loads(existing_queue)
                        existing_eids = {q["entity_id"] for q in existing}
                        queue = [q for q in queue if q["entity_id"] not in existing_eids] + existing
                    except Exception:
                        pass
                mem_set("appareils_queue", json.dumps(queue))
                _poser_question_appareil_suivant()
        except Exception:
            pass

    if nouvelles_autres:
        conn.commit()
        # Compteur global pour rassurer l'utilisateur
        nb_total = conn.execute("SELECT COUNT(*) FROM cartographie").fetchone()[0]
        nb_surveilles = conn.execute("SELECT COUNT(*) FROM appareils WHERE surveiller=1").fetchone()[0]

        msg_new = f"🔍 DÉTECTION — {len(nouvelles_autres)} nouvel(le)(s) entité(s)\n━━━━━━━━━━━━━━━━━━\n"
        for desc in nouvelles_autres[:8]:
            msg_new += f"  • {desc}\n"
        if len(nouvelles_autres) > 8:
            msg_new += f"  ... +{len(nouvelles_autres) - 8} autres\n"
        msg_new += f"\n📊 {nb_total} entités cartographiées | {nb_surveilles} appareils sous surveillance"
        msg_new += f"\n🔄 Catégorisation automatique dans < 1h"
        telegram_send(msg_new)
        log.info(f"🔍 {len(nouvelles_autres)} nouvelles entités détectées")

    conn.close()


def _remonter_erreurs():
    """SKILL AUTO-GUÉRISON — Pipeline fermé, 0 intervention utilisateur.

    Cycle complet :
    1. CAPTURE : _ErrorCaptureHandler intercepte log.error()
    2. TRIAGE : grouper par signature, anti-spam 6h
    3. DIAGNOSTIC : si erreur ≥ 3x/1h → auto-correction Sonnet
    4. CORRECTION : patch appliqué + restart SANS demander
    5. VÉRIFICATION : si erreur revient après fix → rollback
    6. NOTIFICATION : 1 seul message résumé — jamais de spam

    L'utilisateur ne voit RIEN. Jamais. Les erreurs sont le problème du script, pas de l'utilisateur.
    """
    # # global _erreurs_buffer, _erreurs_vues    # via shared# via shared

    if not _erreurs_buffer:
        return

    # Copier et vider le buffer
    erreurs = _erreurs_buffer.copy()
    _erreurs_buffer.clear()

    # Grouper par signature
    groupes = {}
    for ts, msg, sig in erreurs:
        if sig not in groupes:
            groupes[sig] = {"count": 0, "first_ts": ts, "last_ts": ts, "msg": msg}
        groupes[sig]["count"] += 1
        groupes[sig]["last_ts"] = ts

    now = datetime.now()

    h1 = (now - timedelta(hours=1)).isoformat()
    h24 = (now - timedelta(hours=24)).isoformat()

    for sig, info in groupes.items():
        # ═══ TOUJOURS ENREGISTRER — pas d'anti-spam sur le comptage ═══
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO decisions_log (action, contexte, resultat, succes, created_at) VALUES (?, ?, ?, 0, ?)",
                ("ERREUR_AUTO", json.dumps({"sig": sig[:80], "n": info["count"]}, ensure_ascii=False),
                 info["msg"][:200], now.isoformat())
            )
            conn.commit()

            # Compter le TOTAL sur la dernière heure (cumul de tous les ticks)
            nb_1h = conn.execute(
                "SELECT COUNT(*) FROM decisions_log WHERE action='ERREUR_AUTO' AND contexte LIKE ? AND created_at > ?",
                (f"%{sig[:40]}%", h1)
            ).fetchone()[0]

            deja_fix = conn.execute(
                "SELECT COUNT(*) FROM decisions_log WHERE action='AUTO_FIX_OK' AND contexte LIKE ? AND created_at > ?",
                (f"%{sig[:40]}%", h24)
            ).fetchone()[0]

            deja_tente = conn.execute(
                "SELECT COUNT(*) FROM decisions_log WHERE action='AUTO_FIX_FAIL' AND contexte LIKE ? AND created_at > ?",
                (f"%{sig[:40]}%", h24)
            ).fetchone()[0]

            conn.close()
        except Exception:
            nb_1h = info["count"]
            deja_fix = 0
            deja_tente = 0

        # ═══ DÉCISION ═══
        if nb_1h < 3:
            continue  # Pas encore récurrent → silence

        if deja_fix > 0:
            continue  # Déjà corrigé → pas de boucle

        if deja_tente > 0:
            continue  # Déjà tenté et échoué → attendre 24h

        # Anti-spam sur l'ACTION seulement (pas le comptage)
        last_action = _erreurs_vues.get(sig)
        if last_action:
            try:
                if (now - datetime.fromisoformat(last_action)).total_seconds() < 3600:
                    continue
            except Exception:
                pass
        _erreurs_vues[sig] = now.isoformat()

        # ═══ AUTO-CORRECTION ═══
        log.info(f"🔧 Auto-guérison: {nb_1h} occurrences/1h → correction: {sig[:60]}")

        if not verifier_budget():
            continue

        try:
            resultat = _auto_guerison(sig, info["msg"])
            action_db = "AUTO_FIX_OK" if resultat == "OK" else "AUTO_FIX_FAIL"
            try:
                conn2 = sqlite3.connect(DB_PATH)
                conn2.execute(
                    "INSERT INTO decisions_log (action, contexte, resultat, succes, created_at) VALUES (?, ?, ?, ?, ?)",
                    (action_db, json.dumps({"sig": sig[:80]}, ensure_ascii=False),
                     resultat or "echec", 1 if resultat == "OK" else 0, now.isoformat())
                )
                conn2.commit()
                conn2.close()
            except Exception:
                pass
            if resultat == "FAIL":
                # Retry avec plus de contexte (logs élargis)
                _auto_guerison(sig, info["msg"], nb_occurrences, retry=True)
        except Exception:
            pass

    # Nettoyer les vieilles signatures
    cutoff = (now - timedelta(hours=24)).isoformat()
    _erreurs_vues = {k: v for k, v in _erreurs_vues.items() if v > cutoff}


def _auto_guerison(signature, message_erreur, nb_occurrences=2, retry=False):
    """Correction autonome — Sonnet lit le script, propose un patch, l'applique, redémarre.
    AUCUNE intervention utilisateur. AUCUN bouton. AUCUNE confirmation. SILENCE TOTAL."""

    msg_clean = message_erreur
    if "] " in msg_clean:
        msg_clean = msg_clean.split("] ", 1)[-1]

    # 1. Lire le script
    try:
        cfg_secret = CFG.get("deploy_secret", "")
        req_r = urllib.request.Request("http://localhost:8501/read")
        req_r.add_header("Authorization", f"Bearer {cfg_secret}")
        resp_r = urllib.request.urlopen(req_r, timeout=15)
        script_data = json.loads(resp_r.read().decode())
        script_code = script_data["content"]
        script_lines = script_data["lines"]
    except Exception as e:
        log.error(f"auto-guérison: lecture script: {e}")
        return "FAIL"

    # 2. Lire les derniers logs d'erreur (plus de contexte en retry)
    nb_logs = 100 if retry else 30
    try:
        req_l = urllib.request.Request(f"http://localhost:8501/logs?n={nb_logs}")
        req_l.add_header("Authorization", f"Bearer {cfg_secret}")
        resp_l = urllib.request.urlopen(req_l, timeout=10)
        all_logs = json.loads(resp_l.read().decode()).get("lines", [])
        # Filtrer les erreurs + contexte
        logs_recents = "\n".join([l for l in all_logs if "ERROR" in l or "error" in l.lower()][-20:])
        if not logs_recents:
            logs_recents = "\n".join(all_logs[-15:])
    except Exception:
        logs_recents = message_erreur

    # 3. Extraire le contexte pertinent (pas les 12K lignes)
    # Chercher les lignes qui contiennent le pattern d'erreur
    erreur_mots = [m for m in msg_clean.split() if len(m) > 4][:5]
    lignes_script = script_code.split("\n")
    lignes_pertinentes = set()
    for i, ligne in enumerate(lignes_script):
        if any(mot in ligne for mot in erreur_mots):
            # Prendre 30 lignes avant et après
            for j in range(max(0, i-30), min(len(lignes_script), i+30)):
                lignes_pertinentes.add(j)

    # Si rien trouvé, envoyer les 500 premières + 500 dernières lignes
    if not lignes_pertinentes:
        contexte = "\n".join(f"L{i+1}: {l}" for i, l in enumerate(lignes_script[:500]))
        contexte += "\n...\n"
        contexte += "\n".join(f"L{i+1}: {l}" for i, l in enumerate(lignes_script[-500:], len(lignes_script)-500))
    else:
        indices = sorted(lignes_pertinentes)
        contexte = "\n".join(f"L{i+1}: {lignes_script[i]}" for i in indices)

    # 4. Demander à Sonnet un patch — en SILENCE
    try:
        client = anthropic.Anthropic(api_key=CFG["anthropic_api_key"])
        r = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=(
                "Tu es le système d'auto-guérison d'un script Python (assistant.py, "
                f"{script_lines} lignes).\n"
                "Une erreur BLOQUE le script. Tu DOIS la corriger. L'utilisateur ne doit rien faire.\n\n"
                "MÉTHODE :\n"
                "1. Lis le message d'erreur — identifie la variable/fonction/ligne qui plante\n"
                "2. Cherche cette ligne dans le script\n"
                "3. Propose un fix MINIMAL (try/except, valeur par défaut, guard clause)\n\n"
                "FORMAT — JSON brut uniquement :\n"
                "{\"old_str\": \"code_exact_à_remplacer\", \"new_str\": \"nouveau_code\", \"explication\": \"ce_que_tu_corriges\"}\n\n"
                "RÈGLES :\n"
                "- old_str = copie EXACTE (espaces, indentation, guillemets identiques au script)\n"
                "- old_str doit apparaître 1 SEULE FOIS\n"
                "- Change le MINIMUM — un try/except ou un 'if x:' suffit souvent\n"
                "- PAS de markdown, PAS de ```, PAS de texte avant/après\n"
                + ("\nATTENTION RETRY : le premier patch a échoué car old_str ne correspondait pas. "
                   "Sois PLUS PRÉCIS — copie le code EXACTEMENT tel qu'il est dans le script, "
                   "y compris chaque espace d'indentation.\n" if retry else "")
            ),
            messages=[{"role": "user", "content":
                f"ERREUR RÉCURRENTE ({nb_occurrences}x en 60s) :\n{msg_clean[:300]}\n\n"
                f"LOGS RÉCENTS :\n{logs_recents[:1000]}\n\n"
                f"CONTEXTE DU SCRIPT (lignes pertinentes) :\n{contexte[:15000]}"
            }]
        )
        reponse = r.content[0].text.strip()
        log_token_usage(r.usage.input_tokens, r.usage.output_tokens)
    except Exception as e:
        log.error(f"auto-guérison: Sonnet: {e}")
        return "FAIL"

    # 4. Parser le patch — robuste (Sonnet peut ajouter du texte autour)
    try:
        texte = reponse.replace("```json", "").replace("```", "").strip()
        # Trouver le JSON dans la réponse (entre { et })
        idx_start = texte.find("{")
        idx_end = texte.rfind("}") + 1
        if idx_start >= 0 and idx_end > idx_start:
            texte = texte[idx_start:idx_end]
        patch = json.loads(texte)
        old_str = patch.get("old_str", "")
        new_str = patch.get("new_str", "")
        explication = patch.get("explication", "")
    except Exception as ex_json:
        log.error(f"auto-guérison: JSON invalide ({ex_json}) — réponse: {reponse[:200]}")
        return "FAIL"

    if not old_str:
        log.info(f"auto-guérison: Sonnet ne peut pas corriger — {explication[:100]}")
        return "SKIP"

    # Vérifier unicité
    if script_code.count(old_str) != 1:
        log.error(f"auto-guérison: old_str trouvé {script_code.count(old_str)} fois")
        return "FAIL"

    # 5. Appliquer le patch — SANS DEMANDER
    try:
        payload = json.dumps({"mode": "replace", "old_str": old_str, "new_str": new_str}).encode()
        sig = hmac.new(cfg_secret.encode(), payload, hashlib.sha256).hexdigest()
        req_p = urllib.request.Request("http://localhost:8501/patch", data=payload, method="POST")
        req_p.add_header("Content-Type", "application/json")
        req_p.add_header("Authorization", f"HMAC {sig}")
        resp_p = urllib.request.urlopen(req_p, timeout=15)
        result = json.loads(resp_p.read().decode())
        if result.get("status") != "ok":
            log.error(f"auto-guérison: patch échoué: {result}")
            return "FAIL"
    except Exception as e:
        log.error(f"auto-guérison: patch: {e}")
        return "FAIL"

    # 6. Log silencieux — l'utilisateur ne voit RIEN
    log.info(f"🔧 Auto-guérison : {explication[:150]} — restart")

    # 7. Restart
    try:
        payload_r = json.dumps({"action": "restart"}).encode()
        sig_r = hmac.new(cfg_secret.encode(), payload_r, hashlib.sha256).hexdigest()
        req_restart = urllib.request.Request("http://localhost:8501/restart", data=payload_r, method="POST")
        req_restart.add_header("Content-Type", "application/json")
        req_restart.add_header("Authorization", f"HMAC {sig_r}")
        urllib.request.urlopen(req_restart, timeout=15)
    except Exception:
        pass  # Le restart tue le process, l'exception est normale

    return "OK"


def _verifier_watches(index):
    """Vérifie toutes les alertes dynamiques (watches) créées par l'utilisateur."""
    try:
        conn = sqlite3.connect(DB_PATH)
        watches = conn.execute("SELECT id, entity_pattern, condition, state_value, message, cooldown_min, last_triggered FROM watches WHERE active=1").fetchall()
        conn.close()
    except Exception:
        return

    if not watches:
        return

    import fnmatch
    now = datetime.now()

    for watch_id, pattern, condition, state_value, message, cooldown_min, last_triggered in watches:
        # Cooldown check
        if last_triggered:
            try:
                lt = datetime.fromisoformat(last_triggered)
                if (now - lt).total_seconds() < cooldown_min * 60:
                    continue
            except Exception:
                pass

        # Find matching entities
        matching_eids = [eid for eid in index if fnmatch.fnmatch(eid, pattern)]
        if not matching_eids and "*" not in pattern:
            # Exact match attempt
            if pattern in index:
                matching_eids = [pattern]

        for eid in matching_eids:
            e = index[eid]
            state = e["state"]
            fname = e.get("attributes", {}).get("friendly_name", eid)

            triggered = False
            if condition in ("unavailable", "offline"):
                triggered = state in ("unavailable", "unknown", "offline")
            elif condition == "equals":
                triggered = str(state).lower() == str(state_value).lower()
            elif condition == "not_equals":
                triggered = str(state).lower() != str(state_value).lower()
            elif condition == "above":
                try:
                    triggered = float(state) > float(state_value)
                except (ValueError, TypeError):
                    pass
            elif condition == "below":
                try:
                    triggered = float(state) < float(state_value)
                except (ValueError, TypeError):
                    pass

            if triggered:
                # Format message
                alert_msg = message.replace("{entity_id}", eid).replace("{state}", str(state)).replace("{friendly_name}", fname)
                _alerter_si_nouveau(
                    f"watch_{watch_id}_{eid}",
                    alert_msg,
                    delai_h=cooldown_min / 60
                )
                # Update last_triggered
                try:
                    conn2 = sqlite3.connect(DB_PATH)
                    conn2.execute("UPDATE watches SET last_triggered=? WHERE id=?", (now.isoformat(), watch_id))
                    conn2.commit()
                    conn2.close()
                except Exception:
                    pass
                break  # One alert per watch per cycle


def surveillance_monitoring():
    """Thread principal de monitoring — mode sniper.
    Tick rapide (60s) : coupure EDF, PAC, erreurs — réaction immédiate.
    Tick complet (5 min) : NAS, Zigbee, météo, intelligence — analyse profonde."""
    _tick = 0
    while True:
        time.sleep(60)  # Tick rapide = 60 secondes
        _tick += 1
        _watchdog["monitoring_last_run"] = datetime.now()

        try:
            etats = ha_get("states")
            if not etats:
                continue

            index = {e["entity_id"]: e for e in etats}
            now = datetime.now()

            # ═══ TICK RAPIDE (60s) — Alertes critiques ═══
            _surveiller_coupure_edf(index)
            _surveiller_pac_correlee(index, etats)
            _verifier_watches(index)

            # Conso fantôme nocturne
            try:
                _alerte_conso_fantome_nocturne(index, now)
            except Exception:
                pass

            # Congélateur coupure
            try:
                _alerte_congelateur_coupure(index, now)
            except Exception:
                pass

            # Mode vacances auto
            try:
                _detecter_mode_vacances(now)
            except Exception:
                pass

            # Backup DB (3h chaque nuit)
            try:
                _backup_auto_db(now)
            except Exception:
                pass

            # Google Home / Alexa vocal scripts
            try:
                _check_vocal_scripts(index, now)
            except Exception as _e_vocal:
                log.error(f"Vocal scripts error: {_e_vocal}")

            # Fuite d'eau
            try:
                _detecter_fuite_eau(index, now)
            except Exception:
                pass

            # Coupure internet
            try:
                _detecter_coupure_internet(now)
            except Exception:
                pass

            # Zigbee device mort (1x/jour 9h)
            try:
                _alerte_zigbee_device_mort(index, now)
            except Exception:
                pass

            # Tempo/EJP (1x/jour 19h)
            try:
                _notif_tempo_ejp(now)
            except Exception:
                pass


            # Rollback auto (1x/h)
            try:
                _rollback_si_erreurs_repetees(now)
            except Exception:
                pass

            # Deploy server monitoring (2x/h)
            try:
                _monitoring_deploy_server(now)
            except Exception:
                pass

            # Auto-update GitHub (24h)
            try:
                _auto_update_github()
            except Exception:
                pass

            # Remontée erreurs — chaque minute
            try:
                _remonter_erreurs()
            except Exception as ex_err:
                log.debug(f"remontée erreurs: {ex_err}")

            # ═══ TICK COMPLET (5 min) — Surveillance profonde ═══
            if _tick % 5 != 0:
                continue

            _surveiller_nas(index, now)
            _surveiller_zigbee(index, now)
            _surveiller_imprimante(index, now)
            _surveiller_batteries_critiques(etats, now)
            _surveiller_bridge_z2m(index)
            _surveiller_meteo_france(index)

            # ═══ ÉCONOMIES COUPE-VEILLE ═══
            # Les prises "coupe_veille" coupent le standby des appareils
            # (TV 5-15W, PC 3-8W, etc.). Chaque heure OFF = standby évité.
            # On mesure toutes les 5 min, on enregistre toutes les heures.
            try:
                _compteur_veille = getattr(surveillance_monitoring, "_cv", {})
                conn_cv = sqlite3.connect(DB_PATH)
                appareils_cv = conn_cv.execute(
                    "SELECT entity_id, nom_personnalise FROM appareils WHERE type_appareil='coupe_veille' AND surveiller=1"
                ).fetchall()
                conn_cv.close()

                for eid_cv, nom_cv in appareils_cv:
                    # Trouver le switch associé
                    switch_eid = eid_cv.replace("sensor.", "switch.").replace("_power", "")
                    e_switch = index.get(switch_eid)
                    e_sensor = index.get(eid_cv)

                    if not e_switch:
                        continue

                    is_off = e_switch.get("state") == "off"

                    if is_off:
                        # Switch coupé → standby évité
                        # Estimer le standby par la dernière mesure connue quand le switch était ON
                        # ou utiliser une valeur baseline si disponible
                        standby_w = _compteur_veille.get(f"{eid_cv}_last_on_w", 5)  # défaut 5W
                        _compteur_veille[f"{eid_cv}_off_min"] = _compteur_veille.get(f"{eid_cv}_off_min", 0) + 5
                        # Toutes les 60 min, enregistrer l'économie
                        if _compteur_veille.get(f"{eid_cv}_off_min", 0) >= 60:
                            kwh_saved = standby_w * 1 / 1000  # 1 heure
                            eur_saved = kwh_saved * tarif_prix_kwh_actuel()
                            enregistrer_economie("coupe_veille", f"{nom_cv} standby évité ({standby_w}W)", eur_saved, kwh_saved)
                            _compteur_veille[f"{eid_cv}_off_min"] = 0
                    else:
                        # Switch ON → mesurer la conso pour connaître le standby
                        _compteur_veille[f"{eid_cv}_off_min"] = 0
                        if e_sensor:
                            try:
                                w = float(e_sensor.get("state", 0))
                                if 0 < w < 50:  # Standby = <50W
                                    _compteur_veille[f"{eid_cv}_last_on_w"] = w
                            except (ValueError, TypeError):
                                pass

                surveillance_monitoring._cv = _compteur_veille
            except Exception:
                pass

            # ═══ MOTEUR D'ÉCONOMIES PROACTIF — Le cœur du business model ═══
            # Toutes les 5 min : chercher des euros à gagner pour l'utilisateur
            try:
                _moteur_economies_proactif(etats, index, now)
            except Exception as _ex_eco:
                log.error(f"moteur_economies: {_ex_eco}")

            # Détection nouvelles entités (0 token)
            try:
                _detecter_nouvelles_entites(index)
            except Exception as ex_det:
                log.error(f"❌ détection nouvelles entités: {ex_det}")

            # ═══ PURGE EXPERTISE ONE-SHOT ═══
            try:
                _nb_exp = conn_purge = None
                conn_purge = sqlite3.connect(DB_PATH)
                _nb_exp = conn_purge.execute("SELECT COUNT(*) FROM expertise").fetchone()[0]
                if _nb_exp > 50:
                    _fond = [r[0] for r in conn_purge.execute("SELECT id FROM expertise WHERE source LIKE 'lecon_fondatrice%'").fetchall()]
                    _top = [r[0] for r in conn_purge.execute("SELECT id FROM expertise WHERE source NOT LIKE 'lecon_fondatrice%' ORDER BY confiance DESC LIMIT 30").fetchall()]
                    _garder = set(_fond + _top)
                    if _garder:
                        _ids = ",".join(str(i) for i in _garder)
                        conn_purge.execute(f"DELETE FROM expertise WHERE id NOT IN ({_ids})")
                    _dups = conn_purge.execute("SELECT insight, COUNT(*) FROM expertise GROUP BY insight HAVING COUNT(*)>1").fetchall()
                    for _ins, _c in _dups:
                        _dup_ids = [r[0] for r in conn_purge.execute("SELECT id FROM expertise WHERE insight=? ORDER BY confiance DESC", (_ins,)).fetchall()]
                        for _did in _dup_ids[1:]:
                            conn_purge.execute("DELETE FROM expertise WHERE id=?", (_did,))
                    conn_purge.commit()
                    _nb_apres = conn_purge.execute("SELECT COUNT(*) FROM expertise").fetchone()[0]
                    log.info(f"🧹 Expertise purgée : {_nb_exp} → {_nb_apres}")
                    telegram_send(f"🧹 Expertise nettoyée : {_nb_exp} → {_nb_apres} règles")
                conn_purge.close()
            except Exception as _ex_p:
                log.error(f"Purge: {_ex_p}")

            # ═══ Vérifier si le MD a été modifié → envoi mail ═══
            try:
                verifier_md_change()
            except Exception:
                pass

            # ═══ ENVOI MD ONE-SHOT ═══
            try:
                if mem_get("envoyer_md_maintenant") == "oui":
                    mem_set("envoyer_md_maintenant", "")
                    envoyer_md_par_mail()
                    telegram_send("📧 Cahier des Charges envoyé par mail.", force=True)
            except Exception:
                pass

            # ═══════════════════════════════════════
            # MOTEUR D'INTELLIGENCE AUTONOME
            # Cycle : Observer → Mémoriser → Apprendre → Décider → Agir
            # ═══════════════════════════════════════
            try:
                _cycle_intelligence(etats, index, now)
            except Exception as ex_ia:
                log.error(f"❌ cycle_intelligence: {ex_ia}")

        except Exception as ex:
            log.error(f"❌ surveillance_monitoring: {ex}")
            apprentissage_log_echec("monitoring", str(ex))


def _surveiller_nas(index, now):
    """Surveille les NAS — uniquement les capteurs sensor.* pertinents"""
    entites_nas = cartographie_get_par_categorie("nas")

    # Domaines ignorés : button, automation, switch, update = pas de la surveillance
    DOMAINES_NAS_IGNORES = {"button", "automation", "switch", "update", "binary_sensor"}

    for entity_id, sous_cat, piece in entites_nas:
        if entity_id not in index:
            continue

        domaine = entity_id.split(".")[0]
        if domaine in DOMAINES_NAS_IGNORES:
            continue

        e = index[entity_id]
        etat = e["state"]
        eid_low = entity_id.lower()
        fname = e.get("attributes", {}).get("friendly_name", entity_id)
        unite = e.get("attributes", {}).get("unit_of_measurement", "")

        # NAS sensor hors ligne — uniquement les capteurs critiques (état volume, état drive)
        # Ignorer : température unknown (capteur intermittent), mémoire, CPU
        if domaine == "sensor" and etat in ("unavailable", "unknown"):
            # Ne PAS alerter pour température (souvent unknown = pas grave)
            # Ne PAS alerter pour CPU/mémoire/débit (informatif seulement)
            if any(k in eid_low for k in ["temperature", "cpu", "processeur", "memoire", "memory", "debit"]):
                continue
            # Alerter seulement pour état volume ou état drive = critique
            if any(k in eid_low for k in ["_etat", "_status", "drive"]):
                _alerter_si_nouveau(
                    f"nas_offline_{entity_id}",
                    f"🚨 NAS capteur critique hors ligne\n{fname}",
                    delai_h=12
                )
            continue

        # Statut volume : "normal" = OK, "attention" = espace plein, "critical" = RAID dégradé
        if any(k in eid_low for k in ["_etat", "_status"]) and "volume" in eid_low:
            if etat.lower() not in ["normal", "on", "ok", "healthy", ""]:
                try:
                    float(etat)  # Si c'est un nombre, c'est pas un statut
                except ValueError:
                    # "attention" = espace disque plein (pas un disque cassé)
                    if etat.lower() == "attention":
                        _alerter_si_nouveau(
                            f"nas_volume_{entity_id}",
                            f"⚠️ NAS — Espace disque insuffisant\n{fname}\nSynology passe en 'attention' quand >90% plein",
                            delai_h=24
                        )
                    else:
                        # "critical", "crashed", "degraded" = vrai problème RAID/disque
                        _alerter_si_nouveau(
                            f"nas_volume_{entity_id}",
                            f"🚨 NAS — Volume dégradé\n{fname} = {etat}",
                            delai_h=2
                        )

        # Espace disque : UNIQUEMENT si unité = % et > 90%
        if "volume_used" in eid_low or ("used" in eid_low and "volume" in eid_low):
            if unite == "%":
                try:
                    val = float(etat)
                    if val > 95:
                        _alerter_si_nouveau(
                            f"nas_espace_{entity_id}",
                            f"⚠️ NAS — Espace disque {val:.0f}%\n{fname}",
                            delai_h=24
                        )
                except Exception:
                    pass

        # Température disque : UNIQUEMENT si "temperature" dans entity_id ET unité °C
        if "temperature" in eid_low and unite in ("°C", "C"):
            try:
                temp = float(etat)
                if temp > 55:
                    _alerter_si_nouveau(
                        f"nas_temp_{entity_id}",
                        f"🌡️ NAS — Température disque élevée\n{fname} = {temp}°C",
                        delai_h=2
                    )
            except Exception:
                pass


def _surveiller_zigbee(index, now):
    """Surveille TOUS les devices Zigbee physiques (via linkquality) — hors ligne + LQI faible"""
    # Sous-entités logiques — unavailable fréquent = NORMAL
    EXCLUSIONS_ZIGBEE = {
        "silent_mode", "powerful_mode", "child_lock",
        "energy_consumption", "frequency", "voltage",
        "current", "power_factor", "energy", "identify",
        "countdown", "power_outage", "indicator_mode",
        "switch_type", "child_lock",
    }

    # ══ PHASE 1 : Collecter TOUS les devices Zigbee via linkquality ══
    # Un device Zigbee = au moins une entité avec attribut linkquality
    zigbee_devices = {}  # entity_id principal → {lqi, piece, fname, state}
    for eid, e in index.items():
        lqi = e.get("attributes", {}).get("linkquality")
        if lqi is None:
            continue
        # Exclure sous-entités logiques
        if any(excl in eid.lower() for excl in EXCLUSIONS_ZIGBEE):
            continue
        attrs = e.get("attributes", {})
        fname = attrs.get("friendly_name", eid)
        carto = cartographie_get(eid)
        piece = carto[2] if carto else ""
        try:
            lqi_val = int(lqi)
        except Exception:
            lqi_val = -1
        zigbee_devices[eid] = {
            "lqi": lqi_val, "piece": piece, "fname": fname,
            "state": e["state"], "entity": e
        }

    # ══ PHASE 2 : Surveillance hors ligne ══
    for eid, info in zigbee_devices.items():
        etat = info["state"]
        piece = info["piece"]

        if etat not in ["unavailable", "unknown"]:
            absence = zigbee_absence_get(eid)
            if absence:
                signaler = zigbee_absence_retour(eid)
                if signaler:
                    piece_str = f" [{piece}]" if piece else ""
                    telegram_send(f"✅ Device Zigbee revenu en ligne\n{eid}{piece_str}")
            continue

        absence = zigbee_absence_get(eid)
        if absence:
            depuis_str, statut = absence
            depuis = datetime.fromisoformat(depuis_str)
            if statut == "anormal" and (now - depuis).total_seconds() > 7200:
                _alerter_si_nouveau(
                    f"zigbee_anormal_{eid}",
                    f"🚨 Zigbee toujours hors ligne après 2h\n{eid}",
                    delai_h=4
                )
        else:
            zigbee_absence_creer(eid)
            piece_str = f" [{piece}]" if piece else ""
            telegram_send_buttons(
                f"⚠️ Device Zigbee hors ligne\n{eid}{piece_str}",
                [
                    {"text": "✅ Normal", "callback_data": f"zigbee_normal:{eid}"},
                    {"text": "❌ Anormal", "callback_data": f"zigbee_anormal:{eid}"},
                ]
            )

    # ══ PHASE 3 : Surveillance LQI faible ══
    # LQI > 0 mais device en ligne = signal faible (pas critique)
    # Critique = hors ligne (géré en Phase 2)
    LQI_FAIBLE = 50
    for eid, info in zigbee_devices.items():
        lqi = info["lqi"]
        if lqi < 0 or info["state"] in ("unavailable", "unknown"):
            continue
        fname = info["fname"]
        piece = info["piece"]
        piece_str = f" [{piece}]" if piece else ""

        if lqi <= LQI_FAIBLE:
            _alerter_si_nouveau(
                f"lqi_faible_{eid}",
                f"⚠️ LQI faible — {fname}{piece_str}\nLQI={lqi} — envisager un routeur ou rapprocher le device.",
                delai_h=48
            )


def _surveiller_bridge_z2m(index):
    """Bridge Z2M hors ligne → alerte urgente"""
    entites_bridge = cartographie_get_par_categorie("reseau_zigbee")
    for entity_id, sous_cat, piece in entites_bridge:
        domaine = entity_id.split(".")[0]
        if domaine == "button":
            continue
        if domaine not in {"sensor", "binary_sensor"}:
            continue
        if "bridge" in entity_id.lower() and ("state" in entity_id.lower() or "connection" in entity_id.lower()):
            if entity_id in index:
                if index[entity_id]["state"] in ["unavailable", "unknown", "offline"]:
                    _alerter_si_nouveau(
                        "bridge_z2m_offline",
                        f"🚨 BRIDGE Z2M HORS LIGNE\n{entity_id}",
                        delai_h=1
                    )


def _surveiller_imprimante(index, now):
    """Imprimante Brother — uniquement cartouches encre (sensor.* avec unité %)"""
    entites_imprimante = cartographie_get_par_categorie("impression")

    # Domaines ignorés : button, automation, switch, update = commandes, pas surveillance
    DOMAINES_IGNORES_IMP = {"button", "automation", "switch", "update"}

    for entity_id, sous_cat, piece in entites_imprimante:
        if entity_id not in index:
            continue

        domaine = entity_id.split(".")[0]
        if domaine in DOMAINES_IGNORES_IMP:
            continue

        e = index[entity_id]
        etat = e["state"]
        eid_low = entity_id.lower()
        fname = e.get("attributes", {}).get("friendly_name", entity_id)
        unite = e.get("attributes", {}).get("unit_of_measurement", "")

        # ═══ Brother — Cartouches encre ═══
        if domaine == "sensor" and unite == "%":
            if any(k in eid_low for k in ["ink", "toner", "cartouche", "drum", "black", "cyan", "magenta", "yellow"]):
                try:
                    val = float(etat)
                    if val < 15:
                        _alerter_si_nouveau(
                            f"imprimante_{entity_id}",
                            f"🖨️ Cartouche faible — {fname} : {int(val)}%",
                            delai_h=48
                        )
                except Exception:
                    pass

        # OctoPrint / Ender 3 : PAS de surveillance automatique
        # Leçon 14/03 : OctoPrint unavailable = imprimante 3D en veille, pas une urgence
        if "octoprint" in eid_low:
            continue


def _surveiller_batteries_critiques(etats, now):
    """Batteries < 10% → alerte même la nuit"""
    for e in etats:
        eid = e["entity_id"]
        attrs = e.get("attributes", {})
        is_battery = (
            attrs.get("device_class") == "battery" or
            "etat_de_charge" in eid.lower() or
            "state_of_charge" in eid.lower() or
            (("battery" in eid.lower() or "batterie" in eid.lower()) and
             "puissance" not in eid.lower() and "power" not in eid.lower())
        )
        if not is_battery:
            continue
        unite = attrs.get("unit_of_measurement", "")
        if unite and unite not in ["%", ""]:
            continue
        try:
            val = float(e["state"])
            if not (0 <= val <= 100):
                continue
            if val < 10:
                derniere = batterie_get_derniere_alerte(eid)
                if derniere:
                    delta = (now - datetime.fromisoformat(derniere)).total_seconds()
                    if delta < 43200:
                        continue
                carto = cartographie_get(eid)
                piece = carto[2] if carto else ""
                piece_str = f" [{piece}]" if piece else ""
                telegram_send(f"🚨 BATTERIE CRITIQUE{piece_str}\n{eid} : {int(val)}%")
                batterie_set_alerte(eid)
        except Exception:
            pass


def _surveiller_meteo_france(index):
    """Alertes intempéries Météo France — lun-ven 5h-20h (tempête 24/7)"""
    now = datetime.now()
    jour_semaine = now.weekday()  # 0=lundi, 6=dimanche
    heure = now.hour

    # Uniquement lundi-vendredi (0-4)
    est_semaine = jour_semaine <= 4

    # Plage horaire standard : 5h-20h
    en_plage_horaire = 5 <= heure < 20

    # sensor.93_weather_alert — vigilance départementale
    eid_meteo = role_get("alerte_meteo") or "sensor.93_weather_alert"
    alerte_93 = index.get(eid_meteo)
    if not alerte_93:
        return

    attrs = alerte_93.get("attributes", {})

    # Mapping des risques Météo France
    vigilances = {
        "Vent violent":     attrs.get("Vent violent", "Vert"),
        "Pluie-inondation": attrs.get("Pluie-inondation", "Vert"),
        "Orages":           attrs.get("Orages", "Vert"),
        "Neige-verglas":    attrs.get("Neige-verglas", "Vert"),
        "Grand-froid":      attrs.get("Grand-froid", "Vert"),
        "Inondation":       attrs.get("Inondation", "Vert"),
    }

    # Niveaux de gravité
    NIVEAUX = {"Vert": 0, "Jaune": 1, "Orange": 2, "Rouge": 3}

    for risque, couleur in vigilances.items():
        niveau = NIVEAUX.get(couleur, 0)
        if niveau == 0:
            continue  # Vert = RAS

        # Tempête / Vent violent Rouge = alerte permanente (24/7, 7j/7)
        est_tempete = risque == "Vent violent" and niveau >= 3

        if est_tempete:
            # Alerte tempête → toujours, pas de filtre jour/heure
            _alerter_si_nouveau(
                f"meteo_tempete_{risque}",
                f"🌪️ TEMPÊTE — ALERTE {couleur.upper()}\n"
                f"Vigilance Météo France (93)\n"
                f"Risque : {risque}\n"
                f"Restez à l'abri — évitez tout déplacement.",
                delai_h=2
            )
            continue

        # Autres risques : lun-ven 5h-20h uniquement
        if not est_semaine or not en_plage_horaire:
            continue

        if niveau == 1:
            icone = "🟡"
            urgence = "Soyez vigilant"
            delai = 6
        elif niveau == 2:
            icone = "🟠"
            urgence = "Soyez très vigilant — adaptez vos déplacements"
            delai = 3
        else:  # Rouge
            icone = "🔴"
            urgence = "DANGER — évitez les déplacements"
            delai = 1

        _alerter_si_nouveau(
            f"meteo_{risque}_{couleur}",
            f"{icone} VIGILANCE {couleur.upper()} — {risque}\n"
            f"Météo France (93 — Seine-Saint-Denis)\n"
            f"{urgence}",
            delai_h=delai
        )

    # Compléments : pluie prochaine heure + rafales + prévisions J+1
    if est_semaine and en_plage_horaire:
        # Pluie dans l'heure
        rain = index.get(role_get("meteo_pluie") or "sensor.pavillons_sous_bois_next_rain")
        if rain:
            rain_attrs = rain.get("attributes", {})
            forecast_1h = rain_attrs.get("1_hour_forecast", {})
            if isinstance(forecast_1h, dict):
                pluie_prevue = [t for t, v in forecast_1h.items() if "pluie" in v.lower() or "rain" in v.lower()]
                if pluie_prevue:
                    _alerter_si_nouveau(
                        "meteo_pluie_1h",
                        f"🌧️ Pluie prévue dans l'heure\n"
                        f"Département — Météo France\n"
                        f"Créneaux : {', '.join(pluie_prevue[:4])}",
                        delai_h=2
                    )

        # Rafales actuelles
        weather = index.get(role_get("meteo") or "weather.pavillons_sous_bois")
        if weather:
            w_attrs = weather.get("attributes", {})
            rafales = w_attrs.get("wind_gust_speed", 0)
            try:
                rafales_val = float(rafales)
                if rafales_val >= 80:
                    _alerter_si_nouveau(
                        "meteo_rafales_fortes",
                        f"💨 RAFALES FORTES : {int(rafales_val)} km/h\n"
                        f"Département — Météo France\n"
                        f"Sécurisez les objets extérieurs.",
                        delai_h=3
                    )
                elif rafales_val >= 60:
                    _alerter_si_nouveau(
                        "meteo_rafales",
                        f"💨 Rafales de vent : {int(rafales_val)} km/h\n"
                        f"Département — Météo France",
                        delai_h=6
                    )
            except Exception:
                pass

        # Neige probable (> 40%)
        snow = index.get(role_get("meteo_risque_neige") or "sensor.pavillons_sous_bois_snow_chance")
        if snow and snow["state"] not in ("unavailable", "unknown"):
            try:
                snow_pct = int(float(snow["state"]))
                if snow_pct >= 40:
                    _alerter_si_nouveau(
                        "meteo_neige_probable",
                        f"❄️ Risque de neige : {snow_pct}%\n"
                        f"Département — Météo France\n"
                        f"Anticipez vos déplacements.",
                        delai_h=6
                    )
            except Exception:
                pass

    # ═══ PRÉVISIONS ANTICIPÉES J+1 — alerte le soir (19h-20h) ou le matin (5h-6h) ═══
    if est_semaine and (5 <= heure <= 6 or 19 <= heure <= 20):
        forecast = ha_get_forecast("weather.pavillons_sous_bois", "daily")

        if forecast:
            # Chercher les prévisions pour demain
            demain = (now + timedelta(days=1)).strftime("%Y-%m-%d")
            previsions_demain = []
            for prev in forecast:
                dt_str = prev.get("datetime", "")
                if demain in dt_str:
                    previsions_demain.append(prev)

            if not previsions_demain and len(forecast) >= 2:
                previsions_demain = [forecast[1]]

            for prev in previsions_demain[:1]:  # Une seule alerte pour demain
                condition = prev.get("condition", "")
                precip = prev.get("precipitation", 0) or 0
                precip_prob = prev.get("precipitation_probability", 0) or 0
                temp_max = prev.get("temperature", "?")
                temp_min = prev.get("templow", "?")
                wind_speed = prev.get("wind_speed", 0) or 0

                alertes = []

                # Pluie significative demain (> 5mm)
                try:
                    precip_val = float(precip)
                    precip_prob_val = float(precip_prob)
                    if precip_val >= 10:
                        alertes.append(f"🌧️ Fortes pluies : {precip_val:.1f} mm ({int(precip_prob_val)}%)")
                    elif precip_val >= 5:
                        alertes.append(f"🌧️ Pluie : {precip_val:.1f} mm ({int(precip_prob_val)}%)")
                except Exception:
                    pass

                # Vent fort demain
                try:
                    wind_val = float(wind_speed)
                    if wind_val >= 50:
                        alertes.append(f"💨 Vent fort : {int(wind_val)} km/h")
                except Exception:
                    pass

                # Neige / verglas
                conditions_dangereuses = ["snowy", "snowy-rainy", "hail", "exceptional"]
                if condition in conditions_dangereuses:
                    labels = {"snowy": "❄️ Neige", "snowy-rainy": "❄️ Neige/pluie mêlées",
                              "hail": "🧊 Grêle", "exceptional": "🚨 Conditions exceptionnelles"}
                    alertes.append(labels.get(condition, f"⚠️ {condition}"))

                # Gel
                try:
                    if temp_min != "?" and float(temp_min) <= 0:
                        alertes.append(f"🥶 Gel : {temp_min}°C mini — risque verglas")
                except Exception:
                    pass

                if alertes:
                    jour_label = "demain" if heure >= 19 else "aujourd'hui"
                    msg = (
                        f"📅 PRÉVISIONS {jour_label.upper()}\n"
                        f"Département — Météo France\n"
                        f"━━━━━━━━━━━━━━\n"
                        + "\n".join(alertes)
                        + f"\nTempératures : {temp_min}°C → {temp_max}°C"
                        + f"\nCondition : {condition}"
                    )
                    _alerter_si_nouveau(
                        f"meteo_prevision_{demain}",
                        msg,
                        delai_h=10
                    )


def _surveiller_coupure_edf(index):
    """Détecte une coupure EDF et restaure l'état exact d'avant la coupure"""
    # # # global _prises_snapshot, _coupure_edf_alertee, _snapshot_valide      # via shared# via shared# via shared

    prises_commande = cartographie_get_par_categorie("prise_connectee")
    switches = [
        (eid, pc) for eid, sc, pc in prises_commande
        if eid.startswith("switch.") and "child_lock" not in eid
    ]

    if not switches:
        return

    etats_actuels = {}
    for eid, piece in switches:
        e = index.get(eid)
        if not e:
            continue
        etat = e["state"]
        if etat in ("on", "off"):
            etats_actuels[eid] = etat

    total = len(etats_actuels)
    if total == 0:
        return

    prises_off = [eid for eid, etat in etats_actuels.items() if etat == "off"]
    ratio_off = len(prises_off) / total

    # Détection coupure : > 60% OFF simultanément ET ≥ 3 prises OFF
    if ratio_off >= 0.6 and len(prises_off) >= 3:
        if not _coupure_edf_alertee and _snapshot_valide and _prises_snapshot:
            shared._coupure_edf_alertee = True

            # Sauvegarder le snapshot en SQLite pour survivre à un restart
            mem_set("edf_snapshot", json.dumps(_prises_snapshot))

            a_rallumer = [eid for eid, etat in _prises_snapshot.items() if etat == "on" and etats_actuels.get(eid) == "off"]
            deja_off = [eid for eid, etat in _prises_snapshot.items() if etat == "off"]

            noms_rallumer = []
            for eid in a_rallumer:
                e = index.get(eid, {})
                fname = e.get("attributes", {}).get("friendly_name", eid) if isinstance(e, dict) else eid
                piece = dict(switches).get(eid, "")
                piece_str = f" [{piece}]" if piece else ""
                noms_rallumer.append(f"  🔴→🟢 {fname}{piece_str}")

            noms_off = []
            for eid in deja_off[:5]:
                e = index.get(eid, {})
                fname = e.get("attributes", {}).get("friendly_name", eid) if isinstance(e, dict) else eid
                noms_off.append(f"  ⚫ {fname} (était OFF → reste OFF)")

            msg = (
                f"🚨 COUPURE EDF DÉTECTÉE\n"
                f"{len(prises_off)}/{total} prises OFF simultanément\n\n"
                f"À restaurer ({len(a_rallumer)} prises étaient ON) :\n"
                + "\n".join(noms_rallumer[:10])
            )
            if noms_off:
                msg += "\n\nDéjà OFF avant coupure :\n" + "\n".join(noms_off)
            msg += "\n\nRestaurer l'état d'avant la coupure ?"

            boutons = [
                {"text": "✅ Restaurer", "callback_data": "edf_restaurer:all"},
                {"text": "❌ Ne rien faire", "callback_data": "edf_laisser:all"},
            ]
            telegram_send_buttons(msg, boutons)
            log.warning(f"🚨 Coupure EDF : {len(a_rallumer)} prises à restaurer ON, {len(deja_off)} restent OFF")
    else:
        # Situation normale → mettre à jour le snapshot et reset flag
        if ratio_off < 0.4:
            shared._prises_snapshot = dict(etats_actuels)
            shared._snapshot_valide = True
            if _coupure_edf_alertee:
                shared._coupure_edf_alertee = False


def surveillance_prises():
    """Thread de surveillance des prises connectées — polling adaptatif.
    Mode sniper : 20s quand un cycle est actif (précision phases),
    60s quand tout est calme (économie ressources)."""
    _sniper_mode = False
    while True:
        # Polling adaptatif : rapide si cycle en cours, lent sinon
        has_cycle_actif = any(v == "actif" for v in _etat_prises.values())
        if has_cycle_actif and not _sniper_mode:
            _sniper_mode = True
            log.info("🎯 Mode sniper activé — polling 20s")
        elif not has_cycle_actif and _sniper_mode:
            _sniper_mode = False
            log.info("😴 Mode veille — polling 60s")
        time.sleep(POLL_PRISES_ACTIF if has_cycle_actif else POLL_PRISES_IDLE)
        _watchdog["prises_last_run"] = datetime.now()

        # Les prises tournent TOUJOURS — détection cycles même avant code SMS
        try:
            etats = ha_get("states")
            if not etats:
                continue

            index = {e["entity_id"]: e for e in etats}
            production_w = ha_get_production_solaire_actuelle(etats)

            prises = cartographie_get_par_categorie("prise_connectee")

            prises_puissance = []
            for eid, sc, pc in prises:
                if not eid.startswith("sensor."):
                    continue
                e_state = index.get(eid)
                if e_state:
                    unit = e_state.get("attributes", {}).get("unit_of_measurement", "")
                    if unit in ["W", "w", "Watt"]:
                        prises_puissance.append((eid, sc, pc))
                        continue
                if any(k in eid.lower() for k in ["power", "puissance", "watt"]):
                    prises_puissance.append((eid, sc, pc))
            prises = prises_puissance

            # Exclure les prises qui ne sont PAS des machines à cycles
            EXCLUSIONS_PRISES = {"anker", "solarbank", "ecojoko", "pc_salon", "ventilateur", "chambre_tv"}

            for entity_id, sous_cat, piece in prises:
                if entity_id not in index:
                    continue

                # Exclure les prises non-machine
                if any(excl in entity_id.lower() for excl in EXCLUSIONS_PRISES):
                    continue
                _app_excl = appareil_get(entity_id)
                if _app_excl:
                    if not _app_excl.get("surveiller", True):
                        continue
                    # Coupe-veille et monitoring : pas de détection de cycles
                    if _app_excl["type"] in ("coupe_veille", "monitoring_energie"):
                        continue

                e = index[entity_id]
                attrs = e.get("attributes", {})
                fname = attrs.get("friendly_name", entity_id)
                for suffixe in [" Puissance", " Power", " Consommation", " Watt"]:
                    if fname.endswith(suffixe):
                        fname = fname[:-len(suffixe)].strip()
                        break

                puissance_w = None
                for key in ["current_power_w", "power", "current_consumption", "watt"]:
                    if key in attrs:
                        try:
                            puissance_w = float(attrs[key])
                            break
                        except Exception:
                            pass

                if puissance_w is None and ("power" in entity_id.lower() or "watt" in entity_id.lower()):
                    try:
                        puissance_w = float(e["state"])
                    except Exception:
                        pass

                if puissance_w is None:
                    continue

                en_cours = cycle_en_cours(entity_id)
                etat_precedent = _etat_prises.get(entity_id, "inactif")

                if entity_id not in _puissances_historique:
                    _puissances_historique[entity_id] = []

                # ═══ LOGIQUE CYCLE CORRIGÉE ═══
                # SEUIL_CYCLE_W (200W) = démarrer un NOUVEAU cycle (chauffage/essorage)
                # SEUIL_FIN_W (10W) = machine VRAIMENT arrêtée
                # Entre les deux (10-200W) = machine en phase lavage/rinçage → cycle CONTINUE
                if puissance_w > SEUIL_FIN_W:
                    # Machine consomme → cycle en cours ou démarrage
                    ts_now = datetime.now().isoformat()
                    _puissances_historique[entity_id].append((ts_now, puissance_w))
                    # Ne pas reset la grâce si défroissage (rappel envoyé + puissance < 200W)
                    if _rappel_linge_envoye.get(entity_id) and puissance_w < SEUIL_CYCLE_W:
                        pass  # Défroissage — laisser la grâce expirer normalement
                    else:
                        _grace_fin.pop(entity_id, None)  # Annuler le timer de fin
                        _defroissage_detecte.pop(entity_id, None)

                    # Stocker en SQLite (survit aux restarts — plus jamais besoin de CSV ou API history)
                    try:
                        _conn_m = sqlite3.connect(DB_PATH)
                        _conn_m.execute("INSERT INTO cycle_mesures (entity_id, watts, ts) VALUES (?, ?, ?)",
                                       (entity_id, puissance_w, ts_now))
                        _conn_m.commit()
                        _conn_m.close()
                    except Exception:
                        pass

                    # Tracker la dernière phase haute (pour grâce intelligente)
                    if puissance_w > 1500:
                        _derniere_phase_haute[entity_id] = "C"  # Chauffage
                    elif puissance_w > 500:
                        _derniere_phase_haute[entity_id] = "E"  # Essorage
                    elif puissance_w > 50:
                        if entity_id not in _derniere_phase_haute:
                            _derniere_phase_haute[entity_id] = "L"  # Lavage

                    # Auto-détection cycle doux : si conso > SEUIL_FIN_W depuis 5+ min sans cycle
                    if etat_precedent != "actif" and puissance_w <= SEUIL_CYCLE_W:
                        hist = _puissances_historique.get(entity_id, [])
                        if len(hist) >= 15:  # 15 mesures × 20s = 5 min de conso continue
                            moy = sum(w for _, w in hist[-15:]) / 15
                            if moy > SEUIL_FIN_W:
                                # Cycle doux détecté — démarrer comme un cycle normal
                                puissance_w = max(puissance_w, moy)
                                log.info(f"🔄 Cycle doux détecté: {fname} ({moy:.0f}W moy sur 5min)")

                    if etat_precedent != "actif" and (puissance_w > SEUIL_CYCLE_W or (len(_puissances_historique.get(entity_id, [])) >= 15 and sum(w for _, w in _puissances_historique.get(entity_id, [])[-15:]) / max(1, min(15, len(_puissances_historique.get(entity_id, [])))) > SEUIL_FIN_W)):
                        # NOUVEAU cycle : puissance forte (>200W) OU conso continue > 5 min
                        _etat_prises[entity_id] = "actif"
                        _rappel_linge_envoye.pop(entity_id, None)
                        # Nom personnalisé si configuré
                        _app_start = appareil_get(entity_id)
                        _nom_start = _app_start["nom"] if _app_start and _app_start["nom"] else fname
                        cycle_debut(entity_id, _nom_start, int(production_w))
                        couverture = ""
                        try:
                            eid_conso = role_get("conso_temps_reel") or "sensor.ecojoko_consommation_temps_reel"
                            e_eco = index.get(eid_conso)
                            conso_reseau_w = float(e_eco["state"]) if e_eco else 0
                            # Formule corrigée v1.5.0 :
                            # Ecojoko = tirage EDF seul, conso réelle = EDF + production solaire
                            conso_totale_w = conso_reseau_w + production_w
                            if production_w > 0 and conso_totale_w > 0:
                                pct = min(100, int(production_w / conso_totale_w * 100))
                                if pct >= 100:
                                    couverture = "\n☀️ Couvert à 100% par le solaire"
                                else:
                                    couverture = f"\n☀️ Couverture solaire : {pct}%"
                        except Exception:
                            pass
                        # Estimation coût + conseil
                        prix_kwh_now = tarif_prix_kwh_actuel()
                        conso_estimee = 1.2  # kWh moyen cycle machine
                        # Chercher la conso moyenne pour cette machine
                        try:
                            _conn_est = sqlite3.connect(DB_PATH)
                            avg_row = _conn_est.execute(
                                "SELECT AVG(conso_kwh) FROM cycles_appareils WHERE entity_id=? AND fin IS NOT NULL AND conso_kwh > 0",
                                (entity_id,)
                            ).fetchone()
                            if avg_row and avg_row[0]:
                                conso_estimee = avg_row[0]
                            _conn_est.close()
                        except Exception:
                            pass
                        cout_estime = round(conso_estimee * prix_kwh_now, 2)

                        msg_start = f"🔄 {_nom_start} en marche\nPuissance : {int(puissance_w)}W | {datetime.now().strftime('%H:%M')}"
                        msg_start += couverture

                        # Estimation coût
                        if production_w > 500:
                            pct_sol = min(100, int(production_w / max(puissance_w, 1) * 100))
                            cout_reel = round(cout_estime * (100 - pct_sol) / 100, 2)
                            msg_start += f"\n💰 Estimation : ~{cout_reel:.2f}€ (solaire {pct_sol}%)"
                        else:
                            msg_start += f"\n💰 Estimation : ~{cout_estime:.2f}€"

                        telegram_send(msg_start)
                        log.info(f"Cycle démarré : {_nom_start} ({int(puissance_w)}W) ~{cout_estime:.2f}€")
                else:
                    if etat_precedent == "actif":
                        if entity_id not in _grace_fin:
                            _grace_fin[entity_id] = datetime.now()
                            last_phase = _derniere_phase_haute.get(entity_id, "L")
                            log.debug(f"Grâce démarré : {fname} (dernière phase: {last_phase})")

                        # ═══ GRÂCE INTELLIGENTE ═══
                        # Type machine : table appareils (configuré par l'utilisateur) ou fallback friendly_name
                        _appareil = appareil_get(entity_id)
                        if _appareil and _appareil["type"] != "autre":
                            _type_machine = _appareil["type"]
                        else:
                            # Fallback friendly_name pour les prises pas encore configurées
                            _fname_low = fname.lower()
                            if any(k in _fname_low for k in ("sèche", "seche", "séche", "dryer", "dry")):
                                _type_machine = "seche_linge"
                            elif any(k in _fname_low for k in ("vaisselle", "vaiselle", "dishwash")):
                                _type_machine = "lave_vaisselle"
                            elif "lav" in _fname_low:
                                _type_machine = "lave_linge"
                            else:
                                _type_machine = "autre"
                        _is_seche_linge = _type_machine == "seche_linge"
                        _is_lave_vaisselle = _type_machine == "lave_vaisselle"
                        _is_lave_linge = _type_machine == "lave_linge"

                        last_phase = _derniere_phase_haute.get(entity_id, "L")

                        if _is_seche_linge:
                            grace_sec = GRACE_APRES_SECHAGE * 60
                        elif _is_lave_vaisselle:
                            grace_sec = GRACE_APRES_VAISSELLE * 60
                        elif _is_lave_linge and last_phase == "E":
                            # Après essorage → hublot 5 min → grâce courte
                            grace_sec = GRACE_APRES_ESSORAGE * 60
                        elif _is_lave_linge and last_phase == "C":
                            # Après chauffage → pause rinçage→essorage possible → grâce longue
                            grace_sec = GRACE_APRES_LAVAGE * 60
                        else:
                            grace_sec = GRACE_APRES_SECHAGE * 60

                        elapsed = (datetime.now() - _grace_fin[entity_id]).total_seconds()

                        # ═══ RAPPEL IMMÉDIAT — toutes les machines ═══
                        if not _rappel_linge_envoye.get(entity_id) and elapsed >= 40:
                            # Durée du cycle depuis le début
                            duree_cycle_min = 0
                            if en_cours:
                                try:
                                    duree_cycle_min = (datetime.now() - datetime.fromisoformat(en_cours[0])).total_seconds() / 60
                                except Exception:
                                    pass

                            # Durée minimale : un cycle trop court = c'est une pause, pas la fin
                            _min_rappel = DUREE_MIN_SECHE_LINGE if _is_seche_linge else (DUREE_MIN_LAVE_LINGE if _is_lave_linge else (DUREE_MIN_LAVE_VAISSELLE if _is_lave_vaisselle else 10))

                            if duree_cycle_min >= _min_rappel:
                                _rappel_linge_envoye[entity_id] = True
                                _app_rappel = appareil_get(entity_id)
                                _nom_rappel = _app_rappel["nom"] if _app_rappel and _app_rappel["nom"] else fname

                                if _is_seche_linge:
                                    telegram_send(
                                        f"👕 {_nom_rappel} — Linge chaud !\n"
                                        f"Séchage terminé ({int(duree_cycle_min)} min).\n"
                                        f"Sortez le linge — plus facile à plier.\n"
                                        f"⏳ Défroissage possible, fin dans ~{int(grace_sec/60) - 1} min."
                                    )
                                elif _is_lave_linge:
                                    telegram_send(
                                        f"🧺 {_nom_rappel} — Cycle terminé !\n"
                                        f"Durée : {int(duree_cycle_min)} min.\n"
                                        f"🚪 Hublot se déverrouille dans ~5 min.\n"
                                        f"Préparez le sèche-linge ou l'étendoir."
                                    )
                                elif _is_lave_vaisselle:
                                    telegram_send(
                                        f"🍽️ {_nom_rappel} — Vaisselle prête !\n"
                                        f"Cycle terminé ({int(duree_cycle_min)} min).\n"
                                        f"⚠️ Attention vaisselle chaude — laissez refroidir 10 min."
                                    )
                                else:
                                    telegram_send(
                                        f"✅ {_nom_rappel} — Cycle en fin.\n"
                                        f"Durée : {int(duree_cycle_min)} min."
                                    )
                                log.info(f"📢 Rappel immédiat : {_nom_rappel} ({int(duree_cycle_min)} min)")

                        # Durée minimale : un sèche-linge de 13 min n'existe pas
                        duree_min_requise = 0
                        if _is_seche_linge:
                            duree_min_requise = DUREE_MIN_SECHE_LINGE
                        elif _is_lave_linge:
                            duree_min_requise = DUREE_MIN_LAVE_LINGE
                        elif _is_lave_vaisselle:
                            duree_min_requise = DUREE_MIN_LAVE_VAISSELLE

                        # Calculer la durée réelle du cycle
                        duree_cycle_actuelle = 0
                        if en_cours:
                            try:
                                debut_cycle = datetime.fromisoformat(en_cours[0])
                                duree_cycle_actuelle = (datetime.now() - debut_cycle).total_seconds() / 60
                            except Exception:
                                pass

                        if duree_cycle_actuelle < duree_min_requise:
                            # Cycle trop court → c'est une pause, pas la fin
                            log.debug(f"Cycle {fname}: {duree_cycle_actuelle:.0f}min < minimum {duree_min_requise}min → pause, pas fin")
                            continue

                        if elapsed >= grace_sec:
                            _etat_prises[entity_id] = "inactif"
                            _grace_fin.pop(entity_id, None)
                            _derniere_phase_haute.pop(entity_id, None)
                            _rappel_linge_envoye.pop(entity_id, None)
                            _defroissage_detecte.pop(entity_id, None)
                            if en_cours:
                                debut_dt = datetime.fromisoformat(en_cours[0])
                                duree_h = (datetime.now() - debut_dt).total_seconds() / 3600
                                # Lire les mesures depuis SQLite (source de vérité — survit aux restarts)
                                mesures_brutes = []
                                try:
                                    _conn_r = sqlite3.connect(DB_PATH)
                                    rows = _conn_r.execute(
                                        "SELECT ts, watts FROM cycle_mesures WHERE entity_id=? ORDER BY ts",
                                        (entity_id,)
                                    ).fetchall()
                                    mesures_brutes = [(ts, w) for ts, w in rows]
                                    # Purger les mesures du cycle terminé
                                    _conn_r.execute("DELETE FROM cycle_mesures WHERE entity_id=?", (entity_id,))
                                    _conn_r.commit()
                                    _conn_r.close()
                                except Exception:
                                    # Fallback sur la mémoire
                                    mesures_brutes = _puissances_historique.get(entity_id, [])

                                watts_list = [w for _, w in mesures_brutes] if mesures_brutes and isinstance(mesures_brutes[0], tuple) else mesures_brutes
                                puissance_moy = sum(watts_list) / len(watts_list) if watts_list else puissance_w
                                conso_kwh = round(puissance_moy * duree_h / 1000, 3)

                                # Analyser le profil de puissance pour identifier le programme
                                profil_cycle = _analyser_profil_cycle(mesures_brutes)

                                _puissances_historique[entity_id] = []
                                resultat = cycle_fin(entity_id, conso_kwh)
                                if resultat:
                                    duree = resultat["duree_min"]
                                    couv = resultat.get("couverture_pct", 0)
                                    cout_r = resultat.get("cout_reseau", 0)
                                    eco = resultat.get("economie", 0)
                                    prod = resultat.get("prod_solaire_moy", 0)

                                    # ═══ NOTIFICATION — ce que l'utilisateur veut savoir ═══
                                    # 1. Combien ça a coûté
                                    # 2. Solaire ou pas
                                    # Type machine depuis table appareils
                                    _app_fin = appareil_get(entity_id)
                                    _type_fin = _app_fin["type"] if _app_fin else "autre"
                                    # Nom personnalisé si dispo
                                    _nom_machine = _app_fin["nom"] if _app_fin and _app_fin["nom"] else fname

                                    msg_fin = f"✅ {_nom_machine} terminé — {duree} min"

                                    # Coût + solaire
                                    cout_t = resultat.get("cout_total", 0)
                                    if couv >= 100:
                                        msg_fin += f"\n☀️ {conso_kwh:.2f} kWh — 100% solaire, gratuit !"
                                        enregistrer_economie("cycle_solaire", f"{fname} 100% solaire", cout_t, conso_kwh)
                                    elif couv > 0:
                                        msg_fin += f"\n💰 {conso_kwh:.2f} kWh — {cout_r:.2f}€ ({couv}% solaire, économie {eco:.2f}€)"
                                        if eco > 0:
                                            enregistrer_economie("cycle_solaire", f"{fname} {couv}% solaire", eco, eco / max(tarif_prix_kwh_actuel(), 0.01))
                                    else:
                                        msg_fin += f"\n💰 {conso_kwh:.2f} kWh — {cout_t:.2f}€"

                                    # Cumul économies du mois
                                    try:
                                        eco_mois = get_economies_mois()
                                        if eco_mois["total_eur"] > 0.01:
                                            msg_fin += f"\n📈 Ce mois : {eco_mois['total_eur']:.2f}€ économisés"
                                    except Exception:
                                        pass

                                    telegram_send(msg_fin)

                                    # ═══ APPRENTISSAGE SILENCIEUX (en DB, pas dans le message) ═══
                                    try:
                                        skill_cycle_machine_signature(
                                            entity_id, fname, duree, conso_kwh, puissance_moy, profil_cycle
                                        )
                                    except Exception:
                                        pass
                                    try:
                                        _conn_prof = sqlite3.connect(DB_PATH)
                                        _last_id = _conn_prof.execute(
                                            "SELECT id FROM cycles_appareils WHERE entity_id=? AND fin IS NOT NULL ORDER BY id DESC LIMIT 1",
                                            (entity_id,)
                                        ).fetchone()
                                        if _last_id:
                                            _conn_prof.execute(
                                                "UPDATE cycles_appareils SET programme=?, profil_json=? WHERE id=?",
                                                (profil_cycle.get("signature", ""), json.dumps(profil_cycle, ensure_ascii=False), _last_id[0])
                                            )
                                        _conn_prof.commit()
                                        _conn_prof.close()
                                    except Exception:
                                        pass
                                    log.info(f"Cycle terminé : {fname} {duree}min {conso_kwh}kWh {cout_t:.2f}€ solaire:{couv}%")
                    else:
                        _etat_prises[entity_id] = "inactif"
                        _grace_fin.pop(entity_id, None)

        except Exception as ex:
            log.error(f"❌ surveillance_prises: {ex}")
            apprentissage_log_echec("prises", str(ex))


def _maj_baseline_entities():
    """Met à jour BASELINE_ENTITIES à partir des rôles découverts.
    Sur une nouvelle installation, les rôles remplacent les valeurs par défaut."""
    # global BASELINE_ENTITIES  # via shared
    dynamiques = role_decouvrir_baselines()
    if dynamiques:
        shared.BASELINE_ENTITIES = dynamiques
        log.info(f"📊 BASELINE_ENTITIES mis à jour: {len(dynamiques)} entités")


def baseline_collecter(etats):
    """Collecte un point de baseline pour les entités suivies — appelé toutes les 5 min"""
    index = {e["entity_id"]: e for e in etats}
    now = datetime.now()
    jour = now.weekday()  # 0=lundi, 6=dimanche
    heure = now.hour

    conn = sqlite3.connect(DB_PATH)
    for eid, label in BASELINE_ENTITIES.items():
        e = index.get(eid)
        if not e or e["state"] in ("unavailable", "unknown"):
            continue
        try:
            val = float(e["state"])
        except Exception:
            continue

        # Upsert : moyenne glissante pondérée
        row = conn.execute(
            "SELECT valeur_moyenne, nb_mesures FROM baselines WHERE entity_id=? AND jour_semaine=? AND heure=?",
            (eid, jour, heure)
        ).fetchone()

        if row:
            ancien_moy, nb = row
            # Moyenne mobile exponentielle pondérée (poids récent plus fort)
            nouveau_nb = min(nb + 1, 100)  # Cap à 100 pour éviter inertie infinie
            alpha = 2.0 / (nouveau_nb + 1)  # Poids du nouveau point
            nouvelle_moy = ancien_moy * (1 - alpha) + val * alpha
            conn.execute(
                "UPDATE baselines SET valeur_moyenne=?, nb_mesures=?, updated_at=? WHERE entity_id=? AND jour_semaine=? AND heure=?",
                (round(nouvelle_moy, 2), nouveau_nb, now.isoformat(), eid, jour, heure)
            )
        else:
            conn.execute(
                "INSERT INTO baselines (entity_id, jour_semaine, heure, valeur_moyenne, nb_mesures, updated_at) VALUES (?, ?, ?, ?, 1, ?)",
                (eid, jour, heure, round(val, 2), now.isoformat())
            )
    conn.commit()
    conn.close()


def baseline_detecter_anomalies(etats):
    """Détecte les écarts significatifs par rapport aux baselines"""
    index = {e["entity_id"]: e for e in etats}
    now = datetime.now()
    jour = now.weekday()
    heure = now.hour

    conn = sqlite3.connect(DB_PATH)
    for eid, label in BASELINE_ENTITIES.items():
        e = index.get(eid)
        if not e or e["state"] in ("unavailable", "unknown"):
            continue
        try:
            val = float(e["state"])
        except Exception:
            continue

        row = conn.execute(
            "SELECT valeur_moyenne, nb_mesures FROM baselines WHERE entity_id=? AND jour_semaine=? AND heure=?",
            (eid, jour, heure)
        ).fetchone()

        if not row or row[1] < 30:
            continue  # Minimum 30 mesures avant de comparer (fiabilité)

        moy, nb = row
        if moy < 5:
            continue  # Ignorer les baselines proches de 0 (bruit)

        ecart_pct = abs(val - moy) / moy * 100

        # Seuils par type d'entité — élevés pour éviter les faux positifs
        if "temp" in label:
            seuil = 40  # 40% d'écart sur la température
        elif "production" in label:
            # Production solaire varie énormément (nuages) → seuil très haut
            # Et 0W la nuit est normal → ne pas comparer si baseline < 50W
            if moy < 50:
                continue
            seuil = 200
        else:
            seuil = 150  # 150% d'écart sur la conso (la conso varie beaucoup)

        if ecart_pct > seuil:
            sens = "↗️ au-dessus" if val > moy else "↘️ en-dessous"
            fname = e.get("attributes", {}).get("friendly_name", eid)
            unite = e.get("attributes", {}).get("unit_of_measurement", "")
            _alerter_si_nouveau(
                f"baseline_{eid}_{jour}_{heure}",
                f"📊 ANOMALIE BASELINE\n{fname}\n"
                f"Actuel : {val} {unite} | Habituel : {moy:.0f} {unite}\n"
                f"Écart : {ecart_pct:.0f}% {sens}\n"
                f"(basé sur {nb} mesures, {['lun','mar','mer','jeu','ven','sam','dim'][jour]} {heure}h)",
                delai_h=6
            )
    conn.close()


def cmd_baselines():
    """Affiche l'état des baselines collectées"""
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now()
    jour = now.weekday()
    heure = now.hour
    jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

    rapport = "📊 BASELINES COMPORTEMENTALES\n━━━━━━━━━━━━━━━━━━\n"

    # Stats globales
    total = conn.execute("SELECT COUNT(*) FROM baselines").fetchone()[0]
    entites_uniques = conn.execute("SELECT COUNT(DISTINCT entity_id) FROM baselines").fetchone()[0]
    rapport += f"Points collectés : {total}\n"
    rapport += f"Entités suivies : {entites_uniques}\n\n"

    # Valeurs actuelles vs baseline pour ce créneau
    rapport += f"📍 Maintenant : {jours_fr[jour]} {heure}h\n"
    for eid, label in BASELINE_ENTITIES.items():
        row = conn.execute(
            "SELECT valeur_moyenne, nb_mesures FROM baselines WHERE entity_id=? AND jour_semaine=? AND heure=?",
            (eid, jour, heure)
        ).fetchone()
        if row:
            moy, nb = row
            rapport += f"  {label} : baseline={moy:.0f} ({nb} mesures)\n"
        else:
            rapport += f"  {label} : pas encore de données\n"

    # Résumé par entité : couverture horaire
    rapport += "\n📈 COUVERTURE :\n"
    for eid, label in BASELINE_ENTITIES.items():
        nb_slots = conn.execute(
            "SELECT COUNT(*) FROM baselines WHERE entity_id=?", (eid,)
        ).fetchone()[0]
        pct = int(nb_slots / (7 * 24) * 100)
        barre = "█" * (pct // 10) + "░" * (10 - pct // 10)
        rapport += f"  {label} : {barre} {pct}% ({nb_slots}/168 créneaux)\n"

    conn.close()

    if total < 50:
        rapport += "\n💡 Les baselines se construisent automatiquement.\nCompter ~2 semaines pour une couverture complète."

    return rapport


def skill_fenetre_solaire(etats):
    """Apprend la meilleure fenêtre de production solaire par jour de la semaine.
    Skip silencieux si pas de panneaux solaires.
    Objectif : recommander le créneau optimal pour lancer les machines."""
    if not role_get("production_solaire_w"):
        return
    index = {e["entity_id"]: e for e in etats}
    now = datetime.now()
    jour = now.weekday()
    heure = now.hour

    # Ne collecter que de jour (7h-20h)
    if heure < 7 or heure > 20:
        return

    # Lire production solaire totale
    production_w = ha_get_production_solaire_actuelle(etats)
    if production_w <= 0:
        return

    # Charger skill existant
    data, nb = skill_get("fenetre_solaire")
    if not data:
        data = {}

    # Structure : { "0": {"7": [moy, nb], "8": [moy, nb], ...}, "1": {...}, ... }
    jour_str = str(jour)
    heure_str = str(heure)
    if jour_str not in data:
        data[jour_str] = {}
    if heure_str not in data[jour_str]:
        data[jour_str][heure_str] = [0, 0]

    ancien_moy, ancien_nb = data[jour_str][heure_str]
    nouveau_nb = min(ancien_nb + 1, 100)
    alpha = 2.0 / (nouveau_nb + 1)
    nouvelle_moy = ancien_moy * (1 - alpha) + production_w * alpha
    data[jour_str][heure_str] = [round(nouvelle_moy, 1), nouveau_nb]

    skill_set("fenetre_solaire", data, nb + 1)


def _analyser_profil_cycle(mesures):
    """Analyse le profil de puissance d'un cycle et identifie les phases.
    Input: [(timestamp_iso, watts), ...]
    Output: {"phases": [...], "programme": "chauffage 15min + lavage 33min + essorage 3min", "signature": "C15-L33-E3"}
    """
    if not mesures or len(mesures) < 3:
        return {"phases": [], "programme": "inconnu", "signature": "?"}

    # Normaliser les données
    points = []
    for item in mesures:
        if isinstance(item, tuple) and len(item) == 2:
            ts, w = item
            points.append((ts, float(w) if str(w).replace(".", "").isdigit() else 0))
        else:
            points.append(("", float(item) if str(item).replace(".", "").isdigit() else 0))

    if not points:
        return {"phases": [], "programme": "inconnu", "signature": "?"}

    # Détecter les phases par seuils de puissance
    # C = Chauffage (>1500W), L = Lavage (50-500W), E = Essorage (500-1500W), P = Pause (<50W)
    phases = []
    phase_actuelle = None
    phase_debut_ts = None
    phase_watts = []

    def _classifier_watts(w):
        if w > 1500: return "C"    # Chauffage
        if w > 500:  return "E"    # Essorage
        if w > 50:   return "L"    # Lavage/Rinçage
        return "P"                  # Pause

    def _duree_min_entre(ts_debut, ts_fin):
        """Calcule la durée en minutes entre 2 timestamps ISO."""
        try:
            from datetime import datetime as _dt
            # Gérer les formats avec/sans Z et fuseaux
            for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z",
                        "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
                try:
                    d1 = _dt.strptime(ts_debut.replace("Z", "+00:00")[:26], fmt.replace("%z", ""))
                    d2 = _dt.strptime(ts_fin.replace("Z", "+00:00")[:26], fmt.replace("%z", ""))
                    return max(1, int((d2 - d1).total_seconds() / 60))
                except Exception:
                    continue
        except Exception:
            pass
        return 2  # fallback

    for idx, (ts, w) in enumerate(points):
        cat = _classifier_watts(w)
        if cat != phase_actuelle:
            if phase_actuelle is not None and len(phase_watts) >= 2 and phase_debut_ts:
                duree_phase = _duree_min_entre(phase_debut_ts, ts)
                phases.append({
                    "type": phase_actuelle,
                    "duree_min": duree_phase,
                    "watts_moy": round(sum(phase_watts) / len(phase_watts)),
                    "watts_max": max(phase_watts),
                    "nb_mesures": len(phase_watts),
                })
            phase_actuelle = cat
            phase_debut_ts = ts
            phase_watts = [w]
        else:
            phase_watts.append(w)

    # Dernière phase
    if phase_actuelle and len(phase_watts) >= 2 and phase_debut_ts:
        last_ts = points[-1][0] if points else phase_debut_ts
        duree_phase = _duree_min_entre(phase_debut_ts, last_ts)
        phases.append({
            "type": phase_actuelle,
            "duree_min": max(1, duree_phase),
            "watts_moy": round(sum(phase_watts) / len(phase_watts)),
            "watts_max": max(phase_watts),
            "nb_mesures": len(phase_watts),
        })

    # Construire la signature compacte : C15-L33-E3 (type + durée en min)
    sig_parts = []
    for p in phases:
        sig_parts.append(f"{p['type']}{p['duree_min']}")
    signature = "-".join(sig_parts) if sig_parts else "?"

    # Identifier le programme
    has_chauffage = any(p["type"] == "C" for p in phases)
    duree_chauffage = sum(p["duree_min"] for p in phases if p["type"] == "C")
    has_essorage = any(p["type"] == "E" for p in phases)
    duree_totale = sum(p["duree_min"] for p in phases)
    watts_max = max((p["watts_max"] for p in phases), default=0)

    # Pas de classification — le script ne devine RIEN.
    # La signature est factuelle. Le nom du programme vient de l'utilisateur.

    return {
        "phases": phases,
        "signature": signature,
        "duree_totale_min": duree_totale,
        "watts_max": watts_max,
    }


def _similarite_signature(sig1, sig2):
    """Compare deux signatures de cycle. Retourne un score 0-100.
    Signatures : 'C15-L33-E3' — on compare les phases et durées."""
    if sig1 == sig2:
        return 100
    try:
        def _parse_sig(sig):
            phases = {}
            for part in sig.split("-"):
                if len(part) >= 2:
                    phases[part[0]] = int(part[1:])
            return phases
        p1, p2 = _parse_sig(sig1), _parse_sig(sig2)
        if not p1 or not p2:
            return 0
        # Mêmes phases présentes ?
        all_types = set(list(p1.keys()) + list(p2.keys()))
        score = 0
        for t in all_types:
            d1 = p1.get(t, 0)
            d2 = p2.get(t, 0)
            if d1 == 0 or d2 == 0:
                score -= 20  # Phase manquante
            else:
                ratio = min(d1, d2) / max(d1, d2)
                score += ratio * (100 / len(all_types))
        return max(0, min(100, int(score)))
    except Exception:
        return 0


def skill_cycle_machine_signature(entity_id, friendly_name, duree_min, conso_kwh, puissance_moy, profil=None):
    """Apprentissage des programmes par l'utilisateur.
    Le script ne devine RIEN. Il observe une signature et :
    1. Cherche si une signature similaire a déjà été nommée → la reconnaît
    2. Sinon → demande à l'utilisateur via Telegram (une seule fois par signature)
    """
    data, nb = skill_get("cycle_signatures")
    if not data:
        data = {}

    sig = profil.get("signature", "?") if profil else "?"

    if entity_id not in data:
        data[entity_id] = {"nom": friendly_name, "programmes": {}, "nb_cycles_total": 0}

    info = data[entity_id]
    info["nom"] = friendly_name
    info["nb_cycles_total"] = info.get("nb_cycles_total", 0) + 1

    if "programmes" not in info:
        info["programmes"] = {}

    # ═══ CHERCHER une signature connue ═══
    best_match = None
    best_score = 0
    for prog_name, prog_data in info["programmes"].items():
        score = _similarite_signature(sig, prog_data.get("signature", ""))
        if score > best_score:
            best_score = score
            best_match = prog_name

    if best_match and best_score >= 70:
        # Programme reconnu → mettre à jour les stats
        p = info["programmes"][best_match]
        n = p["nb_cycles"]
        alpha = 2.0 / (min(n + 1, 30) + 1)
        p["duree_moy"] = round(p["duree_moy"] * (1 - alpha) + duree_min * alpha, 1)
        p["conso_moy"] = round(p["conso_moy"] * (1 - alpha) + conso_kwh * alpha, 3)
        p["puissance_moy"] = round(p["puissance_moy"] * (1 - alpha) + puissance_moy * alpha, 0)
        p["nb_cycles"] = min(n + 1, 50)
        p["dernier"] = datetime.now().isoformat()
        data[entity_id] = info
        skill_set("cycle_signatures", data, nb + 1)
        return best_match  # Programme reconnu

    # ═══ SIGNATURE INCONNUE → demander à l'utilisateur ═══
    # Stocker temporairement les données du cycle pour quand l'utilisateur répondra
    mem_set(f"cycle_pending_{entity_id}", json.dumps({
        "signature": sig,
        "duree_min": duree_min,
        "conso_kwh": conso_kwh,
        "puissance_moy": puissance_moy,
        "profil": profil,
        "timestamp": datetime.now().isoformat(),
    }))

    # Enregistrement silencieux (pas de question à l'utilisateur)
    log.info(f"Signature cycle {friendly_name}: {sig[:40]} | {duree_min}min | {conso_kwh:.2f}kWh")

    data[entity_id] = info
    skill_set("cycle_signatures", data, nb + 1)
    return None  # Pas encore nommé


def skill_comportement_pac(etats):
    """Apprend la corrélation PAC / température extérieure / saison.
    Skip silencieux si pas de PAC."""
    if not role_get("pac_climate"):
        return
    index = {e["entity_id"]: e for e in etats}
    now = datetime.now()
    mois = now.month
    heure = now.hour

    # Trouver PAC
    pac_state = None
    pac_conso = 0
    for e in etats:
        if e["entity_id"].startswith("climate."):
            carto = cartographie_get(e["entity_id"])
            if carto and "chauffage" in carto[0]:
                pac_state = e["state"]
                break

    if not pac_state:
        return

    pac_en_service = pac_state in ("auto", "heat", "cool", "fan_only", "heat_cool")

    # Température extérieure
    temp_ext = None
    e_ext = index.get(role_get("temp_exterieure") or "sensor.ecojoko_temperature_exterieure")
    if e_ext and e_ext["state"] not in ("unavailable", "unknown"):
        try:
            temp_ext = float(e_ext["state"])
        except Exception:
            pass
    if temp_ext is None:
        return

    # Conso PAC
    e_pac = index.get(role_get("pac_conso") or "sensor.pompe_a_chaleur_air_eau_energy_current")
    if e_pac and e_pac["state"] not in ("unavailable", "unknown"):
        try:
            pac_conso = float(e_pac["state"])
        except Exception:
            pass

    # Stocker : par tranche de température (arrondi à 2°C)
    data, nb = skill_get("comportement_pac")
    if not data:
        data = {"tranches": {}, "mois": {}}

    tranche = str(round(temp_ext / 2) * 2)  # Ex: 12.3°C → "12"
    if tranche not in data["tranches"]:
        data["tranches"][tranche] = {"pac_on": 0, "pac_off": 0, "conso_moy": 0, "nb": 0}

    t = data["tranches"][tranche]
    if pac_en_service:
        t["pac_on"] += 1
    else:
        t["pac_off"] += 1
    t["nb"] += 1
    if pac_conso > 0:
        ancien_n = max(t["nb"] - 1, 1)
        t["conso_moy"] = round((t["conso_moy"] * ancien_n + pac_conso) / t["nb"], 1)
    data["tranches"][tranche] = t

    # Stats par mois
    mois_str = str(mois)
    if mois_str not in data["mois"]:
        data["mois"][mois_str] = {"pac_on": 0, "pac_off": 0, "nb": 0}
    m = data["mois"][mois_str]
    if pac_en_service:
        m["pac_on"] += 1
    else:
        m["pac_off"] += 1
    m["nb"] += 1
    data["mois"][mois_str] = m

    skill_set("comportement_pac", data, nb + 1)


def skill_sante_hote():
    """Surveille la santé de la machine qui héberge le script.
    RAM, disque, CPU, taille DB, taille logs, latence HA, latence Telegram.
    S'auto-optimise : purge logs, compacte la DB, alerte si problème."""
    import os, resource, shutil

    now = datetime.now()
    problemes = []
    metriques = {}

    # ═══ RAM du process Python ═══
    try:
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        ram_mb = rusage.ru_maxrss / 1024  # Linux KB → MB
        metriques["ram_mb"] = round(ram_mb, 1)
        if ram_mb > 200:
            problemes.append(f"RAM élevée : {ram_mb:.0f} MB")
        if ram_mb > 400:
            problemes.append(f"🚨 RAM critique : {ram_mb:.0f} MB — fuite mémoire probable")
    except Exception:
        pass

    # ═══ Disque ═══
    try:
        usage = shutil.disk_usage("/home")
        disque_pct = usage.used / usage.total * 100
        disque_libre_mb = usage.free / (1024 * 1024)
        metriques["disque_pct"] = round(disque_pct, 1)
        metriques["disque_libre_mb"] = round(disque_libre_mb, 0)
        if disque_libre_mb < 500:
            problemes.append(f"Disque presque plein : {disque_libre_mb:.0f} MB restants")
        if disque_libre_mb < 100:
            problemes.append(f"🚨 Disque critique : {disque_libre_mb:.0f} MB — risque d'arrêt")
    except Exception:
        pass

    # ═══ Taille DB ═══
    try:
        db_size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
        metriques["db_mb"] = round(db_size_mb, 2)
        if db_size_mb > 50:
            problemes.append(f"Base SQLite volumineuse : {db_size_mb:.1f} MB")
            # Auto-optimisation : VACUUM
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("VACUUM")
                conn.close()
                db_size_after = os.path.getsize(DB_PATH) / (1024 * 1024)
                if db_size_after < db_size_mb * 0.9:
                    log.info(f"🧹 DB compactée : {db_size_mb:.1f} → {db_size_after:.1f} MB")
                    metriques["db_mb"] = round(db_size_after, 2)
            except Exception:
                pass
    except Exception:
        pass

    # ═══ Taille logs ═══
    try:
        log_total = 0
        log_dir = os.path.dirname(LOG_PATH)
        for f in os.listdir(log_dir):
            if f.startswith("assistant.log"):
                log_total += os.path.getsize(os.path.join(log_dir, f))
        log_total_mb = log_total / (1024 * 1024)
        metriques["logs_mb"] = round(log_total_mb, 1)
    except Exception:
        pass

    # ═══ Latence HA ═══
    # Ne PAS tester ici — le monitoring principal le fait déjà.
    # Un timeout ponctuel n'est PAS une panne. Seul un échec CONTINU compte.
    try:
        last_mon = _watchdog.get("monitoring_last_run")
        if last_mon:
            age_mon = (now - last_mon).total_seconds() / 60
            metriques["monitoring_age_min"] = round(age_mon, 1)
            if age_mon > 15:
                # Monitoring bloqué depuis 15 min = HA vraiment inaccessible
                problemes.append(f"🚨 HA inaccessible (monitoring bloqué {age_mon:.0f} min)")
    except Exception:
        pass

    # ═══ Threads actifs ═══
    try:
        nb_threads = threading.active_count()
        metriques["threads"] = nb_threads
        if nb_threads < 5:
            problemes.append(f"Threads bas : {nb_threads} (devrait être ~11)")
    except Exception:
        pass

    # ═══ Stocker dans skills ═══
    data, nb = skill_get("sante_hote")
    if not data:
        data = {"historique": [], "alertes": 0}

    data["historique"].append({
        "timestamp": now.isoformat(),
        "metriques": metriques,
        "nb_problemes": len(problemes)
    })
    data["historique"] = data["historique"][-100:]  # Garder 100 derniers points

    # ═══ Alerter si problèmes ═══
    if problemes:
        data["alertes"] = data.get("alertes", 0) + 1
        for p in problemes:
            if "🚨" in p:
                _alerter_si_nouveau(
                    f"hote_{p[:30]}",
                    f"🖥️ SANTÉ HÔTE\n{p}",
                    delai_h=12
                )
            else:
                _alerter_si_nouveau(
                    f"hote_{p[:30]}",
                    f"🖥️ Santé hôte\n⚠️ {p}",
                    delai_h=24
                )

    # ═══ Auto-nettoyage decisions_log (garder 30 jours) ═══
    try:
        trente_jours = (now - timedelta(days=30)).isoformat()
        conn = sqlite3.connect(DB_PATH)
        deleted = conn.execute(
            "DELETE FROM decisions_log WHERE created_at < ?", (trente_jours,)
        ).rowcount
        conn.commit()
        conn.close()
        if deleted > 0:
            log.info(f"🧹 decisions_log : {deleted} entrées anciennes purgées")
    except Exception:
        pass

    # ═══ Auto-nettoyage historique conversations (garder 7 jours) ═══
    try:
        sept_jours = (now - timedelta(days=7)).isoformat()
        conn = sqlite3.connect(DB_PATH)
        deleted = conn.execute(
            "DELETE FROM historique WHERE created_at < ?", (sept_jours,)
        ).rowcount
        conn.commit()
        conn.close()
        if deleted > 0:
            log.info(f"🧹 historique : {deleted} conversations anciennes purgées")
    except Exception:
        pass

    skill_set("sante_hote", data, nb + 1)


def cmd_sante():
    """Affiche la santé de la machine hôte"""
    data, nb = skill_get("sante_hote")
    if not data or not data.get("historique"):
        return "🖥️ Pas encore de données — attendre un cycle monitoring"

    dernier = data["historique"][-1]
    m = dernier.get("metriques", {})

    rapport = f"🖥️ SANTÉ HÔTE ({nb} contrôles)\n━━━━━━━━━━━━━━━━━━\n"
    rapport += f"  RAM         : {m.get('ram_mb', '?')} MB\n"
    rapport += f"  Disque      : {m.get('disque_pct', '?')}% ({m.get('disque_libre_mb', '?')} MB libre)\n"
    rapport += f"  Base SQLite : {m.get('db_mb', '?')} MB\n"
    rapport += f"  Logs        : {m.get('logs_mb', '?')} MB\n"
    rapport += f"  Latence HA  : {m.get('latence_ha_ms', '?')} ms\n"
    rapport += f"  Threads     : {m.get('threads', '?')}\n"
    rapport += f"  Monitoring  : {m.get('monitoring_age_min', '?')} min\n"
    rapport += f"  Alertes     : {data.get('alertes', 0)}\n"

    # Tendance RAM
    hist = data["historique"]
    if len(hist) >= 5:
        ram_values = [h["metriques"].get("ram_mb", 0) for h in hist[-10:] if "ram_mb" in h.get("metriques", {})]
        if len(ram_values) >= 2:
            tendance = ram_values[-1] - ram_values[0]
            if tendance > 10:
                rapport += f"  ⚠️ RAM en hausse : +{tendance:.0f} MB sur {len(ram_values)} cycles\n"
            elif tendance < -5:
                rapport += f"  ✅ RAM stable/baisse\n"

    return rapport


def skill_hote():
    """Surveille la machine hôte du script — RAM, CPU, disque, DB, logs.
    S'auto-optimise : purge logs, vacuum DB, alerte si ressources critiques."""
    import shutil

    now = datetime.now()
    metriques = {}

    # ═══ RAM ═══
    try:
        with open("/proc/meminfo") as f:
            meminfo = {}
            for line in f:
                parts = line.split()
                meminfo[parts[0].rstrip(":")] = int(parts[1])
            total_mb = meminfo.get("MemTotal", 0) / 1024
            dispo_mb = meminfo.get("MemAvailable", 0) / 1024
            used_pct = (1 - dispo_mb / total_mb) * 100 if total_mb > 0 else 0
            metriques["ram_total_mb"] = round(total_mb)
            metriques["ram_dispo_mb"] = round(dispo_mb)
            metriques["ram_pct"] = round(used_pct, 1)
    except Exception:
        pass

    # ═══ CPU (load average 5 min) ═══
    try:
        load1, load5, load15 = os.getloadavg()
        metriques["cpu_load5"] = round(load5, 2)
    except Exception:
        pass

    # ═══ DISQUE ═══
    try:
        usage = shutil.disk_usage("/home")
        metriques["disque_total_gb"] = round(usage.total / (1024**3), 1)
        metriques["disque_libre_gb"] = round(usage.free / (1024**3), 1)
        metriques["disque_pct"] = round(usage.used / usage.total * 100, 1)
    except Exception:
        pass

    # ═══ TAILLE DB ═══
    try:
        db_size_kb = os.path.getsize(DB_PATH) / 1024
        metriques["db_kb"] = round(db_size_kb)
    except Exception:
        pass

    # ═══ TAILLE LOGS ═══
    log_total_kb = 0
    try:
        log_dir = os.path.dirname(LOG_PATH)
        for f in os.listdir(log_dir):
            if f.startswith("assistant.log"):
                log_total_kb += os.path.getsize(os.path.join(log_dir, f)) / 1024
        metriques["logs_kb"] = round(log_total_kb)
    except Exception:
        pass

    # ═══ NB TABLES / LIGNES DB ═══
    try:
        conn = sqlite3.connect(DB_PATH)
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        metriques["db_tables"] = len(tables)
        total_rows = 0
        for (tname,) in tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {tname}").fetchone()[0]
            total_rows += count
        metriques["db_rows"] = total_rows
        conn.close()
    except Exception:
        pass

    # ═══ STOCKER DANS SKILL ═══
    data, nb = skill_get("hote")
    if not data:
        data = {"historique": [], "actions": []}

    data["historique"].append({
        "timestamp": now.isoformat(),
        "metriques": metriques
    })
    data["historique"] = data["historique"][-200:]  # Garder 200 points max
    data["derniere_mesure"] = metriques

    # ═══ AUTO-OPTIMISATION ═══
    actions = []

    # 1. VACUUM DB si > 5 MB
    if metriques.get("db_kb", 0) > 5000:
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("VACUUM")
            conn.close()
            new_size = os.path.getsize(DB_PATH) / 1024
            economie = metriques["db_kb"] - new_size
            if economie > 100:
                actions.append(f"VACUUM DB : {metriques['db_kb']}KB → {new_size:.0f}KB (-{economie:.0f}KB)")
                log.info(f"🧹 VACUUM DB : économie {economie:.0f}KB")
        except Exception:
            pass

    # 2. Purger decisions_log > 30 jours
    try:
        conn = sqlite3.connect(DB_PATH)
        trente_jours = (now - timedelta(days=30)).isoformat()
        deleted = conn.execute(
            "DELETE FROM decisions_log WHERE created_at < ? AND succes != 0", (trente_jours,)
        ).rowcount
        conn.commit()
        conn.close()
        if deleted > 0:
            actions.append(f"Purge decisions_log : {deleted} entrées > 30 jours")
    except Exception:
        pass

    # 3. Purger historique conversations > 7 jours
    try:
        conn = sqlite3.connect(DB_PATH)
        sept_jours = (now - timedelta(days=7)).isoformat()
        deleted = conn.execute(
            "DELETE FROM historique WHERE created_at < ?", (sept_jours,)
        ).rowcount
        conn.commit()
        conn.close()
        if deleted > 0:
            actions.append(f"Purge historique : {deleted} conversations > 7 jours")
    except Exception:
        pass

    # 4. Purger skills dynamiques historique > 500 points
    try:
        conn = sqlite3.connect(DB_PATH)
        dyn_rows = conn.execute(
            "SELECT nom, donnees FROM skills WHERE nom LIKE 'dyn_%'"
        ).fetchall()
        for nom, donnees_json in dyn_rows:
            d = json.loads(donnees_json)
            hist = d.get("historique", [])
            if len(hist) > 200:
                d["historique"] = hist[-200:]
                conn.execute(
                    "UPDATE skills SET donnees=? WHERE nom=?",
                    (json.dumps(d, ensure_ascii=False), nom)
                )
                actions.append(f"Trim {nom} : {len(hist)} → 200 points")
        conn.commit()
        conn.close()
    except Exception:
        pass

    if actions:
        data["actions"] = data.get("actions", []) + [{
            "timestamp": now.isoformat(),
            "actions": actions
        }]
        data["actions"] = data["actions"][-50:]

    skill_set("hote", data, nb + 1)

    # ═══ ALERTES ═══
    ram_pct = metriques.get("ram_pct", 0)
    disque_pct = metriques.get("disque_pct", 0)

    if ram_pct > 90:
        _alerter_si_nouveau(
            "hote_ram_critique",
            f"🖥️ RAM CRITIQUE : {ram_pct:.0f}% utilisée ({metriques.get('ram_dispo_mb', 0)} MB libre)",
            delai_h=6
        )

    if disque_pct > 90:
        _alerter_si_nouveau(
            "hote_disque_critique",
            f"🖥️ DISQUE CRITIQUE : {disque_pct:.0f}% utilisé ({metriques.get('disque_libre_gb', 0)} GB libre)",
            delai_h=12
        )


def cmd_hote():
    """Affiche la santé de la machine hôte"""
    data, nb = skill_get("hote")
    if not data or "derniere_mesure" not in data:
        return "🖥️ Pas encore de données hôte — prochain scan dans 5 min."

    m = data["derniere_mesure"]
    rapport = "🖥️ SANTÉ MACHINE HÔTE\n━━━━━━━━━━━━━━━━━━\n"

    # RAM
    ram_pct = m.get("ram_pct", 0)
    ram_bar = "█" * int(ram_pct / 10) + "░" * (10 - int(ram_pct / 10))
    rapport += f"\n💾 RAM : [{ram_bar}] {ram_pct:.0f}%\n"
    rapport += f"   {m.get('ram_dispo_mb', '?')} MB libre / {m.get('ram_total_mb', '?')} MB\n"

    # CPU
    rapport += f"\n⚡ CPU load (5 min) : {m.get('cpu_load5', '?')}\n"

    # Disque
    disque_pct = m.get("disque_pct", 0)
    disque_bar = "█" * int(disque_pct / 10) + "░" * (10 - int(disque_pct / 10))
    rapport += f"\n💿 Disque : [{disque_bar}] {disque_pct:.0f}%\n"
    rapport += f"   {m.get('disque_libre_gb', '?')} GB libre / {m.get('disque_total_gb', '?')} GB\n"

    # DB
    rapport += f"\n🗄️ Base SQLite : {m.get('db_kb', '?')} KB | {m.get('db_tables', '?')} tables | {m.get('db_rows', '?')} lignes\n"

    # Logs
    rapport += f"📋 Logs : {m.get('logs_kb', '?')} KB\n"

    # Actions d'optimisation
    actions_recentes = data.get("actions", [])
    if actions_recentes:
        derniere = actions_recentes[-1]
        rapport += f"\n🧹 DERNIÈRE OPTIMISATION ({derniere['timestamp'][:16]}) :\n"
        for a in derniere["actions"][:5]:
            rapport += f"  • {a}\n"

    rapport += f"\n📊 {nb} mesures collectées"

    return rapport


def skill_optimisation_tarif(etats):
    """Apprend les patterns de consommation par période tarifaire.
    Objectif : savoir combien on dépense en HP vs HC vs WE, et optimiser."""
    tarif = tarif_get()
    if not tarif or "type" not in tarif:
        return  # Pas de tarif configuré

    index = {e["entity_id"]: e for e in etats}
    now = datetime.now()
    prix_now = tarif_prix_kwh_actuel()

    # Lire consommation actuelle
    conso_w = 0
    eid_conso = role_get("conso_temps_reel")
    if eid_conso:
        e = index.get(eid_conso)
        if e and e["state"] not in ("unavailable", "unknown"):
            try:
                conso_w = float(e["state"])
            except Exception:
                pass

    if conso_w <= 0:
        return

    # Production solaire
    production_w = ha_get_production_solaire_actuelle(etats)

    # Déterminer la période tarifaire actuelle
    ttype = tarif.get("type", "base")
    periode = "base"
    if ttype in ("hphc", "weekend_hphc", "weekend_plus_hphc"):
        hc = _est_heure_creuse_plages(tarif.get("heures_creuses", []))
        we = _est_weekend_ou_ferie() if "weekend" in ttype else False
        jc = _est_jour_choisi(tarif) if "plus" in ttype else False
        if we or jc:
            periode = "weekend_jour"
        elif hc:
            periode = "hc"
        else:
            periode = "hp"
    elif ttype in ("weekend", "weekend_plus"):
        we = _est_weekend_ou_ferie()
        jc = _est_jour_choisi(tarif) if "plus" in ttype else False
        periode = "weekend_jour" if (we or jc) else "semaine"

    # Stocker dans le skill
    data, nb = skill_get("optimisation_tarif")
    if not data:
        data = {"periodes": {}, "mois_en_cours": now.strftime("%Y-%m"), "total_kwh": 0, "total_eur": 0}

    # Reset mensuel
    mois = now.strftime("%Y-%m")
    if data.get("mois_en_cours") != mois:
        # Archiver le mois précédent
        ancien_mois = data.get("mois_en_cours", "?")
        archives = data.get("archives", [])
        archives.append({
            "mois": ancien_mois,
            "periodes": data.get("periodes", {}),
            "total_kwh": data.get("total_kwh", 0),
            "total_eur": data.get("total_eur", 0),
        })
        data["archives"] = archives[-6:]  # Garder 6 mois
        data["periodes"] = {}
        data["total_kwh"] = 0
        data["total_eur"] = 0
        data["mois_en_cours"] = mois

    # Accumuler (toutes les 5 min = 1/12 d'heure)
    kwh_5min = conso_w / 1000 / 12
    eur_5min = kwh_5min * prix_now

    if periode not in data["periodes"]:
        data["periodes"][periode] = {"kwh": 0, "eur": 0, "nb_mesures": 0}

    data["periodes"][periode]["kwh"] = round(data["periodes"][periode]["kwh"] + kwh_5min, 3)
    data["periodes"][periode]["eur"] = round(data["periodes"][periode]["eur"] + eur_5min, 3)
    data["periodes"][periode]["nb_mesures"] += 1
    data["total_kwh"] = round(data.get("total_kwh", 0) + kwh_5min, 3)
    data["total_eur"] = round(data.get("total_eur", 0) + eur_5min, 3)

    # Stocker aussi la production solaire pour calculer l'autoconsommation
    solaire_kwh = production_w / 1000 / 12
    data["solaire_kwh"] = round(data.get("solaire_kwh", 0) + solaire_kwh, 3)

    skill_set("optimisation_tarif", data, nb + 1)


def cmd_tarif_bilan():
    """Bilan mensuel tarification — consommation par période + économies"""
    data, nb = skill_get("optimisation_tarif")
    if not data or not data.get("periodes"):
        return "⚡ Pas encore de données tarif — le skill collecte toutes les 5 min."

    tarif = tarif_get()
    rapport = f"⚡ BILAN TARIF — {data.get('mois_en_cours', '?')}\n━━━━━━━━━━━━━━━━━━\n"
    rapport += f"Fournisseur : {tarif.get('fournisseur', '?')} — {tarif.get('nom', tarif.get('type', '?'))}\n\n"

    periodes = data.get("periodes", {})
    noms = {"hp": "🔴 Heures Pleines", "hc": "🔵 Heures Creuses", "base": "⚪ Base",
            "semaine": "🔴 Semaine", "weekend_jour": "🟢 WE/Jour choisi"}

    total_kwh = 0
    total_eur = 0
    for periode, vals in sorted(periodes.items()):
        nom = noms.get(periode, periode)
        kwh = vals["kwh"]
        eur = vals["eur"]
        total_kwh += kwh
        total_eur += eur
        prix_moy = eur / kwh if kwh > 0 else 0
        rapport += f"{nom}\n  {kwh:.1f} kWh | {eur:.2f}€ | moy {prix_moy:.4f}€/kWh\n"

    rapport += f"\n📊 TOTAL : {total_kwh:.1f} kWh | {total_eur:.2f}€\n"

    # Économie solaire
    solaire_kwh = data.get("solaire_kwh", 0)
    if solaire_kwh > 0:
        prix_moy_global = total_eur / total_kwh if total_kwh > 0 else 0.2
        eco_solaire = round(solaire_kwh * prix_moy_global, 2)
        rapport += f"☀️ Production solaire : {solaire_kwh:.1f} kWh → ~{eco_solaire}€ économisés\n"

    # Recommandation
    if "hp" in periodes and "hc" in periodes:
        pct_hp = periodes["hp"]["kwh"] / total_kwh * 100 if total_kwh > 0 else 0
        if pct_hp > 60:
            rapport += f"\n💡 {pct_hp:.0f}% de votre conso est en HP — décaler les machines en HC pour économiser"

    if "semaine" in periodes and "weekend_jour" in periodes:
        pct_sem = periodes["semaine"]["kwh"] / total_kwh * 100 if total_kwh > 0 else 0
        if pct_sem > 70:
            rapport += f"\n💡 {pct_sem:.0f}% de votre conso est en semaine — décaler les gros usages au WE"

    return rapport


def skill_recommandations_proactives():
    """Force de proposition — analyse les données et recommande des actions pour économiser.
    Appelé toutes les 24h. Le ROI de chaque recommandation est tracé.
    C'est CE skill qui justifie le coût des tokens."""

    if not verifier_budget():
        return

    conn = sqlite3.connect(DB_PATH)

    # ═══ COLLECTER LES DONNÉES POUR L'ANALYSE ═══
    donnees = []

    # 1. Bilan tarif du mois
    data_tarif, nb_tarif = skill_get("optimisation_tarif")
    if data_tarif and data_tarif.get("periodes"):
        periodes = data_tarif["periodes"]
        total_kwh = data_tarif.get("total_kwh", 0)
        total_eur = data_tarif.get("total_eur", 0)
        solaire_kwh = data_tarif.get("solaire_kwh", 0)
        donnees.append(f"BILAN MOIS: {total_kwh:.0f}kWh {total_eur:.1f}€ solaire:{solaire_kwh:.0f}kWh")
        for p, v in periodes.items():
            pct = v["kwh"] / total_kwh * 100 if total_kwh > 0 else 0
            donnees.append(f"  {p}: {v['kwh']:.0f}kWh {v['eur']:.1f}€ ({pct:.0f}%)")

    # 2. Cycles machines
    cycles = conn.execute(
        "SELECT friendly_name, AVG(duree_min), AVG(conso_kwh), AVG(cout_eur), COUNT(*), "
        "AVG(production_solaire_w) FROM cycles_appareils "
        "WHERE fin IS NOT NULL GROUP BY friendly_name"
    ).fetchall()
    if cycles:
        donnees.append("MACHINES:")
        for fname, duree, conso, cout, nb, prod in cycles:
            donnees.append(f"  {fname}: ~{duree:.0f}min ~{conso:.2f}kWh ~{cout:.2f}€ x{nb} solaire:{prod:.0f}W")

    # 3. Tarif
    tarif = tarif_get()
    ttype = tarif.get("type", "base")
    donnees.append(f"CONTRAT: {tarif.get('fournisseur', '?')} {ttype}")
    if ttype in ("hphc", "weekend_hphc", "weekend_plus_hphc"):
        prix_hp = tarif.get("prix_hp", tarif.get("prix_hp_semaine", 0))
        prix_hc = tarif.get("prix_hc", tarif.get("prix_hc_weekend_jour", 0))
        donnees.append(f"  HP:{prix_hp}€ HC:{prix_hc}€ delta:{(prix_hp-prix_hc):.4f}€/kWh")
    if "weekend" in ttype:
        p_sem = tarif.get("prix_semaine", tarif.get("prix_hp_semaine", 0))
        p_we = tarif.get("prix_weekend", tarif.get("prix_hc_weekend_jour", tarif.get("prix_weekend_jour", 0)))
        donnees.append(f"  Semaine:{p_sem}€ WE:{p_we}€")

    # 4. Fenêtre solaire
    data_sol, nb_sol = skill_get("fenetre_solaire")
    if data_sol and nb_sol >= 20:
        jours_fr = ['lun', 'mar', 'mer', 'jeu', 'ven', 'sam', 'dim']
        pics = []
        for j in range(7):
            j_str = str(j)
            if j_str in data_sol:
                best = max(data_sol[j_str].items(), key=lambda x: x[1][0])
                pics.append(f"{jours_fr[j]}:{best[0]}h={int(best[1][0])}W")
        if pics:
            donnees.append(f"SOLAIRE PICS: {' '.join(pics)}")

    # 5. ROI tokens
    mois = datetime.now().strftime("%Y-%m")
    tokens_row = conn.execute(
        "SELECT tokens_in, tokens_out FROM tokens WHERE mois=?", (mois,)
    ).fetchone()
    total_tokens = (tokens_row[0] + tokens_row[1]) if tokens_row else 0
    cout_tokens = round(total_tokens * 0.000001, 2)  # Haiku ~$1/1M tokens
    donnees.append(f"TOKENS MOIS: {total_tokens} (~{cout_tokens}€)")

    conn.close()

    if len(donnees) < 5:
        return  # Pas assez de données

    # ═══ CLAUDE ANALYSE ET RECOMMANDE ═══
    prompt = (
        "Tu es le conseiller énergie de l'utilisateur. Ton rôle : lui faire ÉCONOMISER de l'argent.\n"
        "Tu dois PROUVER que les tokens qu'il paye sont rentables.\n\n"
        "Données de sa maison :\n" + "\n".join(donnees) + "\n\n"
        "RÉPONDS EN JSON STRICT :\n"
        "{\n"
        "  \"recommandations\": [\n"
        "    {\"action\": \"ce qu'il doit faire (concret, 1 phrase)\",\n"
        "     \"economie_mois_eur\": 5.0,\n"
        "     \"difficulte\": \"facile|moyen|avancé\",\n"
        "     \"automatisable\": true}\n"
        "  ],\n"
        "  \"bilan_roi\": \"1 phrase sur tokens dépensés vs économies générées\",\n"
        "  \"score_optimisation\": 65\n"
        "}\n"
        "RÈGLES :\n"
        "- Max 3 recommandations, les plus rentables en premier\n"
        "- Économie en €/mois RÉALISTE (pas optimiste)\n"
        "- Si pas assez de données, dis-le honnêtement\n"
        "- Juste le JSON, rien d'autre"
    )

    try:
        client = anthropic.Anthropic(api_key=CFG["anthropic_api_key"])
        r = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        log_token_usage(r.usage.input_tokens, r.usage.output_tokens)
        texte = r.content[0].text.strip().replace("```json", "").replace("```", "").strip()

        try:
            resultat = json.loads(texte)
        except Exception:
            return

        recos = resultat.get("recommandations", [])
        bilan_roi = resultat.get("bilan_roi", "")
        score_optim = resultat.get("score_optimisation", 0)

        # Stocker les recommandations
        data_reco = {
            "date": datetime.now().isoformat(),
            "recommandations": recos,
            "bilan_roi": bilan_roi,
            "score_optimisation": score_optim,
            "cout_tokens_mois": cout_tokens,
        }
        skill_set("recommandations", data_reco)

        # Calculer économie totale estimée
        eco_totale = sum(r.get("economie_mois_eur", 0) for r in recos)

        # Message Telegram
        msg = f"💰 RECOMMANDATIONS ÉCONOMIES\n━━━━━━━━━━━━━━━━━━\n"
        for i, reco in enumerate(recos[:3], 1):
            diff = reco.get("difficulte", "?")
            eco = reco.get("economie_mois_eur", 0)
            auto = "🤖" if reco.get("automatisable") else "👤"
            msg += f"\n{i}. {reco.get('action', '?')}\n   {auto} {diff} | ~{eco:.0f}€/mois\n"

        msg += f"\n━━━━━━━━━━━━━━━━━━"
        msg += f"\n💰 Économie potentielle : ~{eco_totale:.0f}€/mois"
        msg += f"\n🔑 Coût tokens ce mois : ~{cout_tokens:.2f}€"
        if eco_totale > cout_tokens:
            roi = int(eco_totale / max(cout_tokens, 0.01))
            msg += f"\n📈 ROI : x{roi} (chaque 1€ de tokens → {roi}€ économisés)"
        msg += f"\n🎯 Score optimisation : {score_optim}/100"

        telegram_send(msg)
        log.info(f"💰 Recommandations: {len(recos)}, économie ~{eco_totale:.0f}€/mois, ROI tokens:{cout_tokens:.2f}€")

    except Exception as e:
        log.error(f"❌ recommandations: {e}")


def cmd_roi():
    """Affiche le ROI : tokens dépensés vs économies générées.
    Le ROI est le KPI fondamental. Si ROI > 1 → chaque token est rentable.
    C'est ce chiffre qui justifie le business model."""
    conn = sqlite3.connect(DB_PATH)
    mois = datetime.now().strftime("%Y-%m")

    # Coût tokens
    tokens_row = conn.execute(
        "SELECT tokens_in, tokens_out FROM tokens WHERE mois=?", (mois,)
    ).fetchone()
    total_tokens = (tokens_row[0] + tokens_row[1]) if tokens_row else 0
    cout_tokens = round(total_tokens * 0.000001, 2)  # Haiku ~$1/1M

    # Économies cycles solaire
    cycles_sol = conn.execute(
        "SELECT COUNT(*), SUM(conso_kwh), SUM(cout_eur) FROM cycles_appareils "
        "WHERE production_solaire_w > 500 AND fin IS NOT NULL AND created_at LIKE ?",
        (f"{mois}%",)
    ).fetchall()

    # Dernières recommandations
    data_reco, _ = skill_get("recommandations")
    conn.close()

    # ═══ ÉCONOMIES RÉELLES (table economies) ═══
    eco_data = get_economies_mois(mois)
    eco_reelle = eco_data["total_eur"]
    eco_kwh = eco_data["total_kwh"]
    nb_actions = eco_data["nb_actions"]

    rapport = f"📈 ROI ASSISTANT IA — {mois}\n━━━━━━━━━━━━━━━━━━\n"

    # Coût tokens
    rapport += f"\n🔑 INVESTISSEMENT\n  {total_tokens:,} tokens | {cout_tokens:.2f}€\n"

    # Économies mesurées par type
    rapport += f"\n💰 ÉCONOMIES RÉELLES ({nb_actions} actions)\n"
    for type_eco, info in eco_data.get("par_type", {}).items():
        type_labels = {
            "cycle_solaire": "☀️ Cycles solaire",
            "tarif_optimal": "⚡ Optimisation tarif",
            "surconso_evitee": "📉 Surconso évitée",
            "recommandation_appliquee": "💡 Recommandations",
        }
        label = type_labels.get(type_eco, type_eco)
        rapport += f"  {label} : +{info['eur']:.2f}€ ({info['nb']}x)\n"
    rapport += f"  ━━━\n  Total mesuré : {eco_reelle:.2f}€ | {eco_kwh:.1f} kWh\n"

    # Économies potentielles (recommandations non encore appliquées)
    eco_potentielle = 0
    if data_reco and "recommandations" in data_reco:
        eco_potentielle = sum(r.get("economie_mois_eur", 0) for r in data_reco["recommandations"])
        score = data_reco.get("score_optimisation", 0)
        rapport += f"\n💡 POTENTIEL NON EXPLOITÉ\n"
        for r in data_reco["recommandations"][:3]:
            rapport += f"  • {r.get('action', '?')} → ~{r.get('economie_mois_eur', 0):.0f}€/mois\n"
        rapport += f"  Score optimisation : {score}/100\n"

    # ROI = économies réelles / coût tokens
    rapport += f"\n━━━━━━━━━━━━━━━━━━\n"
    rapport += f"📊 LE CERCLE VERTUEUX\n"
    rapport += f"  Tokens    : {cout_tokens:.2f}€/mois\n"
    rapport += f"  Économies : {eco_reelle:.2f}€ (réel) + ~{eco_potentielle:.0f}€ (potentiel)\n"
    total_eco = eco_reelle + eco_potentielle
    if cout_tokens > 0:
        roi = total_eco / cout_tokens
        rapport += f"  ROI       : x{roi:.1f}\n"
        if roi >= 5:
            rapport += "  ✅ Chaque 1€ de tokens rapporte {:.0f}€ d'économies\n".format(roi)
        elif roi >= 1:
            rapport += "  🟡 Rentable — l'expertise grandit\n"
        else:
            rapport += "  🔴 En construction — les baselines s'accumulent\n"
    else:
        rapport += "  ROI : ∞ (0€ de tokens ce mois)\n"

    rapport += f"\n💡 Plus le script apprend, moins il consomme de tokens,\n   et plus il fait d'économies. C'est le cercle vertueux."
    rapport += f"\n\n💡 Plus l'IA apprend, plus le ROI monte."

    return rapport


def skill_suggestion_machine(etats):
    """Suggère le meilleur moment pour lancer une machine — basé sur la fenêtre solaire.
    Sans panneaux solaires, les rappels programmés fonctionnent mais pas les suggestions solaires."""
    now = datetime.now()
    jour = now.weekday()
    heure = now.hour

    # ═══ VÉRIFIER RAPPEL PROGRAMMÉ ═══
    rappel = mem_get("rappel_machine")
    if rappel:
        try:
            dt_rappel = datetime.fromisoformat(rappel)
            if now >= dt_rappel:
                heure_str = mem_get("rappel_machine_heure", f"{dt_rappel.hour}h{dt_rappel.minute:02d}")
                production_w = ha_get_production_solaire_actuelle(etats)
                mem_set("rappel_machine", "")
                mem_set("rappel_machine_heure", "")

                # Si ECU retourne 0W (glitch capteur), vérifier le skill fenêtre solaire
                if production_w == 0:
                    try:
                        data_sol, nb_sol = skill_get("fenetre_solaire")
                        jour_str = str(now.weekday())
                        heure_rappel = str(now.hour)
                        if data_sol and jour_str in data_sol and heure_rappel in data_sol[jour_str]:
                            prod_attendue = data_sol[jour_str][heure_rappel][0]
                            if prod_attendue > 500:
                                production_w = int(prod_attendue)  # Utiliser la prédiction
                    except Exception:
                        pass

                if production_w > 500:
                    telegram_send(
                        f"⏰ RAPPEL MACHINE — {heure_str}\n"
                        f"☀️ Production solaire : {int(production_w)} W\n"
                        f"C'est le bon moment pour lancer la machine !"
                    )
                else:
                    telegram_send(
                        f"⏰ RAPPEL MACHINE — {heure_str}\n"
                        f"☁️ Production solaire faible : {int(production_w)} W\n"
                        f"Vous pouvez lancer quand même ou attendre une éclaircie."
                    )
                log.info(f"⏰ Rappel machine déclenché : {heure_str}, prod={int(production_w)}W")
        except Exception:
            mem_set("rappel_machine", "")

    # Pas de suggestion si hors créneaux utiles ou pas jour de machine
    if jour not in JOURS_MACHINES:
        return
    if heure < 8 or heure > 16:
        return

    # Vérifier qu'on n'a pas déjà suggéré aujourd'hui
    derniere_suggestion = mem_get("derniere_suggestion_machine")
    if derniere_suggestion:
        try:
            dt = datetime.fromisoformat(derniere_suggestion)
            if (now - dt).total_seconds() < 12 * 3600:
                return
        except Exception:
            pass

    data, nb = skill_get("fenetre_solaire")
    if not data or nb < 20:
        return  # Pas assez d'apprentissage

    jour_str = str(jour)
    if jour_str not in data:
        return

    # Trouver le créneau avec la meilleure production
    meilleur_heure = None
    meilleure_prod = 0
    for h_str, (moy, n) in data[jour_str].items():
        if n >= 3 and moy > meilleure_prod:
            h_int = int(h_str)
            if h_int >= heure and h_int <= 16:  # Créneaux futurs seulement
                meilleure_prod = moy
                meilleur_heure = h_int

    if meilleur_heure is None or meilleure_prod < 500:
        return  # Pas de créneau solaire intéressant

    # Vérifier production actuelle
    production_w = ha_get_production_solaire_actuelle(etats)

    if heure == meilleur_heure and production_w >= meilleure_prod * 0.6:
        # C'est maintenant le meilleur créneau !
        jours_fr = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']

        # Croiser solaire + tarif = économie maximale
        prix_now = tarif_prix_kwh_actuel()
        tarif = tarif_get()
        ttype = tarif.get("type", "base")

        info_tarif = ""
        if ttype in ("weekend", "weekend_hphc", "weekend_plus", "weekend_plus_hphc"):
            if _est_weekend_ou_ferie() or _est_jour_choisi(tarif):
                info_tarif = f"\n💰 Tarif réduit (WE/jour choisi) : {prix_now}€/kWh"
            else:
                info_tarif = f"\n💰 Tarif semaine : {prix_now}€/kWh"
        elif ttype == "hphc":
            hc = _est_heure_creuse_plages(tarif.get("heures_creuses", []))
            info_tarif = f"\n💰 {'HC' if hc else 'HP'} : {prix_now}€/kWh"

        # Estimation économie (cycle type 1.5 kWh, machine ~2000W)
        couv_pct = min(100, int(production_w / 2000 * 100))
        part_reseau = max(0, 100 - couv_pct) / 100
        cout_estime = round(1.5 * prix_now * part_reseau, 2)
        eco_solaire = round(1.5 * prix_now - cout_estime, 2)
        info_eco = f"\n💡 ~{couv_pct}% solaire → ~{cout_estime}€ réseau, ~{eco_solaire}€ économisé"

        telegram_send(
            f"☀️ BON CRÉNEAU MACHINE\n"
            f"Production solaire : {int(production_w)} W\n"
            f"Créneau optimal ({jours_fr[jour]} {meilleur_heure}h) : ~{int(meilleure_prod)} W habituels"
            f"{info_tarif}{info_eco}\n\n"
            f"Répondez l'heure (ex: 12h30) ou ❌"
        )
        mem_set("derniere_suggestion_machine", now.isoformat())
        mem_set("attente_heure_machine", "oui")
        log.info(f"☀️ Suggestion machine : {meilleur_heure}h, {int(meilleure_prod)}W, {prix_now}€/kWh")


def cmd_skills():
    """Affiche l'état des skills appris"""
    rapport = "🧠 SKILLS AUTONOMES\n━━━━━━━━━━━━━━━━━━\n"

    # 1. Fenêtre solaire
    data_sol, nb_sol = skill_get("fenetre_solaire")
    rapport += f"\n☀️ FENÊTRE SOLAIRE ({nb_sol} apprentissages)\n"
    if data_sol and nb_sol >= 10:
        jours_fr = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
        for j in range(7):
            j_str = str(j)
            if j_str in data_sol:
                heures = data_sol[j_str]
                if heures:
                    best_h = max(heures.items(), key=lambda x: x[1][0])
                    rapport += f"  {jours_fr[j]} : pic à {best_h[0]}h → {int(best_h[1][0])} W ({best_h[1][1]} mesures)\n"
    else:
        rapport += "  En cours d'apprentissage...\n"

    # 2. Signatures machines
    data_cyc, nb_cyc = skill_get("cycle_signatures")
    rapport += f"\n🔄 SIGNATURES MACHINES ({nb_cyc} apprentissages)\n"
    if data_cyc:
        for eid, info in data_cyc.items():
            rapport += (
                f"  {info['nom']} : {info['duree_moy']:.0f} min | "
                f"{info['conso_moy']:.2f} kWh | {info['puissance_moy']:.0f} W moy | "
                f"{info['nb_cycles']} cycles\n"
            )
    else:
        rapport += "  Aucun cycle enregistré encore\n"

    # 3. Comportement PAC
    data_pac, nb_pac = skill_get("comportement_pac")
    rapport += f"\n🌡️ COMPORTEMENT PAC ({nb_pac} apprentissages)\n"
    if data_pac and "tranches" in data_pac:
        tranches = data_pac["tranches"]
        for temp in sorted(tranches.keys(), key=lambda x: float(x)):
            t = tranches[temp]
            total = t["pac_on"] + t["pac_off"]
            if total >= 5:
                pct_on = int(t["pac_on"] / total * 100)
                rapport += f"  {temp}°C : PAC ON {pct_on}% | Conso moy {t['conso_moy']:.0f} W ({total} mesures)\n"
    else:
        rapport += "  En cours d'apprentissage...\n"

    if nb_sol < 20:
        rapport += "\n💡 Les skills se construisent au fil des jours.\nSuggestions machine actives après ~1 semaine."

    # 4. Skills dynamiques (créées automatiquement)
    conn = sqlite3.connect(DB_PATH)
    dyn_rows = conn.execute(
        "SELECT nom, donnees, nb_apprentissages FROM skills WHERE nom LIKE 'dyn_%'"
    ).fetchall()
    conn.close()

    if dyn_rows:
        rapport += f"\n🤖 SKILLS DYNAMIQUES ({len(dyn_rows)})\n"
        for nom, donnees_json, nb in dyn_rows:
            try:
                definition = json.loads(donnees_json)
                desc = definition.get("description", nom)
                action = definition.get("action", "?")
                entites = definition.get("entites", [])
                hist_len = len(definition.get("historique", []))
                rapport += f"  {nom} : {desc}\n"
                rapport += f"    Action: {action} | Entités: {len(entites)} | Points: {hist_len}\n"
            except Exception:
                rapport += f"  {nom} : (erreur lecture)\n"
    else:
        rapport += "\n🤖 SKILLS DYNAMIQUES : aucune (se créent automatiquement)\n"

    return rapport


def envoyer_md_par_mail():
    """Envoie le Cahier des Charges par mail en pièce jointe"""
    md_path = os.path.join(os.path.dirname(DB_PATH), "Cahier_des_Charges.md")
    if not os.path.exists(md_path):
        return False
    try:
        with open(md_path, "r") as f:
            contenu = f.read()
        ok = envoyer_email(
            f"[AssistantIA] Cahier des Charges — {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"Mise à jour automatique du Cahier des Charges.\n"
            f"Version actuelle : {len(contenu.split(chr(10)))} lignes, {len(contenu)//1024} KB.\n\n"
            f"Ce fichier contient toutes les consignes pour reprendre le projet.\n"
            f"Collez la section REPRISE dans une nouvelle conversation Claude.",
            piece_jointe=md_path
        )
        if ok:
            log.info("📧 MD envoyé par mail")
        return ok
    except Exception as e:
        log.error(f"❌ Envoi MD mail: {e}")
        return False


def verifier_md_change():
    """Vérifie si le MD a été modifié — si oui, envoie par mail"""
    # global _md_dernier_hash  # via shared
    md_path = os.path.join(os.path.dirname(DB_PATH), "Cahier_des_Charges.md")
    if not os.path.exists(md_path):
        return
    try:
        with open(md_path, "rb") as f:
            h = hashlib.md5(f.read()).hexdigest()
        if _md_dernier_hash is None:
            shared._md_dernier_hash = h  # Premier run — pas d'envoi
            return
        if h != _md_dernier_hash:
            shared._md_dernier_hash = h
            log.info("📄 MD modifié — envoi par mail")
            envoyer_md_par_mail()
    except Exception:
        pass


def cognitif_generer_hypotheses(etats, index):
    """Génère des hypothèses testables à partir des données.
    Une hypothèse = une prédiction vérifiable sur le comportement de la maison."""

    conn = sqlite3.connect(DB_PATH)

    # Pas trop d'hypothèses actives
    nb_actives = conn.execute("SELECT COUNT(*) FROM hypotheses WHERE active=1").fetchone()[0]
    if nb_actives >= 15:
        conn.close()
        return

    now = datetime.now()
    jour = now.weekday()
    heure = now.hour
    jours_fr = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']

    # Charger données pour construire les hypothèses
    baselines = {}
    for eid, label in BASELINE_ENTITIES.items():
        row = conn.execute(
            "SELECT valeur_moyenne, nb_mesures FROM baselines WHERE entity_id=? AND jour_semaine=? AND heure=?",
            (eid, jour, heure)
        ).fetchone()
        if row and row[1] >= 5:
            baselines[label] = row[0]

    # Charger fenêtre solaire
    data_sol, nb_sol = skill_get("fenetre_solaire")

    # Charger PAC
    data_pac, nb_pac = skill_get("comportement_pac")

    hypotheses_candidates = []

    # ═══ HYPOTHÈSES SOLAIRE ═══
    if data_sol and nb_sol >= 20:
        jour_str = str(jour)
        if jour_str in data_sol:
            creneaux = data_sol[jour_str]
            if creneaux:
                best = max(creneaux.items(), key=lambda x: x[1][0])
                best_h = int(best[0])
                best_w = best[1][0]

                # H: "Demain à Xh la production sera >Y W"
                demain = (jour + 1) % 7
                demain_str = str(demain)
                if demain_str in data_sol:
                    creneaux_d = data_sol[demain_str]
                    if creneaux_d:
                        best_d = max(creneaux_d.items(), key=lambda x: x[1][0])
                        hypotheses_candidates.append({
                            "enonce": f"Demain {jours_fr[demain]} à {best_d[0]}h, production solaire > {int(best_d[1][0] * 0.7)}W",
                            "categorie": "solaire",
                            "condition_test": json.dumps({
                                "type": "valeur_min",
                                "entity_id": role_get("production_solaire_w") or "sensor.ecu_current_power",
                                "jour": demain,
                                "heure": int(best_d[0]),
                                "seuil": best_d[1][0] * 0.7
                            })
                        })

    # ═══ HYPOTHÈSES PAC ═══
    if data_pac and nb_pac >= 20:
        temp_ext = None
        e_ext = index.get(role_get("temp_exterieure") or "sensor.ecojoko_temperature_exterieure")
        if e_ext and e_ext["state"] not in ("unavailable", "unknown"):
            try:
                temp_ext = float(e_ext["state"])
            except Exception:
                pass

        if temp_ext is not None:
            tranche = str(round(temp_ext / 2) * 2)
            tranches = data_pac.get("tranches", {})
            if tranche in tranches:
                t = tranches[tranche]
                total = t["pac_on"] + t["pac_off"]
                if total >= 5:
                    pct_on = t["pac_on"] / total
                    if pct_on > 0.7:
                        hypotheses_candidates.append({
                            "enonce": f"Avec {temp_ext:.0f}°C dehors, la PAC devrait être ON ({pct_on:.0%} historique)",
                            "categorie": "pac",
                            "condition_test": json.dumps({
                                "type": "etat_attendu",
                                "entity_pattern": "climate.",
                                "etats_valides": ["auto", "heat", "cool", "fan_only", "heat_cool"],
                                "temp_ext_range": [temp_ext - 2, temp_ext + 2]
                            })
                        })

    # ═══ HYPOTHÈSES CONSOMMATION ═══
    conso_baseline = baselines.get("conso_edf_w")
    if conso_baseline and conso_baseline > 100:
        hypotheses_candidates.append({
            "enonce": f"Consommation EDF {jours_fr[jour]} {heure}h devrait être ~{conso_baseline:.0f}W ±40%",
            "categorie": "energie",
            "condition_test": json.dumps({
                "type": "valeur_range",
                "entity_id": role_get("conso_temps_reel") or "sensor.ecojoko_consommation_temps_reel",
                "min": conso_baseline * 0.6,
                "max": conso_baseline * 1.4,
                "jour": jour,
                "heure": heure
            })
        })

    # Stocker les nouvelles (éviter doublons)
    for h in hypotheses_candidates:
        existing = conn.execute(
            "SELECT id FROM hypotheses WHERE enonce LIKE ? AND active=1",
            (f"%{h['enonce'][:50]}%",)
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO hypotheses (enonce, categorie, condition_test, confiance, active, created_at, updated_at) "
                "VALUES (?, ?, ?, 0.5, 1, ?, ?)",
                (h["enonce"], h["categorie"], h["condition_test"],
                 now.isoformat(), now.isoformat())
            )

    conn.commit()
    conn.close()


def cognitif_tester_hypotheses(etats, index):
    """Teste les hypothèses actives contre la réalité.
    Chaque test renforce ou affaiblit la confiance."""

    conn = sqlite3.connect(DB_PATH)
    now = datetime.now()
    jour = now.weekday()
    heure = now.hour

    hypotheses = conn.execute(
        "SELECT id, enonce, condition_test, confiance, predictions, confirmations, refutations "
        "FROM hypotheses WHERE active=1"
    ).fetchall()

    for h_id, enonce, cond_json, confiance, predictions, confirmations, refutations in hypotheses:
        try:
            cond = json.loads(cond_json)
            cond_type = cond.get("type", "")
            resultat = None  # None = pas testable maintenant, True = confirmé, False = réfuté

            if cond_type == "valeur_min":
                if cond.get("jour") == jour and cond.get("heure") == heure:
                    eid = cond["entity_id"]
                    e = index.get(eid)
                    if e and e["state"] not in ("unavailable", "unknown"):
                        try:
                            val = float(e["state"])
                            resultat = val >= cond["seuil"]
                        except Exception:
                            pass

            elif cond_type == "valeur_range":
                if cond.get("jour") == jour and cond.get("heure") == heure:
                    eid = cond["entity_id"]
                    e = index.get(eid)
                    if e and e["state"] not in ("unavailable", "unknown"):
                        try:
                            val = float(e["state"])
                            resultat = cond["min"] <= val <= cond["max"]
                        except Exception:
                            pass

            elif cond_type == "etat_attendu":
                pattern = cond.get("entity_pattern", "")
                etats_valides = cond.get("etats_valides", [])
                for eid, e in index.items():
                    if pattern in eid:
                        carto = cartographie_get(eid)
                        if carto and "chauffage" in carto[0]:
                            resultat = e["state"] in etats_valides
                            break

            if resultat is not None:
                predictions += 1
                if resultat:
                    confirmations += 1
                    new_conf = min(1.0, confiance + 0.05)
                else:
                    refutations += 1
                    new_conf = max(0.0, confiance - 0.1)

                conn.execute(
                    "UPDATE hypotheses SET predictions=?, confirmations=?, refutations=?, "
                    "confiance=?, updated_at=? WHERE id=?",
                    (predictions, confirmations, refutations, round(new_conf, 3),
                     now.isoformat(), h_id)
                )

                # Désactiver les hypothèses trop faibles
                if new_conf < 0.15 and predictions >= 5:
                    conn.execute("UPDATE hypotheses SET active=0 WHERE id=?", (h_id,))
                    log.info(f"❌ Hypothèse abandonnée: {enonce[:60]}")

                # Promouvoir les hypothèses très fiables en expertise
                if new_conf > 0.85 and predictions >= 10:
                    existing_exp = conn.execute(
                        "SELECT id FROM expertise WHERE insight LIKE ?",
                        (f"%{enonce[:40]}%",)
                    ).fetchone()
                    if not existing_exp:
                        # Cap 50
                        _nb_exp = conn.execute("SELECT COUNT(*) FROM expertise").fetchone()[0]
                        if _nb_exp >= 50:
                            conn.execute(
                                "DELETE FROM expertise WHERE id = ("
                                "SELECT id FROM expertise WHERE source NOT LIKE 'lecon_fondatrice%' "
                                "ORDER BY confiance ASC LIMIT 1)")
                        conn.execute(
                            "INSERT INTO expertise (categorie, insight, confiance, nb_validations, source, created_at, updated_at) "
                            "VALUES (?, ?, ?, ?, 'hypothese_validee', ?, ?)",
                            (cond.get("categorie", "general"),
                             f"VALIDÉ: {enonce}",
                             new_conf, predictions,
                             now.isoformat(), now.isoformat())
                        )
                        log.info(f"★ Hypothèse promue en expertise: {enonce[:60]}")

        except Exception as ex:
            log.error(f"❌ Test hypothèse {h_id}: {ex}")

    conn.commit()
    conn.close()


def cognitif_calculer_score():
    """Calcule le score d'intelligence global — mesure la croissance du système."""
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    # Métriques
    nb_expertise = conn.execute("SELECT COUNT(*) FROM expertise").fetchone()[0]
    nb_hypotheses = conn.execute("SELECT COUNT(*) FROM hypotheses WHERE active=1").fetchone()[0]

    # Taux de prédiction
    hyp_stats = conn.execute(
        "SELECT SUM(predictions), SUM(confirmations) FROM hypotheses WHERE predictions > 0"
    ).fetchone()
    total_pred = hyp_stats[0] or 0
    total_conf = hyp_stats[1] or 0
    taux_prediction = (total_conf / total_pred * 100) if total_pred > 0 else 0

    nb_skills = conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
    nb_baselines = conn.execute("SELECT COUNT(*) FROM baselines").fetchone()[0]

    # Échecs/succès du jour
    today_start = now.replace(hour=0, minute=0, second=0).isoformat()
    nb_echecs = conn.execute(
        "SELECT COUNT(*) FROM decisions_log WHERE succes=0 AND created_at > ?", (today_start,)
    ).fetchone()[0]
    nb_succes = conn.execute(
        "SELECT COUNT(*) FROM decisions_log WHERE succes=1 AND created_at > ?", (today_start,)
    ).fetchone()[0]

    # Estimation économies (basée sur les suggestions machines solaire)
    cycles_solaire = conn.execute(
        "SELECT COUNT(*), SUM(conso_kwh) FROM cycles_appareils "
        "WHERE production_solaire_w > 500 AND fin IS NOT NULL"
    ).fetchone()
    nb_cycles_sol = cycles_solaire[0] or 0
    kwh_solaire = cycles_solaire[1] or 0
    economie = round(kwh_solaire * 0.22, 2)  # ~0.22€/kWh tarif bleu

    # ═══ CALCUL SCORE ═══
    # Score composite : chaque dimension contribue
    score = 0.0

    # Expertise (0-25 pts) : nb de règles × confiance moyenne
    avg_conf = conn.execute("SELECT AVG(confiance) FROM expertise").fetchone()[0] or 0
    score += min(25, nb_expertise * avg_conf * 2)

    # Prédiction (0-25 pts) : taux de prédiction correct
    score += min(25, taux_prediction * 0.25)

    # Couverture (0-25 pts) : baselines + skills
    couverture = min(168 * 5, nb_baselines) / (168 * 5) * 100  # 168 créneaux × 5 entités
    score += min(25, couverture * 0.25)

    # Résilience (0-25 pts) : ratio succès/total
    total_decisions = nb_echecs + nb_succes
    resilience_pts = 0
    if total_decisions > 0:
        resilience = nb_succes / total_decisions * 100
        resilience_pts = min(25, resilience * 0.25)
        score += resilience_pts
    else:
        resilience_pts = 12.5
        score += resilience_pts  # Neutre si pas de données

    score = round(score, 1)

    # Niveau
    if score >= 80:
        niveau = "🏆 EXPERT"
    elif score >= 60:
        niveau = "🥇 AVANCÉ"
    elif score >= 40:
        niveau = "🥈 INTERMÉDIAIRE"
    elif score >= 20:
        niveau = "🥉 DÉBUTANT"
    else:
        niveau = "🌱 INITIAL"

    # Stocker
    conn.execute(
        "INSERT OR REPLACE INTO intelligence_score "
        "(date, score_global, nb_expertise, nb_hypotheses_actives, taux_prediction, "
        "nb_skills, nb_baselines, nb_echecs_jour, nb_succes_jour, economie_estimee, details) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (today, score, nb_expertise, nb_hypotheses, round(taux_prediction, 1),
         nb_skills, nb_baselines, nb_echecs, nb_succes, economie,
         json.dumps({"niveau": niveau, "couverture": round(couverture, 1)}, ensure_ascii=False))
    )
    conn.commit()
    conn.close()

    return {
        "score": score, "niveau": niveau,
        "expertise": nb_expertise, "hypotheses": nb_hypotheses,
        "taux_prediction": taux_prediction, "skills": nb_skills,
        "baselines": nb_baselines, "couverture": couverture,
        "echecs_jour": nb_echecs, "succes_jour": nb_succes,
        "resilience_pts": resilience_pts, "economie": economie
    }


def cmd_intelligence():
    """Tableau de bord complet — score d'intelligence + évolution"""
    metrics = cognitif_calculer_score()

    conn = sqlite3.connect(DB_PATH)

    # Historique des scores
    historique = conn.execute(
        "SELECT date, score_global FROM intelligence_score ORDER BY date DESC LIMIT 7"
    ).fetchall()

    # Hypothèses actives
    hypotheses = conn.execute(
        "SELECT enonce, confiance, predictions, confirmations FROM hypotheses "
        "WHERE active=1 ORDER BY confiance DESC LIMIT 5"
    ).fetchall()

    # Top expertise
    top_exp = conn.execute(
        "SELECT insight, confiance FROM expertise ORDER BY confiance DESC LIMIT 5"
    ).fetchall()

    conn.close()

    s = metrics
    rapport = (
        f"🧠 INTELLIGENCE — {s['niveau']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"\n"
        f"📊 SCORE GLOBAL : {s['score']}/100\n"
        f"\n"
        f"  Expertise    : {s['expertise']} règles → {min(25, s['expertise'] * 0.5):.0f}/25 pts\n"
        f"  Prédiction   : {s['taux_prediction']:.0f}% correct → {min(25, s['taux_prediction'] * 0.25):.0f}/25 pts\n"
        f"  Couverture   : {s['couverture']:.0f}% baselines → {min(25, s['couverture'] * 0.25):.0f}/25 pts\n"
        f"  Résilience   : {s['succes_jour']}✅ {s['echecs_jour']}❌ → {s.get('resilience_pts', 0):.0f}/25 pts\n"
    )

    # Barre de progression
    filled = int(s['score'] / 10)
    bar = "█" * filled + "░" * (10 - filled)
    rapport += f"\n  [{bar}] {s['score']:.0f}%\n"

    # Évolution
    if len(historique) >= 2:
        prev = historique[1][1]
        delta = s['score'] - prev
        arrow = "↗️" if delta > 0 else ("↘️" if delta < 0 else "→")
        rapport += f"\n📈 Évolution : {arrow} {delta:+.1f} pts depuis hier\n"

    if len(historique) >= 2:
        rapport += "\n📅 HISTORIQUE :\n"
        for date, score in historique[:7]:
            bar_h = "█" * int(score / 10) + "░" * (10 - int(score / 10))
            rapport += f"  {date[5:10]} [{bar_h}] {score:.0f}\n"

    # Hypothèses
    if hypotheses:
        rapport += f"\n🔮 HYPOTHÈSES ACTIVES ({s['hypotheses']}) :\n"
        for enonce, conf, pred, confirm in hypotheses:
            taux = f"{confirm}/{pred}" if pred > 0 else "non testée"
            etoiles = "★" * min(5, int(conf * 5))
            rapport += f"  {etoiles} {enonce[:60]}\n    → {taux}\n"

    # Top expertise
    if top_exp:
        rapport += f"\n📚 TOP EXPERTISE :\n"
        for insight, conf in top_exp:
            etoiles = "★" * min(5, int(conf * 5))
            rapport += f"  {etoiles} {insight[:70]}\n"

    # Économies
    if s['economie'] > 0:
        rapport += f"\n💰 ÉCONOMIES ESTIMÉES : {s['economie']:.2f}€ (cycles solaire)\n"

    rapport += f"\n🧠 {s['skills']} skills | {s['baselines']} baselines | {s['hypotheses']} hypothèses"

    return rapport


def apprentissage_log_echec(source, description, contexte=None):
    """Enregistre un échec pour en tirer une leçon"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO decisions_log (action, contexte, resultat, succes, created_at) VALUES (?, ?, ?, 0, ?)",
        (f"ECHEC_{source}", json.dumps(contexte or {}, ensure_ascii=False),
         description, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    log.warning(f"📕 Échec enregistré [{source}]: {description[:100]}")


def apprentissage_log_succes(source, description, contexte=None):
    """Enregistre un succès pour renforcer le pattern"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO decisions_log (action, contexte, resultat, succes, created_at) VALUES (?, ?, ?, 1, ?)",
        (f"SUCCES_{source}", json.dumps(contexte or {}, ensure_ascii=False),
         description, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def apprentissage_tirer_lecons():
    """Analyse les échecs récents et en tire des leçons — appelé toutes les 12h.
    C'est ici que l'IA grandit : elle relit ses échecs et crée des règles pour ne pas les répéter."""

    conn = sqlite3.connect(DB_PATH)

    # Charger les échecs des 7 derniers jours
    sept_jours = (datetime.now() - timedelta(days=7)).isoformat()
    echecs = conn.execute(
        "SELECT action, contexte, resultat, created_at FROM decisions_log "
        "WHERE succes=0 AND created_at > ? ORDER BY created_at DESC LIMIT 20",
        (sept_jours,)
    ).fetchall()

    # Charger les succès récents aussi
    succes = conn.execute(
        "SELECT action, resultat FROM decisions_log "
        "WHERE succes=1 AND created_at > ? ORDER BY created_at DESC LIMIT 20",
        (sept_jours,)
    ).fetchall()

    # Charger l'expertise existante
    expertise = conn.execute(
        "SELECT insight FROM expertise ORDER BY confiance DESC LIMIT 15"
    ).fetchall()

    conn.close()

    if not echecs and not succes:
        return  # Rien à apprendre

    if not verifier_budget():
        return

    # Construire le prompt
    donnees = []
    if echecs:
        donnees.append(f"ÉCHECS RÉCENTS ({len(echecs)}) :")
        for action, ctx, res, date in echecs:
            donnees.append(f"  [{date[:16]}] {action}: {res[:150]}")

    if succes:
        donnees.append(f"\nSUCCÈS RÉCENTS ({len(succes)}) :")
        for action, res in succes[:10]:
            donnees.append(f"  {action}: {res[:100]}")

    if expertise:
        donnees.append("\nEXPERTISE ACTUELLE :")
        for (ins,) in expertise:
            donnees.append(f"  {ins}")

    prompt_system = (
        "Tu es une IA qui apprend de ses erreurs. Tu analyses tes échecs et tes succès "
        "pour en extraire des LEÇONS PERMANENTES.\n\n"
        "OBJECTIF : Chaque leçon est une règle que tu ne violeras plus jamais.\n\n"
        "RÉPONDS EN JSON STRICT :\n"
        "{\n"
        "  \"lecons\": [\n"
        "    {\"categorie\": \"monitoring|alerte|code|energie|zigbee|general\",\n"
        "     \"lecon\": \"la règle à retenir (impératif, max 80 chars)\",\n"
        "     \"source_echec\": \"quel échec a enseigné ça\",\n"
        "     \"confiance\": 0.6}\n"
        "  ],\n"
        "  \"patterns_succes\": [\"ce qui a bien marché à reproduire\"],\n"
        "  \"resume\": \"bilan en 1 phrase\"\n"
        "}\n"
        "Pas de markdown, juste JSON. Si rien à apprendre : {\"lecons\": [], \"patterns_succes\": [], \"resume\": \"RAS\"}"
    )

    try:
        client = anthropic.Anthropic(api_key=CFG["anthropic_api_key"])
        r = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            system=prompt_system,
            messages=[{"role": "user", "content": "\n".join(donnees)}]
        )
        texte = r.content[0].text.strip().replace("```json", "").replace("```", "").strip()
        log_token_usage(r.usage.input_tokens, r.usage.output_tokens)

        try:
            resultat = json.loads(texte)
        except Exception:
            return

        lecons = resultat.get("lecons", [])
        patterns = resultat.get("patterns_succes", [])
        resume = resultat.get("resume", "")

        # Stocker les leçons comme expertise
        conn2 = sqlite3.connect(DB_PATH)
        nouvelles = 0
        for lecon in lecons:
            texte_l = lecon.get("lecon", "")
            cat = lecon.get("categorie", "general")
            conf = lecon.get("confiance", 0.6)
            source = lecon.get("source_echec", "")
            if not texte_l or len(texte_l) < 10:
                continue

            # Chercher un doublon : même catégorie + texte similaire (20 premiers chars)
            existing = conn2.execute(
                "SELECT id, confiance FROM expertise WHERE categorie=? AND insight LIKE ?",
                (cat, f"%{texte_l[:20]}%",)
            ).fetchone()

            if existing:
                new_conf = min(1.0, existing[1] + 0.15)
                conn2.execute(
                    "UPDATE expertise SET confiance=?, nb_validations=nb_validations+1, updated_at=? WHERE id=?",
                    (new_conf, datetime.now().isoformat(), existing[0])
                )
            else:
                # Cap 50 — ne JAMAIS dépasser
                nb_total = conn2.execute("SELECT COUNT(*) FROM expertise").fetchone()[0]
                if nb_total >= 50:
                    conn2.execute(
                        "DELETE FROM expertise WHERE id = ("
                        "SELECT id FROM expertise WHERE source NOT LIKE 'lecon_fondatrice%' "
                        "ORDER BY confiance ASC LIMIT 1)")
                conn2.execute(
                    "INSERT INTO expertise (categorie, insight, confiance, nb_validations, source, created_at, updated_at) "
                    "VALUES (?, ?, ?, 1, ?, ?, ?)",
                    (cat, texte_l, conf, f"echec:{source}", datetime.now().isoformat(), datetime.now().isoformat())
                )
                nouvelles += 1

        conn2.commit()
        conn2.close()

        if nouvelles > 0 or lecons:
            telegram_send(
                f"📕 APPRENTISSAGE\n━━━━━━━━━━━━━━━━━━\n"
                f"{resume}\n\n"
                f"Nouvelles leçons : {nouvelles}\n"
                f"Leçons renforcées : {len(lecons) - nouvelles}\n"
                f"Patterns succès : {len(patterns)}"
            )
            log.info(f"📕 Apprentissage: {nouvelles} nouvelles leçons, {len(lecons)} total")

    except Exception as e:
        log.error(f"❌ apprentissage_tirer_lecons: {e}")


def apprentissage_auto_correction():
    """Vérifie si des problèmes récurrents nécessitent un patch automatique.
    Appelé toutes les 24h. Si un même type d'échec revient > 3 fois, propose un fix."""

    conn = sqlite3.connect(DB_PATH)

    # Compter les types d'échecs récurrents (7 derniers jours)
    sept_jours = (datetime.now() - timedelta(days=7)).isoformat()
    echecs = conn.execute(
        "SELECT action, COUNT(*) as nb FROM decisions_log "
        "WHERE succes=0 AND created_at > ? GROUP BY action HAVING nb >= 3 "
        "ORDER BY nb DESC LIMIT 5",
        (sept_jours,)
    ).fetchall()

    conn.close()

    if not echecs:
        return

    if not verifier_budget():
        return

    for action, nb in echecs:
        log.debug(f"Échec récurrent: {action} ({nb}x/7j)")


def _cycle_intelligence(etats, index, now):
    """Cerveau autonome — tourne toutes les 5 minutes"""
    # global _intelligence_compteur  # via shared
    shared._intelligence_compteur += 1

    # ═══ PHASE 1 : OBSERVER — Prendre un snapshot de l'état complet ═══
    snapshot = _observer(etats, index, now)

    # ═══ PHASE 2 : MÉMORISER — Stocker dans les baselines ═══
    baseline_collecter(etats)

    # ═══ PHASE 3 : APPRENDRE — Alimenter les skills ═══
    skill_fenetre_solaire(etats)
    skill_comportement_pac(etats)
    skill_optimisation_tarif(etats)
    try:
        _tarif_apprendre_plages_hc(etats)
    except Exception:
        pass
    skill_dynamique_collecter(etats)

    # ═══ PHASE 3b : SANTÉ HÔTE — Toutes les 15 min ═══
    if _intelligence_compteur % 3 == 0:
        try:
            skill_sante_hote()
        except Exception as ex_sh:
            log.error(f"❌ sante_hote: {ex_sh}")

    # ═══ PHASE 4 : COMPARER — Détecter anomalies vs mémoire ═══
    anomalies = _comparer(etats, index, now, snapshot)

    # ═══ PHASE 5 : DÉCIDER — Agir selon les anomalies ═══
    _decider(anomalies, etats, index, now)

    # ═══ PHASE 6 : SUGGESTIONS — Proposer des actions (périodique) ═══
    skill_suggestion_machine(etats)

    # ═══ PHASE 7 : AUTO-APPRENTISSAGE — Créer skills si patterns récurrents ═══
    if _intelligence_compteur % 12 == 0:  # Toutes les heures
        _auto_apprendre(etats, index, now)

    # ═══ PHASE 7b : COGNITIF — Hypothèses + Tests ═══
    try:
        cognitif_tester_hypotheses(etats, index)
        if _intelligence_compteur % 12 == 0:  # Toutes les heures
            cognitif_generer_hypotheses(etats, index)
        if _intelligence_compteur % 288 == 0:  # Toutes les 24h
            score_data = cognitif_calculer_score()
            if score_data["score"] > 0:
                log.info(f"🧠 Score intelligence: {score_data['score']}/100 ({score_data['niveau']})")
    except Exception as ex_cog:
        log.error(f"❌ cognitif: {ex_cog}")

    # ═══ PHASE 8 : ANALYSE IA — Claude analyse les données accumulées ═══
    # Toutes les 6h : analyse de corrélation sur les skills/baselines
    if _intelligence_compteur % 72 == 0 and _intelligence_compteur > 0:
        try:
            _analyse_ia_periodique(etats, index, now)
        except Exception as ex_ia:
            log.error(f"❌ analyse_ia: {ex_ia}")
            apprentissage_log_echec("analyse_ia", str(ex_ia))

    # ═══ PHASE 9 : APPRENTISSAGE — Tirer les leçons des échecs ═══
    # Toutes les 12h : relire les échecs, en tirer des règles permanentes
    if _intelligence_compteur % 144 == 0 and _intelligence_compteur > 0:
        try:
            apprentissage_tirer_lecons()
        except Exception as ex_app:
            log.error(f"❌ apprentissage: {ex_app}")

    # ═══ PHASE 9b : FILTRE APPRENANT — Analyser les messages envoyés/filtrés ═══
    if _intelligence_compteur % 144 == 0 and _intelligence_compteur > 0:
        try:
            filtre_analyser_messages()
        except Exception as ex_fa:
            log.error(f"❌ filtre_analyser: {ex_fa}")

    # ═══ PHASE 10 : AUTO-CONTRÔLE — Détecter les problèmes récurrents ═══
    # Toutes les 24h : vérifier si des échecs se répètent
    if _intelligence_compteur % 288 == 0 and _intelligence_compteur > 0:
        try:
            apprentissage_auto_correction()
        except Exception as ex_ctrl:
            log.error(f"❌ auto_correction: {ex_ctrl}")

    # ═══ PHASE 11 : RECOMMANDATIONS — Force de proposition pour économiser ═══
    # Toutes les 24h (décalé de 6h par rapport à phase 10)
    if _intelligence_compteur % 288 == 72 and _intelligence_compteur > 72:
        try:
            skill_recommandations_proactives()
        except Exception as ex_reco:
            log.error(f"❌ recommandations: {ex_reco}")

    # Log discret
    if _intelligence_compteur % 60 == 0:  # Toutes les 5h
        nb_skills = 0
        try:
            conn = sqlite3.connect(DB_PATH)
            nb_skills = conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
            nb_baselines = conn.execute("SELECT COUNT(*) FROM baselines").fetchone()[0]
            conn.close()
        except Exception:
            pass
        log.info(f"🧠 Intelligence: cycle #{_intelligence_compteur} | {nb_skills} skills | {nb_baselines} baselines")


def _observer(etats, index, now):
    """Phase 1 : Capture un snapshot structuré de l'état de la maison"""
    snapshot = {
        "timestamp": now.isoformat(),
        "nb_entites": len(etats),
        "nb_unavailable": sum(1 for e in etats if e["state"] in ("unavailable", "unknown")),
    }

    # Production solaire
    try:
        snapshot["production_w"] = ha_get_production_solaire_actuelle(etats)
    except Exception:
        snapshot["production_w"] = 0

    # Consommation EDF
    e_eco = index.get(role_get("conso_temps_reel") or "sensor.ecojoko_consommation_temps_reel")
    if e_eco and e_eco["state"] not in ("unavailable", "unknown"):
        try:
            snapshot["conso_edf_w"] = float(e_eco["state"])
        except Exception:
            pass

    # Températures
    for eid, key in [
        (role_get("temp_interieure") or "sensor.ecojoko_temperature_interieure", "temp_int"),
        (role_get("temp_exterieure") or "sensor.ecojoko_temperature_exterieure", "temp_ext"),
    ]:
        e = index.get(eid)
        if e and e["state"] not in ("unavailable", "unknown"):
            try:
                snapshot[key] = float(e["state"])
            except Exception:
                pass

    # PAC
    for e in etats:
        if e["entity_id"].startswith("climate."):
            carto = cartographie_get(e["entity_id"])
            if carto and "chauffage" in carto[0]:
                snapshot["pac_state"] = e["state"]
                snapshot["pac_on"] = e["state"] in ("auto", "heat", "cool", "fan_only", "heat_cool")
                break

    # Prises actives
    snapshot["prises_actives"] = sum(1 for eid, etat in _etat_prises.items() if etat == "actif")

    # Sauvegarder snapshot en mémoire pour l'historique
    mem_set("dernier_snapshot", json.dumps(snapshot))

    return snapshot


def _comparer(etats, index, now, snapshot):
    """Phase 4 : Compare l'état actuel avec la mémoire et les baselines"""
    anomalies = []

    # Anomalies baselines
    baseline_detecter_anomalies(etats)

    # Anomalie : nombre d'entités unavailable anormalement élevé
    pct_ko = snapshot["nb_unavailable"] / max(snapshot["nb_entites"], 1) * 100
    if pct_ko > 30:
        anomalies.append({
            "type": "entites_ko",
            "message": f"{snapshot['nb_unavailable']}/{snapshot['nb_entites']} entités hors ligne ({pct_ko:.0f}%)",
            "severite": "haute" if pct_ko > 50 else "moyenne",
        })

    # Anomalie : production solaire nulle en plein jour
    # Vérifier que c'est VRAIMENT 0 (pas un glitch capteur)
    if ha_est_jour(etats) and snapshot.get("production_w", 0) == 0:
        heure = now.hour
        if 9 <= heure <= 16:
            # Vérifier le snapshot précédent — si déjà 0W au cycle précédent, c'est confirmé
            prev_zero = False
            try:
                prev_json = mem_get("snapshot_precedent")
                if prev_json:
                    prev = json.loads(prev_json)
                    if prev.get("production_w", 0) == 0:
                        prev_zero = True
            except Exception:
                pass
            if prev_zero:
                anomalies.append({
                    "type": "solaire_zero",
                    "message": f"Production solaire 0W confirmé en plein jour ({heure}h) — 2 cycles consécutifs",
                    "severite": "haute",
                })

    # Anomalie : consommation EDF anormalement haute
    conso = snapshot.get("conso_edf_w", 0)
    if conso > 8000:
        anomalies.append({
            "type": "conso_extreme",
            "message": f"Consommation EDF très élevée : {int(conso)}W",
            "severite": "haute",
        })

    # Anomalie : température intérieure en chute
    temp_int = snapshot.get("temp_int")
    if temp_int is not None and temp_int < 16:
        anomalies.append({
            "type": "temp_basse",
            "message": f"Température intérieure basse : {temp_int}°C",
            "severite": "haute" if temp_int < 14 else "moyenne",
        })

    # PAC : on n'alerte PAS ici — le thermostat fait du on/off naturellement
    # La surveillance PAC est gérée par _surveiller_pac_correlee qui vérifie
    # la temp intérieure sur la durée, pas un snapshot ponctuel

    # Comparer avec le snapshot précédent
    # PAS de détection "chute brutale" solaire — le capteur ECU glitche à 0W
    # entre deux mises à jour (toutes les 5 min). Un 0W ponctuel n'est PAS une chute.
    # La détection "solaire_zero" sur 2 cycles consécutifs suffit.

    # Sauvegarder pour le prochain cycle
    mem_set("snapshot_precedent", json.dumps(snapshot))

    return anomalies


def _decider(anomalies, etats, index, now):
    """Phase 5 : Agit sur les anomalies détectées"""
    for anomalie in anomalies:
        severite = anomalie.get("severite", "moyenne")
        msg = anomalie["message"]
        atype = anomalie["type"]

        if severite == "haute":
            _alerter_si_nouveau(
                f"ia_{atype}",
                f"🧠 ALERTE INTELLIGENCE\n🚨 {msg}",
                delai_h=2
            )
        elif severite == "moyenne":
            _alerter_si_nouveau(
                f"ia_{atype}",
                f"🧠 INTELLIGENCE\n⚠️ {msg}",
                delai_h=6
            )


def _auto_apprendre(etats, index, now):
    """Phase 7 : Analyse les patterns récurrents et crée de nouvelles compétences"""
    conn = sqlite3.connect(DB_PATH)

    # Vérifier si des entités importantes ne sont PAS suivies par les baselines
    # Chercher des entités énergie avec beaucoup de variations
    categories_energie = ["energie_solaire", "energie_conso", "energie_chauffage",
                          "prise_connectee", "energie_batterie", "energie_production"]

    entites_suivies = set(BASELINE_ENTITIES.keys())
    nb_dyn = conn.execute("SELECT COUNT(*) FROM skills WHERE nom LIKE 'dyn_%'").fetchone()[0]

    if nb_dyn >= 10:
        conn.close()
        return  # Déjà au max

    for cat in categories_energie:
        entites_cat = cartographie_get_par_categorie(cat)
        for eid, sc, pc in entites_cat:
            if eid in entites_suivies:
                continue
            if not eid.startswith("sensor."):
                continue

            e = index.get(eid)
            if not e or e["state"] in ("unavailable", "unknown"):
                continue

            unite = e.get("attributes", {}).get("unit_of_measurement", "")
            if unite not in ("W", "kWh", "°C", "%"):
                continue

            # Vérifier si un skill dynamique existe déjà pour cette entité
            existing = conn.execute(
                "SELECT nom FROM skills WHERE nom LIKE 'dyn_%' AND donnees LIKE ?",
                (f"%{eid}%",)
            ).fetchone()
            if existing:
                continue

            # Créer automatiquement un skill de collecte
            fname = e.get("attributes", {}).get("friendly_name", eid)
            definition = {
                "description": f"Suivi auto {fname} ({unite})",
                "entites": [eid],
                "action": "collecter",
                "seuil": None,
                "cree_le": now.isoformat(),
                "cree_par": "auto_apprendre",
                "historique": []
            }
            nom = f"dyn_auto_{eid.split('.')[1][:30]}"
            skill_set(nom, definition, 0)
            log.info(f"🧠 Auto-apprentissage : {nom} — {fname}")

            nb_dyn += 1
            if nb_dyn >= 10:
                break
        if nb_dyn >= 10:
            break

    conn.close()


def _analyse_ia_periodique(etats, index, now):
    """Phase 8 : Claude analyse les données accumulées et produit des insights.
    C'est ici que l'IA apporte sa vraie valeur — corrélation, prédiction, optimisation.
    Un humain ne peut pas faire ça gratuitement."""

    if not verifier_budget():
        return  # Pas de tokens → pas d'analyse

    conn = sqlite3.connect(DB_PATH)

    # ═══ COLLECTER TOUTES LES DONNÉES ACCUMULÉES ═══
    donnees_ia = []

    # 1. Baselines : patterns par jour/heure
    baselines_resume = {}
    rows = conn.execute(
        "SELECT entity_id, jour_semaine, heure, valeur_moyenne, nb_mesures FROM baselines WHERE nb_mesures >= 5 ORDER BY entity_id, jour_semaine, heure"
    ).fetchall()
    for eid, jour, heure, moy, nb in rows:
        label = BASELINE_ENTITIES.get(eid, eid)
        if label not in baselines_resume:
            baselines_resume[label] = {}
        jours_fr = ['lun', 'mar', 'mer', 'jeu', 'ven', 'sam', 'dim']
        cle = f"{jours_fr[jour]}_{heure}h"
        baselines_resume[label][cle] = round(moy, 1)

    if baselines_resume:
        donnees_ia.append("BASELINES COMPORTEMENTALES (moyennes par créneau) :")
        for label, creneaux in baselines_resume.items():
            # Résumé : min, max, créneau pic
            vals = list(creneaux.values())
            if vals:
                pic_creneau = max(creneaux.items(), key=lambda x: x[1])
                creux_creneau = min(creneaux.items(), key=lambda x: x[1])
                donnees_ia.append(
                    f"  {label}: pic={pic_creneau[0]}→{pic_creneau[1]} | "
                    f"creux={creux_creneau[0]}→{creux_creneau[1]} | "
                    f"moyenne={sum(vals)/len(vals):.0f} ({len(creneaux)} créneaux)"
                )

    # 2. Skills : ce que l'IA a appris
    skills_rows = conn.execute("SELECT nom, donnees, nb_apprentissages FROM skills").fetchall()
    for nom, donnees_json, nb in skills_rows:
        try:
            data = json.loads(donnees_json)
            if nom == "fenetre_solaire" and nb >= 10:
                jours_fr = ['lun', 'mar', 'mer', 'jeu', 'ven', 'sam', 'dim']
                pics = []
                for j in range(7):
                    j_str = str(j)
                    if j_str in data:
                        best = max(data[j_str].items(), key=lambda x: x[1][0])
                        pics.append(f"{jours_fr[j]} {best[0]}h={int(best[1][0])}W")
                if pics:
                    donnees_ia.append(f"SKILL FENÊTRE SOLAIRE ({nb} apprentissages) : " + " | ".join(pics))

            elif nom == "cycle_signatures" and data:
                for eid, info in data.items():
                    donnees_ia.append(
                        f"SKILL MACHINE {info['nom']}: {info['duree_moy']:.0f}min, "
                        f"{info['conso_moy']:.2f}kWh, {info['puissance_moy']:.0f}W, "
                        f"{info['nb_cycles']} cycles"
                    )

            elif nom == "comportement_pac" and nb >= 10:
                tranches = data.get("tranches", {})
                resume_pac = []
                for temp in sorted(tranches.keys(), key=lambda x: float(x)):
                    t = tranches[temp]
                    total = t["pac_on"] + t["pac_off"]
                    if total >= 5:
                        pct = int(t["pac_on"] / total * 100)
                        resume_pac.append(f"{temp}°C→PAC:{pct}%on/{t['conso_moy']:.0f}W")
                if resume_pac:
                    donnees_ia.append(f"SKILL PAC ({nb} obs) : " + " | ".join(resume_pac))

            elif nom.startswith("dyn_") and "historique" in data and len(data["historique"]) >= 5:
                desc = data.get("description", nom)
                hist = data["historique"]
                vals_num = []
                for h in hist[-20:]:
                    v = h.get("valeurs", {})
                    for val in v.values():
                        if isinstance(val, (int, float)):
                            vals_num.append(val)
                if vals_num:
                    donnees_ia.append(
                        f"SKILL DYN {desc}: moy={sum(vals_num)/len(vals_num):.1f} "
                        f"min={min(vals_num):.1f} max={max(vals_num):.1f} ({len(hist)} points)"
                    )
        except Exception:
            pass

    # 3. Derniers cycles machines
    cycles = conn.execute(
        "SELECT friendly_name, debut, duree_min, conso_kwh, cout_eur, production_solaire_w "
        "FROM cycles_appareils WHERE fin IS NOT NULL ORDER BY created_at DESC LIMIT 10"
    ).fetchall()
    if cycles:
        donnees_ia.append("HISTORIQUE CYCLES (10 derniers) :")
        total_kwh = 0
        total_cout = 0
        for fname, debut, duree, conso, cout, prod in cycles:
            date = debut[:10] if debut else "?"
            solaire = f" | solaire:{prod}W" if prod else ""
            donnees_ia.append(f"  {fname} {date} {duree}min {conso:.2f}kWh {cout:.2f}€{solaire}")
            total_kwh += conso or 0
            total_cout += cout or 0
        donnees_ia.append(f"  TOTAL: {total_kwh:.2f}kWh | {total_cout:.2f}€")

    # 4. État actuel
    snapshot_json = mem_get("dernier_snapshot", "{}")
    try:
        snapshot = json.loads(snapshot_json)
        donnees_ia.append(f"SNAPSHOT ACTUEL: prod={snapshot.get('production_w', 0)}W | "
                         f"conso_edf={snapshot.get('conso_edf_w', 0)}W | "
                         f"temp_int={snapshot.get('temp_int', '?')}°C | "
                         f"temp_ext={snapshot.get('temp_ext', '?')}°C | "
                         f"PAC={'ON' if snapshot.get('pac_on') else 'OFF'} | "
                         f"machines_actives={snapshot.get('prises_actives', 0)}")
    except Exception:
        pass

    conn.close()

    if len(donnees_ia) < 3:
        return  # Pas assez de données pour une analyse pertinente

    # ═══ CHARGER L'EXPERTISE ACCUMULÉE ═══
    expertise_existante = []
    try:
        rows_exp = conn.execute(
            "SELECT categorie, insight, confiance, nb_validations FROM expertise "
            "ORDER BY confiance DESC LIMIT 20"
        ).fetchall()
        for cat, insight, conf, nb_val in rows_exp:
            etoiles = "★" * min(5, int(conf * 5))
            expertise_existante.append(f"[{cat}] {etoiles} ({nb_val} valid.) : {insight}")
    except Exception:
        pass

    conn.close()

    if len(donnees_ia) < 3:
        return

    # ═══ DEMANDER À CLAUDE D'ANALYSER ET CAPITALISER ═══
    prompt_system = (
        "Tu es le LEAD expert domotique et énergie de l'utilisateur. "
        "Tu accumules de l'expertise à chaque analyse — chaque token dépensé te rend plus intelligent.\n\n"
        "Tu as accès à :\n"
        "1. Les données brutes de la maison (baselines, skills, cycles, snapshot)\n"
        "2. Ton expertise ACCUMULÉE des analyses précédentes\n\n"
        "TON RÔLE :\n"
        "- CORRÉLER : trouver des liens invisibles entre les données\n"
        "- PRÉDIRE : anticiper les problèmes et les opportunités\n"
        "- OPTIMISER : proposer des actions concrètes pour économiser\n"
        "- CAPITALISER : extraire des règles réutilisables\n\n"
        "RÉPONDS EN JSON STRICT :\n"
        "{\n"
        "  \"analyse\": \"ton analyse concise (max 400 chars)\",\n"
        "  \"insights\": [\n"
        "    {\"categorie\": \"energie|pac|solaire|machine|zigbee|general\",\n"
        "     \"insight\": \"la règle/corrélation apprise (max 100 chars)\",\n"
        "     \"confiance\": 0.5}\n"
        "  ],\n"
        "  \"actions_recommandees\": [\"action 1\", \"action 2\"],\n"
        "  \"expertise_obsolete\": [\"insight périmé à retirer si trouvé\"]\n"
        "}\n"
        "Pas de markdown, pas de ```, juste le JSON.\n"
        "Si pas assez de données : {\"analyse\": \"Données insuffisantes\", \"insights\": [], \"actions_recommandees\": [], \"expertise_obsolete\": []}"
    )

    prompt_user = "DONNÉES ACCUMULÉES :\n" + "\n".join(donnees_ia)
    if expertise_existante:
        prompt_user += "\n\nTON EXPERTISE ACCUMULÉE (construis dessus, ne répète pas) :\n" + "\n".join(expertise_existante)

    try:
        client = anthropic.Anthropic(api_key=CFG["anthropic_api_key"])
        r = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1200,
            system=prompt_system,
            messages=[{"role": "user", "content": prompt_user}]
        )
        texte = r.content[0].text.strip().replace("```json", "").replace("```", "").strip()
        log_token_usage(r.usage.input_tokens, r.usage.output_tokens)

        # Parser la réponse
        try:
            resultat = json.loads(texte)
        except Exception:
            resultat = {"analyse": texte[:400], "insights": [], "actions_recommandees": [], "expertise_obsolete": []}

        analyse = resultat.get("analyse", "")
        insights = resultat.get("insights", [])
        actions = resultat.get("actions_recommandees", [])
        obsoletes = resultat.get("expertise_obsolete", [])

        # ═══ CAPITALISER — Stocker les nouveaux insights ═══
        conn2 = sqlite3.connect(DB_PATH)
        for ins in insights:
            cat = ins.get("categorie", "general")
            texte_ins = ins.get("insight", "")
            conf = ins.get("confiance", 0.5)
            if not texte_ins or len(texte_ins) < 10:
                continue

            # Vérifier si un insight similaire existe déjà (catégorie + 20 premiers chars)
            existing = conn2.execute(
                "SELECT id, confiance, nb_validations FROM expertise WHERE categorie=? AND insight LIKE ?",
                (cat, f"%{texte_ins[:20]}%",)
            ).fetchone()

            if existing:
                new_conf = min(1.0, existing[1] + 0.1)
                conn2.execute(
                    "UPDATE expertise SET confiance=?, nb_validations=nb_validations+1, updated_at=? WHERE id=?",
                    (new_conf, now.isoformat(), existing[0])
                )
            else:
                # Vérifier le total — NE PAS dépasser 50 règles
                nb_total = conn2.execute("SELECT COUNT(*) FROM expertise").fetchone()[0]
                if nb_total >= 50:
                    # Supprimer la plus faible non-fondatrice
                    conn2.execute(
                        "DELETE FROM expertise WHERE id = ("
                        "SELECT id FROM expertise WHERE source NOT LIKE 'lecon_fondatrice%' "
                        "ORDER BY confiance ASC LIMIT 1)"
                    )
                conn2.execute(
                    "INSERT INTO expertise (categorie, insight, confiance, nb_validations, source, created_at, updated_at) "
                    "VALUES (?, ?, ?, 1, 'analyse_auto', ?, ?)",
                    (cat, texte_ins, conf, now.isoformat(), now.isoformat())
                )
                log.info(f"🧠 Nouvel insight: [{cat}] {texte_ins[:60]}...")

        # Retirer l'expertise obsolète
        for obs in obsoletes:
            if obs and len(obs) > 10:
                conn2.execute(
                    "DELETE FROM expertise WHERE insight LIKE ? AND confiance < 0.5",
                    (f"%{obs[:50]}%",)
                )

        # Logger la décision
        conn2.execute(
            "INSERT INTO decisions_log (action, contexte, resultat, created_at) VALUES (?, ?, ?, ?)",
            ("analyse_periodique", json.dumps({"nb_donnees": len(donnees_ia)}, ensure_ascii=False),
             json.dumps({"nb_insights": len(insights), "nb_actions": len(actions)}, ensure_ascii=False),
             now.isoformat())
        )

        conn2.commit()
        conn2.close()

        # Stocker l'analyse
        mem_set("derniere_analyse_ia", analyse)
        mem_set("derniere_analyse_ia_date", now.isoformat())

        # Construire le message Telegram — LISIBLE, pas de JSON
        # Nettoyer l'analyse : supprimer tout JSON résiduel
        analyse_clean = analyse
        if "{" in analyse_clean or '"analyse"' in analyse_clean:
            # Essai 1 : parser comme JSON complet
            try:
                parsed = json.loads(analyse_clean)
                if isinstance(parsed, dict) and "analyse" in parsed:
                    analyse_clean = parsed["analyse"]
            except Exception:
                # Essai 2 : extraire le champ "analyse" par regex (JSON tronqué)
                import re
                m = re.search(r'"analyse"\s*:\s*"((?:[^"\\]|\\.)*)"', analyse_clean)
                if m:
                    analyse_clean = m.group(1).replace('\\"', '"').replace('\\n', ' ')
                else:
                    # Essai 3 : supprimer tout ce qui ressemble à du JSON
                    analyse_clean = re.sub(r'[{\[\]}":]', '', analyse_clean)
                    analyse_clean = re.sub(r'\s+', ' ', analyse_clean).strip()[:500]

        msg = f"🧠 ANALYSE INTELLIGENCE\n{now.strftime('%d/%m %H:%M')}\n━━━━━━━━━━━━━━━━━━\n{analyse_clean}"
        if actions:
            msg += "\n\n💡 RECOMMANDATIONS :\n" + "\n".join(f"  • {a}" for a in actions[:3])
        nb_exp = 0
        try:
            conn3 = sqlite3.connect(DB_PATH)
            nb_exp = conn3.execute("SELECT COUNT(*) FROM expertise").fetchone()[0]
            conn3.close()
        except Exception:
            pass
        msg += f"\n\n📚 Expertise : {nb_exp} règles apprises"

        telegram_send(msg)
        log.info(f"🧠 Analyse IA: {len(insights)} insights, {len(actions)} actions ({r.usage.input_tokens}+{r.usage.output_tokens} tokens)")

    except Exception as e:
        log.error(f"❌ analyse_ia: {e}")


def tarif_cout_cycle(conso_kwh, duree_min, debut_iso=None):
    """Calcule le coût d'un cycle complet, en tenant compte HP/HC si le cycle chevauche"""
    tarif = tarif_get()

    if tarif.get("type") == "base":
        prix = tarif.get("prix_kwh", 0.2516)
        return {
            "cout_total": round(conso_kwh * prix, 3),
            "detail": f"{prix}€/kWh (base)",
            "prix_moyen_kwh": prix
        }

    if tarif.get("type") == "hphc":
        # Approximation : prix moyen pondéré sur la durée du cycle
        # Pour être précis il faudrait intégrer minute par minute
        # Simplification : prix au moment du début + prix au moment de la fin / 2
        prix_debut = tarif_prix_kwh_actuel()
        if debut_iso:
            try:
                debut_dt = datetime.fromisoformat(debut_iso)
                h_debut = debut_dt.hour * 60 + debut_dt.minute
                # Vérifier si le début était en HC
                heures_creuses = tarif.get("heures_creuses", [])
                debut_hc = False
                for plage in heures_creuses:
                    d_str, f_str = plage.split("-")
                    dh, dm = map(int, d_str.split(":"))
                    fh, fm = map(int, f_str.split(":"))
                    d_min, f_min = dh * 60 + dm, fh * 60 + fm
                    if d_min > f_min:
                        if h_debut >= d_min or h_debut < f_min:
                            debut_hc = True
                    else:
                        if d_min <= h_debut < f_min:
                            debut_hc = True
                prix_debut = tarif.get("prix_hc" if debut_hc else "prix_hp", 0.25)
            except Exception:
                pass

        prix_fin = tarif_prix_kwh_actuel()
        prix_moyen = (prix_debut + prix_fin) / 2
        cout = round(conso_kwh * prix_moyen, 3)
        detail_hp = f"HP:{tarif.get('prix_hp')}€" if not tarif_est_heure_creuse() else ""
        detail_hc = f"HC:{tarif.get('prix_hc')}€" if tarif_est_heure_creuse() else ""
        return {
            "cout_total": cout,
            "detail": f"{prix_moyen:.4f}€/kWh ({detail_hp or detail_hc})",
            "prix_moyen_kwh": prix_moyen
        }

    return {"cout_total": round(conso_kwh * 0.2516, 3), "detail": "défaut", "prix_moyen_kwh": 0.2516}


def _tarif_detecter_heures_creuses():
    """Détecte automatiquement les heures creuses dans HA.
    Supporte : Lixee ZLinky, LinkYTIC, ESPHome TIC, HA-Linky, Ecojoko, tout capteur HC.
    Si les plages ne sont pas trouvables directement, active l'auto-apprentissage."""
    etats = ha_get("states")
    if not etats:
        return None

    hc_confirmee = False  # Le contrat est HP/HC (pas base)
    ptec_entity = None    # Entité période tarifaire en cours

    for e in etats:
        eid = e["entity_id"]
        eid_low = eid.lower()
        attrs = e.get("attributes", {})
        etat = e["state"]

        # ═══ 1. Attribut direct avec plages horaires ═══
        for k, v in attrs.items():
            k_low = str(k).lower()
            if any(kw in k_low for kw in ["heure_creuse", "off_peak", "offpeak_hours",
                                           "hc_hours", "heures_creuses_ranges"]):
                if isinstance(v, str) and "-" in v:
                    return [p.strip() for p in v.split(",") if "-" in p]
                if isinstance(v, list):
                    return v

        # ═══ 2. Lixee ZLinky / LinkYTIC / ESPHome — PTEC ═══
        # PTEC = "HC.." (heures creuses) ou "HP.." (heures pleines)
        if any(kw in eid_low for kw in ["ptec", "tarif_actuel", "periode_tarifaire",
                                         "current_tariff", "tariff_index"]):
            ptec_entity = eid
            if "hc" in etat.lower():
                hc_confirmee = True

        # ═══ 3. Index HCHC / HCHP (confirme abonnement HC) ═══
        if any(kw in eid_low for kw in ["hchc", "hchp", "index_hc", "index_hp",
                                         "consommation_hc", "consommation_hp",
                                         "off_peak_hours_index", "peak_hours_index"]):
            hc_confirmee = True

        # ═══ 4. Ecojoko — consommation HC/HP réseau ═══
        if "ecojoko" in eid_low and ("_hc_" in eid_low or "_hp_" in eid_low):
            hc_confirmee = True

        # ═══ 5. Attribut Linky / ZLinky avec plages dans les attributs ═══
        if any(kw in eid_low for kw in ["linky", "zlinky", "lixee", "teleinfo"]):
            for k, v in attrs.items():
                v_str = str(v)
                if ":" in v_str and "-" in v_str and any(h in v_str for h in ["22:", "23:", "06:", "07:"]):
                    plages = [p.strip() for p in v_str.split(",") if ":" in p and "-" in p]
                    if plages:
                        return plages

    # ═══ 6. Si HC confirmée mais plages pas trouvées → auto-apprentissage ═══
    if hc_confirmee:
        # Sauvegarder les infos pour l'apprentissage
        mem_set("tarif_hc_confirmee", "oui")
        if ptec_entity:
            mem_set("tarif_ptec_entity", ptec_entity)
            # Lancer l'apprentissage des plages HC
            mem_set("tarif_apprendre_hc", "oui")
            log.info(f"🔍 HC confirmée via {ptec_entity} — apprentissage des plages activé")
        else:
            log.info("🔍 HC confirmée (index HCHC/HP) mais pas de capteur PTEC temps réel")

    return None


def _tarif_apprendre_plages_hc(etats):
    """Apprend les plages HC en observant les transitions PTEC.
    Appelé toutes les 5 min par le monitoring. En 24h, déduit les plages exactes."""
    if mem_get("tarif_apprendre_hc") != "oui":
        return

    ptec_eid = mem_get("tarif_ptec_entity")
    if not ptec_eid:
        return

    index = {e["entity_id"]: e for e in etats}
    e = index.get(ptec_eid)
    if not e:
        return

    etat = e["state"].lower().strip()
    now = datetime.now()
    heure_min = f"{now.hour}:{now.minute:02d}"

    # Stocker chaque observation (heure → HC ou HP)
    data, nb = skill_get("apprentissage_hc")
    if not data:
        data = {"observations": {}, "plages_deduites": []}

    # Clé = heure (arrondie à 30 min)
    minute_arrondie = 0 if now.minute < 30 else 30
    cle = f"{now.hour:02d}:{minute_arrondie:02d}"

    est_hc = "hc" in etat
    if cle not in data["observations"]:
        data["observations"][cle] = {"hc": 0, "hp": 0}
    data["observations"][cle]["hc" if est_hc else "hp"] += 1

    # Après 48 observations (24h à 1/30min), déduire les plages
    nb_obs = sum(v["hc"] + v["hp"] for v in data["observations"].values())
    if nb_obs >= 48:
        # Construire les plages HC
        heures_hc = []
        for h_str in sorted(data["observations"].keys()):
            obs = data["observations"][h_str]
            if obs["hc"] > obs["hp"]:
                heures_hc.append(h_str)

        if heures_hc:
            # Convertir en plages continues
            plages = _construire_plages(heures_hc)
            data["plages_deduites"] = plages

            # Appliquer au tarif
            tarif = tarif_get()
            if tarif and "type" in tarif:
                tarif["heures_creuses"] = plages
                tarif["hc_source"] = "auto_appris"
                tarif["configure_le"] = now.isoformat()
                skill_set("tarification", tarif)
                mem_set("tarif_apprendre_hc", "termine")
                telegram_send(
                    f"🧠 Heures creuses auto-apprises !\n"
                    f"Plages détectées : {', '.join(plages)}\n"
                    f"Source : observation PTEC sur 24h"
                )
                log.info(f"🧠 HC auto-apprises : {plages}")

    skill_set("apprentissage_hc", data, nb + 1)


def _construire_plages(heures_hc):
    """Convertit une liste d'heures HC ['22:00', '22:30', '23:00', ...] en plages ['22:00-06:00']"""
    if not heures_hc:
        return []

    # Convertir en minutes
    minutes = []
    for h in heures_hc:
        parts = h.split(":")
        minutes.append(int(parts[0]) * 60 + int(parts[1]))
    minutes.sort()

    # Trouver les plages continues (avec gestion du passage minuit)
    plages = []
    debut = minutes[0]
    prev = minutes[0]
    for m in minutes[1:]:
        if m - prev > 30:  # Gap > 30 min = nouvelle plage
            plages.append((debut, prev + 30))
            debut = m
        prev = m
    plages.append((debut, prev + 30))

    # Convertir en format HH:MM-HH:MM
    result = []
    for d, f in plages:
        dh, dm = d // 60, d % 60
        fh, fm = f // 60, f % 60
        if fh >= 24:
            fh -= 24
        result.append(f"{dh:02d}:{dm:02d}-{fh:02d}:{fm:02d}")

    return result


def tarif_configurer_questionnaire():
    """Lance le questionnaire de configuration tarifaire sur Telegram"""
    mem_set("attente_tarif_etape", "fournisseur")
    liste = []
    idx = 1
    for cle, fournisseur in FOURNISSEURS.items():
        if cle != "autre":
            liste.append(f"  {idx} → {fournisseur['nom']}")
            idx += 1
    liste.append(f"  {idx} → Autre fournisseur")

    telegram_send(
        "⚡ CONFIGURATION TARIF ÉLECTRICITÉ\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Quel est votre fournisseur ?\n\n" +
        "\n".join(liste)
    )


def tarif_traiter_reponse(texte):
    """Traite les réponses au questionnaire tarifaire. Retourne True si consommé."""
    etape = mem_get("attente_tarif_etape")
    if not etape:
        return False

    t = texte.strip().lower()

    # ═══ ÉTAPE 1 : Choix fournisseur ═══
    if etape == "fournisseur":
        cles = [c for c in FOURNISSEURS.keys() if c != "autre"]
        idx = None
        # Par numéro
        try:
            num = int(t)
            if 1 <= num <= len(cles):
                idx = cles[num - 1]
            elif num == len(cles) + 1:
                idx = "autre"
        except ValueError:
            # Par nom
            for c, f in FOURNISSEURS.items():
                if t in c or t in f["nom"].lower():
                    idx = c
                    break

        if idx == "autre":
            mem_set("tarif_temp_fournisseur", "autre")
            mem_set("attente_tarif_etape", "custom_fournisseur")
            telegram_send("🏢 Nom de votre fournisseur ?")
            return True

        if idx is None:
            telegram_send("Fournisseur non reconnu. Répondez par le numéro ou le nom.")
            return True

        fournisseur = FOURNISSEURS[idx]
        mem_set("tarif_temp_fournisseur", idx)

        # Lister les offres
        offres = fournisseur["offres"]
        if len(offres) == 1:
            # Une seule offre → la sélectionner directement
            cle_offre = list(offres.keys())[0]
            return _tarif_appliquer_offre(idx, cle_offre)

        msg = f"⚡ {fournisseur['nom']} — Quelle offre ?\n\n"
        for i, (cle, offre) in enumerate(offres.items(), 1):
            if offre["type"] == "base":
                msg += f"  {i} → {offre['nom']} ({offre.get('prix_kwh', '?')}€/kWh)\n"
            elif offre["type"] == "hphc":
                msg += f"  {i} → {offre['nom']} (HP:{offre.get('prix_hp')}€ / HC:{offre.get('prix_hc')}€)\n"
            elif offre["type"] == "tempo":
                msg += f"  {i} → {offre['nom']} (Bleu HC:{offre.get('prix_bleu_hc')}€)\n"
            else:
                msg += f"  {i} → {offre['nom']}\n"
        mem_set("attente_tarif_etape", "offre")
        telegram_send(msg)
        return True

    # ═══ ÉTAPE 1b : Fournisseur custom ═══
    if etape == "custom_fournisseur":
        mem_set("tarif_temp_fournisseur_nom", texte.strip())
        mem_set("attente_tarif_etape", "custom_type")
        telegram_send("Type d'abonnement ?\n  1 → Base (prix unique)\n  2 → HP/HC")
        return True

    if etape == "custom_type":
        if t in ("1", "base"):
            mem_set("attente_tarif_etape", "custom_prix")
            mem_set("tarif_temp_type", "base")
            telegram_send("💰 Prix du kWh TTC ?\nExemple : 0.2516")
        else:
            mem_set("attente_tarif_etape", "custom_hp")
            mem_set("tarif_temp_type", "hphc")
            telegram_send("💰 Prix Heures Pleines (€/kWh TTC) ?")
        return True

    if etape == "custom_prix":
        try:
            prix = float(t.replace(",", ".").replace("€", "").strip())
            data = {
                "type": "base",
                "fournisseur": mem_get("tarif_temp_fournisseur_nom") or "Inconnu",
                "prix_kwh": prix,
                "configure_le": datetime.now().isoformat()
            }
            skill_set("tarification", data)
            mem_set("attente_tarif_etape", "")
            telegram_send(f"✅ Tarif configuré\n{data['fournisseur']} Base : {prix}€/kWh")
            return True
        except Exception:
            telegram_send("Format invalide. Exemple : 0.2516")
            return True

    if etape == "custom_hp":
        try:
            prix = float(t.replace(",", ".").replace("€", "").strip())
            mem_set("tarif_temp_hp", str(prix))
            mem_set("attente_tarif_etape", "custom_hc")
            telegram_send(f"✅ HP : {prix}€\n💰 Prix Heures Creuses (€/kWh TTC) ?")
            return True
        except Exception:
            telegram_send("Format invalide.")
            return True

    if etape == "custom_hc":
        try:
            prix_hc = float(t.replace(",", ".").replace("€", "").strip())
            mem_set("tarif_temp_hc", str(prix_hc))
            mem_set("attente_tarif_etape", "custom_plages")
            telegram_send("🕐 Plages heures creuses ?\nExemple : 22:00-06:00")
            return True
        except Exception:
            telegram_send("Format invalide.")
            return True

    if etape == "custom_plages":
        plages = [p.strip() for p in t.replace(" ", "").split(",") if "-" in p]
        if not plages:
            telegram_send("Format invalide. Exemple : 22:00-06:00")
            return True
        data = {
            "type": "hphc",
            "fournisseur": mem_get("tarif_temp_fournisseur_nom") or "Inconnu",
            "prix_hp": float(mem_get("tarif_temp_hp") or "0.27"),
            "prix_hc": float(mem_get("tarif_temp_hc") or "0.2068"),
            "heures_creuses": plages,
            "configure_le": datetime.now().isoformat()
        }
        skill_set("tarification", data)
        mem_set("attente_tarif_etape", "")
        telegram_send(
            f"✅ Tarif HP/HC configuré\n"
            f"{data['fournisseur']}\n"
            f"HP : {data['prix_hp']}€ | HC : {data['prix_hc']}€\n"
            f"Plages HC : {', '.join(plages)}"
        )
        return True

    # ═══ ÉTAPE 2 : Choix offre ═══
    if etape == "offre":
        fournisseur_cle = mem_get("tarif_temp_fournisseur")
        if fournisseur_cle not in FOURNISSEURS:
            mem_set("attente_tarif_etape", "")
            return False

        offres = FOURNISSEURS[fournisseur_cle]["offres"]
        cles_offres = list(offres.keys())

        idx = None
        try:
            num = int(t)
            if 1 <= num <= len(cles_offres):
                idx = cles_offres[num - 1]
        except ValueError:
            for c, o in offres.items():
                if t in c or t in o["nom"].lower():
                    idx = c
                    break

        if idx is None:
            telegram_send("Offre non reconnue. Répondez par le numéro.")
            return True

        return _tarif_appliquer_offre(fournisseur_cle, idx)

    # ═══ ÉTAPE 2b : Jour choisi (Week-End Plus) ═══
    if etape == "jour_choisi":
        jours_map = {"1": 0, "lundi": 0, "2": 2, "mercredi": 2, "3": 4, "vendredi": 4}
        jour = jours_map.get(t)
        if jour is None:
            telegram_send("Répondez 1 (Lundi), 2 (Mercredi) ou 3 (Vendredi)")
            return True

        tarif_en_cours = json.loads(mem_get("tarif_temp_data") or "{}")
        tarif_en_cours["jour_choisi"] = jour
        jours_noms = {0: "Lundi", 2: "Mercredi", 4: "Vendredi"}

        # Si HP/HC → demander les heures creuses
        if "hphc" in tarif_en_cours.get("type", ""):
            mem_set("tarif_temp_data", json.dumps(tarif_en_cours))
            mem_set("attente_tarif_etape", "heures_creuses")
            telegram_send(
                f"✅ Jour choisi : {jours_noms[jour]}\n\n"
                f"🕐 Vos plages heures creuses ?\nExemple : 22:00-06:00"
            )
            return True

        # Sinon c'est fini
        tarif_en_cours["configure_le"] = datetime.now().isoformat()
        skill_set("tarification", tarif_en_cours)
        mem_set("attente_tarif_etape", "")
        telegram_send(
            f"✅ Tarif configuré\n"
            f"{tarif_en_cours.get('fournisseur', '')} — {tarif_en_cours.get('nom', '')}\n"
            f"Jour choisi : {jours_noms[jour]}\n"
            f"Semaine : {tarif_en_cours.get('prix_semaine', '?')}€\n"
            f"WE + jour + fériés : {tarif_en_cours.get('prix_weekend_jour', '?')}€"
        )
        return True

    # ═══ ANNULATION à tout moment ═══
    if t in ("annuler", "stop", "cancel", "non"):
        mem_set("attente_tarif_etape", "")
        telegram_send("❌ Configuration tarif annulée.")
        return True

    # ═══ ÉTAPE 3 : Heures creuses pour offre HP/HC ═══
    if etape == "heures_creuses":
        plages = [p.strip() for p in t.replace(" ", "").split(",") if "-" in p]
        if not plages:
            telegram_send("Format invalide. Exemple : 22:00-06:00")
            return True

        tarif_en_cours = json.loads(mem_get("tarif_temp_data") or "{}")
        tarif_en_cours["heures_creuses"] = plages
        tarif_en_cours["configure_le"] = datetime.now().isoformat()
        skill_set("tarification", tarif_en_cours)
        mem_set("attente_tarif_etape", "")

        telegram_send(
            f"✅ Tarif configuré\n"
            f"{tarif_en_cours.get('fournisseur', '')} — {tarif_en_cours.get('nom', '')}\n"
            f"HP : {tarif_en_cours.get('prix_hp')}€ | HC : {tarif_en_cours.get('prix_hc')}€\n"
            f"Plages HC : {', '.join(plages)}"
        )
        return True

    mem_set("attente_tarif_etape", "")
    return False


def _tarif_appliquer_offre(fournisseur_cle, offre_cle):
    """Applique une offre fournisseur connue — les tarifs sont pré-remplis"""
    fournisseur = FOURNISSEURS[fournisseur_cle]
    offre = fournisseur["offres"][offre_cle]
    nom_f = fournisseur["nom"]

    if offre["type"] == "base":
        data = {
            "type": "base",
            "fournisseur": nom_f,
            "nom": offre["nom"],
            "prix_kwh": offre["prix_kwh"],
            "abo_mois": offre.get("abo_mois", 0),
            "configure_le": datetime.now().isoformat()
        }
        skill_set("tarification", data)
        mem_set("attente_tarif_etape", "")
        telegram_send(
            f"✅ Tarif configuré automatiquement\n"
            f"{nom_f} — {offre['nom']}\n"
            f"Prix : {offre['prix_kwh']}€/kWh TTC"
        )
        return True

    elif offre["type"] == "hphc":
        data = {
            "type": "hphc",
            "fournisseur": nom_f,
            "nom": offre["nom"],
            "prix_hp": offre["prix_hp"],
            "prix_hc": offre["prix_hc"],
            "abo_mois": offre.get("abo_mois", 0),
        }
        # Chercher les heures creuses automatiquement dans HA
        hc_auto = _tarif_detecter_heures_creuses()
        if hc_auto:
            data["heures_creuses"] = hc_auto
            data["configure_le"] = datetime.now().isoformat()
            skill_set("tarification", data)
            mem_set("attente_tarif_etape", "")
            telegram_send(
                f"✅ {nom_f} — {offre['nom']}\n"
                f"HP : {offre['prix_hp']}€ | HC : {offre['prix_hc']}€\n"
                f"🕐 Heures creuses auto-détectées : {', '.join(hc_auto)}"
            )
        else:
            mem_set("tarif_temp_data", json.dumps(data))
            mem_set("attente_tarif_etape", "heures_creuses")
            telegram_send(
                f"✅ {nom_f} — {offre['nom']}\n"
                f"HP : {offre['prix_hp']}€ | HC : {offre['prix_hc']}€\n\n"
                f"🕐 Heures creuses non trouvées dans HA.\n"
                f"Regardez sur votre compteur Linky (touche +) ou facture.\n"
                f"Exemple : 22:00-06:00"
            )
        return True

    elif offre["type"] == "tempo":
        data = {
            "type": "tempo",
            "fournisseur": nom_f,
            "nom": offre["nom"],
            "prix_bleu_hp": offre["prix_bleu_hp"],
            "prix_bleu_hc": offre["prix_bleu_hc"],
            "prix_blanc_hp": offre["prix_blanc_hp"],
            "prix_blanc_hc": offre["prix_blanc_hc"],
            "prix_rouge_hp": offre["prix_rouge_hp"],
            "prix_rouge_hc": offre["prix_rouge_hc"],
            "abo_mois": offre.get("abo_mois", 0),
        }
        mem_set("tarif_temp_data", json.dumps(data))
        mem_set("attente_tarif_etape", "heures_creuses")
        telegram_send(
            f"✅ {nom_f} — {offre['nom']}\n"
            f"Bleu : HP {offre['prix_bleu_hp']}€ / HC {offre['prix_bleu_hc']}€\n"
            f"Blanc : HP {offre['prix_blanc_hp']}€ / HC {offre['prix_blanc_hc']}€\n"
            f"Rouge : HP {offre['prix_rouge_hp']}€ / HC {offre['prix_rouge_hc']}€\n\n"
            f"🕐 Vos plages heures creuses ?\nExemple : 22:00-06:00"
        )
        return True

    elif offre["type"] in ("weekend", "weekend_hphc", "weekend_plus", "weekend_plus_hphc"):
        data = {
            "type": offre["type"],
            "fournisseur": nom_f,
            "nom": offre["nom"],
            "abo_mois": offre.get("abo_mois", 0),
        }
        for k, v in offre.items():
            if k.startswith("prix_"):
                data[k] = v

        if "plus" in offre["type"]:
            mem_set("tarif_temp_data", json.dumps(data))
            mem_set("attente_tarif_etape", "jour_choisi")
            telegram_send(
                f"✅ {nom_f} — {offre['nom']}\n"
                f"Tarifs pré-remplis automatiquement.\n\n"
                f"📅 Quel jour choisi en semaine ?\n"
                f"  1 → Lundi\n  2 → Mercredi\n  3 → Vendredi"
            )
            return True

        if "hphc" in offre["type"]:
            mem_set("tarif_temp_data", json.dumps(data))
            mem_set("attente_tarif_etape", "heures_creuses")
            telegram_send(
                f"✅ {nom_f} — {offre['nom']}\n"
                f"Tarifs pré-remplis.\n\n"
                f"🕐 Vos plages heures creuses ?\nExemple : 22:00-06:00"
            )
            return True

        data["configure_le"] = datetime.now().isoformat()
        skill_set("tarification", data)
        mem_set("attente_tarif_etape", "")
        telegram_send(
            f"✅ Tarif configuré\n{nom_f} — {offre['nom']}\n"
            f"Semaine : {data.get('prix_semaine', '?')}€ | WE+fériés : {data.get('prix_weekend', '?')}€"
        )
        return True

    return False


def cmd_md():
    """Envoie le Cahier des Charges par mail"""
    ok = envoyer_md_par_mail()
    if ok:
        return "📧 Cahier des Charges envoyé par mail."
    return "❌ Échec envoi mail — vérifier config SMTP."


def cmd_sms():
    """Renvoie un code SMS et verrouille le canal (sécurité)"""
    # global canal_verrouille  # via shared
    shared.canal_verrouille = True
    envoyer_code_sms()
    return "📱 Code SMS envoyé — canal verrouillé."


def cmd_tarif():
    """Affiche ou configure le tarif électricité"""
    tarif = tarif_get()
    prix_actuel = tarif_prix_kwh_actuel()
    est_hc = tarif_est_heure_creuse()

    rapport = "⚡ TARIF ÉLECTRICITÉ\n━━━━━━━━━━━━━━━━━━\n"
    rapport += f"Fournisseur : {tarif.get('fournisseur', 'EDF')}\n"
    rapport += f"Type : {tarif.get('type', 'base')}\n"

    if tarif.get("type") == "hphc":
        rapport += f"HP : {tarif.get('prix_hp')}€/kWh\n"
        rapport += f"HC : {tarif.get('prix_hc')}€/kWh\n"
        rapport += f"Plages HC : {', '.join(tarif.get('heures_creuses', []))}\n"
        rapport += f"\nActuellement : {'🔵 HC' if est_hc else '🔴 HP'} — {prix_actuel}€/kWh"
    else:
        rapport += f"Prix : {tarif.get('prix_kwh', prix_actuel)}€/kWh\n"

    if tarif.get("configure_le"):
        rapport += f"\nConfiguré le : {tarif['configure_le'][:10]}"

    rapport += "\n\nPour modifier : /tarif config"
    return rapport


def skill_dynamique_collecter(etats):
    """Exécute toutes les skills dynamiques enregistrées"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT nom, donnees FROM skills WHERE nom LIKE 'dyn_%'"
    ).fetchall()
    conn.close()

    index = {e["entity_id"]: e for e in etats}
    now = datetime.now()

    for nom, donnees_json in rows:
        try:
            definition = json.loads(donnees_json)
            entites = definition.get("entites", [])
            seuil = definition.get("seuil", None)
            action = definition.get("action", "collecter")  # collecter | alerter | comparer
            description = definition.get("description", nom)

            valeurs = {}
            for eid in entites:
                e = index.get(eid)
                if e and e["state"] not in ("unavailable", "unknown"):
                    try:
                        valeurs[eid] = float(e["state"])
                    except Exception:
                        valeurs[eid] = e["state"]

            if not valeurs:
                continue

            if action == "collecter":
                # Stocker les valeurs dans l'historique du skill
                historique = definition.get("historique", [])
                historique.append({
                    "timestamp": now.isoformat(),
                    "valeurs": valeurs
                })
                # Garder les 200 dernières mesures max
                definition["historique"] = historique[-200:]
                skill_set(nom, definition)

            elif action == "alerter" and seuil is not None:
                # Alerter si une valeur dépasse le seuil
                for eid, val in valeurs.items():
                    if isinstance(val, (int, float)) and val > float(seuil):
                        fname = index[eid].get("attributes", {}).get("friendly_name", eid)
                        _alerter_si_nouveau(
                            f"dyn_{nom}_{eid}",
                            f"🧠 SKILL {description}\n{fname} = {val} (seuil: {seuil})",
                            delai_h=6
                        )

            elif action == "comparer":
                # Comparer deux entités
                if len(entites) >= 2:
                    v1 = valeurs.get(entites[0])
                    v2 = valeurs.get(entites[1])
                    if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                        ratio = v1 / v2 if v2 > 0 else 0
                        historique = definition.get("historique", [])
                        historique.append({
                            "timestamp": now.isoformat(),
                            "ratio": round(ratio, 3),
                            "v1": v1, "v2": v2
                        })
                        definition["historique"] = historique[-200:]
                        skill_set(nom, definition)

        except Exception as ex:
            log.error(f"❌ Skill dynamique {nom}: {ex}")


def skill_creer_auto(question, etats):
    """Haiku décide si une nouvelle compétence est nécessaire et la crée."""
    index = {e["entity_id"]: e for e in etats}

    # Ne pas créer trop de skills
    conn = sqlite3.connect(DB_PATH)
    nb_dyn = conn.execute("SELECT COUNT(*) FROM skills WHERE nom LIKE 'dyn_%'").fetchone()[0]
    conn.close()
    if nb_dyn >= 10:
        return None  # Max 10 skills dynamiques

    prompt = (
        "Tu es l'assistant domotique de l'utilisateur.\n"
        "Il pose cette question : \"" + question + "\"\n\n"
        "Dois-tu créer une NOUVELLE compétence de surveillance pour y répondre à l'avenir ?\n"
        "Une compétence surveille des entités Home Assistant et apprend un pattern.\n\n"
        "Réponds UNIQUEMENT en JSON :\n"
        "Si NON : {\"creer\": false}\n"
        "Si OUI : {\"creer\": true, \"nom\": \"dyn_nom_court\", \"description\": \"ce que ça fait\", "
        "\"entites\": [\"sensor.xxx\", \"sensor.yyy\"], \"action\": \"collecter\", \"seuil\": null}\n\n"
        "Actions possibles : collecter (historique), alerter (seuil dépassé), comparer (ratio 2 entités).\n"
        "IMPORTANT : les entités doivent exister dans Home Assistant.\n"
        "Réponds JUSTE le JSON, rien d'autre."
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

        if not resultat.get("creer"):
            return None

        nom = resultat.get("nom", "")
        if not nom.startswith("dyn_"):
            nom = f"dyn_{nom}"

        # Vérifier que les entités existent
        entites = resultat.get("entites", [])
        entites_valides = [eid for eid in entites if eid in index]
        if not entites_valides:
            return None

        definition = {
            "description": resultat.get("description", nom),
            "entites": entites_valides,
            "action": resultat.get("action", "collecter"),
            "seuil": resultat.get("seuil"),
            "cree_le": datetime.now().isoformat(),
            "cree_par": "auto",
            "historique": []
        }

        skill_set(nom, definition, 0)
        log.info(f"🧠 Nouveau skill créé : {nom} — {definition['description']}")
        telegram_send(
            f"🧠 NOUVELLE COMPÉTENCE CRÉÉE\n"
            f"Nom : {nom}\n"
            f"Rôle : {definition['description']}\n"
            f"Entités : {', '.join(entites_valides)}\n"
            f"Action : {definition['action']}"
        )
        return nom

    except Exception as ex:
        log.error(f"❌ skill_creer_auto: {ex}")
        return None


def cmd_audit():
    telegram_send("🔍 Audit en cours...")
    etats = ha_get("states")
    if not etats:
        return "❌ AUDIT — HA inaccessible"

    total = len(etats)
    hors_ligne = [e for e in etats if e["state"] in ["unavailable", "unknown"]]
    domaines_ko = {}
    for e in hors_ligne:
        d = e["entity_id"].split(".")[0]
        domaines_ko.setdefault(d, []).append(e["entity_id"])

    rapport  = f"📊 AUDIT HOME ASSISTANT\n━━━━━━━━━━━━━━━━━━━━\n"
    rapport += f"Total : {total} | ✅ {total - len(hors_ligne)} | ❌ {len(hors_ligne)}\n"

    if hors_ligne:
        for domaine, ids in sorted(domaines_ko.items()):
            rapport += f"\n[{domaine}]\n"
            for eid in ids[:5]:
                rapport += f"  • {eid}\n"
            if len(ids) > 5:
                rapport += f"  ... et {len(ids)-5} autres\n"

    contexte = ha_get_contexte_intelligent("audit général état maison", etats)
    prompt = (
        "Entités HORS LIGNE :\n"
        + "\n".join(f"  • {e['entity_id']}" for e in hors_ligne[:20])
        + "\n\nPour chacune, une ligne : normal ou anormal ? Sois concis."
    )
    analyse = appel_claude(prompt, contexte)
    rapport += f"\n🤖 {analyse}"
    return rapport


def cmd_energie(detail=False):
    etats = ha_get("states")
    if not etats:
        return "❌ ÉNERGIE — HA inaccessible"

    index = {e["entity_id"]: e for e in etats}
    now_str = datetime.now().strftime("%H:%M — %A %d/%m/%Y")

    def _val(eid, default="?"):
        e = index.get(eid)
        if e and e["state"] not in ("unavailable", "unknown"):
            return e["state"]
        return default

    def _val_unite(eid):
        e = index.get(eid)
        if e and e["state"] not in ("unavailable", "unknown"):
            unite = e.get("attributes", {}).get("unit_of_measurement", "")
            return f"{e['state']} {unite}".strip()
        return "—"

    # ═══ RÉSUMÉ (toujours affiché) ═══
    rapport = f"⚡ BILAN ÉNERGIE\n{now_str}\n━━━━━━━━━━━━━━━━━━\n"

    # — SOLAIRE — (section entière masquée si pas de panneaux solaires)
    _has_solar = role_get("production_solaire_w")
    _has_batterie = role_get("batterie_soc") or role_get("batterie_soc_anker")

    if _has_solar:
        rapport += "\n☀️ SOLAIRE\n"
        ecu_w = role_val("production_solaire_w", index, "0")
        ecu_kwh = role_val("production_solaire_kwh", index, "0")
        ecu_inv = role_val("onduleurs_total", index, None)
        ecu_inv_on = role_val("onduleurs_online", index, None)
        rapport += f"  Production : {ecu_w} W | Aujourd'hui : {ecu_kwh} kWh\n"
        if ecu_inv and ecu_inv_on:
            if str(ecu_inv) != str(ecu_inv_on):
                est_jour = ha_est_jour(etats)
                if not est_jour or (ecu_w in ("0", "?") and str(ecu_inv_on) in ("0", "1")):
                    rapport += f"  🌙 Onduleurs : {ecu_inv_on}/{ecu_inv} (veille nocturne)\n"
                else:
                    rapport += f"  🚨 Onduleurs : {ecu_inv_on}/{ecu_inv} en ligne\n"
            else:
                rapport += f"  ✅ Onduleurs : {ecu_inv_on}/{ecu_inv} en ligne\n"

    if _has_batterie:
        rapport += "\n🔋 BATTERIE\n"
        anker_soc = role_val("batterie_soc", index, None) or role_val("batterie_soc_anker", index, None)
        if anker_soc and anker_soc != "?":
            try:
                soc_val = float(anker_soc) if anker_soc not in ("?", None) else 0
                soc_icone = "🟢" if soc_val >= 80 else ("🟡" if soc_val >= 30 else "🔴")
                rapport += f"  {soc_icone} SOC : {anker_soc}%\n"
            except (ValueError, TypeError):
                rapport += f"  🔋 SOC : {anker_soc}% (valeur non numérique)\n"
        anker_prod = role_val("batterie_prod_solaire", index, None)
        if anker_prod and anker_prod != "?":
            rapport += f"  ☀️ Charge solaire : {anker_prod} W\n"
        anker_output = role_val("batterie_sortie", index, None)
        if anker_output and anker_output != "?":
            rapport += f"  🏠 Injection maison : {anker_output} W\n"
        anker_mode = role_val("batterie_mode", index, None)
        if anker_mode and anker_mode != "?":
            rapport += f"  Mode : {anker_mode}\n"
        anker_prise_eid = role_get("batterie_puissance")
        if anker_prise_eid:
            e_prise = index.get(anker_prise_eid)
            if e_prise and e_prise["state"] not in ("unavailable", "unknown"):
                try:
                    w_val = float(e_prise["state"])
                    # Puissance positive = charge (depuis panneaux), négative = décharge (vers maison)
                    if w_val < 0:
                        rapport += f"  ⚡ Décharge : {abs(int(w_val))} W (priorité batterie)\n"
                    else:
                        rapport += f"  🔌 Prise : {int(w_val)} W\n"
                except (ValueError, TypeError):
                    rapport += f"  🔌 Prise : {e_prise['state']} W\n"

    if _has_solar:
        try:
            production_w = ha_get_production_solaire_actuelle(etats)
            conso_rt = role_val("conso_temps_reel", index, None)
            if conso_rt and conso_rt not in ("?", None) and production_w > 0:
                edf_w = float(conso_rt)
                conso_totale = edf_w + production_w
                if conso_totale > 0:
                    couv = min(100, int(production_w / conso_totale * 100))
                    rapport += f"\n  ☀️ Couverture solaire : {couv}%\n"
        except Exception:
            pass

    # — CONSOMMATION —
    rapport += "\n🔌 CONSOMMATION\n"
    eco_rt = role_val("conso_temps_reel", index)
    eco_jour = role_val("conso_jour_eur", index)
    conso_kwh = role_val("conso_jour_kwh", index)
    if eco_rt != "?":
        rapport += f"  Temps réel (EDF) : {eco_rt} W\n"
    if eco_jour != "?":
        rapport += f"  Dépense du jour : {eco_jour} €\n"
    if conso_kwh != "?":
        rapport += f"  Conso totale : {conso_kwh} kWh\n"

    # — CHAUFFAGE / PAC — (masquée si pas de PAC, températures toujours affichées)
    _has_pac = role_get("pac_climate")
    if _has_pac:
        rapport += "\n🌡️ CHAUFFAGE\n"
        for e in etats:
            if e["entity_id"].startswith("climate."):
                carto = cartographie_get(e["entity_id"])
                if carto and "chauffage" in carto[0]:
                    state = e["state"]
                    attrs = e.get("attributes", {})
                    temp_eau = attrs.get("current_temperature", "?")
                    temp_consigne = attrs.get("temperature", "?")
                    if state in ["auto", "heat", "cool", "fan_only", "heat_cool"]:
                        rapport += f"  ✅ PAC : EN SERVICE (mode {state})\n"
                    else:
                        rapport += f"  ⚫ PAC : {state}\n"
                    rapport += f"  Eau : {temp_eau}°C | Consigne : {temp_consigne}°C\n"
                    break
        pac_energy = role_val("pac_conso", index)
        if pac_energy != "?":
            rapport += f"  Conso PAC : {pac_energy} W\n"

    # Températures : toujours affichées (utile même sans PAC)
    temp_int = role_val("temp_interieure", index)
    temp_ext = role_val("temp_exterieure", index)
    if temp_int != "?" or temp_ext != "?":
        if not _has_pac:
            rapport += "\n🌡️ TEMPÉRATURES\n"
        if temp_int != "?":
            rapport += f"  T° intérieure : {temp_int}°C\n"
        if temp_ext != "?":
            rapport += f"  T° extérieure : {temp_ext}°C\n"

    # — CYCLES EN COURS —
    cycles_actifs = []
    for eid, etat_p in _etat_prises.items():
        if etat_p == "actif":
            e = index.get(eid)
            fname = e.get("attributes", {}).get("friendly_name", eid) if e else eid
            en_cours = cycle_en_cours(eid)
            duree = ""
            if en_cours:
                debut_dt = datetime.fromisoformat(en_cours[0])
                mins = int((datetime.now() - debut_dt).total_seconds() / 60)
                duree = f" ({mins} min)"
            cycles_actifs.append(f"{fname}{duree}")
    if cycles_actifs:
        rapport += "\n🔄 CYCLES EN COURS\n"
        for c in cycles_actifs:
            rapport += f"  ▶️ {c}\n"

    # — MÉTÉO —
    for e in etats:
        if e["entity_id"].startswith("weather."):
            attrs = e.get("attributes", {})
            temp = attrs.get("temperature", "?")
            hum = attrs.get("humidity", "?")
            rapport += f"\n🌤️ MÉTÉO : {temp}°C | Humidité {hum}%\n"
            break

    # Graphique énergie du jour
    try:
        graph_bytes = generer_graphique_energie(etats, index)
        if graph_bytes:
            telegram_send_photo(graph_bytes, "⚡ Énergie du jour")
    except Exception:
        pass

    if not detail:
        rapport += "\n💡 /energie detail → rapport complet"
        return rapport

    # ═══ DÉTAIL (uniquement si demandé) ═══
    rapport += "\n━━━━━━━━━━━━━━━━━━\n📋 DÉTAIL COMPLET\n"

    # Toutes les prises avec puissance
    rapport += "\n🔌 PRISES CONNECTÉES\n"
    prises = cartographie_get_par_categorie("prise_connectee")
    for eid, sc, pc in prises:
        if not eid.startswith("sensor."):
            continue
        e = index.get(eid)
        if not e:
            continue
        unite = e.get("attributes", {}).get("unit_of_measurement", "")
        if unite not in ("W", "w", "Watt"):
            continue
        fname = e.get("attributes", {}).get("friendly_name", eid)
        for suffixe in [" Puissance", " Power", " Consommation"]:
            if fname.endswith(suffixe):
                fname = fname[:-len(suffixe)].strip()
                break
        try:
            val = float(e["state"])
            # Croiser avec le statut réel du cycle
            cycle_actif = _etat_prises.get(eid) == "actif"
            app = appareil_get(eid)
            app_nom = app["nom"] if app and app.get("nom") else fname
            app_type = app["type"] if app else ""

            if cycle_actif:
                # Cycle en cours — même si puissance basse (pause rinçage, etc.)
                icone = "🔵"
                statut = f" [cycle en cours]"
            elif val > 5:
                icone = "🟢"
                statut = ""
            else:
                icone = "⚫"
                statut = ""

            # Exclure les prises monitoring (Anker etc.) de l'affichage "actif"
            if app_type == "monitoring_energie" and not cycle_actif:
                icone = "📊"
                statut = " [monitoring]"
            elif app_type == "ignorer":
                continue

            rapport += f"  {icone} {app_nom} : {int(val)} W{statut}\n"
        except Exception:
            rapport += f"  ❓ {fname} : {e['state']}\n"

    # Toutes les entités solaire
    rapport += "\n☀️ ENTITÉS SOLAIRE\n"
    cats_detail = ["energie_solaire", "energie_batterie", "energie_production"]
    for cat in cats_detail:
        entites_cat = cartographie_get_par_categorie(cat)
        if entites_cat:
            rapport += f"  [{cat}]\n"
            for eid, sc, pc in entites_cat:
                e = index.get(eid)
                if e:
                    unite = e.get("attributes", {}).get("unit_of_measurement", "")
                    etat = e["state"]
                    icone = "❌" if etat in ("unavailable", "unknown") else "✅"
                    rapport += f"    {icone} {eid} = {etat} {unite}\n"

    # Chauffage complet
    rapport += "\n🌡️ CHAUFFAGE COMPLET\n"
    entites_chauff = cartographie_get_par_categorie("energie_chauffage")
    for eid, sc, pc in entites_chauff:
        e = index.get(eid)
        if e:
            unite = e.get("attributes", {}).get("unit_of_measurement", "")
            etat = e["state"]
            icone = "❌" if etat in ("unavailable", "unknown") else "✅"
            rapport += f"  {icone} {eid} = {etat} {unite}\n"

    return rapport


def cmd_solaire():
    # Pas de panneaux → message clair
    if not role_get("production_solaire_w"):
        return "☀️ Aucun panneau solaire détecté.\nSi vous venez d'installer des panneaux, faites /scan pour les détecter."

    etats = ha_get("states")
    if not etats:
        return "❌ SOLAIRE — HA inaccessible"
    index = {e["entity_id"]: e for e in etats}
    entites = cartographie_get_par_categorie("energie_solaire")
    rapport = "☀️ PRODUCTION SOLAIRE\n━━━━━━━━━━━━━━━━━━\n"
    if entites:
        for eid, sous, piece in entites:
            if eid in index:
                e = index[eid]
                unite = e.get("attributes", {}).get("unit_of_measurement", "")
                rapport += f"  {eid} = {e['state']} {unite}\n"
    else:
        rapport += "Aucun capteur solaire cartographié — lance `scan`\n"

    # Graphique solaire
    try:
        graph_bytes = generer_graphique_energie(etats, index)
        if graph_bytes:
            telegram_send_photo(graph_bytes, "☀️ Solaire du jour")
    except Exception:
        pass

    return rapport


def cmd_batteries():
    etats = ha_get("states")
    if not etats:
        return "❌ BATTERIES — HA inaccessible"
    batteries = []
    for e in etats:
        eid = e["entity_id"]
        is_battery = (
            "battery" in eid.lower() or "batterie" in eid.lower() or
            e.get("attributes", {}).get("device_class") == "battery" or
            "etat_de_charge" in eid.lower()
        )
        if not is_battery:
            continue
        try:
            val = float(e["state"])
            carto = cartographie_get(eid)
            piece = carto[2] if carto else ""
            batteries.append((eid, piece, int(val)))
        except Exception:
            continue
    batteries.sort(key=lambda x: x[2])
    rapport = "🔋 ÉTAT DES BATTERIES\n━━━━━━━━━━━━━━━━━━\n"
    for eid, piece, val in batteries:
        icone = "🚨" if val < 10 else ("⚠️" if val < 20 else ("🟡" if val < 50 else "✅"))
        piece_str = f" [{piece}]" if piece else ""
        rapport += f"{icone} {eid}{piece_str} : {val}%\n"
    return rapport if len(batteries) > 0 else "🔋 Aucune batterie détectée"


def cmd_zigbee():
    etats = ha_get("states")
    if not etats:
        return "❌ ZIGBEE — HA inaccessible"
    index = {e["entity_id"]: e for e in etats}

    # Collecter TOUS les devices Zigbee via linkquality
    devices = []  # (eid, fname, piece, lqi, state)
    seen_devices = set()  # Éviter doublons par device physique
    for e in etats:
        lqi = e.get("attributes", {}).get("linkquality")
        if lqi is None:
            continue
        eid = e["entity_id"]
        # Dédupliquer par préfixe device (sensor.prise_X et switch.prise_X = même device)
        device_key = eid.split(".", 1)[1] if "." in eid else eid
        # Normaliser : prendre la première entité rencontrée par device
        base_key = device_key
        for suffix in ["_power", "_current", "_voltage", "_energy", "_puissance", "_battery"]:
            if base_key.endswith(suffix):
                base_key = base_key[:-len(suffix)]
                break
        if base_key in seen_devices:
            continue
        seen_devices.add(base_key)

        attrs = e.get("attributes", {})
        fname = attrs.get("friendly_name", eid)
        carto = cartographie_get(eid)
        piece = carto[2] if carto else ""
        try:
            lqi_val = int(lqi)
        except Exception:
            lqi_val = -1
        devices.append((eid, fname, piece, lqi_val, e["state"]))

    # Trier par LQI croissant (les plus faibles en premier)
    devices.sort(key=lambda x: x[3])

    total = len(devices)
    ko = [d for d in devices if d[4] in ("unavailable", "unknown")]
    critiques = [d for d in devices if 0 <= d[3] <= 30 and d[4] not in ("unavailable", "unknown")]
    faibles = [d for d in devices if 30 < d[3] <= 50 and d[4] not in ("unavailable", "unknown")]
    bons = [d for d in devices if 50 < d[3] <= 100 and d[4] not in ("unavailable", "unknown")]
    excellents = [d for d in devices if d[3] > 100 and d[4] not in ("unavailable", "unknown")]

    rapport = f"📡 RÉSEAU ZIGBEE — {total} devices\n━━━━━━━━━━━━━━━━━━\n"

    # Hors ligne
    if ko:
        rapport += f"\n❌ HORS LIGNE ({len(ko)})\n"
        for eid, fname, piece, lqi, state in ko:
            piece_str = f" [{piece}]" if piece else ""
            rapport += f"  {fname}{piece_str}\n"
    else:
        rapport += "\n✅ Tous en ligne\n"

    # LQI critique
    if critiques:
        rapport += f"\n🚨 LQI CRITIQUE ≤30 ({len(critiques)})\n"
        for eid, fname, piece, lqi, state in critiques:
            piece_str = f" [{piece}]" if piece else ""
            rapport += f"  LQI={lqi} — {fname}{piece_str}\n"

    # LQI faible
    if faibles:
        rapport += f"\n⚠️ LQI FAIBLE 31-50 ({len(faibles)})\n"
        for eid, fname, piece, lqi, state in faibles:
            piece_str = f" [{piece}]" if piece else ""
            rapport += f"  LQI={lqi} — {fname}{piece_str}\n"

    # Stats résumé
    if bons or excellents:
        rapport += f"\n✅ LQI BON 51-100 : {len(bons)} devices"
        rapport += f"\n✅ LQI EXCELLENT >100 : {len(excellents)} devices\n"

    # Top 5 meilleurs et 5 pires (en ligne)
    en_ligne = [d for d in devices if d[4] not in ("unavailable", "unknown") and d[3] >= 0]
    if len(en_ligne) >= 5:
        rapport += "\n📊 TOP 5 meilleurs :\n"
        for eid, fname, piece, lqi, state in sorted(en_ligne, key=lambda x: -x[3])[:5]:
            rapport += f"  LQI={lqi} — {fname}\n"
        rapport += "\n📊 TOP 5 plus faibles :\n"
        for eid, fname, piece, lqi, state in sorted(en_ligne, key=lambda x: x[3])[:5]:
            piece_str = f" [{piece}]" if piece else ""
            rapport += f"  LQI={lqi} — {fname}{piece_str}\n"

    return rapport


def cmd_nas():
    etats = ha_get("states")
    if not etats:
        return "❌ NAS — HA inaccessible"
    index = {e["entity_id"]: e for e in etats}
    entites_nas = cartographie_get_par_categorie("nas")
    rapport = "🗄️ NAS SYNOLOGY\n━━━━━━━━━━━━━━\n"
    if not entites_nas:
        return rapport + "Aucun NAS cartographié — lance `scan`"
    for eid, sous, piece in entites_nas:
        if eid in index:
            e = index[eid]
            unite = e.get("attributes", {}).get("unit_of_measurement", "")
            rapport += f"  {eid} = {e['state']} {unite}\n"
    return rapport


def cmd_automatisations():
    etats = ha_get("states")
    if not etats:
        return "❌ AUTOMATISATIONS — HA inaccessible"
    autos = [e for e in etats if e["entity_id"].startswith("automation.")]
    actives = [e for e in autos if e["state"] == "on"]
    inactives = [e for e in autos if e["state"] == "off"]
    rapport  = f"⚙️ AUTOMATISATIONS\n━━━━━━━━━━━━━━━\n"
    rapport += f"Total: {len(autos)} | Actives: {len(actives)} | Inactives: {len(inactives)}\n"
    rapport += "(unavailable = conditionnel, normal)\n"
    if inactives:
        rapport += "\n⚠️ Désactivées :\n"
        for e in inactives[:10]:
            rapport += f"  • {e['entity_id']}\n"
    return rapport


def cmd_addons():
    etats = ha_get("states")
    if not etats:
        return "❌ ADD-ONS — HA inaccessible"
    updates = [e for e in etats if e["entity_id"].startswith("update.")]
    rapport = "🧩 ADD-ONS\n━━━━━━━━━━\n"
    for e in updates[:20]:
        nom  = e.get("attributes", {}).get("friendly_name", e["entity_id"])
        etat = "🔄 MAJ dispo" if e["state"] == "on" else "✅"
        rapport += f"  {etat} {nom}\n"
    return rapport


def cmd_budget():
    tokens_in, tokens_out = get_token_usage()
    cout = (tokens_in * 0.000001) + (tokens_out * 0.000005)
    budget = CFG.get("anthropic_monthly_budget_usd", 10)
    pct = (cout / budget * 100) if budget > 0 else 0
    reste = max(0, budget - cout)

    if pct >= 100:
        icone = "🛑"
        statut = "DÉPASSÉ — commandes IA désactivées"
    elif pct >= 90:
        icone = "🚨"
        statut = "CRITIQUE"
    elif pct >= 80:
        icone = "⚠️"
        statut = "ATTENTION"
    elif pct >= 50:
        icone = "📊"
        statut = "MI-PARCOURS"
    else:
        icone = "✅"
        statut = "OK"

    return (
        f"💰 BUDGET API — {icone} {statut}\n━━━━━━━━━━━━\n"
        f"Tokens in  : {tokens_in:,}\n"
        f"Tokens out : {tokens_out:,}\n"
        f"Coût       : ${cout:.3f}\n"
        f"Budget     : ${budget}\n"
        f"Restant    : ${reste:.3f}\n"
        f"Usage      : {pct:.1f}%"
    )


def cmd_debug():
    """Diagnostic développeur"""
    now = datetime.now()
    anomalies = []

    last_mon = _watchdog.get("monitoring_last_run")
    if last_mon and (now - last_mon).total_seconds() > 900:
        anomalies.append(f"⚠️ Thread monitoring silencieux depuis {int((now-last_mon).total_seconds()//60)} min")

    last_pri = _watchdog.get("prises_last_run")
    if last_pri and (now - last_pri).total_seconds() > 600:
        anomalies.append(f"⚠️ Thread prises silencieux depuis {int((now-last_pri).total_seconds()//60)} min")

    bloque = _watchdog.get("offset_bloque_depuis")
    if bloque and (now - bloque).total_seconds() > 300:
        anomalies.append(f"🚨 Offset Telegram bloqué depuis {int((now-bloque).total_seconds()//60)} min")

    erreurs = _watchdog.get("erreurs", [])
    if len(erreurs) >= 3:
        anomalies.append(f"🚨 {len(erreurs)} exceptions — dernière : {erreurs[-1][1][:80]}")

    tokens_in, tokens_out = get_token_usage()
    budget = CFG.get("budget_mensuel", 10)
    cout = (tokens_in * 0.000001) + (tokens_out * 0.000005)
    if cout >= budget * 0.8:
        anomalies.append(f"⚠️ Budget tokens : {cout:.2f}€ / {budget}€ ({int(cout/budget*100)}%)")

    if not anomalies:
        return f"🔧 DEBUG — v{VERSION}\n✅ Aucune anomalie interne\nHeure VM : {now.strftime('%d/%m/%Y %H:%M:%S')}"

    rapport = f"🔧 DEBUG — v{VERSION}\n━━━━━━━━━━━━━━━━━━━━\n"
    rapport += "\n".join(anomalies)
    rapport += f"\n\nHeure VM : {now.strftime('%d/%m/%Y %H:%M:%S')}"
    return rapport


def cmd_logs():
    try:
        with open(LOG_PATH) as f:
            lignes = f.readlines()
        return "📋 LOGS:\n" + "".join(lignes[-20:])
    except Exception as e:
        return f"❌ Logs: {e}"


def cmd_memoire():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        'SELECT cle, valeur FROM memoire ORDER BY updated_at DESC LIMIT 20'
    ).fetchall()
    conn.close()
    rapport = "🧠 MÉMOIRE\n━━━━━━━━━━\n"
    for cle, valeur in rows:
        rapport += f"  {cle}: {valeur[:50]}\n"
    return rapport


def cmd_scan():
    """Lance un scan complet et envoie directement le résultat."""
    telegram_send("🔍 Scan Home Assistant en cours...")
    try:
        ha_refresh_areas()
        nb_areas = len(_areas_id_to_name)

        conn = sqlite3.connect(DB_PATH)
        for sql in [
            "UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id LIKE 'select.prise_%'",
            "UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id LIKE 'number.prise_%'",
            "UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id LIKE 'update.prise_%'",
            "UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id LIKE 'button.prise_%'",
            "UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id LIKE 'switch.prise_%_child_lock'",
            "UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id LIKE 'sensor.prise_%_current'",
            "UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id LIKE 'sensor.prise_%_voltage'",
            "UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id LIKE 'sensor.prise_%_energy'",
            "UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id LIKE 'automation.prise_%'",
            "UPDATE cartographie SET categorie='prise_connectee', sous_categorie='puissance' WHERE entity_id LIKE 'sensor.prise_%_power'",
            "UPDATE cartographie SET categorie='prise_connectee', sous_categorie='commande' WHERE entity_id LIKE 'switch.prise_%' AND entity_id NOT LIKE '%_child_lock'",
        ]:
            conn.execute(sql)
        conn.commit()
        conn.close()
        log.info("✅ Prises recatégorisées en base")

        etats = ha_get("states")
        if not etats:
            telegram_send("❌ Scan impossible — HA inaccessible")
            return ""
        nb_entites = len(etats)
        index = {e["entity_id"]: e for e in etats}

        conn = sqlite3.connect(DB_PATH)
        for e in etats:
            conn.execute(
                "INSERT OR REPLACE INTO entites (entity_id, state, attributes, updated_at) VALUES (?, ?, ?, ?)",
                (e["entity_id"], e["state"], json.dumps(e.get("attributes", {})), datetime.now().isoformat())
            )
        nb_avant = conn.execute("SELECT COUNT(*) FROM cartographie").fetchone()[0]
        conn.commit()
        conn.close()

        mem_set("ha_scan_date", datetime.now().isoformat())
        mem_set("ha_entites_count", nb_entites)

        decouverte_auto(etats)

        conn = sqlite3.connect(DB_PATH)
        nb_apres = conn.execute("SELECT COUNT(*) FROM cartographie").fetchone()[0]
        toutes_prises = conn.execute(
            "SELECT entity_id FROM cartographie WHERE categorie='prise_connectee' AND entity_id LIKE 'sensor.%'"
        ).fetchall()
        nb_prises = sum(
            1 for (eid,) in toutes_prises
            if index.get(eid, {}).get("attributes", {}).get("unit_of_measurement", "") in ["W", "w", "Watt"]
        )
        conn.close()

        nouvelles = max(0, nb_apres - nb_avant)
        traiter_entites_en_attente(index)

        telegram_send(
            f"✅ SCAN HA — {nb_entites} entités\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Catégorisées : {nb_apres}\n"
            f"Nouvelles    : {nouvelles}\n"
            f"Prises (puissance) : {nb_prises} surveillées\n"
            f"Pièces HA    : {nb_areas} areas chargées"
        )
        return ""
    except Exception as ex:
        log.error(f"❌ cmd_scan: {ex}")
        return f"❌ Erreur scan : {ex}"


def cmd_calendrier():
    """Affiche les événements du calendrier HA — utilisé pour les recommandations."""
    if not CFG.get("ha_url"):
        return "❌ HA non configuré"

    etats = ha_get("states")
    if not etats:
        return "❌ HA inaccessible"

    calendriers = [e for e in etats if e["entity_id"].startswith("calendar.")]
    if not calendriers:
        return "📅 Aucun calendrier détecté dans HA.\nIntégrez Google Calendar, CalDAV ou Local Calendar."

    rapport = "📅 CALENDRIERS HA\n━━━━━━━━━━━━━━━━━━\n"
    for cal in calendriers:
        attrs = cal.get("attributes", {})
        fname = attrs.get("friendly_name", cal["entity_id"])
        state = cal["state"]  # on = événement en cours
        message = attrs.get("message", "")
        start = attrs.get("start_time", "")
        end = attrs.get("end_time", "")

        icone = "🟢" if state == "on" else "⚪"
        rapport += f"\n{icone} {fname}"
        if state == "on" and message:
            rapport += f"\n  📌 {message}"
            if start:
                rapport += f"\n  ⏰ {start[:16]} → {end[:16] if end else '?'}"
        elif state == "off":
            if message:
                rapport += f"\n  Prochain : {message}"
                if start:
                    rapport += f" ({start[:16]})"
            else:
                rapport += f"\n  Pas d'événement à venir"
        rapport += "\n"

    rapport += "\n💡 Le script utilise le calendrier pour optimiser les recommandations :"
    rapport += "\n  • Absent → reporter les alertes non critiques"
    rapport += "\n  • Présent → suggérer les machines au bon moment"
    return rapport


def _ha_get_calendar_events():
    """Récupère les événements des 24 prochaines heures depuis les calendriers HA."""
    events = []
    try:
        etats = ha_get("states")
        if not etats:
            return events
        for e in etats:
            if e["entity_id"].startswith("calendar.") and e["state"] == "on":
                attrs = e.get("attributes", {})
                events.append({
                    "calendar": attrs.get("friendly_name", e["entity_id"]),
                    "message": attrs.get("message", ""),
                    "start": attrs.get("start_time", ""),
                    "end": attrs.get("end_time", ""),
                })
    except Exception:
        pass
    return events


def cmd_dashboard():
    """Pousse les stats AssistantIA vers HA sous forme de sensors.
    L'utilisateur peut ensuite les afficher dans Lovelace."""
    if not CFG.get("ha_url") or not CFG.get("ha_token"):
        return "❌ HA non configuré"

    headers = {"Authorization": f"Bearer {CFG['ha_token']}", "Content-Type": "application/json"}
    url_base = f"{CFG['ha_url']}/api/states"
    pushed = 0

    # 1. ROI
    eco = get_economies_mois()
    mois = datetime.now().strftime("%Y-%m")
    conn = sqlite3.connect(DB_PATH)
    tokens_row = conn.execute("SELECT tokens_in, tokens_out FROM tokens WHERE mois=?", (mois,)).fetchone()
    conn.close()
    total_tokens = (tokens_row[0] + tokens_row[1]) if tokens_row else 0
    cout_tokens = round(total_tokens * 0.000001, 2)
    roi = round(eco["total_eur"] / max(cout_tokens, 0.01), 1)

    sensors = {
        "sensor.assistantia_economies_mois": {
            "state": round(eco["total_eur"], 2),
            "attributes": {"unit_of_measurement": "€", "friendly_name": "AssistantIA Économies mois", "icon": "mdi:piggy-bank",
                           "nb_actions": eco["nb_actions"], "kwh": round(eco["total_kwh"], 1)}
        },
        "sensor.assistantia_cout_tokens": {
            "state": cout_tokens,
            "attributes": {"unit_of_measurement": "€", "friendly_name": "AssistantIA Coût tokens", "icon": "mdi:currency-eur",
                           "tokens": total_tokens}
        },
        "sensor.assistantia_roi": {
            "state": roi,
            "attributes": {"unit_of_measurement": "x", "friendly_name": "AssistantIA ROI", "icon": "mdi:chart-line"}
        },
    }

    # 2. Derniers cycles
    conn = sqlite3.connect(DB_PATH)
    last_cycle = conn.execute(
        "SELECT friendly_name, duree_min, conso_kwh, cout_eur FROM cycles_appareils WHERE fin IS NOT NULL ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if last_cycle:
        sensors["sensor.assistantia_dernier_cycle"] = {
            "state": last_cycle[0],
            "attributes": {"friendly_name": "AssistantIA Dernier cycle", "icon": "mdi:washing-machine",
                           "duree_min": last_cycle[1], "conso_kwh": last_cycle[2], "cout_eur": last_cycle[3]}
        }

    for eid, data_s in sensors.items():
        try:
            r = requests.post(f"{url_base}/{eid}", json=data_s, headers=headers, verify=False, timeout=5)
            if r.status_code in (200, 201):
                pushed += 1
        except Exception:
            pass

    return f"📊 Dashboard : {pushed} sensors poussés vers HA\n💡 Ajoutez-les dans Lovelace pour un tableau de bord visuel."


def cmd_profil():
    """Affiche le profil du foyer — base de mémoire des skills."""
    data, _ = skill_get("foyer")
    if not data:
        _lancer_questionnaire_foyer()
        return "👥 Profil non configuré — questionnaire lancé !"

    labels = {
        "foyer_personnes": "👥 Personnes",
        "foyer_presence": "🏠 Présence semaine",
        "foyer_solaire": "☀️ Panneaux solaires",
        "foyer_solaire_kwc": "☀️ Puissance installée",
        "foyer_chauffage": "🌡️ Chauffage",
        "foyer_eau_chaude": "🚿 Eau chaude",
        "foyer_assistant_vocal": "🗣️ Assistant vocal",
        "foyer_objectif": "🎯 Objectif principal",
    }
    rapport = "👥 PROFIL FOYER\n━━━━━━━━━━━━━━━━━━\n"
    for qid, label in labels.items():
        val = data.get(qid, "")
        if val and val != "n/a":
            rapport += f"  {label} : {val}\n"

    rapport += f"\n🧠 Ce profil alimente les skills :"
    if data.get("foyer_solaire") == "oui":
        rapport += f"\n  ☀️ fenetre_solaire, recommandations solaire"
    if data.get("foyer_chauffage") == "pac":
        rapport += f"\n  🌡️ comportement_pac, surveillance PAC"
    if data.get("foyer_objectif") == "reduire_facture":
        rapport += f"\n  💰 alertes standby renforcées, optimisation tarif"
    if data.get("foyer_assistant_vocal") in ("google", "alexa"):
        rapport += f"\n  🗣️ conseils coupe-veille via {data['foyer_assistant_vocal'].title()}"
    rapport += f"\n\n💡 /profil reset pour reconfigurer"
    return rapport


def cmd_economies():
    """Détail de toutes les économies générées — le nerf de la guerre."""
    conn = sqlite3.connect(DB_PATH)
    mois = datetime.now().strftime("%Y-%m")

    # Total mois
    total = conn.execute(
        "SELECT COALESCE(SUM(euros), 0), COALESCE(SUM(kwh_economises), 0), COUNT(*) "
        "FROM economies WHERE created_at LIKE ?", (f"{mois}%",)
    ).fetchone()

    # Par type
    par_type = conn.execute(
        "SELECT type, SUM(euros), SUM(kwh_economises), COUNT(*) "
        "FROM economies WHERE created_at LIKE ? GROUP BY type ORDER BY SUM(euros) DESC",
        (f"{mois}%",)
    ).fetchall()

    # Par jour (7 derniers jours)
    par_jour = conn.execute(
        "SELECT SUBSTR(created_at, 1, 10), SUM(euros), COUNT(*) "
        "FROM economies WHERE created_at >= ? GROUP BY SUBSTR(created_at, 1, 10) ORDER BY 1 DESC LIMIT 7",
        ((datetime.now() - timedelta(days=7)).isoformat(),)
    ).fetchall()

    # Coût tokens
    tokens_row = conn.execute(
        "SELECT tokens_in, tokens_out FROM tokens WHERE mois=?", (mois,)
    ).fetchone()
    total_tokens = (tokens_row[0] + tokens_row[1]) if tokens_row else 0
    cout_tokens = round(total_tokens * 0.000001, 2)

    conn.close()

    rapport = f"💰 ÉCONOMIES — {mois}\n━━━━━━━━━━━━━━━━━━\n"

    type_labels = {
        "cycle_solaire": "☀️ Cycles solaire",
        "coupe_veille": "🔇 Standby évité",
        "tarif_optimal": "⚡ Optimisation tarif",
        "surconso_evitee": "📉 Surconso évitée",
        "recommandation_appliquee": "💡 Recommandations",
    }

    rapport += f"\n📊 PAR SOURCE\n"
    for type_eco, euros, kwh, nb in par_type:
        label = type_labels.get(type_eco, type_eco)
        rapport += f"  {label}\n    +{euros:.2f}€ | {kwh:.1f} kWh | {nb} actions\n"

    rapport += f"\n📅 PAR JOUR (7 derniers)\n"
    for jour, euros, nb in par_jour:
        bar = "█" * min(20, int(euros * 20))
        rapport += f"  {jour[5:]} : +{euros:.2f}€ {bar} ({nb})\n"

    rapport += f"\n━━━━━━━━━━━━━━━━━━"
    rapport += f"\n💰 Total mois : {total[0]:.2f}€ | {total[1]:.1f} kWh | {total[2]} actions"
    rapport += f"\n🔑 Tokens : {cout_tokens:.2f}€"
    if cout_tokens > 0:
        roi = total[0] / cout_tokens
        rapport += f"\n📈 ROI : x{roi:.1f}"
        if roi >= 5:
            rapport += f" — chaque 1€ rapporte {roi:.0f}€"
    rapport += f"\n\n💡 Le script gagne de l'argent pendant que vous dormez."

    return rapport


def cmd_surveillance():
    """Vue complète de tout ce que le script surveille — rassure l'utilisateur."""
    conn = sqlite3.connect(DB_PATH)
    etats = ha_get("states") or []
    index = {e["entity_id"]: e for e in etats}

    nb_ha = len(etats)
    nb_carto = conn.execute("SELECT COUNT(*) FROM cartographie").fetchone()[0]
    nb_appareils = conn.execute("SELECT COUNT(*) FROM appareils WHERE surveiller=1").fetchone()[0]
    nb_ignores = conn.execute("SELECT COUNT(*) FROM appareils WHERE surveiller=0").fetchone()[0]
    nb_roles = conn.execute("SELECT COUNT(*) FROM roles").fetchone()[0]
    nb_baselines = conn.execute("SELECT COUNT(*) FROM baselines").fetchone()[0]
    nb_expertise = conn.execute("SELECT COUNT(*) FROM expertise").fetchone()[0]

    # Compter par catégorie
    categories = conn.execute(
        "SELECT categorie, COUNT(*) FROM cartographie GROUP BY categorie ORDER BY COUNT(*) DESC"
    ).fetchall()

    # Appareils surveillés
    appareils = conn.execute(
        "SELECT entity_id, type_appareil, nom_personnalise FROM appareils WHERE surveiller=1"
    ).fetchall()

    conn.close()

    rapport = "🛡️ SURVEILLANCE ACTIVE\n━━━━━━━━━━━━━━━━━━\n"
    rapport += f"\n📡 Home Assistant : {nb_ha} entités détectées"
    rapport += f"\n📊 Cartographie : {nb_carto} entités classées"
    rapport += f"\n🎯 Rôles : {nb_roles} auto-découverts"
    rapport += f"\n📈 Baselines : {nb_baselines} comportements appris"
    rapport += f"\n🧠 Expertise : {nb_expertise}/50 règles"

    rapport += f"\n\n🔌 APPAREILS SURVEILLÉS ({nb_appareils})"
    if appareils:
        for eid, type_app, nom in appareils:
            e = index.get(eid)
            state = ""
            if e:
                s = e.get("state", "?")
                u = e.get("attributes", {}).get("unit_of_measurement", "")
                if s not in ("unavailable", "unknown"):
                    state = f" — {s}{u}"
            icone = TYPES_APPAREILS.get(type_app, "🔌")
            rapport += f"\n  {icone}{state}"
    else:
        rapport += "\n  (aucun — tapez /appareils reset)"

    if nb_ignores > 0:
        rapport += f"\n\n⬜ Voie de garage : {nb_ignores} appareil(s) ignoré(s)"

    rapport += f"\n\n📋 CATÉGORIES"
    for cat, nb in categories[:8]:
        rapport += f"\n  {cat} : {nb}"

    # Statut des threads
    now = datetime.now()
    _ts = lambda key: int((now - _watchdog.get(key, now)).total_seconds())
    rapport += f"\n\n⚙️ THREADS"
    rapport += f"\n  Monitoring : {_ts('monitoring_last_run')}s"
    rapport += f"\n  Prises : {_ts('prises_last_run')}s"
    rapport += f"\n  Polling : {_ts('polling_last_update')}s"

    has_cycle = any(v == "actif" for v in _etat_prises.values())
    rapport += f"\n\n🎯 Mode : {'SNIPER 20s' if has_cycle else 'Veille 60s'}"

    return rapport


def cmd_commandes():
    """Menu principal — toutes les commandes en boutons Telegram."""
    # Catégories avec les commandes les plus utiles
    menus = {
        "⚡ Énergie": [
            ("⚡ Énergie", "/energie"),
            ("☀️ Solaire", "/solaire"),
            ("📈 ROI", "/roi"),
            ("⚡ Tarif", "/tarif"),
        ],
        "🏠 Maison": [
            ("🔋 Batteries", "/batteries"),
            ("📡 Zigbee", "/zigbee"),
            ("💾 NAS", "/nas"),
            ("🌡️ Chauffage", "/chauffage"),
        ],
        "🔌 Machines": [
            ("🔌 Appareils", "/appareils"),
            ("🔄 Cycles", "/cycles"),
            ("📋 Programmes", "/programmes"),
            ("🛡️ Surveillance", "/surveillance"),
        ],
        "🧠 IA": [
            ("🧠 Intelligence", "/intelligence"),
            ("📊 Baselines", "/baselines"),
            ("📚 Expertise", "/expertise"),
            ("🎯 Rôles", "/roles"),
        ],
        "📋 Outils": [
            ("📋 Audit", "/audit"),
            ("📅 Calendrier", "/calendrier"),
            ("💰 Économies", "/economies"),
            ("📖 Aide", "/aide"),
        ],
    }

    # Envoyer chaque catégorie comme un groupe de boutons
    for cat_name, cmds in menus.items():
        boutons = [{"text": label, "callback_data": f"cmd:{cmd.replace('/', '')}"} for label, cmd in cmds]
        telegram_send_buttons(cat_name, boutons)

    return ""


def cmd_appareils():
    """Affiche les appareils configurés sur les prises connectées, par catégorie."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT entity_id, type_appareil, nom_personnalise, surveiller FROM appareils ORDER BY type_appareil").fetchall()
    conn.close()
    if not rows:
        return "🔌 Aucun appareil configuré.\nLe questionnaire se lance au prochain démarrage."

    # Grouper par catégorie
    CATEGORIES = {
        "cycles": {"label": "🔄 GROS CONSOMMATEURS (cycles)", "types": {"lave_linge", "seche_linge", "lave_vaisselle", "congelateur", "four"}},
        "veille": {"label": "🔇 COUPE-VEILLE (standby)", "types": {"coupe_veille"}},
        "monitoring": {"label": "📊 MONITORING ÉNERGIE", "types": {"monitoring_energie"}},
        "autre": {"label": "🔌 AUTRES", "types": {"autre"}},
        "ignore": {"label": "⬜ VOIE DE GARAGE", "types": {"ignorer"}},
    }

    rapport = "🔌 APPAREILS SUR PRISES\n━━━━━━━━━━━━━━━━━━\n"
    for cat_key, cat_info in CATEGORIES.items():
        cat_rows = [r for r in rows if r[1] in cat_info["types"]]
        if cat_rows:
            rapport += f"\n{cat_info['label']}\n"
            for eid, type_app, nom, surv in cat_rows:
                rapport += f"  {'✅' if surv else '⬜'} {nom or TYPES_APPAREILS.get(type_app, type_app)}\n"

    rapport += f"\n💡 /appareils reset pour reconfigurer"
    return rapport


def cmd_programmes():
    """Affiche les profils de cycles appris pour chaque machine — données factuelles uniquement."""
    data, nb = skill_get("cycle_signatures")
    if not data:
        return "🔄 Aucun cycle enregistré — les profils s'apprennent automatiquement à chaque cycle."

    rapport = f"🔄 PROFILS DE CYCLES APPRIS\n━━━━━━━━━━━━━━━━━━\n"

    for eid, info in data.items():
        nom = info.get("nom", eid)
        nb_total = info.get("nb_cycles_total", info.get("nb_cycles", 0))
        rapport += f"\n🔌 {nom} ({nb_total} cycles)\n"

        progs = info.get("programmes", {})
        if progs:
            for prog_name, p in sorted(progs.items(), key=lambda x: -x[1].get("nb_cycles", 0)):
                duree = p.get("duree_moy", 0)
                conso = p.get("conso_moy", 0)
                puiss = p.get("puissance_moy", 0)
                nb_p = p.get("nb_cycles", 0)
                sig = p.get("signature", "?")
                prix = tarif_prix_kwh_actuel()
                cout = conso * prix
                rapport += f"  📊 {prog_name} ({nb_p}x)\n"
                rapport += f"    {duree:.0f} min | {conso:.2f} kWh | ~{puiss:.0f}W moy | {cout:.2f}€\n"
                rapport += f"    Signature : {sig}\n"
        else:
            duree = info.get("duree_moy", 0)
            conso = info.get("conso_moy", 0)
            rapport += f"  {duree:.0f} min | {conso:.2f} kWh\n"

    rapport += f"\n📊 {nb} cycles analysés au total"
    rapport += f"\n💡 Coûts calculés sur le tarif actuel ({tarif_prix_kwh_actuel():.4f}€/kWh)"
    return rapport


def cmd_cycles():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        '''SELECT friendly_name, debut, duree_min, conso_kwh, cout_eur, programme
           FROM cycles_appareils WHERE fin IS NOT NULL
           ORDER BY created_at DESC LIMIT 10'''
    ).fetchall()
    conn.close()
    if not rows:
        return "📊 Aucun cycle enregistré"
    rapport = "📊 DERNIERS CYCLES\n━━━━━━━━━━━━━━━━\n"
    for row in rows:
        fname, debut, duree, conso, cout = row[:5]
        prog = row[5] if len(row) > 5 else None
        date = debut[:16].replace("T", " ") if debut else "?"
        rapport += f"  {fname} — {date}\n    {duree}min | {conso:.2f}kWh | {cout:.2f}€"
        if prog:
            rapport += f"\n    🔍 {prog}"
        rapport += "\n"
    return rapport


def cmd_documentation():
    doc = f"""📖 ASSISTANT IA DOMOTIQUE v{VERSION}

Commandes disponibles :
━━━━━━━━━━━━━━━━━━━━
/audit          → État HA + analyse IA
/energie        → Solaire + Ecojoko + PAC + thermostats + météo
/solaire        → Production APSystems + Anker
/batteries      → Piles Zigbee + Anker
/zigbee         → Réseau Zigbee + LQI
/nas            → NAS Synology
/automatisations → Automatisations HA
/addons         → Add-ons HA
/cycles         → Historique cycles machines
/budget         → Consommation tokens API
/scan           → Rescanner et apprendre entités
/debug          → État interne du script
/logs           → 20 dernières lignes de log
/memoire        → Ce que l'IA a mémorisé
/documentation  → Cette aide
/export         → Exporte le script assistant.py
/script         → Exporte le script assistant.py
/claude         → Exécute autonomie Claude

Question libre → Réponse avec contexte HA pertinent"""
    envoyer_email("[AssistantIA] Documentation", doc)
    return doc


def cmd_probleme(description):
    """Auto-correction : lit le script, envoie à Sonnet, applique le patch, redémarre"""
    telegram_send(f"🔧 AUTO-CORRECTION\nProblème : {description}\n\nAnalyse en cours...")

    # 1. Lire le script via deploy server local
    try:
        req_read = urllib.request.Request("http://localhost:8501/read")
        cfg_secret = CFG.get("deploy_secret", "")
        req_read.add_header("Authorization", f"Bearer {cfg_secret}")
        resp_read = urllib.request.urlopen(req_read, timeout=15)
        script_data = json.loads(resp_read.read().decode())
        script_code = script_data["content"]
        script_lines = script_data["lines"]
        telegram_send(f"📄 Script lu : {script_lines} lignes")
    except Exception as e:
        return f"❌ Impossible de lire le script : {e}"

    # 2. Construire le prompt pour Sonnet
    system_prompt = (
        "Tu es un développeur Python expert spécialisé en domotique Home Assistant.\n"
        "L'utilisateur signale un problème dans le script assistant.py.\n"
        "Tu dois analyser le code et proposer UN SEUL patch chirurgical.\n\n"
        "RÈGLES STRICTES :\n"
        "- Réponds UNIQUEMENT en JSON valide, rien d'autre\n"
        "- Format : {\"old_str\": \"code_à_remplacer\", \"new_str\": \"nouveau_code\", \"explication\": \"ce que tu corriges\"}\n"
        "- old_str doit être une copie EXACTE du code actuel (espaces, indentation, guillemets)\n"
        "- old_str doit apparaître UNE SEULE FOIS dans le script\n"
        "- Ne change que le minimum nécessaire\n"
        "- Pas de markdown, pas de ```json, juste le JSON brut\n"
    )

    user_prompt = (
        f"PROBLÈME SIGNALÉ :\n{description}\n\n"
        f"SCRIPT COMPLET ({script_lines} lignes) :\n{script_code}"
    )

    # 3. Appeler Claude Sonnet
    try:
        client = anthropic.Anthropic(api_key=CFG["anthropic_api_key"])
        r = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        reponse_brute = r.content[0].text.strip()
        log_token_usage(r.usage.input_tokens, r.usage.output_tokens)
        telegram_send(f"🤖 Sonnet a répondu ({r.usage.output_tokens} tokens)")
    except Exception as e:
        return f"❌ Erreur appel Sonnet : {e}"

    # 4. Parser le JSON
    try:
        # Nettoyer markdown éventuel
        texte_json = reponse_brute.replace("```json", "").replace("```", "").strip()
        patch_data = json.loads(texte_json)
        old_code = patch_data.get("old_str", "")
        new_code = patch_data.get("new_str", "")
        explication = patch_data.get("explication", "pas d'explication")
    except Exception as e:
        telegram_send(f"❌ Réponse Sonnet non parsable :\n{reponse_brute[:500]}")
        return f"❌ JSON invalide : {e}"

    if not old_code:
        return f"❌ Patch vide — Sonnet n'a pas trouvé de correction.\nExplication : {explication}"

    # 5. Vérifier que old_str existe dans le script
    count = script_code.count(old_code)
    if count == 0:
        telegram_send(f"❌ old_str non trouvé dans le script\nExplication Sonnet : {explication}")
        return "❌ Patch non applicable — old_str absent du script"
    if count > 1:
        telegram_send(f"❌ old_str trouvé {count} fois — ambigu")
        return "❌ Patch ambigu — old_str présent plusieurs fois"

    # 6. Demander confirmation à l'utilisateur
    telegram_send(
        f"📋 PATCH PROPOSÉ\n━━━━━━━━━━━━━━\n"
        f"Explication : {explication}\n\n"
        f"Ancien ({len(old_code)} chars) :\n{old_code[:300]}...\n\n"
        f"Nouveau ({len(new_code)} chars) :\n{new_code[:300]}..."
    )
    telegram_send_buttons(
        "Appliquer ce patch ?",
        [
            {"text": "✅ Appliquer + Restart", "callback_data": "patch_appliquer:auto"},
            {"text": "❌ Annuler", "callback_data": "patch_annuler:auto"},
        ]
    )

    # Stocker le patch en mémoire pour le callback
    mem_set("patch_pending_old", old_code)
    mem_set("patch_pending_new", new_code)
    mem_set("patch_pending_expl", explication)

    return f"🔧 Patch en attente de validation"


def cmd_nettoyer_carto():
    """Nettoie la cartographie énergie — reclassifie les entités Anker et supprime le bruit"""
    conn = sqlite3.connect(DB_PATH)
    modifs = 0

    # ══ RÈGLE 1 : APSystems — garder uniquement les capteurs utiles ══
    # Les entités APSystems utiles : ecu_current_power, ecu_today_energy, ecu_lifetime_energy,
    # ecu_inverters, ecu_inverters_online, inverter_*_temperature
    # Tout le reste (frequency, voltage, signal, binary_sensor, switch, update) → a_ignorer
    rows = conn.execute(
        "SELECT entity_id FROM cartographie WHERE categorie='energie_solaire'"
    ).fetchall()

    # APSystems utiles = rôles solaires connus
    aps_utiles = set()
    for r_solaire in ["production_solaire_w", "production_solaire_kwh", "production_solaire_lifetime", "onduleurs_total", "onduleurs_online"]:
        eid_r = role_get(r_solaire)
        if eid_r:
            aps_utiles.add(eid_r)
    # Fallback si aucun rôle assigné
    if not aps_utiles:
        aps_utiles = {"sensor.ecu_current_power", "sensor.ecu_today_energy",
                      "sensor.ecu_lifetime_energy", "sensor.ecu_inverters",
                      "sensor.ecu_inverters_online"}

    for (eid,) in rows:
        eid_low = eid.lower()

        # Garder les capteurs ECU essentiels
        if eid in aps_utiles:
            continue

        # Garder les températures onduleurs (utile pour diagnostic)
        if "inverter_" in eid_low and "_temperature" in eid_low:
            continue

        # Entités Anker/Solarbank → reclassifier
        if "solarbank_e1600" in eid_low or "system_anker" in eid_low or "mi80_microinverter" in eid_low:
            # SOC / batterie
            if any(k in eid_low for k in ["etat_de_charge", "state_of_charge", "batterie", "battery",
                                           "capacite", "reserve_soc", "charge"]):
                conn.execute("UPDATE cartographie SET categorie='energie_batterie' WHERE entity_id=?", (eid,))
                modifs += 1
            # Production / puissance solaire
            elif any(k in eid_low for k in ["puissance_solaire", "solar_power", "energie_solaire_sb",
                                             "sortie_cc", "alimentation_domestique", "sortie_du_systeme",
                                             "decharge", "alimentation_ac"]):
                conn.execute("UPDATE cartographie SET categorie='energie_production' WHERE entity_id=?", (eid,))
                modifs += 1
            # Config / info → a_ignorer
            elif any(k in eid_low for k in ["firmware", "cloud", "code_d_erreur", "informations",
                                             "mise_a_jour", "devise", "prix", "type_de_prix",
                                             "banques_solaires", "onduleur", "temps_de_donnees",
                                             "economies", "rendement", "actualiser",
                                             "autoriser_l_exportation", "decharge_prioritaire",
                                             "mise_a_jour_automatique", "administration",
                                             "ota", "mode"]):
                conn.execute("UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id=?", (eid,))
                modifs += 1
            # Reste Anker non classé → a_ignorer
            else:
                conn.execute("UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id=?", (eid,))
                modifs += 1
            continue

        # Onduleurs individuels (frequency, voltage, signal) → a_ignorer
        if "inverter_" in eid_low and any(k in eid_low for k in ["frequency", "voltage", "signal"]):
            conn.execute("UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id=?", (eid,))
            modifs += 1
            continue

        # binary_sensor, switch, button, update, automation dans energie_solaire → a_ignorer
        domaine = eid.split(".")[0]
        if domaine in ("binary_sensor", "switch", "button", "update", "automation", "select", "number"):
            conn.execute("UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id=?", (eid,))
            modifs += 1
            continue

        # Ecojoko surplus → energie_conso
        if "ecojoko" in eid_low and "surplus" in eid_low:
            conn.execute("UPDATE cartographie SET categorie='energie_conso' WHERE entity_id=?", (eid,))
            modifs += 1
            continue

        # Energy current/next hour (prévision) → energie_prevision
        if "energy_current_hour" in eid_low or "energy_next_hour" in eid_low:
            conn.execute("UPDATE cartographie SET categorie='energie_prevision' WHERE entity_id=?", (eid,))
            modifs += 1
            continue

    # ══ RÈGLE 2 : sensor.22081212ug_charger_type dans energie_batterie → c'est pas une batterie ══
    conn.execute(
        "UPDATE cartographie SET categorie='a_ignorer' WHERE entity_id='sensor.22081212ug_charger_type'"
    )

    conn.commit()

    # Rapport
    counts = {}
    for (cat, nb) in conn.execute(
        "SELECT categorie, COUNT(*) FROM cartographie WHERE categorie LIKE 'energie%' GROUP BY categorie"
    ).fetchall():
        counts[cat] = nb
    conn.close()

    rapport = f"🧹 NETTOYAGE CARTOGRAPHIE\n━━━━━━━━━━━━━━━━━━\n"
    rapport += f"Modifications : {modifs}\n\n"
    for cat, nb in sorted(counts.items()):
        rapport += f"  [{cat}] : {nb} entités\n"
    rapport += f"\n✅ Terminé — /diag_carto pour vérifier"
    return rapport


def cmd_test_meteo():
    """Test surveillance météo — force un check immédiat sans filtre jour/heure"""
    etats = ha_get("states")
    if not etats:
        return "❌ HA inaccessible"
    index = {e["entity_id"]: e for e in etats}
    rapport = "🧪 TEST SURVEILLANCE MÉTÉO\n━━━━━━━━━━━━━━━━━━\n"

    # 1. Vigilance départementale
    alerte_93 = index.get(role_get("alerte_meteo") or "sensor.93_weather_alert")
    if alerte_93:
        attrs = alerte_93.get("attributes", {})
        rapport += f"\n📊 Vigilance 93 : {alerte_93['state']}\n"
        NIVEAUX = {"Vert": 0, "Jaune": 1, "Orange": 2, "Rouge": 3}
        for risque in ["Vent violent", "Pluie-inondation", "Orages", "Neige-verglas", "Grand-froid", "Inondation"]:
            couleur = attrs.get(risque, "Vert")
            niveau = NIVEAUX.get(couleur, 0)
            if niveau == 0:
                icone = "🟢"
            elif niveau == 1:
                icone = "🟡"
            elif niveau == 2:
                icone = "🟠"
            else:
                icone = "🔴"
            rapport += f"  {icone} {risque} : {couleur}\n"
    else:
        rapport += "\n❌ sensor.93_weather_alert non trouvé\n"

    # 2. Pluie prochaine heure
    rain = index.get(role_get("meteo_pluie") or "sensor.pavillons_sous_bois_next_rain")
    if rain:
        rain_attrs = rain.get("attributes", {})
        forecast_1h = rain_attrs.get("1_hour_forecast", {})
        rapport += f"\n🌧️ Pluie prochaine heure :\n"
        if isinstance(forecast_1h, dict):
            pluie_prevue = [t for t, v in forecast_1h.items() if "pluie" in v.lower()]
            sec = [t for t, v in forecast_1h.items() if "sec" in v.lower()]
            if pluie_prevue:
                rapport += f"  🌧️ Pluie prévue : {', '.join(pluie_prevue)}\n"
            else:
                rapport += f"  ✅ Temps sec ({len(sec)} créneaux)\n"
        else:
            rapport += f"  état: {rain['state']}\n"

    # 3. Rafales
    weather = index.get("weather.pavillons_sous_bois")
    if weather:
        w_attrs = weather.get("attributes", {})
        vent = w_attrs.get("wind_speed", 0)
        rafales = w_attrs.get("wind_gust_speed", 0)
        rapport += f"\n💨 Vent : {vent} km/h | Rafales : {rafales} km/h\n"
        try:
            r_val = float(rafales)
            if r_val >= 80:
                rapport += f"  🔴 RAFALES FORTES → alerte déclenchée\n"
            elif r_val >= 60:
                rapport += f"  🟡 Rafales modérées → alerte déclenchée\n"
            else:
                rapport += f"  ✅ Sous le seuil (60 km/h)\n"
        except Exception:
            pass

    # 4. Neige
    snow = index.get(role_get("meteo_risque_neige") or "sensor.pavillons_sous_bois_snow_chance")
    if snow:
        rapport += f"\n❄️ Risque neige : {snow['state']}%\n"

    # 5. Pluie
    rain_chance = index.get(role_get("meteo_risque_pluie") or "sensor.pavillons_sous_bois_rain_chance")
    if rain_chance:
        rapport += f"🌧️ Risque pluie : {rain_chance['state']}%\n"

    # 6. Prévisions J+1
    rapport += "\n📅 PRÉVISIONS PROCHAINS JOURS :\n"
    forecast = ha_get_forecast("weather.pavillons_sous_bois", "daily")
    if forecast:
        if True:
            for prev in forecast[:3]:
                dt = prev.get("datetime", "?")[:10]
                cond = prev.get("condition", "?")
                precip = prev.get("precipitation", 0) or 0
                precip_prob = prev.get("precipitation_probability", 0) or 0
                temp_max = prev.get("temperature", "?")
                temp_min = prev.get("templow", "?")
                wind = prev.get("wind_speed", 0) or 0
                alertes_j = []
                try:
                    if float(precip) >= 10:
                        alertes_j.append("🌧️ FORTES PLUIES")
                    elif float(precip) >= 5:
                        alertes_j.append("🌧️ Pluie")
                except Exception:
                    pass
                try:
                    if float(wind) >= 50:
                        alertes_j.append("💨 VENT FORT")
                except Exception:
                    pass
                try:
                    if temp_min != "?" and float(temp_min) <= 0:
                        alertes_j.append("🥶 GEL")
                except Exception:
                    pass
                if cond in ("snowy", "snowy-rainy"):
                    alertes_j.append("❄️ NEIGE")
                flag = " ← ⚠️" if alertes_j else ""
                rapport += f"  {dt} : {cond} | {temp_min}→{temp_max}°C | {precip}mm ({int(float(precip_prob))}%) | {int(float(wind))} km/h{flag}\n"
                if alertes_j:
                    rapport += f"    {' | '.join(alertes_j)}\n"
    else:
        rapport += "  ⚠️ Pas de forecast disponible — vérifier l'intégration Météo France\n"

    # 7. Forcer un envoi d'alerte test
    rapport += "\n━━━━━━━━━━━━━━━━━━\n🧪 Envoi alerte test...\n"
    _alerter_si_nouveau(
        "meteo_test_alert",
        "🧪 TEST ALERTE MÉTÉO\n"
        "Ceci est un test de la surveillance météo.\n"
        "Les alertes réelles fonctionneront de la même façon.\n"
        "✅ Système opérationnel",
        delai_h=0
    )
    rapport += "✅ Alerte test envoyée"

    return rapport


def cmd_diag_forecast():
    """Debug : teste tous les moyens de récupérer le forecast"""
    rapport = "🔧 DIAG FORECAST\n━━━━━━━━━━━━━━\n"

    # Test 1 : attributs weather entity
    rapport += "\n[1] Attributs weather.pavillons_sous_bois :\n"
    e = ha_get_etat("weather.pavillons_sous_bois")
    if e:
        attrs = e.get("attributes", {})
        forecast = attrs.get("forecast", None)
        if forecast:
            rapport += f"  ✅ forecast dans attributs : {len(forecast)} entrées\n"
            rapport += f"  Premier : {json.dumps(forecast[0])[:200]}\n"
        else:
            rapport += f"  ❌ Pas de forecast dans attributs\n"
            rapport += f"  Clés dispo : {', '.join(list(attrs.keys())[:15])}\n"

    # Test 2 : service weather.get_forecasts daily
    rapport += "\n[2] Service weather.get_forecasts (daily) :\n"
    try:
        result = ha_post("services/weather/get_forecasts", {
            "entity_id": "weather.pavillons_sous_bois",
            "type": "daily"
        })
        rapport += f"  Type retour : {type(result).__name__}\n"
        rapport += f"  Contenu : {json.dumps(result, ensure_ascii=False)[:500]}\n"
    except Exception as ex:
        rapport += f"  ❌ Erreur : {ex}\n"

    # Test 3 : service weather.get_forecasts hourly
    rapport += "\n[3] Service weather.get_forecasts (hourly) :\n"
    try:
        result2 = ha_post("services/weather/get_forecasts", {
            "entity_id": "weather.pavillons_sous_bois",
            "type": "hourly"
        })
        rapport += f"  Type retour : {type(result2).__name__}\n"
        if result2 and isinstance(result2, dict):
            for k, v in result2.items():
                if isinstance(v, dict) and "forecast" in v:
                    fc = v["forecast"]
                    rapport += f"  ✅ Clé '{k}' → {len(fc)} entrées\n"
                    if fc:
                        rapport += f"  Premier : {json.dumps(fc[0], ensure_ascii=False)[:200]}\n"
                elif isinstance(v, list):
                    rapport += f"  Clé '{k}' → liste {len(v)} éléments\n"
                else:
                    rapport += f"  Clé '{k}' → {str(v)[:100]}\n"
        else:
            rapport += f"  Brut : {str(result2)[:300]}\n"
    except Exception as ex:
        rapport += f"  ❌ Erreur : {ex}\n"

    # Test 4 : endpoint calendar-like
    rapport += "\n[4] ha_get_forecast() :\n"
    fc = ha_get_forecast()
    rapport += f"  Résultat : {len(fc)} entrées\n"
    if fc:
        rapport += f"  Premier : {json.dumps(fc[0], ensure_ascii=False)[:200]}\n"

    return rapport


def cmd_diag_meteo():
    """Liste toutes les entités météo France dans HA"""
    etats = ha_get("states")
    if not etats:
        return "❌ HA inaccessible"
    rapport = "🌦️ DIAG MÉTÉO FRANCE\n━━━━━━━━━━━━━━━━━━\n"
    keywords = ["meteo_france", "meteofrance", "vigilance", "alerte", "weather", "meteo",
                "pluie", "vent", "neige", "verglas", "orage", "inondation", "tempete",
                "rain", "wind", "snow", "storm", "flood"]
    found = []
    for e in etats:
        eid = e["entity_id"].lower()
        fname = e.get("attributes", {}).get("friendly_name", "").lower()
        combined = eid + " " + fname
        if any(k in combined for k in keywords):
            attrs = e.get("attributes", {})
            rapport += f"\n{e['entity_id']}\n"
            rapport += f"  état: {e['state']}\n"
            rapport += f"  nom: {attrs.get('friendly_name', '')}\n"
            for k, v in attrs.items():
                if k not in ("friendly_name", "icon", "entity_picture"):
                    rapport += f"  {k}: {str(v)[:100]}\n"
            found.append(e["entity_id"])
    rapport += f"\n━━━━━━━━━━━━━━━━━━\nTotal: {len(found)} entités"
    return rapport


def cmd_apprentissage():
    """Affiche le journal d'apprentissage : échecs, succès, leçons"""
    conn = sqlite3.connect(DB_PATH)

    # Stats globales
    total = conn.execute("SELECT COUNT(*) FROM decisions_log").fetchone()[0]
    echecs = conn.execute("SELECT COUNT(*) FROM decisions_log WHERE succes=0").fetchone()[0]
    succes = conn.execute("SELECT COUNT(*) FROM decisions_log WHERE succes=1").fetchone()[0]
    nb_expertise = conn.execute("SELECT COUNT(*) FROM expertise").fetchone()[0]

    rapport = f"📕 APPRENTISSAGE CONTINU\n━━━━━━━━━━━━━━━━━━\n"
    rapport += f"Décisions tracées : {total}\n"
    rapport += f"Échecs : {echecs} | Succès : {succes}\n"
    rapport += f"Expertise : {nb_expertise} règles apprises\n"

    # Taux de réussite
    if echecs + succes > 0:
        taux = succes / (echecs + succes) * 100
        if taux >= 90:
            rapport += f"Taux de réussite : {taux:.0f}% 🟢\n"
        elif taux >= 70:
            rapport += f"Taux de réussite : {taux:.0f}% 🟡\n"
        else:
            rapport += f"Taux de réussite : {taux:.0f}% 🔴\n"

    # 5 derniers échecs
    dernieres_erreurs = conn.execute(
        "SELECT action, resultat, created_at FROM decisions_log "
        "WHERE succes=0 ORDER BY created_at DESC LIMIT 5"
    ).fetchall()
    if dernieres_erreurs:
        rapport += "\n❌ DERNIERS ÉCHECS :\n"
        for action, res, date in dernieres_erreurs:
            rapport += f"  [{date[:16]}] {action}\n    {res[:80]}\n"

    # Échecs récurrents
    recurrents = conn.execute(
        "SELECT action, COUNT(*) as nb FROM decisions_log "
        "WHERE succes=0 AND created_at > datetime('now', '-7 days') "
        "GROUP BY action HAVING nb >= 2 ORDER BY nb DESC LIMIT 5"
    ).fetchall()
    if recurrents:
        rapport += "\n🔁 ÉCHECS RÉCURRENTS (7j) :\n"
        for action, nb in recurrents:
            rapport += f"  {action} : {nb} fois\n"

    # Évolution expertise
    recentes = conn.execute(
        "SELECT categorie, insight, confiance FROM expertise "
        "ORDER BY updated_at DESC LIMIT 5"
    ).fetchall()
    if recentes:
        rapport += "\n📚 DERNIÈRES LEÇONS :\n"
        for cat, ins, conf in recentes:
            etoiles = "★" * min(5, int(conf * 5))
            rapport += f"  {etoiles} [{cat}] {ins}\n"

    conn.close()
    return rapport


def cmd_expertise():
    """Affiche l'expertise accumulée par l'IA"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT categorie, insight, confiance, nb_validations, created_at FROM expertise "
        "ORDER BY confiance DESC"
    ).fetchall()
    nb_decisions = conn.execute("SELECT COUNT(*) FROM decisions_log").fetchone()[0]
    conn.close()

    rapport = f"📚 EXPERTISE IA — {len(rows)} règles apprises\n━━━━━━━━━━━━━━━━━━\n"

    if not rows:
        rapport += "Aucune expertise encore — lance /analyse pour commencer.\n"
        rapport += "L'expertise se construit automatiquement toutes les 6h."
        return rapport

    # Grouper par catégorie
    categories = {}
    for cat, insight, conf, nb_val, created in rows:
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((insight, conf, nb_val, created))

    for cat, insights in sorted(categories.items()):
        rapport += f"\n[{cat.upper()}]\n"
        for insight, conf, nb_val, created in insights:
            etoiles = "★" * min(5, int(conf * 5)) + "☆" * (5 - min(5, int(conf * 5)))
            rapport += f"  {etoiles} {insight}\n"
            rapport += f"    Confiance {conf:.0%} | {nb_val} validation(s) | depuis {created[:10]}\n"

    rapport += f"\n📊 {nb_decisions} décisions tracées\n"
    rapport += "\n💡 Confiance : ★☆☆☆☆ = nouvelle | ★★★★★ = validée par les données"

    return rapport


def cmd_analyse():
    """Déclenche une analyse IA immédiate sur les données accumulées"""
    telegram_send("🧠 Analyse en cours — Claude examine vos données...")
    etats = ha_get("states")
    if not etats:
        return "❌ HA inaccessible"
    index = {e["entity_id"]: e for e in etats}
    now = datetime.now()
    try:
        _analyse_ia_periodique(etats, index, now)
        return ""  # Le message est envoyé par _analyse_ia_periodique
    except Exception as e:
        return f"❌ Erreur analyse : {e}"


def cmd_diag_hc():
    """Cherche les heures creuses dans HA (Linky, Ecojoko, attributs)"""
    etats = ha_get("states")
    if not etats:
        return "❌ HA inaccessible"
    rapport = "🔧 RECHERCHE HEURES CREUSES\n━━━━━━━━━━━━━━━━━━\n"
    trouvees = []

    for e in etats:
        eid = e["entity_id"]
        attrs = e.get("attributes", {})
        fname = attrs.get("friendly_name", "")

        # Chercher dans les entity_id
        eid_low = eid.lower()
        if any(k in eid_low for k in ["heure_creuse", "off_peak", "offpeak", "hc_hp", "hp_hc", "linky", "tarif"]):
            rapport += f"\n📌 {eid}\n  {fname} = {e['state']}\n"
            for k, v in attrs.items():
                if isinstance(v, str) and len(v) < 200:
                    rapport += f"  {k}: {v}\n"
                elif isinstance(v, (int, float, bool)):
                    rapport += f"  {k}: {v}\n"
            trouvees.append(eid)

        # Chercher dans les attributs
        for k, v in attrs.items():
            k_low = str(k).lower()
            v_str = str(v).lower()
            if any(kw in k_low for kw in ["heure_creuse", "off_peak", "offpeak", "hc", "tarif_actuel"]):
                if eid not in trouvees:
                    rapport += f"\n📌 {eid} (attr: {k})\n  {fname} = {e['state']}\n  {k}: {v}\n"
                    trouvees.append(eid)
            if any(kw in v_str for kw in ["22:00", "23:00", "06:00", "heure creuse", "off peak"]):
                if eid not in trouvees:
                    rapport += f"\n📌 {eid} (valeur contient HC)\n  {fname} = {e['state']}\n  {k}: {v}\n"
                    trouvees.append(eid)

    if not trouvees:
        rapport += "\nAucune entité HC trouvée dans HA.\nLes heures creuses seront cherchées via Enedis."

    return rapport


def cmd_diag_prises():
    """Diagnostic prises — montre exactement ce que surveillance_prises surveille"""
    etats = ha_get("states")
    if not etats:
        return "❌ HA inaccessible"
    index = {e["entity_id"]: e for e in etats}

    rapport = "🔧 DIAG PRISES\n━━━━━━━━━━━━━━\n"

    # 1. Ce que la cartographie dit
    prises = cartographie_get_par_categorie("prise_connectee")
    rapport += f"\nCartographie prise_connectee : {len(prises)} entités\n"

    # 2. Filtrage sensor.* avec unité W
    prises_w = []
    prises_non_w = []
    for eid, sc, pc in prises:
        if not eid.startswith("sensor."):
            continue
        e = index.get(eid)
        if not e:
            rapport += f"  ❌ {eid} — ABSENT de HA\n"
            continue
        unit = e.get("attributes", {}).get("unit_of_measurement", "")
        etat = e["state"]
        fname = e.get("attributes", {}).get("friendly_name", eid)
        if unit in ("W", "w", "Watt"):
            prises_w.append((eid, fname, etat, unit))
        else:
            prises_non_w.append((eid, fname, etat, unit))

    rapport += f"\n✅ SURVEILLÉES (sensor.* + unité W) : {len(prises_w)}\n"
    for eid, fname, etat, unit in prises_w:
        seuil = "🟢 >200W" if etat not in ("unavailable", "unknown") and float(etat) > 200 else "⚫"
        rapport += f"  {seuil} {fname} = {etat} {unit}\n    {eid}\n"

    if prises_non_w:
        rapport += f"\n⚠️ IGNORÉES (pas unité W) : {len(prises_non_w)}\n"
        for eid, fname, etat, unit in prises_non_w:
            rapport += f"  {fname} = {etat} {unit}\n    {eid}\n"

    # 3. Chercher des sensor puissance NON catégorisés
    rapport += "\n🔍 PUISSANCE NON CATÉGORISÉES :\n"
    for e in etats:
        eid = e["entity_id"]
        if not eid.startswith("sensor."):
            continue
        unit = e.get("attributes", {}).get("unit_of_measurement", "")
        if unit not in ("W", "w", "Watt"):
            continue
        carto = cartographie_get(eid)
        if carto and carto[0] == "prise_connectee":
            continue  # Déjà catégorisé
        fname = e.get("attributes", {}).get("friendly_name", eid)
        if any(k in eid.lower() for k in ["power", "puissance", "watt"]):
            cat = carto[0] if carto else "NON CATÉGORISÉ"
            rapport += f"  ⚠️ {fname} = {e['state']} W | carto: {cat}\n    {eid}\n"

    return rapport


def cmd_diag_ecojoko():
    """Diagnostic Ecojoko — toutes les entités avec leurs valeurs"""
    etats = ha_get("states")
    if not etats:
        return "❌ HA inaccessible"
    rapport = "🔧 DIAG ECOJOKO\n━━━━━━━━━━━━━━\n"
    for e in etats:
        eid = e["entity_id"].lower()
        fname = e.get("attributes", {}).get("friendly_name", "")
        if "ecojoko" in eid or "ecojoko" in fname.lower():
            unite = e.get("attributes", {}).get("unit_of_measurement", "")
            dc = e.get("attributes", {}).get("device_class", "")
            etat = e["state"]
            icone = "❌" if etat in ("unavailable", "unknown") else "✅"
            rapport += f"  {icone} {e['entity_id']}\n    {fname} = {etat} {unite} (dc:{dc})\n"
    return rapport


def cmd_diag_nas():
    """Diagnostic NAS — affiche toutes les entités NAS avec leur état"""
    etats = ha_get("states")
    if not etats:
        return "❌ HA inaccessible"
    index = {e["entity_id"]: e for e in etats}
    rapport = "🔧 DIAG NAS\n━━━━━━━━━━━━━━\n"

    # Toutes les entités avec synology, syno, nas dans le nom
    for e in etats:
        eid = e["entity_id"].lower()
        fname = e.get("attributes", {}).get("friendly_name", "")
        if any(k in eid or k in fname.lower() for k in ["synology", "syno2", "syno_", "nas_"]):
            domaine = e["entity_id"].split(".")[0]
            unite = e.get("attributes", {}).get("unit_of_measurement", "")
            dc = e.get("attributes", {}).get("device_class", "")
            etat = e["state"]
            icone = "❌" if etat in ("unavailable", "unknown") else "✅"
            rapport += f"  {icone} [{domaine}] {e['entity_id']}\n"
            rapport += f"    {fname} = {etat} {unite} (dc:{dc})\n"

    return rapport


def cmd_diag_carto():
    """Diagnostic cartographie — liste toutes les entités par catégorie énergie"""
    conn = sqlite3.connect(DB_PATH)
    rapport = "🔧 DIAG CARTOGRAPHIE\n━━━━━━━━━━━━━━━━━━\n"
    for cat in ["energie_solaire", "energie_chauffage", "energie_conso", "energie_batterie", "energie_production", "energie_prevision"]:
        rows = conn.execute(
            "SELECT entity_id, sous_categorie, friendly_name FROM cartographie WHERE categorie=? ORDER BY entity_id",
            (cat,)
        ).fetchall()
        rapport += f"\n[{cat}] ({len(rows)} entités)\n"
        for eid, sc, fn in rows:
            rapport += f"  {fn or eid} | {sc}\n"
    conn.close()
    return rapport


def cmd_diag_energie():
    """Diagnostic énergie — affiche cartographie + états HA pour debug"""
    etats = ha_get("states")
    if not etats:
        return "❌ HA inaccessible"
    index = {e["entity_id"]: e for e in etats}
    rapport = "🔧 DIAG ÉNERGIE\n━━━━━━━━━━━━━━\n"

    # 1. Micro-onduleurs APSystems
    rapport += "\n📡 APSYSTEMS (entités HA) :\n"
    for e in etats:
        eid = e["entity_id"]
        if "apsystem" in eid.lower() or "microonduleur" in eid.lower() or "micro_onduleur" in eid.lower():
            etat = e["state"]
            unite = e.get("attributes", {}).get("unit_of_measurement", "")
            icone = "❌" if etat in ("unavailable", "unknown") else "✅"
            rapport += f"  {icone} {eid} = {etat} {unite}\n"

    # 2. PAC / climate
    rapport += "\n🌡️ PAC / CLIMATE :\n"
    for e in etats:
        if e["entity_id"].startswith("climate."):
            carto = cartographie_get(e["entity_id"])
            cat_str = carto[0] if carto else "NON CARTOGRAPHIÉ"
            rapport += f"  {e['entity_id']} = {e['state']} | carto: {cat_str}\n"

    # 3. Prises avec sèche-linge
    rapport += "\n🔌 PRISES CONNECTÉES (cartographie) :\n"
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT entity_id, sous_categorie, piece, friendly_name FROM cartographie WHERE categorie='prise_connectee'"
    ).fetchall()
    conn.close()
    for eid, sc, pc, fn in rows:
        e = index.get(eid)
        if e:
            etat = e["state"]
            unite = e.get("attributes", {}).get("unit_of_measurement", "")
            rapport += f"  {fn or eid} [{sc}] = {etat} {unite}\n"
        else:
            rapport += f"  ❌ {fn or eid} — absent de HA\n"

    # 4. Sèche-linge spécifique
    rapport += "\n🔍 RECHERCHE SÈCHE-LINGE :\n"
    for e in etats:
        eid = e["entity_id"].lower()
        fn = e.get("attributes", {}).get("friendly_name", "").lower()
        if any(k in eid or k in fn for k in ["seche", "sèche", "dryer", "secheuse"]):
            carto = cartographie_get(e["entity_id"])
            cat_str = carto[0] if carto else "NON CARTOGRAPHIÉ"
            rapport += f"  {e['entity_id']} = {e['state']} | carto: {cat_str}\n"

    # 5. Catégories énergie dans cartographie
    rapport += "\n📊 CARTOGRAPHIE ÉNERGIE :\n"
    conn = sqlite3.connect(DB_PATH)
    for cat in ["energie_solaire", "energie_chauffage", "energie_conso", "energie_batterie", "energie_production"]:
        rows = conn.execute(
            "SELECT entity_id FROM cartographie WHERE categorie=?", (cat,)
        ).fetchall()
        rapport += f"  [{cat}] : {len(rows)} entités\n"
        for (eid,) in rows[:5]:
            e = index.get(eid)
            etat = e["state"] if e else "ABSENT HA"
            icone = "❌" if etat in ("unavailable", "unknown", "ABSENT HA") else "✅"
            rapport += f"    {icone} {eid} = {etat}\n"
    conn.close()

    return rapport


def cmd_script_export():
    """Exporte le SCRIPT assistant.py via Telegram"""
    try:
        with open(os.path.join(BASE_DIR, "assistant.py"), "r") as f:
            script = f.read()
        
        for i in range(0, len(script), 3500):
            telegram_send(script[i:i+3500])
            time.sleep(0.2)
        
        return "✅ Script exporté en chunks"
    except Exception as e:
        return f"❌ Erreur export: {e}"


def cmd_watches():
    """Liste les alertes dynamiques actives"""
    try:
        conn = sqlite3.connect(DB_PATH)
        watches = conn.execute("SELECT id, entity_pattern, condition, state_value, message, cooldown_min, last_triggered, active FROM watches ORDER BY id").fetchall()
        conn.close()
    except Exception as e:
        return f"❌ Erreur: {e}"

    if not watches:
        return "📭 Aucune alerte configurée.\nDemande-moi en langage naturel, ex: \"Préviens-moi si un onduleur passe offline\""

    lignes = ["🔔 ALERTES DYNAMIQUES", "━━━━━━━━━━━━━━━━━━"]
    for wid, pattern, cond, val, msg, cooldown, last, active in watches:
        status = "🟢" if active else "🔴"
        desc = f"{status} #{wid} — {pattern}"
        desc += f"\n   Condition: {cond}"
        if val:
            desc += f" {val}"
        desc += f"\n   Message: {msg[:60]}"
        desc += f"\n   Cooldown: {cooldown}min"
        if last:
            desc += f"\n   Dernière: {last[:16]}"
        lignes.append(desc)
    return "\n".join(lignes)



# =============================================================================
# FEATURES v7.61 — Auto-update, conso fantôme, congélateur, mode vacances
# =============================================================================

def _alerte_conso_fantome_nocturne(index, now):
    """Détecte une conso anormale entre 1h-5h. CRASH-PROOF."""
    try:
        if not (1 <= now.hour < 5):
            return
        eid_conso = role_get("conso_temps_reel")
        if not eid_conso or eid_conso not in index:
            return
        try:
            conso_w = float(index[eid_conso]["state"])
        except (ValueError, TypeError):
            return
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT AVG(valeur_moyenne) FROM baselines WHERE entity_id=? AND heure BETWEEN 1 AND 4 AND nb_mesures >= 5",
            (eid_conso,)
        ).fetchone()
        conn.close()
        baseline = rows[0] if rows and rows[0] else 200
        seuil = baseline + 150
        if conso_w > seuil:
            _alerter_si_nouveau(
                "conso_fantome_nuit",
                f"👻 CONSO ANORMALE LA NUIT\n━━━━━━━━━━━━━━━━━━\n"
                f"Il est {now.strftime('%H:%M')} — conso réseau : {conso_w:.0f}W\n"
                f"Habituellement : ~{baseline:.0f}W\nSurplus : +{conso_w - baseline:.0f}W\n\n"
                f"Quelque chose est peut-être resté allumé.",
                delai_h=6
            )
    except Exception as e:
        log.debug(f"Conso fantôme: {e}")


def _alerte_congelateur_coupure(index, now):
    """Si coupure EDF > 2h → alerte congélateur au retour. CRASH-PROOF."""
    try:
        eid_conso = role_get("conso_temps_reel")
        if not eid_conso:
            return
        e = index.get(eid_conso)
        if not e:
            return
        state = e.get("state", "")
        if state in ("unavailable", "unknown"):
            debut = mem_get("coupure_edf_debut")
            if not debut:
                mem_set("coupure_edf_debut", now.isoformat())
        else:
            debut = mem_get("coupure_edf_debut")
            if debut:
                mem_set("coupure_edf_debut", "")
                try:
                    dt_debut = datetime.fromisoformat(debut)
                    duree_h = (now - dt_debut).total_seconds() / 3600
                    if duree_h >= 2:
                        _alerter_si_nouveau(
                            "congelateur_coupure",
                            f"⚡ COUPURE EDF DE {duree_h:.1f}H\n━━━━━━━━━━━━━━━━━━\n"
                            f"Début : {dt_debut.strftime('%H:%M')} | Retour : {now.strftime('%H:%M')}\n\n"
                            f"⚠️ Vérifiez le congélateur — chaîne du froid potentiellement compromise.",
                            delai_h=24
                        )
                except Exception:
                    pass
    except Exception as e:
        log.debug(f"Alerte congélateur: {e}")


def _detecter_mode_vacances(now):
    """Si aucune interaction Telegram + aucune machine depuis 48h → mode vacances. CRASH-PROOF."""
    try:
        dernier_msg = mem_get("dernier_message_telegram")
        if not dernier_msg:
            return
        try:
            dt_msg = datetime.fromisoformat(dernier_msg)
        except Exception:
            return
        if (now - dt_msg).total_seconds() / 3600 < 48:
            return
        if mem_get("mode_vacances") == "actif":
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            dernier_cycle = conn.execute(
                "SELECT MAX(debut) FROM cycles_appareils WHERE debut > datetime('now', '-48 hours')"
            ).fetchone()
            conn.close()
            if dernier_cycle and dernier_cycle[0]:
                return
        except Exception:
            pass
        mem_set("mode_vacances", "actif")
        log.info("🏖️ Mode vacances activé (48h sans interaction)")
        telegram_send(
            "🏖️ MODE VACANCES ACTIVÉ\n━━━━━━━━━━━━━━━━━━\n"
            "Aucune interaction depuis 48h.\n"
            "Surveillance réduite (alertes critiques uniquement).\n\n"
            "Envoyez n'importe quel message pour désactiver."
        )
    except Exception as e:
        log.debug(f"Mode vacances: {e}")


def _auto_update_github():
    """Vérifie GitHub pour des mises à jour toutes les 24h. CRASH-PROOF."""
    try:
        repo = "shaine93/assistant-domotique-home-assistant-Claude-IA"
        branch = "main"
        fichiers = ["config.py", "shared.py", "skills.py", "assistant.py"]
        derniere = mem_get("auto_update_last")
        if derniere:
            try:
                dt = datetime.fromisoformat(derniere)
                if (datetime.now() - dt).total_seconds() < 86400:
                    return
            except Exception:
                pass
        url_api = f"https://api.github.com/repos/{repo}/commits/{branch}"
        r_sha = requests.get(url_api, timeout=15)
        if r_sha.status_code != 200:
            return
        sha_distant = r_sha.json().get("sha", "")[:7]
        sha_local = mem_get("auto_update_sha") or ""
        if sha_distant == sha_local:
            mem_set("auto_update_last", datetime.now().isoformat())
            return
        log.info(f"🔄 Mise à jour disponible: {sha_local or '?'} → {sha_distant}")
        fichiers_dl = {}
        for fname in fichiers:
            url_raw = f"https://raw.githubusercontent.com/{repo}/{branch}/{fname}"
            r_dl = requests.get(url_raw, timeout=30)
            if r_dl.status_code != 200:
                log.error(f"Auto-update: impossible de télécharger {fname}")
                return
            fichiers_dl[fname] = r_dl.text
        import py_compile, tempfile
        for fname, contenu in fichiers_dl.items():
            try:
                with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp:
                    tmp.write(contenu)
                    tmp_path = tmp.name
                py_compile.compile(tmp_path, doraise=True)
                os.remove(tmp_path)
            except py_compile.PyCompileError as e:
                log.error(f"Auto-update: syntaxe invalide {fname}: {e}")
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
                return
        backup_dir = os.path.join(BASE_DIR, "versions")
        os.makedirs(backup_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        import shutil
        for fname in fichiers:
            src = os.path.join(BASE_DIR, fname)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(backup_dir, f"{fname}.bak_{ts}"))
        for fname, contenu in fichiers_dl.items():
            with open(os.path.join(BASE_DIR, fname), "w") as f:
                f.write(contenu)
        mem_set("auto_update_sha", sha_distant)
        mem_set("auto_update_last", datetime.now().isoformat())
        log.info(f"✅ Mise à jour appliquée: {sha_distant}")
        telegram_send(
            f"🔄 MISE À JOUR AUTOMATIQUE\n━━━━━━━━━━━━━━━━━━\n"
            f"Version: {sha_distant}\nFichiers: {', '.join(fichiers)}\n"
            f"Redémarrage dans 5 secondes..."
        )
        import subprocess
        time.sleep(5)
        subprocess.Popen(["systemctl", "restart", "assistantia"])
    except Exception as e:
        log.error(f"Auto-update: {e}")



# =============================================================================
# FEATURES v7.62 — Backup DB, Rate limiting, Score DPE, Export PDF
# =============================================================================

def _backup_auto_db(now):
    """Backup memory.db + config.json chaque nuit à 3h. Garde 30 jours. CRASH-PROOF."""
    try:
        if now.hour != 3 or now.minute > 5:
            return
        derniere = mem_get("backup_db_last")
        if derniere:
            try:
                if (now - datetime.fromisoformat(derniere)).total_seconds() < 72000:  # 20h
                    return
            except Exception:
                pass

        import shutil
        backup_dir = os.path.join(BASE_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        ts = now.strftime("%Y%m%d_%H%M")

        # Backup DB
        src_db = os.path.join(BASE_DIR, "memory.db")
        if os.path.exists(src_db):
            shutil.copy2(src_db, os.path.join(backup_dir, f"memory_{ts}.db"))

        # Backup config
        src_cfg = os.path.join(BASE_DIR, "config.json")
        if os.path.exists(src_cfg):
            shutil.copy2(src_cfg, os.path.join(backup_dir, f"config_{ts}.json"))

        # Purge > 30 jours
        import glob
        cutoff = (now - timedelta(days=30)).strftime("%Y%m%d")
        for f in glob.glob(os.path.join(backup_dir, "memory_*.db")) + glob.glob(os.path.join(backup_dir, "config_*.json")):
            fname = os.path.basename(f)
            date_part = fname.split("_")[1][:8] if "_" in fname else ""
            if date_part and date_part < cutoff:
                os.remove(f)

        mem_set("backup_db_last", now.isoformat())
        log.info(f"💾 Backup DB + config → backups/{ts}")
    except Exception as e:
        log.error(f"Backup DB: {e}")


def cmd_score():
    """Score énergétique DPE dynamique de la maison."""
    try:
        conn = sqlite3.connect(DB_PATH)
        now = datetime.now()

        # 1. Couverture solaire (0-25 pts)
        score_solaire = 0
        try:
            rows = conn.execute(
                "SELECT AVG(couverture_pct) FROM cycles_appareils WHERE fin IS NOT NULL AND debut > datetime('now', '-30 days')"
            ).fetchone()
            if rows and rows[0]:
                score_solaire = min(25, int(rows[0] / 4))  # 100% → 25 pts
        except Exception:
            pass

        # 2. Économies mensuelles (0-25 pts)
        score_eco = 0
        try:
            eco = get_economies_mois(now.year, now.month)
            total_eco = sum(e[2] for e in eco) if eco else 0
            score_eco = min(25, int(total_eco * 2.5))  # 10€ → 25 pts
        except Exception:
            pass

        # 3. Standbys détectés et corrigés (0-15 pts)
        score_standby = 15  # Score max par défaut — perdu si standbys actifs
        try:
            nb_standby = conn.execute(
                "SELECT COUNT(*) FROM memoire WHERE cle LIKE 'standby_alerte_%' AND updated_at > datetime('now', '-7 days')"
            ).fetchone()[0]
            score_standby = max(0, 15 - nb_standby * 3)  # -3 par standby
        except Exception:
            pass

        # 4. Santé réseau Zigbee (0-15 pts)
        score_zigbee = 15
        try:
            nb_faibles = conn.execute(
                "SELECT COUNT(*) FROM cartographie WHERE categorie NOT IN ('a_ignorer') AND entity_id LIKE '%lqi%'"
            ).fetchone()[0]
            # Simplifié : si devices surveillés, ok
            score_zigbee = 15 if nb_faibles == 0 else max(5, 15 - nb_faibles)
        except Exception:
            pass

        # 5. Optimisation HC/HP (0-10 pts)
        score_hchp = 0
        try:
            cycles_hc = conn.execute(
                "SELECT COUNT(*) FROM cycles_appareils WHERE fin IS NOT NULL AND debut > datetime('now', '-30 days') AND CAST(strftime('%H', debut) AS INTEGER) BETWEEN 0 AND 6"
            ).fetchone()[0]
            cycles_total = conn.execute(
                "SELECT COUNT(*) FROM cycles_appareils WHERE fin IS NOT NULL AND debut > datetime('now', '-30 days')"
            ).fetchone()[0]
            if cycles_total > 0:
                pct_hc = cycles_hc / cycles_total * 100
                score_hchp = min(10, int(pct_hc / 10))  # 100% HC → 10 pts
        except Exception:
            pass

        # 6. Régularité baselines (0-10 pts)
        score_baselines = 0
        try:
            nb_baselines = conn.execute("SELECT COUNT(*) FROM baselines WHERE nb_mesures >= 10").fetchone()[0]
            score_baselines = min(10, int(nb_baselines / 50))  # 500 baselines → 10 pts
        except Exception:
            pass

        conn.close()

        total = score_solaire + score_eco + score_standby + score_zigbee + score_hchp + score_baselines

        if total >= 80:
            grade, emoji = "A", "🟢"
        elif total >= 60:
            grade, emoji = "B", "🟡"
        elif total >= 40:
            grade, emoji = "C", "🟠"
        else:
            grade, emoji = "D", "🔴"

        return (
            f"🏠 SCORE ÉNERGÉTIQUE MAISON\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"{emoji} **Note : {grade} — {total}/100**\n\n"
            f"☀️ Couverture solaire : {score_solaire}/25\n"
            f"💰 Économies : {score_eco}/25\n"
            f"🔌 Standbys : {score_standby}/15\n"
            f"📡 Réseau Zigbee : {score_zigbee}/15\n"
            f"⏰ Optimisation HC : {score_hchp}/10\n"
            f"📊 Baselines : {score_baselines}/10\n\n"
            f"Le score évolue chaque semaine."
        )
    except Exception as e:
        return f"❌ Erreur score: {e}"


def cmd_export_pdf():
    """Génère et envoie un rapport PDF mensuel par email."""
    try:
        now = datetime.now()
        conn = sqlite3.connect(DB_PATH)

        # Collecter les données du mois
        mois = now.strftime("%B %Y")

        # Économies
        eco = get_economies_mois(now.year, now.month)
        total_eco = sum(e[2] for e in eco) if eco else 0

        # Cycles
        cycles = conn.execute(
            "SELECT entity_id, COUNT(*), SUM(conso_kwh), SUM(cout_reseau) "
            "FROM cycles_appareils WHERE fin IS NOT NULL "
            "AND strftime('%Y-%m', debut) = ? GROUP BY entity_id",
            (now.strftime("%Y-%m"),)
        ).fetchall()

        # Tokens
        tokens = get_token_usage()

        conn.close()

        # Construire le rapport texte (envoi par email)
        rapport = f"📊 RAPPORT MENSUEL — {mois}\n"
        rapport += "=" * 40 + "\n\n"

        rapport += f"💰 ÉCONOMIES : {total_eco:.2f}€\n"
        if eco:
            for e in eco:
                rapport += f"  • {e[1]} : {e[2]:.2f}€\n"

        rapport += f"\n🔄 CYCLES MACHINES :\n"
        for c in cycles:
            app = appareil_get(c[0])
            nom = app["nom"] if app and app.get("nom") else c[0].split(".")[-1]
            rapport += f"  • {nom} : {c[1]} cycles, {c[2]:.1f} kWh, {c[3]:.2f}€\n"

        rapport += f"\n🤖 TOKENS API : {tokens.get('total_tokens', 0):,} ({tokens.get('total_cost', 0):.2f}€)\n"

        # Score
        score_txt = cmd_score()
        rapport += f"\n{score_txt}\n"

        # Envoyer par email
        sujet = f"[AssistantIA] Rapport mensuel — {mois}"
        envoyer_email(sujet, rapport)

        return f"📧 Rapport {mois} envoyé par email.\n\n{rapport[:500]}..."

    except Exception as e:
        return f"❌ Erreur export: {e}"


def cmd_conseil_contrat():
    """Compare le contrat actuel avec les alternatives et conseille."""
    try:
        tarif_actuel, _ = skill_get("tarification")
        if not tarif_actuel or "type" not in tarif_actuel:
            return "⚠️ Aucun contrat configuré. Tapez /tarif pour configurer."

        type_actuel = tarif_actuel.get("type", "")
        fournisseur = tarif_actuel.get("fournisseur", "")

        conn = sqlite3.connect(DB_PATH)
        now = datetime.now()

        # Conso des 30 derniers jours
        # Estimation basée sur cycles + baselines
        try:
            conso_total = conn.execute(
                "SELECT SUM(conso_kwh) FROM cycles_appareils WHERE fin IS NOT NULL AND debut > datetime('now', '-30 days')"
            ).fetchone()[0] or 0
        except Exception:
            conso_total = 0

        conn.close()

        if conso_total < 10:
            return "⚠️ Pas assez de données (< 10 kWh mesurés ce mois). Réessayez dans quelques semaines."

        # Estimation mensuelle
        jours_ecoules = now.day
        conso_mois_estime = conso_total / max(1, jours_ecoules) * 30

        prix_actuel = tarif_prix_kwh_actuel()
        cout_actuel = conso_mois_estime * prix_actuel

        # Comparer avec quelques offres types
        alternatives = [
            ("EDF Zen", 0.2516),
            ("EDF Zen WE", 0.2068),  # Moyenne HP/HC
            ("TotalEnergies Essentielle", 0.2219),
            ("Octopus Eco-Conso", 0.1992),
        ]

        result = f"💡 CONSEIL CONTRAT\n━━━━━━━━━━━━━━━━━━\n\n"
        result += f"Contrat actuel : {fournisseur} ({type_actuel})\n"
        result += f"Conso estimée : {conso_mois_estime:.0f} kWh/mois\n"
        result += f"Coût estimé : {cout_actuel:.0f}€/mois\n\n"
        result += f"Alternatives :\n"

        for nom, prix in alternatives:
            cout_alt = conso_mois_estime * prix
            diff = cout_actuel - cout_alt
            emoji = "✅" if diff > 5 else "➖"
            result += f"  {emoji} {nom} : ~{cout_alt:.0f}€/mois ({'+' if diff < 0 else '-'}{abs(diff):.0f}€)\n"

        result += f"\n⚠️ Estimations simplifiées. Consultez les sites des fournisseurs pour les tarifs exacts."
        return result

    except Exception as e:
        return f"❌ Erreur conseil contrat: {e}"



# =============================================================================
# FEATURES v7.63 — Coupure internet, Zigbee mort, Tempo/EJP
# =============================================================================

def _detecter_coupure_internet(now):
    """Si HA inaccessible > 5 min → log. > 30 min → alerte SMS. CRASH-PROOF."""
    try:
        etats = ha_get("states")
        if etats:
            # HA accessible — reset compteur
            if mem_get("ha_inaccessible_depuis"):
                mem_set("ha_inaccessible_depuis", "")
            return

        # HA inaccessible
        debut = mem_get("ha_inaccessible_depuis")
        if not debut:
            mem_set("ha_inaccessible_depuis", now.isoformat())
            log.warning("⚠️ HA inaccessible — début surveillance")
            return

        try:
            dt_debut = datetime.fromisoformat(debut)
            minutes = (now - dt_debut).total_seconds() / 60
        except Exception:
            return

        if minutes > 30:
            _alerter_si_nouveau(
                "coupure_internet",
                f"🌐 HOME ASSISTANT INACCESSIBLE\n━━━━━━━━━━━━━━━━━━\n"
                f"Depuis {int(minutes)} min ({dt_debut.strftime('%H:%M')})\n"
                f"Vérifiez votre connexion internet ou votre HA.",
                delai_h=2
            )
            # Tenter SMS si configuré
            if minutes > 60 and CFG.get("sms_method"):
                try:
                    _alerter_si_nouveau(
                        "coupure_internet_sms",
                        f"ALERTE: HA inaccessible depuis {int(minutes)}min",
                        delai_h=6
                    )
                except Exception:
                    pass
    except Exception as e:
        log.debug(f"Coupure internet: {e}")


def _alerte_zigbee_device_mort(index, now):
    """Détecte les devices Zigbee unavailable > 24h. CRASH-PROOF."""
    try:
        if now.hour != 9 or now.minute > 5:
            return  # Une fois par jour à 9h
        derniere = mem_get("zigbee_mort_check")
        if derniere:
            try:
                if (now - datetime.fromisoformat(derniere)).total_seconds() < 72000:
                    return
            except Exception:
                pass

        conn = sqlite3.connect(DB_PATH)
        # Chercher les entités Zigbee unavailable
        rows = conn.execute(
            "SELECT entity_id, friendly_name FROM cartographie WHERE categorie NOT IN ('a_ignorer')"
        ).fetchall()
        conn.close()

        morts = []
        for eid, fname in rows:
            e = index.get(eid)
            if e and e.get("state") == "unavailable":
                # Vérifier depuis combien de temps
                last_changed = e.get("last_changed", "")
                if last_changed:
                    try:
                        dt_changed = datetime.fromisoformat(last_changed.replace("Z", "+00:00")).replace(tzinfo=None)
                        heures = (now - dt_changed).total_seconds() / 3600
                        if heures > 24:
                            morts.append((fname or eid, int(heures)))
                    except Exception:
                        pass

        if morts:
            liste = "\n".join(f"  • {nom} ({h}h)" for nom, h in morts[:10])
            _alerter_si_nouveau(
                "zigbee_mort",
                f"📡 DEVICES UNAVAILABLE > 24H\n━━━━━━━━━━━━━━━━━━\n{liste}\n\n"
                f"Vérifiez : batterie vide, hors portée Zigbee, ou device HS.",
                delai_h=24
            )

        mem_set("zigbee_mort_check", now.isoformat())
    except Exception as e:
        log.debug(f"Zigbee mort: {e}")


def _notif_tempo_ejp(now):
    """Si contrat Tempo/EJP, notifie la veille des jours rouges. CRASH-PROOF."""
    try:
        if now.hour != 19 or now.minute > 5:
            return
        tarif, _ = skill_get("tarification")
        if not tarif or tarif.get("type") not in ("tempo", "ejp"):
            return
        derniere = mem_get("tempo_check_last")
        if derniere:
            try:
                if (now - datetime.fromisoformat(derniere)).total_seconds() < 72000:
                    return
            except Exception:
                pass

        # Appeler l'API RTE Tempo
        try:
            url = "https://www.api-couleur-tempo.fr/api/jourTempo/tomorrow"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                couleur = data.get("codeJour", 0)
                # 1=bleu, 2=blanc, 3=rouge
                if couleur == 3:
                    telegram_send(
                        "🔴 JOUR ROUGE TEMPO DEMAIN\n━━━━━━━━━━━━━━━━━━\n"
                        "Tarif très élevé demain.\n"
                        "💡 Décalez toutes les machines à ce soir ou après-demain.\n"
                        "🔌 Réduisez le chauffage si possible."
                    )
                elif couleur == 2:
                    telegram_send(
                        "⚪ JOUR BLANC TEMPO DEMAIN\n"
                        "Tarif intermédiaire — utilisez les heures creuses."
                    )
        except Exception:
            pass

        mem_set("tempo_check_last", now.isoformat())
    except Exception as e:
        log.debug(f"Tempo: {e}")



def _detecter_fuite_eau(index, now):
    """Si capteur d'eau HA détecte une fuite → alerte immédiate. CRASH-PROOF."""
    try:
        for eid, e in index.items():
            if "moisture" in eid or "water_leak" in eid or "fuite" in eid:
                if e.get("state") in ("on", "True", "wet", "detected"):
                    fname = e.get("attributes", {}).get("friendly_name", eid)
                    _alerter_si_nouveau(
                        f"fuite_{eid}",
                        f"💧 FUITE D'EAU DÉTECTÉE\n━━━━━━━━━━━━━━━━━━\n"
                        f"Capteur : {fname}\n"
                        f"État : {e.get('state')}\n\n"
                        f"⚠️ Vérifiez immédiatement !",
                        delai_h=1
                    )
    except Exception as e:
        log.debug(f"Fuite eau: {e}")


def cmd_pieces():
    """Consommation par pièce — areas HA + détection par nom d'entité."""
    try:
        index = ha_get("states")
        if not index:
            return "❌ HA inaccessible."

        index_dict = {e["entity_id"]: e for e in index}
        pieces = {}

        # Pièces connues pour détection par nom
        PIECES_CONNUES = [
            "cuisine", "salon", "chambre", "bureau", "buanderie", "garage",
            "salle de bain", "sdb", "entrée", "couloir", "jardin", "terrasse",
            "grenier", "cave", "cellier", "wc", "toilette",
        ]

        # Filtrer les entités de production solaire
        conn = sqlite3.connect(DB_PATH)
        solaire_ids = set()
        try:
            rows = conn.execute(
                "SELECT entity_id FROM cartographie WHERE categorie IN ('energie_production', 'energie_batterie', 'energie_solaire')"
            ).fetchall()
            solaire_ids = {r[0] for r in rows}
        except Exception:
            pass
        conn.close()

        for eid, e in index_dict.items():
            # Seulement les capteurs de puissance
            if "_power" not in eid or e.get("state") in ("unavailable", "unknown", ""):
                continue
            # Exclure production solaire
            if eid in solaire_ids:
                continue
            try:
                watts = float(e["state"])
            except (ValueError, TypeError):
                continue
            if watts <= 0:
                continue

            # Trouver la pièce
            # 1. Area HA
            area_id = shared._entity_areas.get(eid)
            piece = shared._areas_id_to_name.get(area_id, "") if area_id else ""

            # 2. Fallback: nom de l'entité ou friendly_name
            if not piece:
                fname = e.get("attributes", {}).get("friendly_name", eid).lower()
                eid_low = eid.lower()
                for p in PIECES_CONNUES:
                    if p in eid_low or p in fname:
                        piece = p.capitalize()
                        break
                # Cas spéciaux
                if not piece:
                    if "chambre" in eid_low:
                        # Extraire le nom après "chambre" : prise_chambre_tv → Chambre TV
                        parts = eid_low.split("chambre")
                        if len(parts) > 1:
                            suffix = parts[1].replace("_", " ").strip()
                            piece = f"Chambre {suffix}".strip().title()
                        else:
                            piece = "Chambre"

            if not piece:
                piece = "Autre"

            if piece not in pieces:
                pieces[piece] = []
            pieces[piece].append((eid, watts, e.get("attributes", {}).get("friendly_name", eid)))

        if not pieces:
            return "📊 Aucune donnée de puissance par pièce."

        # Trier par total décroissant
        pieces_total = {p: sum(w for _, w, _ in devs) for p, devs in pieces.items()}
        total = sum(pieces_total.values())
        pieces_triees = sorted(pieces_total.items(), key=lambda x: x[1], reverse=True)

        result = "🏠 CONSOMMATION PAR PIÈCE\n━━━━━━━━━━━━━━━━━━\n\n"
        for piece, watts in pieces_triees:
            pct = int(watts / total * 100) if total > 0 else 0
            barre = "█" * max(1, pct // 5) + "░" * max(0, 20 - pct // 5)
            # Détail appareils
            devs = sorted(pieces[piece], key=lambda x: x[1], reverse=True)
            detail = ", ".join(f"{fn.split(' ')[-1]} {w:.0f}W" for _, w, fn in devs[:3])
            result += f"**{piece}** : {watts:.0f}W ({pct}%)\n{barre}\n{detail}\n\n"

        result += f"**TOTAL : {total:.0f}W**"
        return result

    except Exception as e:
        return f"❌ Erreur pièces: {e}"



# =============================================================================
# FEATURES v7.64 — Rollback auto, deploy server monitoring
# =============================================================================

def _rollback_si_erreurs_repetees(now):
    """Si 3+ crashes en 1h → rollback vers le dernier backup. CRASH-PROOF."""
    try:
        if now.minute != 0:
            return  # Check toutes les heures seulement

        import glob
        crash_log = os.path.join(BASE_DIR, "crash.log")
        if not os.path.exists(crash_log):
            return

        with open(crash_log) as f:
            content = f.read()

        # Compter les crashes récents (dernière heure)
        crashes_recentes = 0
        for line in content.split("\n"):
            if "CRASH" in line:
                try:
                    # Extraire timestamp
                    ts_str = line.split("CRASH")[1][:25].strip()
                    dt = datetime.fromisoformat(ts_str.replace(" ", "T")[:19])
                    if (now - dt).total_seconds() < 3600:
                        crashes_recentes += 1
                except Exception:
                    pass

        if crashes_recentes >= 3:
            # Trouver le backup le plus récent
            backup_dir = os.path.join(BASE_DIR, "versions")
            backups = sorted(glob.glob(os.path.join(backup_dir, "skills.py.bak_*")), reverse=True)
            if backups:
                import shutil
                log.warning(f"⚠️ {crashes_recentes} crashes en 1h — rollback vers {os.path.basename(backups[0])}")
                shutil.copy2(backups[0], os.path.join(BASE_DIR, "skills.py"))
                telegram_send(
                    f"⚠️ ROLLBACK AUTOMATIQUE\n━━━━━━━━━━━━━━━━━━\n"
                    f"{crashes_recentes} crashes détectés en 1h.\n"
                    f"Retour vers la version précédente.\n"
                    f"Redémarrage..."
                )
                import subprocess
                time.sleep(3)
                subprocess.Popen(["systemctl", "restart", "assistantia"])
    except Exception as e:
        log.debug(f"Rollback auto: {e}")


def _monitoring_deploy_server(now):
    """Vérifie que le deploy server répond. CRASH-PROOF."""
    try:
        if now.minute not in (0, 30):
            return  # 2x par heure

        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            result = s.connect_ex(("127.0.0.1", 8501))
            s.close()
            if result == 0:
                return  # Port ouvert = deploy server tourne
        except Exception:
            pass

        _alerter_si_nouveau(
            "deploy_server_down",
            "⚠️ Deploy server ne répond pas sur le port 8501.\n"
            "Le déploiement à distance est indisponible.",
            delai_h=6
        )
    except Exception as e:
        log.debug(f"Monitor deploy: {e}")


def cmd_appareils_connus():
    """Affiche la bibliothèque d'appareils connus."""
    try:
        path = os.path.join(BASE_DIR, "APPAREILS_CONNUS.json")
        if not os.path.exists(path):
            return "⚠️ Fichier APPAREILS_CONNUS.json introuvable."
        with open(path) as f:
            data = json.load(f)
        result = "📚 APPAREILS CONNUS\n━━━━━━━━━━━━━━━━━━\n\n"
        for key, info in data.items():
            emoji = info.get("emoji", "")
            nom = info.get("nom", key)
            conso = info.get("conso_kwh_typique", [0, 0])
            duree = [info.get("duree_min_min", 0), info.get("duree_max_min", 0)]
            result += f"{emoji} **{nom}**\n"
            result += f"  Puissance : {info.get('puissance_min_w', 0)}-{info.get('puissance_max_w', 0)}W\n"
            if duree[1] > 0:
                result += f"  Durée : {duree[0]}-{duree[1]} min\n"
            result += f"  Conso : {conso[0]}-{conso[1]} kWh\n"
            if info.get("pieges"):
                result += f"  ⚠️ {info['pieges'][0]}\n"
            result += "\n"
        return result
    except Exception as e:
        return f"❌ Erreur: {e}"



# =============================================================================
# GOOGLE HOME / ALEXA — Détection commandes vocales via scripts HA
# =============================================================================

_vocal_scripts_last = {}

def _check_vocal_scripts(index, now):
    """Détecte l'exécution des scripts HA assistantia_* → traite + TTS Nest Hub. CRASH-PROOF."""
    global _vocal_scripts_last
    try:
        scripts_map = {
            "script.assistantia_energie": "énergie",
            "script.assistantia_score": "score",
            "script.assistantia_debug": "debug",
            "script.assistantia_pieces": "pieces",
            "script.assistantia_contrat": "contrat",
        }

        found = 0
        for eid in scripts_map:
            if eid in index:
                found += 1
        if found == 0:
            return  # Pas de scripts HA trouvés

        for eid, cmd in scripts_map.items():
            e = index.get(eid)
            if not e:
                continue
            last_triggered = e.get("attributes", {}).get("last_triggered", "")
            if last_triggered == "None":
                last_triggered = ""
            prev = _vocal_scripts_last.get(eid, "")

            if last_triggered and last_triggered != prev:
                _vocal_scripts_last[eid] = last_triggered
                if not prev:
                    continue

                log.info(f"🎙️ Google Home: {cmd} (trigger: {last_triggered[:19]})")

                try:
                    reponse = traiter_message(cmd)
                    tts = reponse.replace("**", "").replace("━", "").replace("═", "")
                    tts = tts.replace("\n\n", ". ").replace("\n", ". ")
                    tts = tts.replace("  ", " ").strip()
                    if len(tts) > 400:
                        tts = tts[:397] + "..."

                    media_players = CFG.get("tts_media_players", ["media_player.chambre_philippe"])
                    for mp in media_players:
                        try:
                            ha_post("services/tts/google_translate_say", {
                                "entity_id": mp,
                                "message": tts
                            })
                        except Exception:
                            pass

                    log.info(f"🎙️ TTS envoyé: {tts[:80]}...")
                except Exception as e:
                    log.error(f"Vocal script error: {e}")

    except Exception as e:
        log.debug(f"Check vocal scripts: {e}")

def traiter_message(texte):
    t = texte.strip().lower()
    # Enlever le "/" au début si présent
    if t.startswith("/"):
        t = t[1:]
    log.info(f"Message: {texte[:80]}")

    # ✅ DICTIONNAIRE CORRIGÉ v1.5.0
    commandes = {
        "audit": cmd_audit,
        "energie": cmd_energie, "énergie": cmd_energie, "chauffage": cmd_energie,
        "solaire": cmd_solaire,
        "batteries": cmd_batteries, "piles": cmd_batteries, "batterie": cmd_batteries,
        "zigbee": cmd_zigbee,
        "nas": cmd_nas,
        "automatisations": cmd_automatisations, "automations": cmd_automatisations,
        "addons": cmd_addons,
        "budget": cmd_budget,
        "debug": cmd_debug,
        "logs": cmd_logs,
        "mémoire": cmd_memoire, "memoire": cmd_memoire,
        "scan": cmd_scan,
        "cycles": cmd_cycles,
        "bilan": bilan_automatique,
        "documentation": cmd_documentation,
        "rapport": cmd_audit,
        "export": cmd_script_export,    # ✅ Export SCRIPT
        "script": cmd_script_export,    # ✅ Export SCRIPT
        "claude": cmd_script_export,    # ✅ Export SCRIPT
        "diag_energie": cmd_diag_energie,  # 🔧 Diagnostic énergie
        "diag_hc": cmd_diag_hc,            # 🔧 Recherche heures creuses
        "diag_prises": cmd_diag_prises,    # 🔧 Diagnostic prises
        "diag_ecojoko": cmd_diag_ecojoko,  # 🔧 Diagnostic Ecojoko
        "diag_nas": cmd_diag_nas,          # 🔧 Diagnostic NAS
        "diag_carto": cmd_diag_carto,      # 🔧 Diagnostic cartographie
        "nettoyer": cmd_nettoyer_carto,    # 🧹 Nettoyage cartographie
        "baselines": cmd_baselines,        # 📊 Baselines comportementales
        "skills": cmd_skills,              # 🧠 Skills autonomes
        "analyse": cmd_analyse,            # 🧠 Déclencher analyse IA
        "expertise": cmd_expertise,        # 📚 Expertise accumulée
        "apprentissage": cmd_apprentissage, # 📕 Journal d'apprentissage
        "intelligence": cmd_intelligence,  # 🧠 Score + tableau de bord
        "roles": cmd_roles,                # 🎯 Rôles auto-découverts
        "sms": cmd_sms,                    # 📱 Renvoyer code SMS
        "md": cmd_md,                      # 📧 Envoyer MD par mail
        "tarif": cmd_tarif,                # ⚡ Tarif électricité
        "bilan_tarif": cmd_tarif_bilan,    # ⚡ Bilan mensuel tarif
        "roi": cmd_roi,                    # 📈 ROI tokens vs économies
        "hote": cmd_hote,                  # 🖥️ Santé machine hôte
        "sante": cmd_sante,                # 🖥️ Santé machine hôte
        "diag_meteo": cmd_diag_meteo,      # 🌦️ Diagnostic météo
        "diag_forecast": cmd_diag_forecast, # 🔧 Debug forecast
        "aide": cmd_documentation,          # 📖 Aide (alias)
        "commandes": cmd_commandes, "commande": cmd_commandes, "menu": cmd_commandes,
        "watches": cmd_watches,
        "score": cmd_score,
        "dpe": cmd_score,
        "export": cmd_export_pdf,
        "pdf": cmd_export_pdf,
        "contrat": cmd_conseil_contrat,
        "conseil": cmd_conseil_contrat,
        "pieces": cmd_pieces,
        "pièces": cmd_pieces,
        "rooms": cmd_pieces,
        "appareils": cmd_appareils_connus,
        "machines": cmd_appareils_connus, "alertes": cmd_watches,  # 🔔 Alertes dynamiques  # 📋 Menu boutons
        "programmes": cmd_programmes,      # 🔄 Programmes machines appris
        "appareils": cmd_appareils,          # 🔌 Appareils sur prises
        "surveillance": cmd_surveillance,    # 🛡️ Tout ce qui est surveillé
        "profil": cmd_profil,                # 👥 Profil foyer
        "economies": cmd_economies,          # 💰 Détail des économies
        "dashboard": cmd_dashboard,          # 📊 Pousser les stats vers HA (Lovelace)
        "calendrier": cmd_calendrier,        # 📅 Événements calendrier HA
        "test_meteo": cmd_test_meteo,      # 🧪 Test surveillance météo
    }

    if t in commandes:
        return commandes[t]()


    # Réponse au questionnaire tarif
    if tarif_traiter_reponse(texte):
        return ""

    # Réponse à une suggestion machine : "12h30", "14h", "13:00"
    attente = mem_get("attente_heure_machine")
    if attente == "oui":
        import re as _re_msg
        # Annulation
        if t in ("non", "❌", "annuler", "pas aujourd'hui"):
            mem_set("attente_heure_machine", "")
            return "✅ Pas de machine aujourd'hui."

        # Parser l'heure : 12h30, 12h, 14:30, 13:00, 12, etc.
        match = _re_msg.match(r"^(\d{1,2})[h:]?(\d{0,2})$", t.replace(" ", ""))
        if match:
            heure_cible = int(match.group(1))
            minutes_cible = int(match.group(2)) if match.group(2) else 0
            if 0 <= heure_cible <= 23 and 0 <= minutes_cible <= 59:
                now_msg = datetime.now()
                cible = now_msg.replace(hour=heure_cible, minute=minutes_cible, second=0)
                if cible <= now_msg:
                    mem_set("attente_heure_machine", "")
                    return f"⚠️ {heure_cible}h{minutes_cible:02d} est déjà passé."

                mem_set("attente_heure_machine", "")
                mem_set("rappel_machine", cible.isoformat())
                mem_set("rappel_machine_heure", f"{heure_cible}h{minutes_cible:02d}")
                telegram_send(
                    f"⏰ Rappel machine programmé à {heure_cible}h{minutes_cible:02d}\n"
                    f"Je surveillerai la production solaire et la prise machine à laver."
                )
                log.info(f"⏰ Rappel machine : {heure_cible}h{minutes_cible:02d}")
                return ""
        # Si pas reconnu, laisser passer vers les commandes normales
        mem_set("attente_heure_machine", "")

    # Commandes avec arguments
    if t == "tarif config":
        tarif_configurer_questionnaire()
        return ""

    # Réponse nom personnalisé pour un appareil "Autre"
    eid_attente = mem_get("attente_nom_appareil")
    if eid_attente:
        mem_set("attente_nom_appareil", "")
        nom_custom = texte.strip()
        if not nom_custom or len(nom_custom) < 2:
            # Pas de nom → voie de garage
            appareil_set(eid_attente, "ignorer", "⬜ Ignoré")
            telegram_send(
                f"⬜ Pas de nom → voie de garage.\n"
                f"Pas de suivi pour cette prise."
            )
        else:
            appareil_set(eid_attente, "autre", nom_custom)
            nb_surveilles = 0
            try:
                conn_nb = sqlite3.connect(DB_PATH)
                nb_surveilles = conn_nb.execute("SELECT COUNT(*) FROM appareils WHERE surveiller=1").fetchone()[0]
                conn_nb.close()
            except Exception:
                pass
            telegram_send(
                f"✅ Enregistré : {nom_custom}\n"
                f"Surveillance activée — cycles, coûts, économies.\n"
                f"📊 {nb_surveilles} appareils sous surveillance"
            )
        # Continuer la queue
        try:
            queue = json.loads(mem_get("appareils_queue") or "[]")
            queue = [q for q in queue if q["entity_id"] != eid_attente]
            mem_set("appareils_queue", json.dumps(queue))
            _poser_question_appareil_suivant()
        except Exception:
            pass
        return ""

    if t in ("profil reset", "profil reconfigurer"):
        skill_set("foyer", {})
        mem_set("profil_foyer_complet", "")
        mem_set("profil_foyer_question", "")
        _lancer_questionnaire_foyer()
        return "🔄 Profil réinitialisé — questionnaire relancé..."

    if t in ("appareils reset", "appareils reconfigurer"):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM appareils")
        conn.commit()
        conn.close()
        mem_set("appareils_configures", "")
        mem_set("appareils_queue", "")
        # Reset des programmes appris (changement de machine = nouvel apprentissage)
        skill_set("programmes_machines", {})
        _lancer_questionnaire_appareils()
        return "🔄 Reconfiguration complète lancée...\nAppareils + programmes appris réinitialisés.\nNouvel apprentissage automatique."

    # Reset d'un seul appareil (changement de machine)
    if t.startswith("programmes reset "):
        nom_machine = t.split(" ", 2)[2].strip() if len(t.split(" ")) > 2 else ""
        programmes, _ = skill_get("programmes_machines")
        if programmes:
            # Chercher l'appareil par nom
            found = False
            for eid, progs in list(programmes.items()):
                app = appareil_get(eid)
                app_nom = (app["nom"] if app else "").lower()
                if nom_machine.lower() in app_nom or nom_machine.lower() in eid.lower():
                    del programmes[eid]
                    skill_set("programmes_machines", programmes)
                    found = True
                    return f"🔄 Programmes de {app['nom'] if app else eid} réinitialisés.\nNouvel apprentissage au prochain cycle."
            if not found:
                return f"❌ Machine '{nom_machine}' non trouvée.\nTapez /appareils pour voir la liste."
        return "❌ Aucun programme enregistré."

    if t.startswith("energie ") or t.startswith("énergie "):
        arg = t.split(" ", 1)[1].strip()
        if arg in ("detail", "détail", "complet", "tout"):
            return cmd_energie(detail=True)

    # Commande /probleme → auto-correction (avec ou sans description)
    if t in ("probleme", "problème"):
        return (
            "🤔 AIDE-MOI À COMPRENDRE\n"
            "Tu tapes /probleme mais sans détail.\n\n"
            "📝 COMMENT ME SIGNALER UN PROBLÈME\n"
            "Sois concis et précis :\n"
            "- Quoi ? (PAC, Zigbee, énergie, NAS, machines…)\n"
            "- Quand ? (maintenant, hier, ce matin…)\n"
            "- Comment ? (ne démarre pas, offline, consomme trop…)\n\n"
            "📌 EXEMPLES\n"
            "✅ /probleme La PAC ne chauffe pas alors qu'il fait 5°C\n"
            "✅ /probleme 3 devices Zigbee sont offline\n"
            "✅ /probleme La conso EDF a doublé d'un coup"
        )
    if t.startswith("probleme ") or t.startswith("problème "):
        description = t.split(" ", 1)[1].strip()
        return cmd_probleme(description)

    # Question libre → contexte intelligent
    etats = ha_get("states")
    contexte = ha_get_contexte_intelligent(texte, etats)

    # skill_creer_auto supprimé ici — gaspillage de tokens (90% = {"creer": false})
    # Les skills dynamiques sont créés par _auto_apprendre (phase 7, toutes les 1h, GRATUIT)

    # Log calendriers dans le contexte
    cal_lines = [l for l in contexte.split("\n") if "CALENDRIER" in l or "ÉVÉNEMENT" in l or "calendar" in l.lower() or "poubelle" in l.lower()]
    log.info(f"CONTEXTE→HAIKU: {len(contexte)} chars, {len(cal_lines)} lignes calendrier: {cal_lines[:5]}")
    resultat = appel_claude(texte, contexte)
    if resultat is None:
        return "Je n'ai pas compris votre demande"
    return resultat


def bilan_automatique():
    """Génère et envoie un bilan complet"""
    # Tracker interaction pour mode vacances
    try:
        mem_set("dernier_message_telegram", datetime.now().isoformat())
        if mem_get("mode_vacances") == "actif":
            mem_set("mode_vacances", "")
            telegram_send("🏠 Mode vacances désactivé — bon retour !")
    except Exception:
        pass
    telegram_send("📊 Génération du bilan automatique en cours...")
    etats = ha_get("states")
    if not etats:
        telegram_send("❌ BILAN — HA inaccessible")
        return

    conn = sqlite3.connect(DB_PATH)
    nb_cycles = conn.execute("SELECT COUNT(*) FROM cycles_appareils WHERE fin IS NOT NULL").fetchone()[0]
    conso_totale = conn.execute("SELECT SUM(conso_kwh) FROM cycles_appareils WHERE fin IS NOT NULL").fetchone()[0] or 0
    cout_total = conn.execute("SELECT SUM(cout_eur) FROM cycles_appareils WHERE fin IS NOT NULL").fetchone()[0] or 0
    nb_absences = conn.execute("SELECT COUNT(*) FROM zigbee_absences").fetchone()[0]
    nb_anormales = conn.execute("SELECT COUNT(*) FROM zigbee_absences WHERE statut='anormal'").fetchone()[0]
    conn.close()

    contexte = f"""Bilan de {CFG.get('bilan_jours', 4)} jours :

CYCLES MACHINES : {nb_cycles}
Consommation : {conso_totale:.2f} kWh
Coût estimé : {cout_total:.2f}€

RÉSEAU ZIGBEE :
Absences détectées : {nb_absences}
Anomalies confirmées : {nb_anormales}

Cartographie : {mem_get('decouverte_count', 0)} entités apprises
"""

    prompt = (
        "Génère un bilan synthétique de la surveillance autonome de la maison. "
        "Résume : machines détectées, anomalies, alertes. "
        "Termine par 3 recommandations. Sois concis."
    )
    bilan = appel_claude(prompt, contexte)
    nb_j = CFG.get('bilan_jours', 4)
    telegram_send(f"📊 BILAN {nb_j} JOURS\n━━━━━━━━━━━━━━━━━━\n{bilan}")
    envoyer_email(
        f"[AssistantIA] Bilan {nb_j} jours — {datetime.now().strftime('%d/%m/%Y')}",
        bilan
    )
    mem_set("dernier_bilan", datetime.now().isoformat())
