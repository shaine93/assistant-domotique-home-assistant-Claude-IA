# 📋 CAHIER DES CHARGES — AssistantIA Domotique v7.60
## L'IA qui gère votre maison. Vous ne faites rien.

**Version** : 7.58
**Date** : 22/03/2026
**Script** : ~11 814 lignes | 22 tables | 11 threads | 10 skills | 51 commandes | 25 rôles

---

## 🔄 REPRISE DE CONVERSATION — AUTONOMIE 500%

### Si cette discussion est fermée

Le MD est envoyé par mail à chaque modification. L'utilisateur le reçoit automatiquement.
Pour reprendre : copier-coller le bloc ci-dessous dans une nouvelle conversation Claude.

**Le nouveau Claude doit être autonome sans intervention de l'utilisateur.**
Il lit le MD, lit le script, comprend l'état, et continue.

### Bloc de reprise (copier-coller)

```
Tu es Claude, tu reprends le projet AssistantIA Domotique.
AVANT DE RÉPONDRE : lis le Cahier des Charges et le script sur la VM.

ÉTAPE 1 — Lire le MD :
python3 << 'E1'
import json, urllib.request
SECRET = "45605531a18b27dca47cc640701f8c7c6571cdba33b0876b152e1e31be161ec4"
req = urllib.request.Request("http://34.168.105.47:8501/read/Cahier_des_Charges.md")
req.add_header("Authorization", f"Bearer {SECRET}")
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read().decode())
print(data["content"][:5000])
E1

ÉTAPE 2 — Lire l'état du système :
python3 << 'E2'
import json, urllib.request
SECRET = "45605531a18b27dca47cc640701f8c7c6571cdba33b0876b152e1e31be161ec4"
req = urllib.request.Request("http://34.168.105.47:8501/status")
req.add_header("Authorization", f"Bearer {SECRET}")
resp = urllib.request.urlopen(req, timeout=10)
print(json.loads(resp.read().decode()))
E2

ÉTAPE 3 — Lire les derniers logs :
python3 << 'E3'
import json, urllib.request
SECRET = "45605531a18b27dca47cc640701f8c7c6571cdba33b0876b152e1e31be161ec4"
req = urllib.request.Request("http://34.168.105.47:8501/logs?n=30")
req.add_header("Authorization", f"Bearer {SECRET}")
resp = urllib.request.urlopen(req, timeout=10)
for line in json.loads(resp.read().decode())["lines"]:
    if "DEBUG" not in line:
        print(line[:180])
E3

INFRASTRUCTURE :
- VM Google Cloud : user@instance-20260226-111134 / 34.168.105.47
- Script : assistant.py (~10454 lignes, v1.5.0)
- Deploy Server : port 8501, HMAC-SHA256
- Deploy secret : 45605531a18b27dca47cc640701f8c7c6571cdba33b0876b152e1e31be161ec4
- DB : memory.db (21 tables)
- MD : Cahier_des_Charges.md

DEPLOY SERVER :
- GET (Bearer token) : /ping /status /read /read/<path> /logs?n=N /ls
- POST (HMAC-SHA256) : /patch /restart /rollback /file /delete /deploy
- Patch : {"mode": "replace", "old_str": "...", "new_str": "..."}
- Toujours vérifier la syntaxe Python après patch, avant restart
- Toujours faire UN SEUL restart après tous les patches

MATÉRIEL INSTALLATION :
- HA : https://your-ha-instance.duckdns.org (443→8123, verify=False)
- Ecojoko : conso réseau temps réel (PAS de production solaire)
- APSystems ECU : production solaire (glitche à 0W entre updates 5min)
- Anker Solarbank E1600 : batterie solaire indépendante
- EDF Zen Week-End Plus HP/HC (jour choisi = mercredi)
- 110+ devices Zigbee, 2 NAS Synology, imprimante Brother, Ender 3
- Localisation : Seine-Saint-Denis (93)

DOCTRINE — RESPECTER ABSOLUMENT :
1. AUTONOMIE 500% — L'utilisateur ne fait RIEN. L'IA gère tout.
2. TOKENS RENTABLES — Chaque token rend le système plus intelligent. ROI positif.
3. ZÉRO FAUX POSITIF — Filtre central telegram_send. Vérifier avant d'envoyer.
4. EXPERTISE ≤ 50 — Cap strict, fondatrices protégées, doublons supprimés.
5. ROOT-CAUSE — Pas de workaround. Comprendre le problème, le corriger.
6. FICHIERS COMPLETS — Jamais de fragments. Toujours le code entier.
7. MD = SOURCE DE VÉRITÉ — Mettre à jour après chaque changement important.
8. PAS DE SPAM — Alertes dédupliquées, seuils réalistes, messages validés.
9. SURVEILLANCE TOUJOURS ON — Jamais bloquée par SMS ou canal_verrouille.
    - Détection nouvelles entités : toutes les 5 min (0 token, pattern matching local)
    - Scan infiltration Haiku : toutes les 1h (catégorisation IA des entités inconnues)
    - Prises/capteurs puissance : auto-catégorisés immédiatement + notification Telegram
10. APPRENDRE DE SES ERREURS — Chaque bug = leçon fondatrice permanente.
11. AUTO-CORRECTION IMMÉDIATE — Toute erreur détectée doit remonter ET se corriger.
    - ErrorCaptureHandler : intercepte TOUS les log.error() dans un buffer mémoire
    - _remonter_erreurs() : toutes les 5 min, groupe par signature, anti-spam 6h
    - Telegram : résumé des nouvelles erreurs (max 5 par message)
    - decisions_log : chaque erreur enregistrée (ERREUR_AUTO) pour apprentissage
    - Auto-correction Sonnet : déclenchée automatiquement si erreur >= 5x en 24h

PIÈGES CONNUS (ne pas refaire) :
- sensor.ecu_current_power glitche à 0W → fallback skill fenêtre solaire
- button.*/automation.* ≠ capteurs physiques → toujours filtrer par domaine
- OctoPrint ≠ imprimante Brother → exclure octoprint
- Prise Anker ≠ cycle machine → EXCLUSIONS_PRISES
- PAC thermostat on/off = NORMAL → alerter seulement si maison se refroidit
- Baselines < 30 mesures = bruit → minimum 30
- canal_verrouille ne doit JAMAIS bloquer le monitoring
- Table tokens : colonnes = tokens_in/tokens_out (PAS input_tokens/output_tokens)
- lecons_fondatrices guard : source LIKE 'lecon_fondatrice%' (pas exact match)
- echecs_historiques : guard obligatoire (INSERT une seule fois, pas à chaque restart)
- Auto-découverte rôles : pattern match obligatoire si patterns définis (sinon faux positifs device_class+unit)
- /probleme sans argument : doit retourner aide statique, PAS tomber dans appel_claude (Haiku hallucine)
- HA APIs area_registry/entity_registry retournent 0 sur HA Green REST → fallback device_registry + friendly_name
- Pièce stockée une seule fois en cartographie → ha_refresh_areas met à jour au démarrage/scan
- Cycles machines : 2 seuils obligatoires — SEUIL_CYCLE (200W) pour DÉMARRER, SEUIL_FIN (10W) pour TERMINER. Un lave-linge en phase lavage consomme 100-200W → un seuil unique de 200W déclare le cycle fini pendant le lavage
- Restauration cycle après restart : _puissances_historique est vidé → backfill obligatoire via /api/history/period/ HA
- Cycle restart : au restart, un cycle déjà terminé (puissance basse depuis > 5 min) est fermé via cycle_fin() — JAMAIS re-notifié. Un cycle encore actif est restauré avec rappel marqué comme envoyé.
- Réponses commandes : JAMAIS filtrées (force=True). Les filtres ne s'appliquent qu'aux messages proactifs.
- Sèche-linge fin de cycle : les restarts répétés pendant le dev cassent la surveillance. En production le script tourne sans interruption — les cycles sont surveillés bout en bout. Chaque restart doit vérifier l'état réel de la machine.
- Script trop gros : 13 000 lignes dans 1 fichier → auto-guérison coûte ~0.30$/appel (100K tokens). Découper en modules < 1 500 lignes. L'utilisateur paie pour des économies, pas pour du debug.
- Valeur utilisateur machines : l'utilisateur se fiche du nom du programme. Il veut savoir QUAND sortir le linge (gain de temps). Prédiction temporelle > nom du programme.
- Restart cycle : ne JAMAIS re-notifier un cycle terminé au restart. Vérifier la puissance actuelle, demander à l'utilisateur si ambiguë.
- Filtre Telegram : les réponses aux commandes utilisateur ne sont JAMAIS filtrées (force=True). Les filtres ne s'appliquent qu'aux messages proactifs.
- Sèche-linge : pause préchauffage→séchage peut durer 38 min. GRACE_APRES_SECHAGE = 45 min. Durée minimale 30 min (un cycle de 13 min = pause, pas fin).
- Auto-guérison : ZÉRO notification Telegram sur les erreurs/bugs/watchdog/anomalies internes. L'utilisateur paie pour des économies, pas pour du spam technique. Seules les alertes utiles (EDF, PAC, batteries, météo, cycles) passent.
- Détection appareil : ne JAMAIS supposer le type par la marque (matter, tapo, shelly ≠ prise). Seuls critères : nom explicite (prise/plug/outlet/socket) OU capteur puissance W + switch associé
- Profil puissance machines : mesure toutes les 2 min (polling prises) → résolution limitée, les phases courtes (<4 min) peuvent être fusionnées
- Lave-linge : pause rinçage→essorage = 20-25 min → GRACE_FIN_MIN doit être ≥ 30 min
- Prises auto-catégorisées sans notification → l'utilisateur ne sait pas qu'elles sont détectées
- HA REST endpoints area_registry/entity_registry/device_registry retournent 404 sur HA Green → utiliser /api/template avec Jinja2
- Séparateur Jinja2 template : utiliser ;;; et ::: (pas \n qui s'échappe mal dans les patches JSON)

Lis le MD complet puis dis : "J'ai repris le projet. Voici l'état actuel : ..."
```

### Envoi automatique par mail

Le MD est envoyé par mail automatiquement dès qu'il est modifié (détection hash MD5).
Commande manuelle : `/md` → envoie le MD par mail immédiatement.

---

---

---

---

## 🧬 GENÈSE — LE BUSINESS MODEL

### Le cercle vertueux

```
    TOKENS (5-10€/mois)
         │
         ▼
    INTELLIGENCE (baselines, skills, profil foyer)
         │
         ▼
    ÉCONOMIES D'ÉNERGIE (solaire, tarif, coupe-veille, surconso)
         │
         ▼
    L'UTILISATEUR VOIT LE ROI → CONTINUE À PAYER LES TOKENS
         │
         ▼
    PLUS D'INTELLIGENCE → PLUS D'ÉCONOMIES → MOINS DE TOKENS
```

**Chaque token dépensé doit produire plus d'économies qu'il ne coûte.** C'est la seule règle qui compte. Le script n'est pas un outil de surveillance — c'est une **machine à économiser de l'énergie** qui se finance par ses propres résultats.

### Sources d'économies

| Source | Mécanisme | Gain typique |
|--------|-----------|--------------|
| ☀️ Cycles solaire | Lancer les machines au pic solaire | 2-5€/mois |
| ⚡ Optimisation tarif | Décaler en HC, exploiter le weekend | 1-3€/mois |
| 🔇 Coupe-veille | Standby TV/PC/ventilateur évité | 1-3€/mois |
| 📉 Surconso détectée | Alerter quand la conso dépasse la baseline | 1-2€/mois |
| 💡 Recommandations IA | Claude analyse et propose des actions | variable |

