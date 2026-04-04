<p align="center">
  <img src="https://img.shields.io/badge/Home%20Assistant-Compatible-41BDF5?logo=homeassistant" />
  <img src="https://img.shields.io/badge/Claude%20AI-Powered-cc785c?logo=anthropic" />
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

<h1 align="center">🏠 AssistantIA Domotique</h1>
<p align="center"><strong>L'IA qui gère votre maison. Vous ne faites rien.</strong></p>
<p align="center"><em>Agent autonome Python — 4 modules — Home Assistant × Claude AI × Telegram</em></p>

---

**AssistantIA** est un agent IA qui surveille votre maison 24/7, apprend vos habitudes, détecte les anomalies, pilote vos appareils, et vous fait économiser de l'énergie — chaque jour, sans intervention.

> **Le business model** : chaque euro en tokens produit 5-20× d'économies mesurées. Le script se finance par ses propres résultats.

---

## ⚡ Ce qui se passe chaque jour

| Heure | L'assistant fait... |
|-------|---------------------|
| **7h00** | Briefing matin : météo, calendrier, trajet, conseil énergie du jour |
| **En continu** | Surveillance : 11 threads, 23 tables, 53 commandes |
| **Pic solaire** | "2700W dispo ! Lancez une machine → 0.32€ gratuit" |
| **Standby oublié** | "TV en veille 12W → 1.8€/mois. Coupez." |
| **Machine lancée** | "🧺 Lave-linge — estimation 0.18€ (solaire 45%)" |
| **Machine finie** | "🧺 Terminé — 1.23 kWh — 0.18€. Hublot déverrouillé." |
| **Sèche-linge** | "👕 Linge chaud ! Sortez-le maintenant." |
| **Onduleur offline** | "⚠️ Micro-onduleur 3 hors ligne depuis 5 min" |
| **21h00** | Bilan du soir : conso, économies, projection facture EDF |
| **Dimanche 20h** | Bilan hebdo avec tendance et recommandations |
| **1er du mois** | Bilan mensuel complet par email |

## 🧠 Intelligence réelle

**Pas un dashboard. Un agent qui pense.**

- **Pilotage vocal** : "Ouvre la serrure", "Allume le salon" → boutons ✅/❌ → exécution HA
- **Alertes dynamiques** : "Préviens-moi si un onduleur passe offline" → surveillance automatique
- **Projection facture** : "Combien va me coûter l'EDF ?" → estimation basée sur la conso réelle
- **Auto-correction** : `/probleme` → Claude Sonnet lit le code, propose un patch, l'applique
- **Score intelligence** : /100 qui progresse chaque semaine (expertise, baselines, résilience, économies)

## 🔧 Installation (10 minutes)

### Prérequis

