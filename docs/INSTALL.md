# 📦 Guide d'installation — AssistantIA Domotique

Quatre méthodes d'installation supportées. Choisissez selon votre environnement.

| Méthode | Difficulté | Auto-recovery | Mises à jour |
|---|---|---|---|
| HA Add-on | 🟢 Très facile | ✅ Supervisor | 1 clic |
| Docker Compose | 🟢 Facile | ✅ `restart: unless-stopped` | `docker compose pull && up -d` |
| Linux natif | 🟡 Moyen | ✅ systemd | `git pull && restart` |
| Manuel | 🟡 Moyen | ❌ | `git pull` |

---

## HA Add-on

**Pré-requis :** Home Assistant OS ou Home Assistant Supervised.

### Étapes

1. Dans Home Assistant, aller dans **Paramètres → Modules complémentaires → Boutique**
2. Cliquer sur les trois points en haut à droite → **Dépôts**
3. Ajouter l'URL : `https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA`
4. Fermer, recharger — trouver **AssistantIA Domotique** dans la liste
5. Cliquer **Installer**
6. Onglet **Configuration** — remplir au minimum :
   - `telegram_token` (via [@BotFather](https://t.me/BotFather))
   - `anthropic_api_key` (via [console.anthropic.com](https://console.anthropic.com))
   - Laisser `sms_method` à `ha_notify` (utilise les notifications HA)
7. Démarrer l'add-on
8. Envoyer un message à votre bot Telegram pour finaliser le setup

### Données persistantes

- `config.json` et `memory.db` sont stockés dans `/config/assistantia/` côté HA
- Les logs sont dans l'onglet **Journal** de l'add-on

### Mise à jour

Bouton **Mettre à jour** dans l'interface HA dès qu'une nouvelle version est publiée.

---

## Docker

**Pré-requis :** Docker + Docker Compose (NAS, Linux, Mac, Windows WSL...).

### Étapes

```bash
# 1. Récupérer le code
git clone https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA.git
cd assistant-domotique-home-assistant-Claude-IA

# 2. Préparer la config
cp env.example .env
nano .env   # remplir TELEGRAM_TOKEN, HA_URL, HA_TOKEN, ANTHROPIC_API_KEY

# 3. Générer config.json (option A: depuis .env)
./install.sh --from-env

# 3bis. (option B: interactif, sans .env)
./install.sh

# 4. Démarrer
docker compose up -d

# 5. Suivre les logs
docker compose logs -f assistantia
```

### Structure après installation

```
.
├── config.json          # vos secrets (chmod 600)
├── .env                 # optionnel
├── data/
│   ├── memory.db        # base SQLite persistante
│   ├── assistant.log    # logs applicatifs
│   └── config.json      # lu par le container
├── docker-compose.yml
└── Dockerfile
```

### Mise à jour

```bash
git pull
docker compose build     # si vous construisez localement
# ou : docker compose pull  (si vous utilisez l'image ghcr.io)
docker compose up -d
```

### Arrêter / redémarrer

```bash
docker compose restart assistantia
docker compose stop
docker compose down      # supprime le container (les données restent dans ./data)
```

---

## Linux natif

**Pré-requis :** Python 3.10+, Raspberry Pi OS / Ubuntu / Debian, accès sudo.

### Étapes

```bash
# 1. Dépendances système
sudo apt update
sudo apt install -y python3 python3-pip git curl jq

# 2. Cloner dans /home/<user>/assistantia (exemple)
cd ~
git clone https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA.git assistantia
cd assistantia

# 3. Wizard d'installation (dépendances + config.json)
./install.sh

# 4. Test manuel
python3 assistant.py
# → Envoyez un message à votre bot Telegram pour vérifier la connexion
# → Ctrl+C pour arrêter

# 5. Déploiement comme service systemd (auto-démarrage au boot, auto-recovery)
sudo ./scripts/install_systemd.sh
```

### Gestion du service

```bash
sudo systemctl status  assistantia.service      # état
sudo systemctl restart assistantia.service      # redémarrer
sudo systemctl stop    assistantia.service      # arrêter
sudo journalctl -u assistantia.service -f       # logs live
tail -f ~/assistantia/assistant.log             # logs applicatifs
```

### Mise à jour

```bash
cd ~/assistantia
git pull
pip3 install --user --upgrade -r requirements.txt
sudo systemctl restart assistantia.service
```

### Désinstaller

```bash
sudo systemctl stop assistantia.service
sudo systemctl disable assistantia.service
sudo rm /etc/systemd/system/assistantia.service
sudo systemctl daemon-reload
rm -rf ~/assistantia       # supprime le code, config et DB
```

---

## Manuel

Pour lancer le bot à la main, sans service, sans Docker.

```bash
git clone https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA.git
cd assistant-domotique-home-assistant-Claude-IA
pip3 install --user -r requirements.txt
./install.sh               # wizard interactif → config.json
python3 assistant.py       # lance le bot
```

Pour le laisser tourner après déconnexion :

```bash
nohup python3 assistant.py > assistant.log 2>&1 &
# ou mieux : tmux new -s assistantia, puis python3 assistant.py, puis Ctrl+B D pour détacher
```

Pour le relancer automatiquement au boot, utilisez plutôt la méthode **Linux natif** avec systemd.

---

## Que se passe-t-il au premier lancement ?

1. **Détection du chat Telegram** — Le bot attend votre premier message pour enregistrer votre `chat_id`. Envoyez n'importe quoi (par exemple « hello »).
2. **Code de sécurité** — Un code à 6 chiffres est envoyé selon `sms_method` (Free Mobile / notification HA / email). Tapez-le dans Telegram pour déverrouiller le canal.
3. **Questionnaire appareils** — Pour chaque prise avec mesure de puissance détectée, le bot demande : lave-linge / sèche-linge / lave-vaisselle / TV / autre.
4. **Profil foyer** — 8 questions rapides : présence, chauffage, eau chaude, solaire, objectif.
5. **Tarif électricité** — Détection automatique HP/HC ou questionnaire.

Durée totale : **10 minutes**. Ensuite, vous ne touchez plus rien.

---

## Vérifier que tout marche

Dans Telegram :

- `/aide` — liste des commandes
- `/audit` — rapport complet (énergie, Zigbee, NAS, batteries)
- `/debug` — threads, watchdog, versions
- `/surveillance` — vue complète des entités surveillées

Si une commande retourne une erreur, consultez [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
