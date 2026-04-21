<h1 align="center">🏠 AssistantIA Domotique</h1>
<p align="center"><strong>Un agent IA conversationnel et autonome pour votre Home Assistant</strong></p>
<p align="center">
  <a href="#-installation-rapide">Installation</a> ·
  <a href="docs/INSTALL.md">Documentation</a> ·
  <a href="docs/TROUBLESHOOTING.md">Dépannage</a> ·
  <a href="docs/BETA_CHANNEL.md">Mode bêta-testeur</a>
</p>

<p align="center">
  <img alt="Version" src="https://img.shields.io/badge/version-v2.0-blue">
  <img alt="Status" src="https://img.shields.io/badge/status-beta-orange">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white">
  <img alt="Home Assistant" src="https://img.shields.io/badge/Home_Assistant-2024.1+-41BDF5?logo=home-assistant&logoColor=white">
  <img alt="Claude AI" src="https://img.shields.io/badge/Claude_AI-powered-D97757">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
</p>

---

**AssistantIA** est un agent IA autonome qui discute avec votre Home Assistant 24/7 via Telegram. Il détecte vos appareils, comprend vos demandes en langage naturel, mesure votre consommation, et vous alerte au bon moment.

> 💬 *« Allume la lumière du salon »* → Claude trouve la bonne entité, appelle le bon service, vous confirme l'action.

## ✨ Ce qu'il fait

- **💬 Pilotage en langage naturel** : plus besoin de chercher dans l'UI ou d'écrire du YAML. Vous dites, Claude fait.
- **🔍 Détection universelle** : Zigbee, Matter, Z-Wave, WiFi, ESPHome — tout ce qui apparaît dans Home Assistant.
- **⚡ Surveillance proactive** : briefing matin, alertes pic solaire, détection standbys, device offline, batteries faibles.
- **🧺 Cycles machines** : détection automatique des lave-linge / sèche-linge / lave-vaisselle + mesure coût en temps réel.
- **🔔 Alertes dynamiques** : *« Préviens-moi si un micro-onduleur passe offline »* → alerte permanente créée.
- **🤖 Auto-correction** : `/probleme <description>` → Claude Sonnet lit le code, propose un patch, vous validez.
- **📊 Mesure des économies** : chaque économie générée (pic solaire, HC, standby éliminé) est enregistrée.

## 🎯 En quoi c'est différent d'une automation classique ?

Beaucoup de choses listées ci-dessus peuvent être faites avec des automations YAML ou Node-RED. La différence tient à **trois choses que le YAML ne fait pas** :

1. **Le langage naturel** — vous créez des alertes, des scènes, ou lancez des actions en phrases entières, sans ouvrir l'interface ni éditer de YAML. Claude identifie les bonnes entités et construit les bons appels de service.
2. **L'auto-correction** — quand quelque chose ne marche pas, vous tapez `/probleme`. Claude lit le code du script, diagnostique, propose un patch, l'applique si vous validez. Zéro terminal.
3. **L'adaptation continue** — le script apprend votre foyer, votre tarif, vos appareils. Il ajuste ses alertes selon ce qu'il observe, pas selon des règles figées que vous avez écrites une fois pour toutes.

Ce n'est pas un remplaçant pour vos automations existantes. C'est une **couche conversationnelle et intelligente** au-dessus de HA.

## 📋 Pré-requis

