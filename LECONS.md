# 📚 Leçons fondatrices — Pièges connus par installation

Ce fichier est enrichi par les bêta testeurs. Chaque piège découvert évite des heures de debug aux suivants.

---

## 🧺 Lave-linge

### Pause rinçage confondue avec fin de cycle
- **Symptôme** : le cycle se termine à 30 min au lieu de 90 min
- **Cause** : pause de 5-15 min entre lavage et essorage, puissance < SEUIL_FIN_W
- **Fix** : grâce intelligente basée sur la dernière phase (chauffage → grâce longue, essorage → grâce courte)

### Hublot verrouillé après fin
- **Symptôme** : notification "terminé" mais impossible d'ouvrir
- **Cause** : sécurité hublot 3-5 min après arrêt moteur
- **Fix** : message "Hublot se déverrouille dans ~5 min"

---

## 👕 Sèche-linge

### Défroissage automatique → cycle 300+ min
- **Symptôme** : cycle annoncé à 311 min au lieu de 40 min
- **Cause** : défroissage automatique = rotation basse (10-50W) toutes les 10 min pendant 2-4h. Reset la grâce.
- **Fix** : après le rappel "linge chaud", les consommations < 200W ne resetent plus la grâce

### Cycle doux non détecté
- **Symptôme** : le sèche-linge tourne en mode éco mais aucune notification
- **Cause** : puissance max 50-180W, jamais > SEUIL_CYCLE_W (200W)
- **Fix** : si conso > SEUIL_FIN_W pendant 5 min continue → démarrer le cycle automatiquement

---

## 🍽️ Lave-vaisselle

### Séchage passif
- **Symptôme** : fin de cycle annoncée 30 min trop tôt ou trop tard
- **Cause** : phase de séchage passif (0W) de 10-30 min en fin, puis conso résiduelle
- **Fix** : grâce spécifique lave-vaisselle (GRACE_APRES_VAISSELLE)

---

## ☀️ Solaire / Anker

### ECU glitch 0W entre updates
- **Symptôme** : production solaire alterne entre 500W et 0W
- **Cause** : l'ECU APSystems envoie 0W entre deux mises à jour (intervalle 5 min)
- **Fix** : ignorer les valeurs 0W si la précédente était > 0 et il fait jour

### Anker Solarbank ≠ cycle machine
- **Symptôme** : la prise Anker déclenche un faux cycle machine
- **Cause** : la charge/décharge de la batterie fait varier la puissance de la prise
- **Fix** : exclure la prise Anker du monitoring cycles

---

## 🌡️ PAC / Chauffage

### Thermostat on/off = normal
- **Symptôme** : alerte "PAC allumée/éteinte" en boucle
- **Cause** : le thermostat coupe et relance normalement le compresseur
- **Fix** : ne pas alerter sur climate auto/heat → c'est le mode normal

---

## 📡 Zigbee

### LQI faible après ajout d'appareil
- **Symptôme** : nouvel appareil avec LQI 30-40, performances dégradées
- **Cause** : table de routage pas encore optimisée
- **Fix** : attendre 24h, ou forcer un "Rediscover Network" dans Z2M + changer de canal WiFi si interférence
### Device offline non détecté — bug critique (24/04/2026)

- **Symptôme** : une prise Zigbee débranchée (`switch.prise_ecojoko`) reste 6h24 hors ligne (passage `unavailable` à 09:53:43, retour à 16:17:39) sans qu'aucune alerte Telegram ne soit envoyée
- **3 causes racines cumulées** identifiées par diagnostic forensique post-incident :

**Cause 1 — `_surveiller_zigbee` cassée silencieusement**

La fonction filtre les devices physiques via l'attribut `linkquality` (L3915 de `skills.py`) :
```python
lqi = e.get("attributes", {}).get("linkquality")
if lqi is None:
    continue
```
Or, sur cette installation HA (Z2M via MQTT, intégration HA standard), **aucune entité ne remonte cet attribut** dans `/api/states`. Vérification : `linkquality` introuvable dans le top 30 des attributs. Conséquence : la fonction n'a **jamais surveillé aucun device** depuis sa création.

**Cause 2 — Table `zigbee_absences` polluée par des entrées orphelines**

La table `zigbee_absences` contient une entrée pour `switch.prise_ecojoko` datée du 7 mars 2026, statut `en_attente`, avec un `retour_en_ligne` rempli quelques minutes plus tard. Cette entrée n'a jamais été nettoyée. Lors d'une nouvelle disparition, le code `_surveiller_zigbee` interroge `zigbee_absence_get(eid)` et trouve l'ancienne entrée → considère que c'est déjà signalé → ne lève pas de nouvelle alerte. Bug de logique : il faut vérifier si l'entrée correspond à la **session actuelle** d'absence, pas à une ancienne.

**Cause 3 — `_alerte_zigbee_device_mort` trop conservatrice**

La fonction filet de sécurité ne tournait qu'**une fois par jour à 9h00-9h05** avec un seuil **24h** d'absence. Le passage en `unavailable` à 09:53:43 n'a pas pu déclencher d'alerte avant le lendemain matin, et la prise a été rebranchée avant.