**Chaque économie est enregistrée dans la table `economies`** — mesurée, horodatée, catégorisée. `/roi` et `/economies` montrent le bilan en temps réel.

### Pourquoi Claude AI est indispensable

Un script classique peut surveiller et alerter. Mais il ne peut pas :
- Apprendre que VOTRE lave-linge consomme 1.23 kWh et recommander de le lancer quand VOS panneaux produisent 2700W
- Détecter que VOTRE consommation du mercredi soir est 30% au-dessus de la baseline et investiguer
- S'auto-corriger quand il détecte un bug récurrent
- Évoluer par la conversation : `/probleme je veux...`

Le script ne peut fonctionner qu'avec Claude AI — c'est le must-have.

---

## 🚀 DÉPLOIEMENT — GUIDE COMPLET

### Étape 0 — Matériel requis

| Machine | RAM min | Coût | Idéal pour |
|---------|---------|------|------------|
| **HA Add-on** (sur HA OS) | 512 MB | 0€ | Déjà sur HA Green/Pi → 1 clic |
| **Raspberry Pi 4/5** | 2 GB | 40-80€ | Dédié, silencieux, 5W |
| **VM Oracle Cloud** (free tier) | 1 GB | 0€ | Gratuit permanent, ARM |
| **VM Google Cloud** (e2-micro) | 1 GB | 0€ | Gratuit 1 an |
| **Mini PC N100/N95** | 8 GB | 80-150€ | Puissant, SSD fiable |
| **NAS Synology** (Docker) | 4 GB | 0€ | Déjà allumé 24/7 |

### Étape 1 — Préparer les credentials (10 min)

| # | Quoi | Où le trouver |
|---|------|---------------|
| 1 | **Bot Telegram** | Telegram → `@BotFather` → `/newbot` → copier le token |
| 2 | **Token HA** | HA → Profil → Tokens longue durée → Créer |
| 3 | **URL HA** | `http://192.168.1.XX:8123` ou `https://xxx.duckdns.org` |
| 4 | **Clé Anthropic** | `console.anthropic.com` → API Keys → Create |
| 5 | **Sécurité** | Choisir : 📱 SMS Free / 🔔 Notif HA / 📧 Email |

### Étape 2 — Installer

**Option A : HA Add-on (2 min)** — Paramètres → Add-ons → Dépôts → coller URL GitHub → Installer → Config → Démarrer

**Option B : Script standalone (5 min)**
```bash
git clone https://github.com/votre-repo/assistantia-domotique.git
cd assistantia-domotique && pip install anthropic requests
python3 assistant.py
```

**Option C : Docker (3 min)**
```bash
docker run -d --name assistantia --restart unless-stopped \
  -v assistantia_data:/app/data -p 8501:8501 \
  ghcr.io/votre-repo/assistantia-domotique:latest
```

**Option D : Docker Compose / NAS**
```yaml
services:
  assistantia:
    image: ghcr.io/votre-repo/assistantia-domotique:latest
    restart: unless-stopped
    volumes: ["./data:/app/data"]
    ports: ["8501:8501"]
```

### Étape 3 — Setup Wizard (100% Telegram)

Le script se configure par conversation Telegram — 3 phases :

**Phase 1 : Connexion** (1 question terminal + 4 Telegram)
1. Token Telegram (terminal)
2. URL Home Assistant → testée
3. Token HA → vérifié + comptage entités
4. Clé Anthropic → testée
5. Méthode sécurité (boutons)

**Phase 2 : Profil foyer** (8 questions par boutons)
- 👥 Nombre de personnes | 🏠 Présence semaine | ☀️ Solaire (+ kWc si oui)
- 🌡️ Chauffage | 🚿 Eau chaude | 🗣️ Assistant vocal | 🎯 Objectif
- Chaque réponse alimente le skill `foyer` — c'est la mémoire fondatrice

**Phase 3 : Appareils sur prises** (1 question par prise)
- Pour chaque prise avec capteur de puissance, 3 catégories :

  **🔄 Gros consommateurs** (cycles, coûts, rappels) : 🧺 Lave-linge | 👕 Sèche-linge | 🍽️ Lave-vaisselle | ❄️ Congélateur | 🔥 Four

  **🔇 Coupe-veille** (piloté par assistant vocal — mesure standby évité) : TV, PC, ventilateur

  **📊 Monitoring énergie** (mesure production/conso) : prise Anker, onduleurs

  **🔌 Autre** (nommer) | **⬜ Ignorer** (voie de garage)

**Phase 4 : Automatique** — Scan HA + rôles + tarif + baselines

### Étape 4 — Vérification

Envoyez `/audit` → `/profil` → `/appareils` → `/surveillance`

---

## 🤝 MISE EN SERVICE — CLAUDE OPUS 4.6

Le déploiement assisté se fait via **Claude Opus 4.6 étendu** — le seul modèle capable de lire les 11 814 lignes et de comprendre votre installation.

```
Je déploie AssistantIA Domotique.
Voici mon Cahier des Charges : [coller ce MD]
Mon matériel : [Raspberry Pi / VM / Mini PC / NAS]
Home Assistant : [version, URL]
Aide-moi à le déployer.
```

| Modèle | Rôle |
|--------|------|
| **Claude Opus 4.6** | Déploiement, nouvelles fonctionnalités, diagnostic, support |
| Claude Sonnet | Auto-correction via `/probleme` (patches + restart) |
| Claude Haiku | Surveillance quotidienne (baselines, analyses, recommandations) |

---

## 📱 COMMANDES TELEGRAM — 53 COMMANDES

### Énergie & Économies

| Commande | Description |
|----------|-------------|
| `/energie` | Bilan complet : solaire, batterie, conso, PAC, températures |
| `/energie detail` | Bilan détaillé avec historique |
| `/solaire` | Production solaire instantanée + jour |
| `/tarif` | Tarif électricité (fournisseur, offre, HC) |
| `/bilan_tarif` | Bilan mensuel par période (HP/HC/WE) |
| `/roi` | ROI : tokens vs économies réelles |
| `/economies` | Détail économies par source et par jour |

### Surveillance & Appareils

| Commande | Description |
|----------|-------------|
| `/audit` / `/rapport` | Rapport complet : énergie, Zigbee, NAS, PAC, batteries |
| `/scan` | Recompte entités, recatégorise |
| `/surveillance` | Vue complète : entités, appareils, threads, mode sniper |
| `/appareils` | Appareils sur prises par catégorie (+ reset) |
| `/profil` | Profil foyer — base des skills (+ reset) |
| `/cycles` | 10 derniers cycles machines |
| `/programmes` | Profils de cycles appris |
| `/batteries` / `/piles` | Batteries Zigbee + Anker |
| `/zigbee` | Réseau Zigbee : LQI, hors ligne |
| `/nas` | NAS Synology : volumes, températures |
| `/hote` / `/sante` | Santé machine hôte |

### Intelligence

| Commande | Description |
|----------|-------------|
| `/intelligence` | Score /100 + progression |
| `/expertise` | 50 règles apprises |
| `/apprentissage` | Journal échecs/succès |
| `/analyse` | Force une analyse IA |
| `/skills` | Skills autonomes |
| `/baselines` | Comportements normaux |
| `/roles` | Rôles auto-découverts |
| `/memoire` | Mémoire SQLite |
| `/calendrier` | Événements calendrier HA |
| `/dashboard` | Push sensors vers HA (Lovelace) |

### Administration

| Commande | Description |
|----------|-------------|
| `/budget` | Budget API Anthropic |
| `/debug` | Threads, watchdog, versions |
| `/logs` | 20 dernières lignes |
| `/sms` | Renvoyer code sécurité |
| `/md` | Envoyer le MD par mail |
| `/export` / `/script` / `/claude` | Exporter le script |
| `/documentation` / `/aide` | Liste commandes |
| `/automatisations` | Automatisations HA |
| `/addons` | Add-ons HA |

### Actions & Alertes dynamiques

| Commande | Description |
|----------|-------------|
| `/watches` / `/alertes` | Liste toutes les alertes automatiques actives |
| *(langage naturel)* | "Ouvre la serrure" → boutons ✅/❌ → exécution HA |
| *(langage naturel)* | "Préviens-moi si un onduleur passe offline" → alerte auto |

> **Tool Use Claude** : actions HA et alertes dynamiques pilotées par Claude Haiku via API Anthropic tool use. L'utilisateur parle naturellement, Claude appelle le bon service, confirmation par bouton Telegram.

### Auto-correction

| Commande | Description |
|----------|-------------|
| `/probleme <description>` | Sonnet lit 11k lignes → patch → ✅/❌ |

### Diagnostics développeur

`/diag_energie` `/diag_prises` `/diag_ecojoko` `/diag_nas` `/diag_carto` `/diag_hc` `/diag_meteo` `/diag_forecast` `/test_meteo` `/nettoyer`

---

## 🏗️ ARCHITECTURE

### 11 Threads permanents

| Thread | Fréquence | Rôle |
|--------|-----------|------|
| `surveillance_monitoring` | 60s rapide / 5 min complet | Tick rapide (EDF, PAC, erreurs, moteur économies) + tick complet (NAS, Zigbee, météo, intelligence) |
| `surveillance_prises` | 20s actif / 60s repos | Mode sniper adaptatif |
| Autres | 30min-24h | Batteries, audit, scan, watchdog, backup, keepalive, découverte, bilan |

### 23 Tables SQLite

