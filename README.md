<h1 align="center">🏠 AssistantIA Domotique</h1>
<p align="center"><strong>L'antivirus de votre maison — propulsé par Claude AI</strong></p>
<p align="center">
  <a href="#-installation-rapide">Installation</a> ·
  <a href="docs/INSTALL.md">Documentation</a> ·
  <a href="docs/TROUBLESHOOTING.md">Dépannage</a> ·
  <a href="docs/BETA_CHANNEL.md">Mode bêta-testeur</a>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white">
  <img alt="Home Assistant" src="https://img.shields.io/badge/Home_Assistant-2024.1+-41BDF5?logo=home-assistant&logoColor=white">
  <img alt="Claude AI" src="https://img.shields.io/badge/Claude_AI-powered-D97757">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
</p>

---

**AssistantIA** est un agent IA autonome qui surveille votre maison 24/7 via Home Assistant. Il apprend vos habitudes, détecte vos appareils, optimise votre consommation, et vous fait économiser de l'argent — chaque jour.

> Le script se finance par ses propres résultats : chaque euro en tokens produit 10 à 20 € d'économies.

## ✨ Ce qu'il fait

- **🔍 Détection universelle** : Zigbee, Matter, Z-Wave, WiFi, ESPHome — tout ce qui apparaît dans Home Assistant
- **⚡ Moteur d'économies proactif** : briefing matin, alertes pic solaire, détection standbys, optimisation HP/HC
- **🧺 Cycles machines** : détection automatique des lave-linge / sèche-linge / lave-vaisselle + estimation coût
- **💬 Pilotage naturel** : « Allume la lumière du salon » → Claude appelle le bon service HA
- **🤖 Auto-correction** : `/probleme <description>` → Claude diagnostique et propose un patch
- **📊 ROI mesuré en euros** : chaque économie enregistrée, cumul par mois, comparaison mois/mois

## 📋 Pré-requis