| # | Quoi | Où l'obtenir | Coût |
|---|------|--------------|------|
| 1 | **Bot Telegram** | [@BotFather](https://t.me/BotFather) → `/newbot` | Gratuit |
| 2 | **Home Assistant** avec token long-lived | Profil → Tokens longue durée | Gratuit |
| 3 | **Clé API Anthropic** | [console.anthropic.com](https://console.anthropic.com) | Variable (voir ci-dessous) |
| 4 | **Une machine Linux** (Pi, VM, NAS, HA Add-on...) | Voir tableau matériel | Variable |

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

⏱ **Temps total** : 10 minutes. Ensuite le bot tourne tout seul.

## 🏗 Sur quel matériel ?

| Machine | RAM min | Coût | Idéal pour |
|---|---|---|---|
| **HA Add-on** (sur HA OS) | 512 MB | 0 € | Vous avez déjà HA Green/Yellow → 1 clic |
| **Raspberry Pi 4/5** | 2 GB | 40-80 € | Dédié, silencieux, 5 W |
| **VM Oracle Cloud** (free tier) | 1 GB | 0 € | Gratuit permanent, ARM |
| **VM Google Cloud** (e2-micro) | 1 GB | 0 € | Gratuit 12 mois |
| **Mini PC N100/N95** | 8 GB | 80-150 € | Puissant, SSD fiable |
| **NAS Synology** (Docker) | 4 GB | 0 € | Déjà allumé 24/7 |

## 💰 Combien ça coûte vraiment ?

Le script est **gratuit et open source (MIT)**. Le seul coût récurrent, ce sont les tokens de l'API Anthropic.

| Poste | Coût |
|---|---|
| Script | **Gratuit** (MIT) |
| Tokens Claude | Variable — dépend de votre usage (voir ci-dessous) |
| Hébergement | Variable — entre 0 € (HA Add-on, VM gratuite) et ~10 € (Pi dédié) |

**Sur les tokens Anthropic :** l'usage normal (1 briefing/jour, quelques commandes conversationnelles, surveillance passive) tourne généralement autour de **5 à 15 €/mois**. Le bot suit son propre budget via `/budget` et coupe si vous dépassez la limite configurée dans `anthropic_monthly_budget_usd`.

**Sur les économies :** le script mesure ce qu'il vous fait économiser (solaire optimisé, machines décalées HC, standbys éliminés) et vous le montre en euros via `/roi`. **À vous de juger si le rapport coût/bénéfice vous convient.** Les économies dépendent énormément de votre installation : si vous avez du solaire + une PAC + un tarif HP/HC, les leviers sont nombreux. Si vous avez une installation minimale, l'économie se limite probablement au coût des tokens eux-mêmes — et c'est ok, l'intérêt se déplace alors vers le confort conversationnel.

> 🧪 **Alternative moins coûteuse prévue** : une version compatible Groq / Ollama est sur la roadmap pour les utilisateurs qui veulent réduire ou supprimer le coût API. Voir les [Issues](https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA/issues) pour suivre ou contribuer.

## 📚 Documentation

- [docs/INSTALL.md](docs/INSTALL.md) — Guide d'installation détaillé (4 méthodes)
- [docs/CONFIGURATION.md](docs/CONFIGURATION.md) — Toutes les clés de `config.json`
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) — Résolution des problèmes courants
- [docs/BETA_CHANNEL.md](docs/BETA_CHANNEL.md) — Mode bêta-testeur (patches à distance, **opt-in**)
- [Cahier_des_Charges.md](Cahier_des_Charges.md) — Spécifications complètes

## 🛡 Sécurité

- `config.json` contient vos secrets : l'installateur lui met automatiquement les droits `600` (lecture propriétaire seul)
- Canal Telegram verrouillé au démarrage avec un code à 6 chiffres (SMS / notif HA / email)
- Toutes les actions HA sensibles (serrure, lumière, climat) passent par un bouton de confirmation ✅/❌
- Mode bêta-testeur **désactivé par défaut** — le `deploy_server` ne s'active que si vous l'activez explicitement. Voir [BETA_CHANNEL.md](docs/BETA_CHANNEL.md) pour les implications.

## 📊 État du projet

**Version actuelle : v2.0 (bêta)**

Le code tourne en production chez l'auteur depuis février 2026. Il est fonctionnellement stable mais n'a **pas encore été validé sur suffisamment d'installations différentes** pour être considéré comme stable au sens général.

**Ce qui est attendu à ce stade :**
- Des bugs découverts par des configurations HA différentes de celle de l'auteur
- Des comportements qui doivent être généralisés (pas tous les foyers ont du solaire, une PAC, etc.)
- Un affinage des prompts Claude pour réduire les tokens consommés

Si vous testez, les retours via [GitHub Issues](https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA/issues) sont précieux, même courts.

## 🗺 Roadmap

**Fait :**
- [x] 51 commandes Telegram + langage naturel
- [x] Détection universelle (Matter / Zigbee / Z-Wave / WiFi)
- [x] Moteur de surveillance proactif (briefing 7h, pic solaire, standby, HP/HC, bilan 21h)
- [x] Auto-correction via `/probleme`
- [x] Intégration Google Home / Alexa (TTS)
- [x] HA Add-on + Docker + systemd
- [x] Installation documentée, opt-in deploy_server

**À venir :**
- [ ] Support Groq et Ollama pour réduire le coût API
- [ ] Ballon thermodynamique (pince ampèremétrique)
- [ ] Dashboard web (FastAPI)
- [ ] App mobile (React Native)
- [ ] Multi-langue (EN complet)

## 🤝 Contribuer

- 🐛 **Bug** → [GitHub Issues](https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA/issues)
- 💡 **Idée** → [GitHub Discussions](https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA/discussions)
- 🧪 **Testeur** → [Forum HACF](https://forum.hacf.fr/t/assistantia-domotique-lia-qui-gere-votre-maison-pendant-que-vous-dormez/78164)

## 📜 Licence

[MIT](LICENSE) — Utilisez, modifiez, partagez librement.

---

<p align="center">
  <strong>AssistantIA Domotique</strong><br>
  <em>Un agent IA conversationnel pour votre Home Assistant.</em><br>
  <em>Il parle votre langue. Il apprend votre maison. Il s'auto-corrige.</em>
</p>