- **Tentatives de patch (24-25/04/2026)** :
  - **v1** : élargir le seuil à 1h, fréquence 15 min, périmètre `cartographie`. Problème : 150 entités unavailable normales (sous-entités logiques `_silent_mode`, `_identify`, services TTS, automations conditionnelles…) auraient déclenché 150 alertes Telegram.
  - **v2** : ajout des filtres `EXCLUSIONS_ZIGBEE` + `linkquality`. Problème : `linkquality` étant cassé sur cette install (cause 1), aucune alerte ne tirait jamais.
  - **Décision** : **rollback complet**. Le bug demande une refonte de `_surveiller_zigbee` qui ne dépende pas de `linkquality`, doublé d'un nettoyage de `zigbee_absences`. Pas un fix d'urgence.

- **Fix à concevoir proprement** (jamais déployé) :
  1. Source de vérité unique : durée depuis `last_changed` lorsque `state == "unavailable"` (universel, pas dépendant d'attributs spécifiques HA)
  2. Périmètre : entités de la cartographie ciblées par catégorie (ex: `prise_connectee/commande` uniquement, pas `_option_*` ou `_silent_mode`)
  3. Cooldown par device (clé `zigbee_mort_<eid>`), pas global
  4. Reset de `zigbee_absences` quand un device est en ligne stable depuis > 1h (purge des entrées dont `retour_en_ligne` est rempli depuis plus d'une heure)
  5. Tester avec un débranchement volontaire avant de pousser en prod

---

## 📋 Comment contribuer

Ajoutez vos pièges via GitHub Issue "Leçon fondatrice" avec :
1. L'appareil concerné
2. Le symptôme observé
3. La cause identifiée
4. Le fix appliqué (ou souhaité)

### Skill heartbeat_pilier — surveillance apprenante des sensors énergétiques (25/04/2026)

- **Contexte** : la leçon précédente identifiait 3 systèmes cassés pour la détection offline. Le skill `heartbeat_pilier` est la première brique de la solution propre : surveillance **apprenante** de la fraîcheur des sensors énergétiques piliers.
- **Périmètre** : 8 sensors énergétiques explicites (Ecojoko x4 + APSystems x2 + Anker x2) + 2 sensors HC/HP traités séparément.
- **Architecture** :
  - Table `sensor_heartbeat` (entity_id PRIMARY KEY, median_sec, p95_sec, p99_sec, samples_count, last_recompute, learning_started, learning_complete)
  - Phase apprentissage : 7 jours d'observation silencieuse à l'installation du sensor
  - Phase calibration : à J+7, calcul des seuils depuis `/api/history` HA (médiane, P95, P99)
  - Phase surveillance : alerte si gap > P99×2 (warning, cooldown 6h) ou P99×5 (critique, cooldown 1h)
  - Recompute hebdomadaire automatique pour s'adapter aux saisons
- **Pourquoi pas de seuil hardcodé** : la mesure périodique des 8 sensors sur 24h a montré que les comportements sont très différents (ex: `ecojoko_consommation_temps_reel` médiane 1 min vs `ecojoko_surplus_de_production` médiane 3 min mais avec gaps légitimes de 7h la nuit). Un seuil unique de 30 min aurait généré des fausses alertes nocturnes.
- **Pourquoi 1 seule commande Telegram (status, pas reset)** : le dispatcher de skills.py attend des fonctions sans argument qui retournent un string. Adapter le dispatcher pour supporter des sous-commandes touche 50+ commandes existantes — risque trop élevé pour un bénéfice mince.
- **Reset de l'apprentissage si besoin (via SSH)** :
  ```bash
  # Reset complet (re-démarre l'apprentissage des 8 sensors)
  sudo sqlite3 /home/lolufe/assistant/memory.db "DELETE FROM sensor_heartbeat;"
  sudo systemctl restart assistant.service
  
  # Reset d'un seul sensor
  sudo sqlite3 /home/lolufe/assistant/memory.db \
    "DELETE FROM sensor_heartbeat WHERE entity_id='sensor.X';"
  ```

---

### Tarif Zen Week-End Plus mal géré par little_monkey (27/04/2026)

- **Symptôme** : `sensor.ecojoko_consommation_hc_reseau` et `_hp_reseau` restent en `unknown` pendant des heures, déclenchant des fausses alertes heartbeat.
- **Diagnostic** :
  - Le tarif "EDF Zen Week-End Plus - Option Heures Creuses" est correctement configuré côté Ecojoko (vérifié sur service.ecojoko.com)
  - L'intégration little_monkey v1.2.4 (la dernière) ne supporte explicitement que HP/HC classique et Tempo (Bleu/Blanc/Rouge) selon son README
  - Zen Week-End Plus est un tarif hybride (HC quotidien + week-end + 1 jour au choix en HC) : ni HP/HC pur, ni Tempo
  - Conséquence : little_monkey reçoit des `null` de l'API Ecojoko pour ces 2 capteurs spécifiques, et HA stocke `unknown`
  - Le sensor `sensor.depense_du_jour_ecojoko` continue de fonctionner car calculé sans découpage HC/HP
- **Décision** : décocher les capteurs HC/HP dans la configuration little_monkey HA → les entités disparaissent → plus de fausses alertes
- **Conséquence acceptée** : pas de découpage HC/HP dans Home Assistant côté Ecojoko. Mais le bot AssistantIA détecte le tarif HC via d'autres entités (Linky/ZLinky/ESPHome/Tempo) en fallback (cf. skills.py L7600-7616), et sait calculer ses plages HC à partir d'historique
- **Patch code** : `_HEARTBEAT_SENSORS_TARIF` vidée dans skills.py — plus de surveillance heartbeat sur ces 2 sensors
- **Action future** : si little_monkey ajoute le support Zen Week-End Plus dans une version ultérieure, recocher les capteurs et ré-ajouter à la liste

---