| # | Quoi | Où l'obtenir | Gratuit ? |
|---|------|--------------|-----------|
| 1 | **Bot Telegram** | [@BotFather](https://t.me/BotFather) → `/newbot` | ✅ |
| 2 | **Home Assistant** avec token long-lived | Profil → Tokens longue durée | ✅ |
| 3 | **Clé API Anthropic** | [console.anthropic.com](https://console.anthropic.com) | ~5-10 €/mois |
| 4 | **Une machine Linux** (Pi, VM, NAS, HA Add-on...) | Voir tableau ci-dessous | Variable |

## 🚀 Installation rapide

Quatre méthodes supportées. **Choisissez celle qui correspond à votre matériel** :

### 1️⃣ HA Add-on — Le plus simple (HA OS / Supervised)

Si vous avez Home Assistant OS (HA Green, Yellow, Blue, etc.) :

1. Dans Home Assistant : **Paramètres → Modules complémentaires → Boutique → ⋮ → Dépôts**
2. Ajoutez : `https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA`
3. Trouvez **AssistantIA Domotique** dans la liste, cliquez **Installer**
4. Configurez : `telegram_token` + `anthropic_api_key` (l'URL HA et le token sont automatiques)
5. **Démarrez**

[📖 Guide détaillé →](docs/INSTALL.md#ha-add-on)

### 2️⃣ Docker Compose — Le plus portable

Sur n'importe quelle machine avec Docker (NAS Synology, Mini PC, Linux...) :

```bash
git clone https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA.git
cd assistant-domotique-home-assistant-Claude-IA
cp env.example .env     # puis éditez .env avec vos credentials
docker compose up -d
docker compose logs -f  # suivez les logs
```

[📖 Guide détaillé →](docs/INSTALL.md#docker)

### 3️⃣ Linux natif (Raspberry Pi, VM, serveur)

Pour un contrôle total, avec systemd pour l'auto-recovery :

```bash
git clone https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA.git
cd assistant-domotique-home-assistant-Claude-IA
./install.sh                       # wizard CLI interactif
sudo ./scripts/install_systemd.sh  # déploie comme service système
```

Le service `assistantia.service` démarre au boot, se relance en cas de crash (`Restart=always`).

[📖 Guide détaillé →](docs/INSTALL.md#linux-natif)

### 4️⃣ Installation manuelle — Pour comprendre ce qui se passe

```bash
git clone https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA.git
cd assistant-domotique-home-assistant-Claude-IA
pip install -r requirements.txt
./install.sh                # génère config.json
python3 assistant.py        # lance le bot
```

[📖 Guide détaillé →](docs/INSTALL.md#manuel)

## 🎯 Après l'installation

1. **Envoyez un message** à votre bot Telegram (n'importe quoi)
   → votre `chat_id` se détecte automatiquement
2. Le bot vous guide : **questionnaire appareils**, **profil foyer**, **tarif électricité**
3. Tapez `/aide` pour voir toutes les commandes disponibles

⏱ **Temps total** : 10 minutes. Ensuite vous ne touchez plus rien.

## 🏗 Sur quel matériel ?

| Machine | RAM min | Coût | Idéal pour |
|---|---|---|---|
| **HA Add-on** (sur HA OS) | 512 MB | 0 € | Vous avez déjà HA Green/Yellow → 1 clic |
| **Raspberry Pi 4/5** | 2 GB | 40-80 € | Dédié, silencieux, 5 W |
| **VM Oracle Cloud** (free tier) | 1 GB | 0 € | Gratuit permanent, ARM |
| **VM Google Cloud** (e2-micro) | 1 GB | 0 € | Gratuit 12 mois |
| **Mini PC N100/N95** | 8 GB | 80-150 € | Puissant, SSD fiable |
| **NAS Synology** (Docker) | 4 GB | 0 € | Déjà allumé 24/7 |

## 💰 Combien ça rapporte ?

| Poste | Montant |
|---|---|
| Script (MIT) | **Gratuit** |
| Tokens Claude | ~5-10 €/mois (diminue avec le temps) |
| Économies typiques | **40-80 €/an** |
| **ROI** | **×10 à ×20** |

> Le mois 6 coûte moins que le mois 1 : l'expertise est locale, les tokens diminuent, les économies augmentent.

## 📚 Documentation

- [docs/INSTALL.md](docs/INSTALL.md) — Guide d'installation détaillé (4 méthodes)
- [docs/CONFIGURATION.md](docs/CONFIGURATION.md) — Toutes les clés de `config.json`
- [docs/COMMANDS.md](docs/COMMANDS.md) — Les 51 commandes Telegram
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) — Résolution des problèmes courants
- [docs/BETA_CHANNEL.md](docs/BETA_CHANNEL.md) — Mode bêta-testeur (patches à distance, **opt-in**)
- [Cahier_des_Charges.md](Cahier_des_Charges.md) — Spécifications complètes

## 🛡 Sécurité

- `config.json` contient vos secrets : l'installateur lui met automatiquement les droits `600` (lecture propriétaire seul)
- Canal Telegram verrouillé au démarrage avec un code à 6 chiffres (SMS / notif HA / email)
- Toutes les actions HA sensibles (serrure, lumière, climat) passent par un bouton de confirmation ✅/❌
- Mode bêta-testeur **désactivé par défaut** — active le deploy_server uniquement si vous l'activez explicitement. Voir [BETA_CHANNEL.md](docs/BETA_CHANNEL.md) pour les implications.

## 🗺 Roadmap

- [x] 51 commandes Telegram + langage naturel
- [x] Détection universelle (Matter / Zigbee / Z-Wave / WiFi)
- [x] Moteur économies proactif (briefing 7h, pic solaire, standby, HP/HC, bilan 21h)
- [x] Auto-correction via `/probleme`
- [x] Intégration Google Home / Alexa (TTS)
- [x] HA Add-on + Docker + systemd
- [ ] Ballon thermodynamique (pince ampèremétrique)
- [ ] Dashboard web (FastAPI)
- [ ] App mobile (React Native)

## 🤝 Contribuer

- 🐛 **Bug** → [GitHub Issues](https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA/issues)
- 💡 **Idée** → [GitHub Discussions](https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA/discussions)
- 🧪 **Bêta testeur** → [Forum HACF](https://forum.hacf.fr/t/assistantia-domotique-lia-qui-gere-votre-maison-pendant-que-vous-dormez/78164)

## 📜 Licence

[MIT](LICENSE) — Utilisez, modifiez, partagez librement.

---

<p align="center">
  <strong>AssistantIA Domotique — L'antivirus de votre maison.</strong><br>
  <em>Il apprend votre maison. Vous le configurez en parlant. Claude AI le fait évoluer.</em><br>
  <em>Chaque jour, il vous fait gagner de l'argent.</em>
</p>