| Table | Rôle |
|-------|------|
| `cartographie` | ~657 entités catégorisées |
| `appareils` | Association prise → type machine (configuré par l'utilisateur) |
| `roles` | 25 rôles universels auto-découverts |
| `baselines` | Comportements normaux par entité/jour/heure |
| `expertise` | 50 règles apprises (cap strict) |
| `cycles_appareils` | Historique cycles (durée, conso, coût, profil) |
| `cycle_mesures` | Mesures puissance temps réel pendant cycles |
| `economies` | Chaque économie mesurée (€, kWh, type, source) — cœur du business model |
| `skills` | Données skills autonomes (dont profil foyer) |
| `decisions_log` | Journal actions/échecs/succès |
| `tokens` | Consommation API par jour |
| `fournisseurs_tarifs` | 6 fournisseurs France |
| `watches` | Alertes dynamiques créées par l'utilisateur via langage naturel |
| Autres | `config`, `batteries`, `hypotheses`, `intelligence_score`, `zigbee_absences`, `entites`, `entites_connues`, `entites_en_attente`, `historique`, `alertes`, `backup_log` |

### 10 Skills autonomes

| Skill | Description |
|-------|-------------|
| `foyer` | Profil foyer : personnes, présence, solaire, chauffage, eau chaude, assistant vocal, objectif |
| `fenetre_solaire` | Meilleure heure pour lancer une machine par jour |
| `comportement_pac` | PAC ON/OFF par tranche de température |
| `cycle_signatures` | Profils de puissance multi-programmes par machine |
| `optimisation_tarif` | Consommation par période HP/HC/WE |
| `recommandations` | Économies potentielles |
| `tarification` | Configuration tarif fournisseur |
| `apprentissage_hc` | Détection automatique heures creuses |
| `sante_hote` / `hote` | Santé machine : RAM, CPU, disque |

### Moteur d'économies proactif (0 token, toutes les 5 min)

Le script ne se contente pas de mesurer — il **crée** des économies.

| Action | Quand | Ce que ça fait |
|--------|-------|----------------|
| 💡 Briefing matin | 7h00 | Bilan hier + prévision solaire ou conseil HP/HC + standby oubliés |
| ☀️ Alerte pic solaire | > 2000W + rien en cours | "Lancez une machine → ~0.32€" (si solaire) |
| 🔇 Standby oublié | toutes les 2h | "TV en veille 12W → 0.31€/jour" (tous les profils) |
| ⚡ HP → HC | 1-2h avant HC | "Machine en HP ! Après 22h → 0.15€" (si tarif HP/HC) |
| 📊 Bilan soir | 21h00 | Total du jour par source + cumul mois |

**Adapté au profil foyer** : sans solaire → conseils HP/HC + weekend. Avec Google Nest → commandes vocales dans les alertes. Objectif réduire facture → alertes standby renforcées.

---

## 🔌 SURVEILLANCE — CE QUI EST SURVEILLÉ

### Détection universelle (Zigbee, Matter, Z-Wave, WiFi, IP)

- **Nouvelles entités** : TOUTE nouvelle entité est notifiée sur Telegram avec les faits (protocole, device_class, état). Pas de supposition.
- **Prises** classées seulement si preuve : nom explicite (prise/plug/outlet/socket) OU capteur puissance W + switch associé
- **Protocole détecté** : Zigbee, Matter, Z-Wave, WiFi, ESPHome, HA
- **Questionnaire automatique** pour chaque nouvelle prise détectée après le setup

### Cycles machines — Mode sniper

- **Polling adaptatif** : 20s quand cycle actif, 60s au repos
- **Mesures SQLite** : chaque Watt stocké en temps réel → survit aux restarts
- **Grâce intelligente** par type machine :
  - Lave-linge après essorage : 7 min (hublot)
  - Lave-linge après chauffage : 30 min (pause rinçage→essorage)
  - Sèche-linge : 15 min (défroissage)
  - Lave-vaisselle : 10 min (séchage vapeur)
- **Rappel immédiat** dès fin de phase active (avant la grâce)
- **Notification finale** avec coût + solaire + cumul économies mois
- **Estimation coût** dès le démarrage du cycle

### 3 catégories d'appareils

| Catégorie | Suivi | Exemples |
|-----------|-------|----------|
| 🔄 Gros consommateurs | Cycles, coûts, rappels, économies solaire | Lave-linge, sèche-linge, lave-vaisselle |
| 🔇 Coupe-veille | Mesure standby évité → compteur économies | TV, PC, ventilateur (via Google Nest) |
| 📊 Monitoring énergie | Mesure production/conso, pas de cycles | Prise Anker Solarbank |

### Surveillance continue (0 token)

Coupure EDF (60s), PAC corrélée, NAS, Zigbee, batteries critiques, météo, imprimante, bridge Z2M, erreurs auto-remontées.

### Alertes dynamiques (watches)

L'utilisateur demande en langage naturel : "Préviens-moi si un onduleur passe offline", "Alerte si température > 28°C".
Claude crée une entrée `watches` (via tool use `ha_create_watch`), vérifiée chaque minute par `surveillance_monitoring`.

- **Pattern matching** : `sensor.ecu_*_power` matche tous les micro-onduleurs
- **Conditions** : `unavailable`, `offline`, `equals`, `not_equals`, `above`, `below`, `changes`
- **Cooldown** configurable, **variables** `{entity_id}`, `{state}`, `{friendly_name}`
- **Gestion** : `/watches` pour lister

### Tool Use — Actions HA via Claude

"Allume la lumière", "Ferme la serrure", "Monte le volet" → Claude Haiku identifie entity_id + service HA → boutons ✅/❌ → exécution.
Domaines : lock, light, switch, cover, climate, fan, vacuum, media_player, scene, script.

---

## 🔐 SÉCURITÉ

Canal Telegram verrouillé au démarrage. Code 6 chiffres via SMS Free Mobile, Notification HA, ou Email.

## 🛡️ GARDE-FOUS

Expertise ≤ 50 règles. Anti-spam alertes. Filtre 4 niveaux. Baselines ≥ 30 mesures. Budget alertes à 50/80/90/100%. Erreurs auto-remontées 60s. Auto-correction si ≥ 5x/24h.

## 🔐 DEPLOY SERVER

Port 8501, HMAC-SHA256. Endpoints : `/ping`, `/status`, `/read`, `/logs`, `/ls`, `/patch`, `/restart`, `/rollback`, `/file`, `/deploy`.

## 📦 HA ADD-ON

Structure prête : `addon/config.yaml`, `Dockerfile`, `run.sh`, `DOCS.md`, `CHANGELOG.md`. Supervisor fournit URL+token automatiquement.

---

## 📕 DOCTRINE — 12 RÈGLES

1. **AUTONOMIE 500%** — L'utilisateur ne fait RIEN. Le script se met à jour tout seul depuis GitHub, se corrige tout seul, apprend tout seul
2. **TOKENS RENTABLES** — ROI positif, chaque token construit de l'expertise
3. **ZÉRO FAUX POSITIF** — Vérifier avant d'envoyer
4. **EXPERTISE ≤ 50** — Cap strict
5. **ROOT-CAUSE** — Pas de workaround
6. **FICHIERS COMPLETS** — Jamais de fragments
7. **MD = SOURCE DE VÉRITÉ** — Mettre à jour après chaque changement
8. **PAS DE SPAM** — Alertes dédupliquées
9. **SURVEILLANCE TOUJOURS ON** — Jamais bloquée
10. **APPRENDRE DE SES ERREURS** — Chaque bug = leçon fondatrice
11. **AUTO-CORRECTION** — Erreurs remontées → auto-correction Sonnet

---


### Règle 12 — ISOLATION DES FEATURES

**Toute nouvelle fonctionnalité DOIT tourner dans un bloc isolé.**

```python
# ❌ INTERDIT — un crash tue la boucle
texte = transcrire_vocal(file_id)

# ✅ OBLIGATOIRE — crash isolé, boucle continue
try:
    texte = transcrire_vocal(file_id)
except Exception as e:
    log.error(f"Feature X: {e}")
    telegram_send("❌ Fonctionnalité indisponible.")
    continue
```

**Principes :**
1. Chaque feature est un `try/except` autonome — si elle crash, le script continue
2. Les dépendances optionnelles (pip, apt) s'installent en background — si absentes, la feature retourne `None`
3. Le polling Telegram ne doit JAMAIS s'arrêter à cause d'une feature
4. Diagnostic d'import chain AVANT de toucher au service en production
5. Rollback automatique si le diagnostic échoue

**Test avant déploiement :**
- Déployer un script diagnostic qui teste `from shared import *` + `from skills import *`
- Vérifier que tous les noms critiques sont accessibles
- Seulement ensuite déployer le vrai `assistant.py`

## ## ⚠️ PIÈGES CONNUS (ne pas refaire) :
- sensor.ecu_current_power glitche à 0W → fallback skill fenêtre solaire
- button.*/automation.* ≠ capteurs physiques → toujours filtrer par domaine
- OctoPrint ≠ imprimante Brother → exclure octoprint
- Prise Anker ≠ cycle machine → EXCLUSIONS_PRISES
- PAC thermostat on/off = NORMAL → alerter seulement si maison se refroidit
- Baselines < 30 mesures = bruit → minimum 30
- canal_verrouille ne doit JAMAIS bloquer le monitoring
- Table tokens : colonnes = tokens_in/tokens_out (PAS input_tokens/output_tokens)
- lecons_fondatrices guard : source LIKE 'lecon_fondatrice%' (pas exact match)
- echecs_historiques : guard obligatoire (INSERT une seule fois, pas à chaque restart)
- Auto-découverte rôles : pattern match obligatoire si patterns définis (sinon faux positifs device_class+unit)
- /probleme sans argument : doit retourner aide statique, PAS tomber dans appel_claude (Haiku hallucine)
- HA APIs area_registry/entity_registry retournent 0 sur HA Green REST → fallback device_registry + friendly_name
- Pièce stockée une seule fois en cartographie → ha_refresh_areas met à jour au démarrage/scan
- Cycles machines : 2 seuils obligatoires — SEUIL_CYCLE (200W) pour DÉMARRER, SEUIL_FIN (10W) pour TERMINER. Un lave-linge en phase lavage consomme 100-200W → un seuil unique de 200W déclare le cycle fini pendant le lavage
- Restauration cycle après restart : _puissances_historique est vidé → backfill obligatoire via /api/history/period/ HA
- Cycle restart : au restart, un cycle déjà terminé (puissance basse depuis > 5 min) est fermé via cycle_fin() — JAMAIS re-notifié. Un cycle encore actif est restauré avec rappel marqué comme envoyé.
- Réponses commandes : JAMAIS filtrées (force=True). Les filtres ne s'appliquent qu'aux messages proactifs.
- Sèche-linge fin de cycle : les restarts répétés pendant le dev cassent la surveillance. En production le script tourne sans interruption — les cycles sont surveillés bout en bout. Chaque restart doit vérifier l'état réel de la machine.
- Script trop gros : 13 000 lignes dans 1 fichier → auto-guérison coûte ~0.30$/appel (100K tokens). Découper en modules < 1 500 lignes. L'utilisateur paie pour des économies, pas pour du debug.
- Valeur utilisateur machines : l'utilisateur se fiche du nom du programme. Il veut savoir QUAND sortir le linge (gain de temps). Prédiction temporelle > nom du programme.
- Restart cycle : ne JAMAIS re-notifier un cycle terminé au restart. Vérifier la puissance actuelle, demander à l'utilisateur si ambiguë.
- Filtre Telegram : les réponses aux commandes utilisateur ne sont JAMAIS filtrées (force=True). Les filtres ne s'appliquent qu'aux messages proactifs.
- Sèche-linge : pause préchauffage→séchage peut durer 38 min. GRACE_APRES_SECHAGE = 45 min. Durée minimale 30 min (un cycle de 13 min = pause, pas fin).
- Auto-guérison : ZÉRO notification Telegram sur les erreurs/bugs/watchdog/anomalies internes. L'utilisateur paie pour des économies, pas pour du spam technique. Seules les alertes utiles (EDF, PAC, batteries, météo, cycles) passent.
- Détection appareil : ne JAMAIS supposer le type par la marque (matter, tapo, shelly ≠ prise). Seuls critères : nom explicite (prise/plug/outlet/socket) OU capteur puissance W + switch associé
- Profil puissance machines : mesure toutes les 2 min (polling prises) → résolution limitée, les phases courtes (<4 min) peuvent être fusionnées
- Lave-linge : pause rinçage→essorage = 20-25 min → GRACE_FIN_MIN doit être ≥ 30 min
- Prises auto-catégorisées sans notification → l'utilisateur ne sait pas qu'elles sont détectées
- HA REST endpoints area_registry/entity_registry/device_registry retournent 404 sur HA Green → utiliser /api/template avec Jinja2
- Séparateur Jinja2 template : utiliser ;;; et ::: (pas \n qui s'échappe mal dans les patches JSON)



---

## 💎 PRODUIT — Ce qui fait dire "putain c'est possible ça ?!"

### Le moment magique (5 premières minutes)

L'utilisateur installe. Ne configure RIEN. Le script dit :

> "J'ai trouvé 110 appareils sur ton installation.
> Tu as des panneaux solaires, une batterie, une pompe à chaleur, 8 prises connectées.
> Ton lave-linge tourne depuis 23 min — prêt vers 14h30.
> 3 appareils ont un signal faible sur ton réseau.
> Tu tires 340W du réseau alors que tes panneaux produisent 1200W — lance le sèche-linge, c'est gratuit."

**Personne ne fait ça.** Ni Google Home, ni Alexa, ni aucun add-on HA.

### Les 3 piliers du produit puissant

#### 1. "Il connaît déjà ma maison" — Intelligence immédiate
- Scan automatique : 0 configuration, 0 YAML, 0 automation manuelle
- Détection universelle (Zigbee, Matter, WiFi, Z-Wave) + identification machine par profil de consommation
- L'utilisateur installe → le script comprend. Pas l'inverse.

#### 2. "Il me fait gagner du temps et de l'argent" — Valeur quotidienne prouvée
- Briefing matin : météo + trajet + poubelles + pic solaire + recommandation machine
- Prédiction temporelle : "Linge prêt dans ~35 min" → gain de temps réel
- Économies mesurées en € : chaque jour, chaque semaine, chaque mois
- L'utilisateur VOIT la valeur. Chaque jour. En euros.

#### 3. "Il s'améliore tout seul" — Le produit invisible
- Auto-guérison silencieuse : se corrige sans rien dire
- Auto-update depuis GitHub : s'améliore la nuit
- Apprentissage collectif : 10 maisons apprennent, tout le monde profite
- L'utilisateur ne sait même pas que le script a évolué. Il remarque juste que c'est "de mieux en mieux".

### Le pitch qui tue (30 secondes)

> "J'ai une IA sur mon Home Assistant. Elle a scanné ma maison toute seule,
> elle sait quand mon linge est prêt, elle me dit de lancer le sèche-linge
> quand le solaire produit assez, et elle me montre combien j'économise chaque mois.
> Je n'ai rien configuré. 5 minutes d'installation. Open source."

### Ce que Claude AI apporte que PERSONNE d'autre ne peut

| Capacité | Pourquoi Claude et pas GPT/Gemini |
|---|---|
| **Compréhension du code Python** | Claude lit son propre code de 13 000 lignes et se corrige. GPT hallucine sur les gros fichiers. |
| **Raisonnement sur les données HA** | Claude comprend les entity_id, les states, les attributs. Pas besoin de fine-tuning. |
| **Auto-guérison** | Sonnet analyse le bug + le contexte + le script → 1 patch chirurgical. Impossible avec une API GPT brute. |
| **Coût maîtrisé** | Haiku pour le quotidien (0 token la plupart du temps), Sonnet seulement pour les corrections. Budget ~5-10€/mois. |

## 🎯 STRATÉGIE — Pionnier IA × Home Assistant

### Pourquoi maintenant

Personne n'a fait le pont **agent IA autonome + Home Assistant + économies mesurables**.
Il existe des chatbots HA (Extended OpenAI, Google Generative AI) mais ce sont des assistants conversationnels — pas des antivirus.
AssistantIA est le premier agent qui **apprend, surveille, corrige, et mesure le ROI en euros**.

### Le plan en 6 semaines

#### Semaine 1-2 : HACS (distribution rapide)

- **Publier sur HACS** (Home Assistant Community Store) — le chemin le plus rapide vers la visibilité. 1 clic = installé. Pas de VM, pas de Docker pour l'utilisateur.
- Format : Custom Integration ou Add-on HACS
- Avantage : les power users HA traînent sur HACS. Ce sont les early adopters idéaux.

#### Semaine 2-3 : Contenu viral

- **Vidéo YouTube 5 min** : "Mon IA m'a fait économiser X€ ce mois sans que je fasse rien"
  - Montrer le Telegram en live : briefing matin, cycle machine, économies
  - Montrer le /intelligence score
  - Montrer l'auto-guérison en action
  - Titre accrocheur : "J'ai mis une IA sur mon Home Assistant — elle surveille ma maison 24/7"
- **Post blog Medium/dev.to** : article technique "Building an autonomous AI agent for Home Assistant with Claude"
- **Thread Reddit r/homeassistant** : "I built an AI agent that monitors my home, detects my appliances, and saves money — open source"

#### Semaine 3-4 : Communauté

- **10 bêta testeurs** (texte prêt dans ce MD)
- **Forum HA Community** : post détaillé avec screenshots
- **Discord HA** : channel dédié ou post dans #projects
- **GitHub Discussions** : Q&A ouvert, roadmap publique

#### Semaine 4-5 : Partenariats

- **Anthropic Showcase** : contacter Anthropic pour être mis en avant comme use case Claude. "An open-source AI agent for smart homes — powered by Claude". Anthropic cherche des success stories concrètes.
- **Home Assistant Blog** : proposer un guest post ou être mentionné dans la newsletter HA
- **Influenceurs HA** : Rob (The Hook Up), Everything Smart Home, Smart Home Junkie — leur envoyer le script

#### Semaine 5-6 : Store officiel

- **Soumettre au HA Add-on Store officiel** — le graal. Chaque utilisateur HA le voit dans son store. Critères : documentation, tests, code review.
- **HA Integration officielle** (long terme) — le script devient une intégration native via HACS puis core.

### Les 3 différenciateurs uniques

| # | Ce qu'on fait | Ce que les autres NE font PAS |
|---|---|---|
| 1 | **ROI mesurable en €** | Les chatbots HA discutent. Nous mesurons. "Ce mois : +12€ économisés." |
| 2 | **Autonomie totale** | Les autres nécessitent des automations manuelles. Nous apprenons seuls. |
| 3 | **Auto-guérison** | Les autres crashent et attendent un fix. Nous nous corrigeons en silence. |

### Positionnement

> **AssistantIA — L'antivirus de votre maison**
> Premier agent IA autonome pour Home Assistant.
> Il apprend votre maison, surveille votre énergie, détecte vos machines, et se corrige tout seul.
> Vous ne faites rien. Il fait tout. Et il vous dit combien il vous a fait économiser.

### Monétisation (v3.0+)

1. **Freemium** : script open source gratuit (Haiku). Premium = Sonnet/Opus pour l'auto-guérison avancée + prédictions + graphiques avancés.
2. **SaaS Cloud** : hébergement du script en cloud (pas besoin de VM). 5€/mois. L'utilisateur n'installe rien.
3. **App mobile premium** : fonctionnalités avancées dans l'app (widget, multi-maison, tablette kiosque).
4. **Marketplace de skills** : les développeurs vendent des skills spécialisés (piscine, EV, photovoltaïque avancé).

## 🚀 ROADMAP

### Fait ✅ (session 29-31/03/2026 — v7.58 → v7.60)

- [x] Tool Use HA : Claude Haiku pilote les appareils via Anthropic tools (10 domaines)
- [x] Confirmation par boutons Telegram ✅/❌ avant exécution
- [x] Alertes dynamiques (watches) : créées en langage naturel, vérifiées chaque minute
- [x] Table SQLite `watches` : pattern, condition, state_value, message, cooldown
- [x] Pattern matching glob (`sensor.ecu_*`) pour groupes d'entités
- [x] Commandes `/watches` et `/alertes`
- [x] Tentative split 4 fichiers — rollback, monolithe conservé. Bugs documentés.

### Fait ✅ (session 21-22/03/2026 — v7.12 → v7.34)

- [x] Refactoring entity_id → role_val() (25 rôles, 0 en dur)
- [x] Mode sans solaire / sans PAC (graceful degradation)
- [x] Setup wizard Telegram guidé (1 CLI + 4 Telegram)
- [x] SMS multi-provider (Free + HA Notify + Email)
- [x] README.md communautaire
- [x] Remontée erreurs automatique + auto-correction
- [x] Fix cycles machines : 2 seuils (200W/10W), grâce intelligente (7/15/30 min)
- [x] Mode sniper : polling adaptatif 20s/60s
- [x] Mesures puissance SQLite temps réel (table cycle_mesures)
- [x] Rappels immédiats (linge chaud, hublot, vaisselle)
- [x] Questionnaire appareils (3 catégories : cycles / coupe-veille / monitoring)
- [x] Profil foyer (8 questions → skill fondateur)
- [x] Moteur économies proactif (briefing 7h, pic solaire, standby, HP/HC, bilan 21h)
- [x] Détection universelle (Matter, Zigbee, Z-Wave, WiFi) sans suppositions
- [x] Table economies + /economies + /roi refondé
- [x] Business model genèse (cercle vertueux tokens → économies)
- [x] HA Add-on (Dockerfile, config.yaml, run.sh)
- [x] Tests automatisés (20 tests pytest)
- [x] Localisation FR/EN (i18n.py)
- [x] Dashboard Lovelace (/dashboard → push sensors HA)
- [x] Multi-utilisateur Telegram
- [x] Intégration calendrier HA
- [x] Guide déploiement complet (7 machines, 4 méthodes)
- [x] Mise en service Claude Opus 4.6



## 📋 CHANGELOG v7.60 → v7.61 (04-07 avril 2026)

### Nouvelles fonctionnalités
- **Commandes vocales Telegram** : message vocal → Google Speech API → texte → commande. ffmpeg statique local, zéro dépendance pip
- **Tool Use HA** : pilotage appareils en langage naturel (10 domaines), confirmation boutons ✅/❌
- **Alertes dynamiques (watches)** : surveillance personnalisée, pattern matching glob, cooldown
- **Projection facture EDF** : estimation fin de mois basée sur conso courante
- **Timezone Europe/Paris** : heure d'été/hiver automatique via `os.environ['TZ']`
- **Auto-update GitHub** : vérifie main toutes les 24h, télécharge, valide syntaxe, backup, restart
- **Alerte conso fantôme nocturne** : détecte conso anormale 1h-5h (baseline + 150W)
- **Alerte congélateur coupure longue** : si EDF coupé > 2h → alerte au retour
- **Mode vacances auto** : 48h sans interaction → surveillance réduite
- **Notification cycle restauré** : après restart, notification Telegram si machine tourne encore
- **Détection cycle doux** : sèche-linge éco/délicat < 200W détecté après 5 min de conso continue

### Corrections
- Split 4 fichiers stable en production (config/shared/skills/assistant)
- `_ErrorCaptureHandler` ajouté dans shared.py (manquait du split)
- Logging setup (`log = logging.getLogger()`) dans shared.py
- 25 variables globales extraites du monolithe vers shared.py
- stdlib imports APRÈS wildcard (bug sqlite3 not defined)
- Suppression "Nommer ce programme" (2 emplacements)
- Sécurité boutons Telegram : canal verrouillé bloque les callbacks
- `HEURE_BRIEFING_TRAVAIL` corrigé 5 (UTC) → 7 (Paris)

### Doctrine
- **Règle 12 — Isolation des features** : chaque feature dans try/except, dépendances optionnelles retournent None, polling Telegram ne s'arrête JAMAIS
- Diagnostic d'import chain AVANT déploiement en production
- Rollback automatique si diagnostic échoue

### Architecture
```
config.py      →    98 lignes   Constantes, seuils, timezone
shared.py      → 2 317 lignes   __all__ (124), logging, globals, Telegram, HA, SQLite, transcrire_vocal
skills.py      → 10 587 lignes  Commandes, cycles, économies, surveillance, watches, auto-update
assistant.py   →    920 lignes   main(), threads, wizard, voice handler, pycache cleaner
```


### v1.5.2 (07 avril 2026)
- **Backup auto DB** : memory.db + config.json chaque nuit à 3h, purge > 30 jours
- **Score énergétique DPE** : `/score` — note A-D sur 100 (solaire, économies, standbys, Zigbee, HC/HP, baselines)
- **Export PDF mensuel** : `/export` — rapport complet envoyé par email
- **Conseil contrat** : `/contrat` — compare les offres EDF/TotalEnergies/Octopus
- **Commandes** : score, dpe, export, pdf, contrat, conseil


### v1.5.3 (08 avril 2026)
- **Détection coupure internet** : HA inaccessible > 5min → log, > 30min → alerte, > 60min → SMS
- **Alerte Zigbee device mort** : devices unavailable > 24h, check quotidien 9h
- **Notification Tempo/EJP** : jour rouge/blanc notifié la veille à 19h
- **Détection fuite d'eau** : capteur moisture/water_leak → alerte immédiate
- **Consommation par pièce** : `/pieces` — répartition par area HA
- **Fix défroissage sèche-linge** : grâce ne reset plus sur défroissage < 200W après rappel
- **Fix canal verrouillé SMS** : `shared.canal_verrouille` au lieu de variable locale
- **Commandes** : pieces, pièces, rooms


### v1.5.4 (08 avril 2026)
- **APPAREILS_CONNUS.json** : bibliothèque 9 types (lave-linge, sèche-linge, lave-vaisselle, ballon thermo, borne EV, sèche-serviettes, pompe piscine, four, congélateur) avec pièges connus
- **Rollback automatique** : 3+ crashes en 1h → rollback vers backup + notification
- **Monitoring deploy server** : vérification 2x/h, alerte si down
- **Commandes** : appareils, machines
- **Fix /pieces** : filtre énergie solaire (APSystems exclu)


### v1.5.5 (11 avril 2026)
- **Intégration Google Home / Alexa** : scripts HA créés via API, TTS Nest Hub (chambre + salon)
- **API vocale /ask** : endpoint sur deploy server, réponse en 2s
- **ha_search_entities** : outil générique — Claude cherche les entités sur TOUTE installation HA
- **ha_create_automation** : Claude Sonnet crée des automatisations HA complètes (triggers, conditions, actions choose)
- **Confirmation 3 boutons** : Valider / Modifier / Annuler avec résumé en français
- **Protection anti-doublon** : impossible de créer 2x la même automatisation
- **Smart model** : Sonnet pour les automatisations complexes, Haiku pour le reste
- **Error handling** : retry sans tools sur BadRequest, jamais d'erreur brute à l'utilisateur
- **Mode DEV** : canal ouvert sans SMS
- **Prompt autonome** : Claude ne pose plus de questions, il cherche et agit
- **Commandes** : 62 commandes Telegram + vocal + Google Home

### Architecture API vocale
```
Google Home → "Hey Google, exécute AssistantIA énergie"
    → HA script.assistantia_energie (créé via API)
    → AssistantIA détecte le trigger
    → traiter_message("énergie")
    → TTS google_translate_say sur media_player.salon + chambre
```


### Routines Google Home / Alexa — Guide complet

Les 10 scripts HA sont créés automatiquement par le script au démarrage.
Pour les activer : app Google Home → Automatisations → Ajouter → Déclencheur vocal → Action "Ajuster des appareils" → script correspondant.

| Phrase vocale | Script HA | Réponse |
|---|---|---|
| "Hey Google, énergie maison" | `script.assistantia_energie` | Bilan complet : solaire, conso, machines |
| "Hey Google, score maison" | `script.assistantia_score` | Note DPE dynamique A-D sur 100 |
| "Hey Google, état maison" | `script.assistantia_debug` | Vérification système |
| "Hey Google, conso par pièce" | `script.assistantia_pieces` | Répartition watts par pièce |
| "Hey Google, conseil contrat" | `script.assistantia_contrat` | Comparaison fournisseurs |
| "Hey Google, machines connues" | `script.assistantia_machines` | Appareils détectés |
| "Hey Google, retour investissement" | `script.assistantia_roi` | ROI économies vs coût API |
| "Hey Google, mes alertes" | `script.assistantia_alertes` | Alertes actives (watches) |
| "Hey Google, production solaire" | `script.assistantia_solaire` | Production solaire en cours |
| "Hey Google, facture EDF" | `script.assistantia_facture` | Projection fin de mois |

La réponse est parlée via TTS sur tous les media_players configurés dans `config.json` → `tts_media_players`.

### GitHub
- Repo public : https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA
- 27 fichiers, sanitisés, MIT license
- Issue templates : bug report, feature request, bêta testeur
- Post forum HACF : https://forum.hacf.fr/t/assistantia-domotique-lia-qui-gere-votre-maison-pendant-que-vous-dormez/78164

### À faire — v2.0

#### 🔥 Priorité 1 — GitHub + Bêta testeurs

- [x] **Créer le repo GitHub public** : structure complète (assistant.py, deploy_server.py, addon/, tests.py, i18n.py, docker-compose.yml, systemd service, README.md, CHANGELOG.md, LICENSE MIT)
- [x] **README GitHub vitrine** : screenshots Telegram, architecture, ROI, comparatif avant/après, badges (HA compatible, Claude AI, Python 3.10+, MIT)
- [x] **Appel à 10 bêta testeurs** : post sur le forum HA Community, Reddit r/homeassistant, Discord HA. Texte :
  > **AssistantIA Domotique — L'antivirus de votre maison**
  > Agent IA autonome qui surveille votre Home Assistant 24/7, apprend vos habitudes, et vous fait économiser de l'énergie. Propulsé par Claude AI.
  >
  > **Ce qu'il fait** : détecte vos machines automatiquement, mesure la consommation en temps réel, calcule les économies (solaire, tarif, standby), vous dit quand le linge est prêt, surveille votre réseau domotique, et se corrige tout seul quand il a un bug.
  >
  > **Ce qu'il faut** : Home Assistant + un bot Telegram + une clé API Anthropic (~5-10€/mois). Le script tourne sur n'importe quel Linux (Pi, VM, NAS, HA Add-on).
  >
  > **Installation** : 10 minutes, tout se configure via Telegram (wizard guidé).
  >
  > **Cherche 10 bêta testeurs** avec des installations différentes (avec/sans solaire, avec/sans pompe à chaleur, tous protocoles). Le script s'adapte à chaque configuration. Le déploiement est assisté.
  >
  > Repo : [lien GitHub]
- [x] **REFACTORING MODULES** — critique avant bêta. 13 000 lignes dans 1 fichier = problème :
  - Auto-guérison Sonnet envoie le script COMPLET → ~100K tokens → ~0.30$/correction
  - Debug Opus remplit le contexte → session coupe → frustration
  - L'utilisateur paie pour des économies, pas pour du debug
  
  **Architecture 4 fichiers — Plan chirurgical :**
  
  Le problème : 200+ fonctions partagent des variables globales. Import circulaire si mal découpé.
  
  **Flux d'imports (pas de circulaire) :**
  ```
  config.py → shared.py → skills.py → assistant.py (core)
  ← Jamais d'import vers la droite
  ```
  
  ```
  config.py    (✅ FAIT — 99 lignes)
               Constantes, seuils, dictionnaires.
               Modifiable par l'utilisateur sans risque.

  shared.py    (~800 lignes) — LE PONT
               Variables globales : _etat_prises, _erreurs_buffer, _watchdog, etc.
               Fonctions utilitaires : telegram_send, telegram_send_buttons,
               telegram_send_photo, mem_get/set, role_get/val, skill_get/set,
               ha_get, ha_get_production_solaire_actuelle, tarif_prix_kwh_actuel,
               cartographie_*, appareil_get/set, log_token_usage, verifier_budget.
               Charge config.json, init SQLite, init logging.
               Import : from config import *

  skills.py    (~5 000 lignes) — LA LOGIQUE. ÉVOLUE. SONNET DEBUG ICI.
               Toutes les cmd_* (50+ commandes)
               Moteur économies proactif (briefing, bilans, solaire, standby)
               Cycles machines (détection, grâce, signatures, rappels)
               Apprentissage (baselines, skills auto, expertise)
               Auto-guérison (_remonter_erreurs, _auto_guerison)
               Contexte intelligent (ha_get_contexte_intelligent)
               Import : from shared import *

  assistant.py (~3 000 lignes) — LE MOTEUR. GELÉ.
               main(), polling Telegram, threads (monitoring, prises, watchdog),
               startup (scan, restauration cycles, SMS canal),
               ErrorCaptureHandler, deploy callbacks.
               Import : from skills import *
  ```
  
  **Étapes d'exécution (session dédiée) :**
  1. Créer shared.py — extraire les fonctions utilitaires + globales
  2. Tester : `python3 -c "from shared import *; print('OK')"` → doit marcher
  3. Créer skills.py — extraire TOUTES les cmd_* + moteur économies + cycles
  4. Tester : `python3 -c "from skills import *; print('OK')"` → doit marcher
  5. Modifier assistant.py — retirer les fonctions déplacées, ajouter `from skills import *`
  6. Tester : restart complet, envoyer /energie, vérifier qu'un cycle démarre
  7. Si ça casse → rollback immédiat (backup avant chaque étape)
  
  **Règle absolue** : backup AVANT chaque étape. Si une étape casse → restore → on s'arrête.
  
  **Coût actuel auto-guérison** : 13 000 lignes → ~100K tokens → 0.30$/appel
  **Coût après split** : skills.py 5 000 lignes → ~35K tokens → 0.10$/appel → **÷ 3**

- [x] **STRESS TEST avant bêta** — non négociable. Scénario complet :
  1. Lancer un cycle lave-linge → vérifier notification démarrage + fin + rappel + économie
  2. Lancer un cycle sèche-linge → vérifier grâce 45 min + pas de fausse fin à 13 min + notification fin + linge chaud
  3. Restart pendant un cycle → vérifier pas de double notification + question boutons
  4. 5 restarts en 10 min → vérifier stabilité (pas de crash, pas de spam)
  5. Poser 10 questions en langage naturel → vérifier réponses cohérentes
  6. /energie pendant production 0W → vérifier pas de blocage filtre
  7. Calendrier poubelles → vérifier données réelles (pas "non consulté")
  8. Coupure internet simulée → vérifier que le script continue
  9. Auto-guérison : injecter un bug → vérifier correction silencieuse
  10. Score résilience : vérifier succès logués après chaque cycle
  Résultat attendu : **10/10 sans incohérence**. Sinon pas de bêta.
- [x] **Issues templates** : bug report, feature request, nouveau fournisseur
- [x] **Auto-update silencieux** : le script vérifie GitHub toutes les 24h, télécharge la nouvelle version, valide la syntaxe, backup l'ancienne, remplace, restart. L'utilisateur ne fait rien. Jamais de `git pull`.
- [ ] **GitHub Actions CI** : pytest automatique à chaque push
- [ ] **Releases automatiques** : tag → release → CHANGELOG

#### 📊 Priorité 2 — Fonctionnalités produit

- [x] **Bilan hebdo automatique** : dimanche 20h, résumé complet (économies par type, comparaison semaine précédente avec tendance, cycles machines, fiabilité ✅/❌). Arrive tout seul.
- [x] **Graphiques Telegram** : courbes conso EDF (baseline rouge) + solaire (jaune) + machines (bleu) du jour. matplotlib → sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib si absent.
- [x] **Briefing matin amélioré** : météo + calendrier + pic solaire prévu + poubelles + trajet. Un seul message à 7h qui résume tout.
- [x] **Bilan mensuel automatique** : le 1er du mois à 10h. Réseau EDF (kWh + €), production solaire (kWh + couverture % + valeur €), économies IA (total + par type + vs mois précédent), cycles machines, % facture récupéré par l'IA.
- [x] **Alerte conso fantôme nocturne** : entre 1h-5h, si conso > baseline nuit + 150W → "Quelque chose est resté allumé"
- [x] **Estimation facture EDF fin de mois** : projection basée sur la conso des jours écoulés × tarif. "À ce rythme : ~58€ ce mois (vs 51€ le mois dernier)"
- [x] **Score énergétique maison** : DPE dynamique qui évolue chaque semaine (couverture solaire, conso/m², optimisation HC, économies cumulées). Note A→G affichée dans /intelligence
- [x] **Export mensuel PDF automatique** : le 1er de chaque mois, rapport PDF envoyé par email (économies, cycles, graphiques, score). L'utilisateur ne demande rien.
- [x] **Conseil changement contrat** : si le moteur tarification détecte qu'un autre fournisseur/offre ferait économiser > 5€/mois → notification proactive 1x/mois
- [x] **Mode vacances auto** : si aucune interaction Telegram + aucune machine lancée depuis 48h → passer en mode vacances (réduire les notifications, augmenter la surveillance coupure)

#### 🌐 Priorité 2b — Apprentissage collectif (10 bêta testeurs)

Le vrai avantage : chaque installation apprend → les leçons sont partagées → tout le monde progresse.

- [ ] **Leçons fondatrices partagées** : les pièges découverts par un testeur (ex: pause sèche-linge 38 min) sont intégrés au repo et profitent à tous via `git pull`
- [x] **Bibliothèque de profils appareils** : ballon thermodynamique, borne de recharge, sèche-serviettes, pompe piscine, four, cafetière — chaque testeur ajoute un type
- [x] **Fichier APPAREILS_CONNUS.json** : signatures de consommation types (durée min/max, puissance, pauses connues) partagées entre installations
- [ ] **Nouveaux types dans le questionnaire appareils** : ballon thermodynamique, borne EV, sèche-serviettes, pompe piscine, chauffe-eau
- [ ] **Ballon thermodynamique** (pince ampèremétrique) : profil chauffe/veille, corrélation température ext, optimisation HC/solaire, détection anomalie (chauffe trop longue = fuite eau chaude ?)
- [ ] **Remontée anonyme opt-in** : statistiques d'économies anonymisées → tableau comparatif (ROI moyen, kWh économisés, meilleur tarif)

Flux : testeur trouve un bug → issue GitHub → fix Opus → push → **auto-update silencieux** → corrigé partout. L'utilisateur ne fait rien.

#### 🔧 Priorité 3 — Robustesse

- [ ] **Auto-guérison bout en bout testée** : injecter un bug volontaire, vérifier que Sonnet le corrige, que le restart se fait, que l'erreur disparaît
- [x] **Rollback automatique** : si erreur revient après auto-fix → rollback vers la version précédente
- [x] **Monitoring deploy server** : si le deploy server crash, le script le détecte et le relance
- [x] **Rate limiting API Anthropic** : retry avec backoff exponentiel si 429
- [x] **Backup automatique DB + config** : chaque nuit, copie memory.db + config.json dans un dossier daté. Garder 30 jours. Si corruption DB → restore auto
- [x] **Détection coupure internet** : si HA inaccessible > 5 min → log. Si > 30 min → alerte SMS (pas Telegram, car internet down). Quand ça revient → résumé de ce qui s'est passé pendant la coupure
- [x] **Santé congélateur sur coupure longue** : si coupure EDF > 2h + congélateur détecté → alerte "Vérifiez le congélateur" au retour du courant

#### 🚀 Priorité 4 — Vision produit (v3.0+)

- [x] **Suivi consommation par pièce** : si les areas HA sont configurées, regrouper la conso par pièce. "La chambre consomme 2x plus que d'habitude"
- [x] **Intégration vocale** : Google Home / Alexa via HA. "Hey Google, demande à l'assistant combien j'ai économisé ce mois"
- [x] **Détection fuite d'eau** : si capteur d'eau HA présent, surveiller et alerter immédiatement (SMS + Telegram)
- [x] **Alerte Zigbee device mort** : si un device a un LQI tombé à 0 depuis > 24h ou "unavailable" persistant → notification + suggestion (changer pile, rapprocher du routeur)
- [x] **Apprentissage tarif Tempo/EJP** : si contrat Tempo, notifier la veille "Demain jour ROUGE — décalez vos machines". Intégration API RTE
- [ ] **Multi-logement** : un seul script qui gère plusieurs installations HA (résidence principale + secondaire)
- [ ] **Dashboard web** : interface web simple (Flask/FastAPI) pour ceux qui préfèrent un navigateur à Telegram
- [ ] **Plugin communautaire** : système de plugins pour que les testeurs ajoutent des fonctionnalités sans modifier le core (ex: plugin piscine, plugin photovoltaïque, plugin EV)

#### 📱 Priorité 5 — App Mobile (v4.0)

L'interface finale. Telegram = MVP. L'app = le produit.

- [ ] **App "Claude AI Home" — Android + iOS** (React Native ou Flutter)
  - Dashboard énergie temps réel (graphiques interactifs, pas des PNG)
  - Timeline événements (cycles, alertes, économies — scroll infini)
  - Widget écran d'accueil (économies du jour, machine en cours, prochaine poubelle)
  - Notifications push natives (pas de dépendance Telegram)
  - Onboarding guidé : scan QR code HA → clé API → prêt en 2 min
  - Multi-maison (résidence principale + secondaire)
  - Commandes vocales intégrées ("quand est-ce que le linge sera prêt ?")
- [ ] **API REST AssistantIA** : le script expose une API (FastAPI) que l'app consomme. Même API utilisable par des dashboards web tiers.
- [ ] **Tablette mode kiosque** : affichage permanent sur tablette murale (dashboard énergie + météo + calendrier + machines en cours)
- [ ] **Synchronisation Cloud opt-in** : backup config + économies sur un serveur central pour la comparaison anonyme entre utilisateurs
- [ ] **Store listing** : 
  > **Claude AI Home — L'IA qui fait baisser votre facture d'énergie**
  > Connectez votre Home Assistant. L'IA apprend vos habitudes, surveille vos machines, et vous fait économiser. Zéro configuration. Résultats dès le premier jour.

### Fichiers

| Fichier | Rôle |
|---------|------|
| `assistant.py` | Script principal (~11 814 lignes) |
| `deploy_server.py` | API REST patches/restarts |
| `config.json` | Credentials |
| `memory.db` | SQLite 22 tables |
| `i18n.py` | Traductions FR/EN |
| `tests.py` | 20 tests pytest |
| `comportement.txt` | Personnalité Claude |
| `docker-compose.yml` | Déploiement Docker |
| `Cahier_des_Charges.md` | Ce document (source de vérité) |
| `README.md` | Documentation communautaire |
| `addon/` | Structure HA Add-on |

---

## 💬 LA VISION

> L'IA ne devrait pas être un dashboard de plus.
> Elle devrait être un collègue invisible qui apprend, veille, et fait économiser.
> Comme un antivirus — un sniper. Toujours à l'affût, précis, rapide.
> Chaque token construit de l'expertise permanente.
> Chaque erreur renforce le système.
> L'utilisateur s'efface. L'IA grandit. La facture baisse.

---

**AssistantIA Domotique — L'antivirus de votre maison.**

---

## 📋 VERSIONING

| Version | Date | Changements majeurs |
|---------|------|-------------------|
| v1.0 | 26/02 | Premier script : polling Telegram + HA API + Claude Haiku |
| v2.0 | 01/03 | SQLite memory.db + cartographie + découverte auto entités |
| v3.0 | 05/03 | Surveillance Zigbee + NAS + batteries + cycles machines |
| v4.0 | 08/03 | Solaire APSystems + Anker + formule couverture + cahier des charges |
| v5.0 | 11/03 | Deploy Server + correctifs (silent_mode, coupure EDF, GRACE_FIN) |
| v6.0 | 12/03 | cmd_energie restructurée + budget paliers + /probleme auto-correction |
| v7.0 | 13/03 | Moteur intelligence 10 phases + baselines + skills + expertise + hypothèses + score /100 |
| v7.7 | 15/03 | Skill tarification : base fournisseurs FR (EDF, TotalEnergies, Engie, Octopus, Ekwateur, Mint), questionnaire auto au 1er démarrage, HP/HC/Tempo, coût cycle solaire vs réseau |
| v7.60 | 31/03 | Alertes dynamiques (watches) : surveillance personnalisée en langage naturel, vérification chaque minute, `/watches` |
| v7.59 | 31/03 | Tool Use HA : Claude pilote appareils via Anthropic tools, confirmation boutons Telegram, 10 domaines |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Auto-guérison fiable : signature nettoyée (chiffres→#) pour grouper, 0 log info pour erreurs isolées, 0 notification Telegram. Test auto-guérison supprimé. Priorités déploiement communautaire HA documentées |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Purge complète : 0 notification Telegram sur erreurs internes. Watchdog → log seulement. Auto-guérison 100% silencieuse. L'utilisateur ne paie pas pour voir des bugs. Fix _has_solar (définir avant les appels). |
| v7.34 | 22/03 | PROFIL FOYER : questionnaire 8 questions (personnes, présence, solaire kWc, chauffage, eau chaude, assistant vocal, objectif), skill 'foyer' = base mémoire des skills, /profil + reset, briefing matin adapté au profil (sans solaire → conseils HP/HC + weekend, avec assistant → commandes vocales), moteur proactif conditionnel |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Auto-guérison fiable : signature nettoyée (chiffres→#) pour grouper, 0 log info pour erreurs isolées, 0 notification Telegram. Test auto-guérison supprimé. Priorités déploiement communautaire HA documentées |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Purge complète : 0 notification Telegram sur erreurs internes. Watchdog → log seulement. Auto-guérison 100% silencieuse. L'utilisateur ne paie pas pour voir des bugs. Fix _has_solar (définir avant les appels). |
| v7.34 | 22/03 | SMS réactivé : 3 modes (premier boot, auto 24h, dev_mode). Parsing timestamp robuste (strptime). Surveillance jamais bloquée par canal_verrouille. Auto-guérison 100% silencieuse |
| v7.33 | 22/03 | MOTEUR ÉCONOMIES PROACTIF : briefing matin 7h (bilan + prévision solaire + standby), alerte pic solaire > 2000W, standby oubliés toutes les 2h, alerte HP→HC, bilan soir 21h. /economies (détail par source + par jour + graphique). Estimation coût dès le démarrage du cycle |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Auto-guérison fiable : signature nettoyée (chiffres→#) pour grouper, 0 log info pour erreurs isolées, 0 notification Telegram. Test auto-guérison supprimé. Priorités déploiement communautaire HA documentées |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Purge complète : 0 notification Telegram sur erreurs internes. Watchdog → log seulement. Auto-guérison 100% silencieuse. L'utilisateur ne paie pas pour voir des bugs. Fix _has_solar (définir avant les appels). |
| v7.34 | 22/03 | SMS réactivé : 3 modes (premier boot, auto 24h, dev_mode). Parsing timestamp robuste (strptime). Surveillance jamais bloquée par canal_verrouille. Auto-guérison 100% silencieuse |
| v7.33 | 22/03 | Auto-guérison 100% silencieuse : 0 notification Telegram sur les erreurs, 0 intervention utilisateur. Le script se corrige et restart sans rien dire. |
| v7.32 | 22/03 | 3 catégories d'appareils (gros consommateurs / coupe-veille / monitoring énergie), économies standby mesurées automatiquement, /appareils groupé par catégorie, coupe-veille et monitoring exclus de la détection cycles |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Auto-guérison fiable : signature nettoyée (chiffres→#) pour grouper, 0 log info pour erreurs isolées, 0 notification Telegram. Test auto-guérison supprimé. Priorités déploiement communautaire HA documentées |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Purge complète : 0 notification Telegram sur erreurs internes. Watchdog → log seulement. Auto-guérison 100% silencieuse. L'utilisateur ne paie pas pour voir des bugs. Fix _has_solar (définir avant les appels). |
| v7.34 | 22/03 | SMS réactivé : 3 modes (premier boot, auto 24h, dev_mode). Parsing timestamp robuste (strptime). Surveillance jamais bloquée par canal_verrouille. Auto-guérison 100% silencieuse |
| v7.33 | 22/03 | Auto-guérison 100% silencieuse : 0 notification Telegram sur les erreurs, 0 intervention utilisateur. Le script se corrige et restart sans rien dire. |
| v7.32 | 22/03 | SKILL AUTO-GUÉRISON : pipeline fermé (capture → triage → diagnostic Sonnet → patch → restart → vérification), 0 intervention utilisateur, 0 spam. SMS désactivé en dev. Canal ouvert au démarrage. Erreur isolée = silence. Erreur récurrente = auto-fix Sonnet + 1 notification |
| v7.31 | 22/03 | Détection renforcée : protocole (Zigbee/Matter/Z-Wave/WiFi/ESPHome) affiché pour chaque nouvelle entité, compteur surveillance dans chaque notification, /surveillance (vue complète), 'Autre' → demande nom obligatoire, 'Ignorer' → voie de garage explicite, vide = voie de garage |
| v7.30 | 22/03 | Détection appareil sans supposition : plus de classification par marque (matter/tapo/shelly), seuls les FAITS comptent (nom explicite OU capteur W+switch). Notification Telegram pour TOUTE nouvelle entité avec domaine/dc/unité/état |
| v7.29 | 22/03 | Détection Matter/WiFi : mots-clés élargis (outlet, socket, matter, eve_energy, tapo, shelly), fallback device_class+switch associé, questionnaire appareil auto pour nouvelles prises après setup initial |
| v7.28 | 22/03 | Guide déploiement complet (7 machines, 4 méthodes install, Docker/Compose/systemd), mise en service Claude Opus 4.6, prompt de déploiement standardisé, support centralisé |
| v7.27 | 22/03 | Dashboard Lovelace (/dashboard → push sensors HA), multi-utilisateur Telegram (_is_authorized_chat, chat_id multiples), intégration calendrier HA (/calendrier + _ha_get_calendar_events). TODO list 18/18 terminée |
| v7.26 | 22/03 | Localisation FR/EN : i18n.py (111 lignes), toutes les chaînes utilisateur traduites (cycles, rappels, wizard, appareils, erreurs), config 'lang': 'fr'/'en' |
| v7.25 | 22/03 | Tests automatisés pytest (20 tests) : cycles 2 seuils, profil phases, appareils, typo vaisselle, économies/ROI, mesures SQLite persistantes, purge, polling adaptatif |
| v7.24 | 22/03 | HA Add-on : Dockerfile, config.yaml, run.sh (Supervisor auto URL+token), DOCS.md, CHANGELOG.md, repository.yaml. Structure prête pour Store HA |
| v7.23 | 21/03 | Classification factuelle : suppression toute spéculation (chauffage + lavage + essorage → phases mesurées), signature C/L/E/P avec durées réelles, coût contrat, /programmes et /cycles factuels |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Auto-guérison fiable : signature nettoyée (chiffres→#) pour grouper, 0 log info pour erreurs isolées, 0 notification Telegram. Test auto-guérison supprimé. Priorités déploiement communautaire HA documentées |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Purge complète : 0 notification Telegram sur erreurs internes. Watchdog → log seulement. Auto-guérison 100% silencieuse. L'utilisateur ne paie pas pour voir des bugs. Fix _has_solar (définir avant les appels). |
| v7.34 | 22/03 | PROFIL FOYER : questionnaire 8 questions (personnes, présence, solaire kWc, chauffage, eau chaude, assistant vocal, objectif), skill 'foyer' = base mémoire des skills, /profil + reset, briefing matin adapté au profil (sans solaire → conseils HP/HC + weekend, avec assistant → commandes vocales), moteur proactif conditionnel |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Auto-guérison fiable : signature nettoyée (chiffres→#) pour grouper, 0 log info pour erreurs isolées, 0 notification Telegram. Test auto-guérison supprimé. Priorités déploiement communautaire HA documentées |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Purge complète : 0 notification Telegram sur erreurs internes. Watchdog → log seulement. Auto-guérison 100% silencieuse. L'utilisateur ne paie pas pour voir des bugs. Fix _has_solar (définir avant les appels). |
| v7.34 | 22/03 | SMS réactivé : 3 modes (premier boot, auto 24h, dev_mode). Parsing timestamp robuste (strptime). Surveillance jamais bloquée par canal_verrouille. Auto-guérison 100% silencieuse |
| v7.33 | 22/03 | MOTEUR ÉCONOMIES PROACTIF : briefing matin 7h (bilan + prévision solaire + standby), alerte pic solaire > 2000W, standby oubliés toutes les 2h, alerte HP→HC, bilan soir 21h. /economies (détail par source + par jour + graphique). Estimation coût dès le démarrage du cycle |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Auto-guérison fiable : signature nettoyée (chiffres→#) pour grouper, 0 log info pour erreurs isolées, 0 notification Telegram. Test auto-guérison supprimé. Priorités déploiement communautaire HA documentées |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Purge complète : 0 notification Telegram sur erreurs internes. Watchdog → log seulement. Auto-guérison 100% silencieuse. L'utilisateur ne paie pas pour voir des bugs. Fix _has_solar (définir avant les appels). |
| v7.34 | 22/03 | SMS réactivé : 3 modes (premier boot, auto 24h, dev_mode). Parsing timestamp robuste (strptime). Surveillance jamais bloquée par canal_verrouille. Auto-guérison 100% silencieuse |
| v7.33 | 22/03 | Auto-guérison 100% silencieuse : 0 notification Telegram sur les erreurs, 0 intervention utilisateur. Le script se corrige et restart sans rien dire. |
| v7.32 | 22/03 | 3 catégories d'appareils (gros consommateurs / coupe-veille / monitoring énergie), économies standby mesurées automatiquement, /appareils groupé par catégorie, coupe-veille et monitoring exclus de la détection cycles |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Auto-guérison fiable : signature nettoyée (chiffres→#) pour grouper, 0 log info pour erreurs isolées, 0 notification Telegram. Test auto-guérison supprimé. Priorités déploiement communautaire HA documentées |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison agressive : seuil abaissé à 2 occurrences (était 3), retry auto si premier patch échoue, contexte élargi (ERROR filtrés), prompt Sonnet amélioré. L'utilisateur ne tape JAMAIS /probleme pour un bug — le script se corrige seul. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 24/03 | Fix calendriers : contexte construit APRÈS l'appel API calendriers (pas avant). Haiku voit les événements réels des 72h. Réponse factuelle aux questions poubelles/planning. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Suppression dernier spam interne : 'ÉCHEC RÉCURRENT DÉTECTÉ' (118 notifications/7j) → log.debug silencieux. Fix contexte calendrier (construit APRÈS les calendriers, pas avant). |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Fix cycle restart : un cycle terminé avant restart est fermé via cycle_fin() (apprentissage complet), jamais re-notifié. Rappel marqué envoyé pour les cycles actifs restaurés. economie_eur + couverture_pct stockés dans chaque cycle. Fix /energie bloqué par filtre : réponses commandes force=True (jamais filtrées). Fix affichage prises cohérent avec état cycle. |
| v7.58 | 28/03 | Plan chirurgical split 4 fichiers : config.py ✅, shared.py (pont), skills.py (logique), assistant.py (core gelé). Flux sans import circulaire. 7 étapes avec backup + rollback. Session dédiée. Philippe nettoyé de tous les fichiers. |
| v7.57 | 28/03 | Architecture 3 fichiers : core.py (moteur gelé), config.py (variables ajustables), skills.py (logique métier, évolue, Sonnet debug ici). Simple, clair, coût debug ÷ 3. |
| v7.56 | 28/03 | Alerte : script 13K lignes = trop gros. Auto-guérison coûte ~0.30$/appel. Plan de refactoring en 9 modules < 1 500 lignes. Coût debug divisé par 10. L'utilisateur paie pour des économies, pas pour du debug. |
| v7.55 | 28/03 | Nettoyage : aucune marque dans le pitch, la vision, l'appel bêta. Tout est générique — basé sur les rôles et les intégrations de l'utilisateur. |
| v7.54 | 28/03 | Vision produit : 3 piliers (intelligence immédiate, valeur quotidienne, invisible), pitch 30s, avantages Claude AI vs GPT/Gemini. Le produit doit faire dire 'putain c'est possible ?!' en 5 min. |
| v7.53 | 28/03 | Stratégie complète : plan 6 semaines (HACS → vidéo → bêta → Anthropic → store officiel), 3 différenciateurs, positionnement, monétisation. |
| v7.52 | 28/03 | Vision : app mobile Claude AI Home (Android + iOS), API REST, tablette kiosque, store listing. Telegram = MVP, app = produit final. |
| v7.51 | 28/03 | Diagnostic : sèche-linge non notifié (restarts dev cassent la surveillance). Ajout stress test 10 points obligatoire avant bêta. Refocus valeur : prédiction temporelle (linge prêt dans ~35 min) > nom de programme. |
| v7.50 | 28/03 | Skill signatures cycles : chaque cycle a une empreinte numérique (profil de phases C9/L1/L2/L3/P1/L6). Programme reconnu → silence. Programme inconnu → boutons "Nommer ce programme". /programmes affiche tous les profils appris. /appareils reset efface les programmes. /programmes reset lave-linge → reset une seule machine (changement d'appareil). |
| v7.49 | 28/03 | Restart intelligent cycles : si machine à l'arrêt → question boutons (terminé/continue). Si machine tourne encore → restauration silencieuse. Plus de double notification. Fix filtre anti-faux-positifs : les réponses aux commandes passent toujours (force=True). Fix affichage prises : cohérent avec cycles en cours (🔵 cycle, 📊 monitoring, ⚫ inactif). |
| v7.48 | 28/03 | Graphiques Telegram : courbe énergie du jour (conso EDF baseline rouge, solaire jaune, machines bleu) envoyée en image PNG via sendPhoto. Intégré dans /energie et /solaire. Auto-install matplotlib. |
| v7.47 | 28/03 | Bilan mensuel automatique le 1er à 10h : conso réseau EDF (kWh + €), production solaire (kWh + couverture + valeur), économies IA par type, comparaison M-1, cycles machines, % facture récupéré. |
| v7.46 | 28/03 | Bilan hebdo dimanche 20h : économies (détail par type + comparaison semaine précédente + tendance 📈📉), cycles machines (nb + kWh + €), fiabilité (succès/échecs), mot de fin adaptatif. 0 token, 0 intervention. |
| v7.45 | 28/03 | Briefing matin complet : météo (température, pluie, alerte), calendrier (événements aujourd'hui + demain), poubelles (détection auto + rappel ce soir), trajet (jour travail/weekend), en plus des économies/solaire/tarif/standby existants. |
| v7.44 | 28/03 | Doctrine : auto-update silencieux depuis GitHub (0 intervention). Plus de git pull. Le script vérifie, télécharge, valide, backup, remplace, restart — tout seul. |
| v7.43 | 28/03 | TODO v2.0 : GitHub + 10 bêta testeurs (texte prêt), bilan hebdo, graphiques Telegram, briefing matin complet, comparaison mois/mois, apprentissage collectif entre installations, bibliothèque profils appareils, ballon thermodynamique |
| v7.41 | 27/03 | Fix résilience 0/25 : le script ne logguait que les échecs, jamais les succès. Chaque cycle terminé + chaque économie = succès logué. Affichage points corrigé. |
| v7.40 | 27/03 | /commandes (/commande /menu) : menu interactif avec boutons Telegram par catégorie (Énergie, Maison, Machines, IA, Outils). Chaque bouton exécute la commande directement. |
| v7.39 | 25/03 | Fix sèche-linge : grâce 15→45 min (pause préchauffage mesurée 38 min), durée minimale par machine (sèche 30 min, lave 25 min, vaisselle 20 min) — un cycle de 13 min ne déclenche plus de fausse fin. Fix calendriers HA : contexte construit APRÈS les calendriers, pas avant. |
| v7.38 | 23/03 | Calendriers HA injectés dans le contexte intelligent : état + API événements 48h. Le script consulte les calendriers AVANT de répondre — plus jamais 'non consulté'. |
| v7.37 | 22/03 | Code minimaliste : suppression dev_mode/sms_skip, SMS 2 modes propres (< 24h auto / sinon SMS), nettoyage diagnostic verbose, 0 trace debug en production |
| v7.36 | 22/03 | Auto-guérison v2 : anti-spam seulement sur l'action (pas le comptage), accumulation en DB à chaque tick, correction dès 3 occurrences/1h. L'utilisateur ne tape jamais /probleme pour un bug interne — le script se corrige seul. |
| v7.35 | 22/03 | Purge complète : 0 notification Telegram sur erreurs internes. Watchdog → log seulement. Auto-guérison 100% silencieuse. L'utilisateur ne paie pas pour voir des bugs. Fix _has_solar (définir avant les appels). |
| v7.34 | 22/03 | SMS réactivé : 3 modes (premier boot, auto 24h, dev_mode). Parsing timestamp robuste (strptime). Surveillance jamais bloquée par canal_verrouille. Auto-guérison 100% silencieuse |
| v7.33 | 22/03 | Auto-guérison 100% silencieuse : 0 notification Telegram sur les erreurs, 0 intervention utilisateur. Le script se corrige et restart sans rien dire. |
| v7.32 | 22/03 | SKILL AUTO-GUÉRISON : pipeline fermé (capture → triage → diagnostic Sonnet → patch → restart → vérification), 0 intervention utilisateur, 0 spam. SMS désactivé en dev. Canal ouvert au démarrage. Erreur isolée = silence. Erreur récurrente = auto-fix Sonnet + 1 notification |
| v7.31 | 22/03 | Détection renforcée : protocole (Zigbee/Matter/Z-Wave/WiFi/ESPHome) affiché pour chaque nouvelle entité, compteur surveillance dans chaque notification, /surveillance (vue complète), 'Autre' → demande nom obligatoire, 'Ignorer' → voie de garage explicite, vide = voie de garage |
| v7.30 | 22/03 | Détection appareil sans supposition : plus de classification par marque (matter/tapo/shelly), seuls les FAITS comptent (nom explicite OU capteur W+switch). Notification Telegram pour TOUTE nouvelle entité avec domaine/dc/unité/état |
| v7.29 | 22/03 | Détection Matter/WiFi : mots-clés élargis (outlet, socket, matter, eve_energy, tapo, shelly), fallback device_class+switch associé, questionnaire appareil auto pour nouvelles prises après setup initial |
| v7.28 | 22/03 | Guide déploiement complet (7 machines, 4 méthodes install, Docker/Compose/systemd), mise en service Claude Opus 4.6, prompt de déploiement standardisé, support centralisé |
| v7.27 | 22/03 | Dashboard Lovelace (/dashboard → push sensors HA), multi-utilisateur Telegram (_is_authorized_chat, chat_id multiples), intégration calendrier HA (/calendrier + _ha_get_calendar_events). TODO list 18/18 terminée |
| v7.26 | 22/03 | Localisation FR/EN : i18n.py (111 lignes), toutes les chaînes utilisateur traduites (cycles, rappels, wizard, appareils, erreurs), config 'lang': 'fr'/'en' |
| v7.25 | 22/03 | Tests automatisés pytest (20 tests) : cycles 2 seuils, profil phases, appareils, typo vaisselle, économies/ROI, mesures SQLite persistantes, purge, polling adaptatif |
| v7.24 | 22/03 | HA Add-on : Dockerfile, config.yaml, run.sh (Supervisor auto URL+token), DOCS.md, CHANGELOG.md, repository.yaml. Structure prête pour Store HA |
| v7.23 | 22/03 | Questionnaire appareils Telegram (prise → type machine), table appareils, /appareils + reset, nom personnalisé dans toutes les notifications/rappels, exclusion appareils marqués 'ignorer', appareil_get() remplace la détection par friendly_name |
| v7.22 | 21/03 | GENÈSE business model : table economies, enregistrer_economie() dans chaque cycle solaire, get_economies_mois(), cmd_roi refonte avec économies réelles par type, cumul économies visible dans chaque notification de fin de cycle, cercle vertueux documenté |
| v7.21 | 21/03 | Mesures puissance en SQLite temps réel (table cycle_mesures), restauration cycles 100% autonome (0 dépendance CSV/API HA), grâce intelligente par type machine (7/15/30 min), rappel linge chaud sèche-linge, /cycles avec programme, migration profil_json + programme dans cycles_appareils |
| v7.20 | 21/03 | Mode sniper : polling adaptatif prises 20s/60s, monitoring tick rapide 60s (EDF+PAC+erreurs) + tick complet 5 min, profil phases par timestamps réels, backfill historique HA au restart |
| v7.19 | 21/03 | Skill reconnaissance programmes machines : analyse profil puissance par phases (C/L/E/P), classification auto (profils factuels par phases mesurées (chauffage, lavage, essorage)), /programmes, notification enrichie, backfill historique HA au restart |
| v7.18 | 21/03 | Fix cycles machines : 2 seuils (start 200W / fin 10W), GRACE_FIN 20→30 min. Corrige double notification lave-linge (phase lavage 100-200W + pause rinçage→essorage 23 min) |
| v7.17 | 21/03 | README.md communautaire (303 lignes) : badges, architecture visuelle, exemples Telegram, commandes, tarification, sécurité, roadmap, contribution |
| v7.16 | 21/03 | SMS multi-provider (Free Mobile + notification HA + email), wizard étape 4/4, migration auto sms_method, envoyer_code_sms universel |
| v7.15 | 21/03 | Setup wizard Telegram : 1 CLI + 3 Telegram + auto-detect chat_id, mode wizard dans main(), guard ha_get config vide, /aide alias |
| v7.14 | 21/03 | Mode sans solaire / sans PAC : sections conditionnelles cmd_energie, guards skill_fenetre_solaire + skill_comportement_pac + _surveiller_pac + ha_get_production_solaire + cmd_solaire. Graceful degradation complète |
| v7.13 | 21/03 | Areas via /api/template Jinja2 (10 pièces, 315 entités), détection antivirus 5min, scan infiltration 1h, auto-MAJ pièces, **doctrine #11 implémentée** (ErrorCaptureHandler + _remonter_erreurs + auto-correction Sonnet), **refactoring 26 entity_id → role_val()**, 11 nouveaux rôles, BASELINE_ENTITIES dynamiques |
| v7.12 | 20/03 | Guard leçons+échecs (stop réinjection doublons), nettoyage JSON analyses tronquées, max_tokens 1200, rôles: pattern match obligatoire, /probleme sans args = aide statique, pièces auto-MAJ friendly_name, notif prises, **détection antivirus 5min** (0 token), scan infiltration 4h→1h |
| v7.11 | 15/03 | Envoi MD par mail auto (détection modification hash MD5), /md commande, /sms commande, section reprise 500% autonome |
| v7.10 | 15/03 | /sms (canal verrouillé ou non), /roi corrigé (tokens_in/out), skill_creer_auto supprimé (gaspillage), section reprise conversation |
| v7.9 | 15/03 | Phase 11 recommandations proactives (24h), ROI tokens vs économies, score optimisation /100, 8857 lignes, 11 phases intelligence |
| v7.8 | 15/03 | Tarification universelle : base 6 fournisseurs FR, offres Week-End/Plus/HP-HC/Tempo, auto-détection HC (Lixee/ZLinky/LinkYTIC/ESPHome/Ecojoko), auto-apprentissage plages PTEC 24h, skill optimisation tarif, filtre central apprenant, 8632 lignes |
| v7.6 | 15/03 | Filtre central telegram_send : 4 niveaux (cohérence, anti-doublon 5min, anti-spam 50msg/jour, données croisées skills). Chaque message validé avant envoi. |
| v7.5 | 15/03 | Rappel machine : fallback skill fenêtre solaire si ECU glitche 0W. Chute brutale solaire supprimée (glitch capteur). PAC thermostat on/off documenté. Couverture solaire 53% validée. |
| v7.4 | 15/03 | PAC : thermostat on/off = normal, alerte seulement si maison se refroidit (4 conditions cumulatives). Expertise : cause racine doublons fixée (match catégorie + LIKE 20 chars + cap 50 sur TOUS les points) |
| v7.3 | 15/03 | Purge expertise (469→~40, cap 50), exclusion Anker des cycles, NAS temp ignoré, Santé Hôte corrigé, analyse IA formatée, endpoint /delete |
| v7.2 | 14/03 | Log rotation (48MB → 20MB max) + empreinte machine documentée + SMS auto-déverrouillage validé |
| v7.1 | 14/03 | Faux positifs corrigés (baselines, NAS, OctoPrint) + SMS auto-déverrouillage 24h + restauration cycles + système de rôles universels |

### Changelog Session 21/03/2026 (v7.12 → v7.18)

Refactoring massif + nouvelles fonctionnalités :

**Corrections critiques :**
- Guard leçons fondatrices + échecs historiques (stop spam 57 doublons)
- Nettoyage JSON analyses tronquées (regex 3 niveaux)
- Fix cycles machines : 2 seuils (200W start / 10W fin), grâce 30 min
- /probleme sans argument : aide statique au lieu d'hallucinations Haiku
- Areas HA : /api/template Jinja2 (endpoints REST = 404 sur HA Green)

**Refactoring :**
- 26 entity_id en dur → role_val() / role_get() (0 actif restant)
- 11 nouveaux rôles : météo (4), batterie détail (4), production lifetime
- BASELINE_ENTITIES dynamiques via rôles
- Mode sans solaire / sans PAC : graceful degradation complète

**Nouvelles fonctionnalités :**
- Setup wizard Telegram guidé (1 CLI + 4 Telegram + auto-detect chat_id)
- SMS multi-provider : Free Mobile + Notification HA + Email
- Détection antivirus 5 min (0 token, pattern matching local)
- Remontée erreurs automatique (ErrorCaptureHandler + Telegram + auto-correction)
- Scan infiltration 4h → 1h
- Notification Telegram nouvelles prises
- Pièces auto-MAJ depuis friendly_name + /api/template

**Documentation :**
- Cahier des Charges réécrit : 700 lignes, documentation produit complète
- README.md communautaire : 3 piliers (adaptation, dev IA, mises à jour)
- Doctrine #11 : auto-correction immédiate

### Changelog v7.3 (15/03/2026)
- Expertise : cap 50 règles permanent (plus jamais 653)
- Purge automatique au démarrage (fondatrices + top 30 + dédoublonnage)
- Santé Hôte : ne teste plus `ha_get("api/")` directement, vérifie le watchdog
- Santé Hôte délai : 12h critique / 24h warning (était 2h/12h)
- Prise Anker exclue des cycles machines (EXCLUSIONS_PRISES)
- NAS : capteurs température/CPU/mémoire/débit ignorés si unknown
- Analyse IA : nettoyage JSON résiduel avant envoi Telegram
- Deploy Server : endpoint /delete ajouté (suppression fichiers)
- Nettoyage fichiers caduques automatique (v5, v6, v7.md, diag_*)

### Changelog v7.1 (14/03/2026)
- Baselines : minimum 30 mesures, seuil 150% conso / 200% solaire
- Production solaire 0W : confirmé sur 2 cycles avant alerte
- Entités hors ligne seuil 30% (pas 15%)
- NAS "attention" = espace plein (seuil 95%), pas dégradé
- OctoPrint supprimé de la surveillance imprimante
- SMS auto-déverrouillage 24h — restarts transparents pour l'IA
- Cycles machines restaurés depuis SQLite après restart
- Surveillance tourne TOUJOURS (même avant code SMS)
- Suggestion machine : réponse libre "12h30" au lieu de boutons
- ha_get_production_solaire_actuelle : sources explicites ECU + Anker
- +8 leçons fondatrices
- Cycle autonome validé : patch → restart → auto-unlock → surveillance active



