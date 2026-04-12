# =============================================================================
# CONFIG.PY — Variables et constantes
# Modifiable par l'utilisateur sans risque de casser le script.
# Pas de logique ici. Que des valeurs.
# =============================================================================

import os

# ═══ CHEMINS ═══
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH  = os.path.join(BASE_DIR, "config.json")
DB_PATH      = os.path.join(BASE_DIR, "memory.db")
LOG_PATH     = os.path.join(BASE_DIR, "assistant.log")
COMPORTEMENT = os.path.join(BASE_DIR, "comportement.txt")

# ═══ VERSION ═══
MODE    = "DEV"
VERSION = "1.5.5"

# ═══ MACHINES — Seuils de détection ═══
SEUIL_CYCLE_W = 200   # Watts minimum pour démarrer un cycle
SEUIL_FIN_W   = 10    # Watts en dessous = machine arrêtée

# ═══ MACHINES — Grâce intelligente (minutes) ═══
GRACE_APRES_ESSORAGE  = 7    # Après essorage (>500W) : hublot 5 min + marge
GRACE_APRES_LAVAGE    = 30   # Après lavage : pause rinçage→essorage possible
GRACE_APRES_SECHAGE   = 45   # Après séchage : couvre pause préchauffage (mesurée 38 min)
GRACE_APRES_VAISSELLE = 10   # Après lave-vaisselle : séchage vapeur

# ═══ MACHINES — Durée minimale (minutes) ═══
DUREE_MIN_SECHE_LINGE    = 30   # Un séchage < 30 min = c'est une pause
DUREE_MIN_LAVE_LINGE     = 25   # Un lavage express = 30 min
DUREE_MIN_LAVE_VAISSELLE = 20   # Un cycle court = 25 min

# ═══ PLANNING ═══
JOURS_MACHINES = {5, 6, 2}  # weekday() — samedi, dimanche, mercredi

# ═══ POLLING — Mode sniper ═══
POLL_PRISES_IDLE  = 60   # Secondes au repos
POLL_PRISES_ACTIF = 20   # Secondes quand un cycle tourne

# ═══ BRIEFING ═══
HEURE_BRIEFING_TRAVAIL = 7    # Heure du briefing lun-ven
HEURE_BRIEFING_WEEKEND = 10   # Heure du briefing sam-dim
HEURE_BILAN_SOIR       = 21   # Heure du bilan quotidien
HEURE_BILAN_HEBDO      = 20   # Heure du bilan dimanche

# ═══ ZIGBEE ═══
LQI_FAIBLE = 50   # En dessous = signal faible

# ═══ TYPES D'APPAREILS ═══
TYPES_APPAREILS = {
    "lave_linge": "🧺 Lave-linge",
    "seche_linge": "👕 Sèche-linge",
    "lave_vaisselle": "🍽️ Lave-vaisselle",
    "congelateur": "❄️ Congélateur",
    "four": "🔥 Four",
    "coupe_veille": "🔇 Coupe-veille",
    "monitoring_energie": "📊 Monitoring énergie",
    "autre": "🔌 Autre (nommer)",
    "ignorer": "⬜ Ignorer",
}

# ═══ RÔLES AUTO-DÉCOUVERTS ═══
ROLES_DEFINIS = {
    "conso_temps_reel": ["sensor.*real*power*", "sensor.*puissance*instantanee*", "sensor.*ecojoko*realtime*"],
    "conso_jour_kwh": ["sensor.*consommation*totale*kwh*", "sensor.*daily*energy*"],
    "conso_jour_eur": ["sensor.*depense*jour*", "sensor.*daily*cost*"],
    "production_solaire_w": ["sensor.*ecu*current*power*", "sensor.*solar*power*", "sensor.*pv*power*"],
    "production_solaire_kwh": ["sensor.*ecu*today*energy*", "sensor.*solar*energy*today*"],
    "production_solaire_lifetime": ["sensor.*ecu*lifetime*energy*", "sensor.*solar*total*"],
    "onduleurs_total": ["sensor.*ecu*inverters", "sensor.*inverter*count*"],
    "onduleurs_online": ["sensor.*ecu*inverters*online*"],
    "batterie_soc": ["sensor.*battery*soc*", "sensor.*state*of*charge*"],
    "batterie_soc_anker": ["sensor.*solarbank*etat*charge*", "sensor.*solarbank*soc*"],
    "batterie_prod_solaire": ["sensor.*solarbank*puissance*solaire*"],
    "batterie_sortie": ["sensor.*solarbank*sortie*", "sensor.*solarbank*output*"],
    "batterie_puissance": ["sensor.*solarbank*puissance*", "sensor.*battery*power*"],
    "batterie_mode": ["sensor.*solarbank*mode*"],
    "pac_climate": ["climate.*pompe*chaleur*", "climate.*pac*", "climate.*heat*pump*"],
    "pac_temperature_ext": ["sensor.*temperature*exterieure*", "sensor.*outdoor*temp*"],
    "pac_consigne": ["number.*temperature*consigne*"],
    "meteo_temperature": ["sensor.*temperature*", "sensor.*outdoor*temp*"],
    "alerte_meteo": ["sensor.*weather*alert*", "sensor.*vigilance*"],
    "meteo_pluie": ["sensor.*next*rain*", "sensor.*rain*forecast*"],
    "meteo_risque_pluie": ["sensor.*rain*chance*", "sensor.*precipitation*probability*"],
    "meteo_risque_neige": ["sensor.*snow*chance*"],
    "meteo_vent": ["sensor.*wind*speed*", "sensor.*vitesse*vent*"],
    "meteo_rafales": ["sensor.*wind*gust*", "sensor.*rafale*"],
}

# ═══ AUTO-GUÉRISON ═══
SEUIL_AUTO_GUERISON = 3   # Occurrences/1h avant correction
AUTO_GUERISON_COOLDOWN = 3600  # Secondes entre 2 tentatives même erreur

# ═══ FILTRES TELEGRAM ═══
MAX_MESSAGES_JOUR = 50   # Anti-spam quotidien
ANTI_DUPLICATE_SEC = 300  # 5 min entre messages identiques