- Home Assistant (Green, Yellow, VM, Docker — n'importe quel mode)
- Un bot Telegram (créé via @BotFather)
- Une clé API Anthropic (~5-10€/mois)
- Python 3.10+ sur n'importe quelle machine (VM, Raspberry Pi, NAS, PC)

### Méthode 1 — Script direct (recommandé)

```bash
# Sur votre machine (VM, RPi, PC, NAS...)
git clone https://github.com/shaine93/assistantia-domotique.git
cd assistantia-domotique
pip3 install -r requirements.txt
python3 assistant.py
```

Au premier lancement, le **Setup Wizard** se déclenche sur Telegram :
1. URL Home Assistant → test de connexion
2. Token HA → vérification API
3. Clé API Anthropic → test Claude
4. Méthode SMS (Free Mobile / HA Notify / Email)
5. **C'est prêt.** Le bot découvre vos entités automatiquement.

### Méthode 2 — Docker

```bash
git clone https://github.com/shaine93/assistantia-domotique.git
cd assistantia-domotique
docker-compose up -d
```

### Méthode 3 — Service systemd

```bash
sudo cp assistantia.service /etc/systemd/system/
sudo systemctl enable assistantia
sudo systemctl start assistantia
```

### Méthode 4 — HA Add-on

Ajoutez ce dépôt dans Home Assistant → Paramètres → Extensions → Dépôts :
```
https://github.com/shaine93/assistantia-domotique
```

## 📱 53 Commandes Telegram

### Énergie & Économies
`/energie` `/solaire` `/tarif` `/bilan_tarif` `/roi` `/economies`

### Surveillance & Appareils
`/audit` `/scan` `/surveillance` `/appareils` `/profil` `/cycles` `/programmes` `/batteries` `/zigbee` `/nas` `/hote`

### Intelligence
`/intelligence` `/expertise` `/apprentissage` `/analyse` `/skills` `/baselines` `/roles` `/memoire` `/calendrier` `/dashboard`

### Actions & Alertes
`/watches` — Alertes dynamiques actives
*(langage naturel)* — "Allume la lumière" → ✅/❌ → exécution
*(langage naturel)* — "Préviens-moi si..." → alerte automatique

### Administration
`/budget` `/debug` `/logs` `/sms` `/md` `/export` `/documentation` `/commandes`

### Auto-correction
`/probleme <description>` — Claude Sonnet lit, patche, corrige

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│                 TELEGRAM                     │
│            (interface unique)                │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│           4 fichiers modulaires              │
│                                              │
│  config.py (98)    Constantes, seuils        │
│       ↓                                      │
│  shared.py (2200)  Globals, utilitaires,     │
│       ↓            Telegram, HA, SQLite      │
│  skills.py (10400) Commandes, cycles,        │
│       ↓            économies, surveillance   │
│  assistant.py (900) main(), threads, wizard  │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │ 11       │  │ Claude   │  │ Tool Use  │  │
│  │ Threads  │  │ Haiku    │  │ Actions   │  │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘  │
│       │             │              │         │
│  ┌────▼─────────────▼──────────────▼──────┐  │
│  │           SQLite (23 tables)           │  │
│  │  cartographie · cycles · économies     │  │
│  │  baselines · expertise · watches       │  │
│  └────────────────────────────────────────┘  │
│                     │                        │
│  ┌──────────────────▼─────────────────────┐  │
│  │           Home Assistant API           │  │
│  │   states · services · calendars        │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

**Architecture 4 fichiers** — chaîne d'imports sans circulaire :
`config.py → shared.py → skills.py → assistant.py`

**11 Threads permanents** : monitoring (60s), prises (20s adaptatif), batteries, audit, watchdog, backup, keepalive, découverte, bilan, scan infiltration

**23 Tables SQLite** : cartographie (~700 entités), cycles_appareils, economies, watches, baselines, expertise, roles, skills, decisions_log...

**10 Skills autonomes** : foyer, fenêtre solaire, comportement PAC, signatures cycles, optimisation tarif, recommandations, tarification, apprentissage HC, santé hôte

## 🔌 Matériel supporté

Le script détecte **tout** ce que Home Assistant voit :

| Protocole | Exemples |
|-----------|----------|
| **Zigbee** (Z2M) | Prises, capteurs, ampoules, volets |
| **Matter** | Serrures SwitchBot, Thread devices |
| **WiFi** | Ecojoko, APSystems, ESPHome |
| **Z-Wave** | Détecteurs, thermostats |
| **IP** | NAS Synology, imprimantes Brother |

**Appareils spécifiquement optimisés** : lave-linge, sèche-linge, lave-vaisselle (détection cycles, grâce intelligente, signatures), panneaux solaires (APSystems, Anker), PAC air/eau, Ecojoko.

## 🔐 Sécurité

- **Code SMS** au démarrage (Free Mobile, HA Notify, ou Email)
- **Canal verrouillé** tant que le code n'est pas saisi
- **Deploy Server** avec authentification HMAC-SHA256
- **Actions HA** toujours avec confirmation bouton ✅/❌
- **Aucune donnée cloud** — tout reste local (SQLite + votre HA)

## 📊 ROI mesuré

```
/roi
📈 ROI AssistantIA
━━━━━━━━━━━━━━━━━━
Tokens : 0.15€
Économies : 0.81€
ROI : ×5.4
```

Le script mesure chaque économie en euros (solaire, HP→HC, standby, machines optimisées) et les compare au coût des tokens API.

## 🤝 Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md).

**Cherche 10 bêta testeurs** avec des installations différentes (avec/sans solaire, avec/sans PAC, tous protocoles). Ouvrez une issue "Bêta testeur" !

## 📋 Fichiers

| Fichier | Rôle |
|---------|------|
| `assistant.py` | Moteur : main(), threads, wizard (900 lignes) |
| `skills.py` | Logique : commandes, cycles, économies, surveillance (10 400 lignes) |
| `shared.py` | Pont : globals, Telegram, HA, SQLite, utilitaires (2 200 lignes) |
| `deploy_server.py` | API REST patches/restarts (HMAC-SHA256) |
| `config.py` | Constantes et seuils (modifiable) |
| `config.json` | Credentials (créé au setup) |
| `memory.db` | SQLite 23 tables |
| `i18n.py` | Traductions FR/EN |
| `tests.py` | Tests pytest |
| `comportement.txt` | Personnalité Claude (personnalisable) |
| `docker-compose.yml` | Déploiement Docker |
| `Cahier_des_Charges.md` | Documentation technique complète |

## 📜 Licence

MIT — Utilisez, modifiez, partagez librement.

---

<p align="center">
  <strong>Fait avec 🧠 par Claude AI et un passionné de domotique</strong><br>
  <em>Home Assistant × Anthropic × Telegram</em>
</p>
