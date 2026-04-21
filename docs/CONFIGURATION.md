# ⚙️ Configuration — AssistantIA Domotique

Toute la configuration est dans `config.json`. Ce fichier est généré automatiquement par `./install.sh`, ou peut être édité à la main.

> ⚠️ `config.json` contient vos secrets. Il est créé avec les permissions `600` (lecture propriétaire seul). **Ne jamais le commit sur git.**

## Structure de `config.json`

| Clé | Type | Requis | Description |
|---|---|---|---|
| `telegram_token` | str | ✅ | Token du bot via [@BotFather](https://t.me/BotFather) |
| `telegram_chat_id` | str | Auto | Détecté au premier message |
| `ha_url` | str | ✅ | URL de Home Assistant (ex: `http://192.168.1.76:8123`) |
| `ha_token` | str | ✅ | Long-lived access token HA |
| `anthropic_api_key` | str | ✅ | Clé API depuis [console.anthropic.com](https://console.anthropic.com) |
| `anthropic_monthly_budget_usd` | int | ✅ | Budget mensuel en USD (alerte à 50/80/100 %) |
| `sms_method` | str | ✅ | `free_mobile` \| `ha_notify` \| `email` |
| `free_mobile_user` | str | Si `free_mobile` | Identifiant Free Mobile |
| `free_mobile_pass` | str | Si `free_mobile` | Clé API Free Mobile |
| `smtp_host` | str | Si `email` | Serveur SMTP (ex: `smtp.gmail.com`) |
| `smtp_port` | int | Si `email` | Port SMTP (587 pour TLS) |
| `smtp_user` | str | Si `email` | Identifiant SMTP |
| `smtp_pass` | str | Si `email` | Mot de passe (ou App Password Gmail) |
| `mail_dest` | str | Si `email` | Adresse email destinataire |
| `poll_interval_sec` | int | ✅ | Intervalle polling Telegram (défaut : 2) |
| `audit_interval_sec` | int | ✅ | Intervalle audit complet en secondes (défaut : 1800) |
| `deploy_secret` | str | ✅ | Secret HMAC 64 chars (auto-généré) — **ne jamais partager** |

## Obtenir les credentials

### 1. Telegram Bot Token

1. Ouvrir Telegram, chercher [@BotFather](https://t.me/BotFather)
2. `/newbot` → choisir un nom → choisir un username terminant par `_bot`
3. BotFather vous donne un token de la forme `123456789:ABCdefGhIJKlmnopQRStuvwxyz`
4. Gardez-le secret — il permet de contrôler votre bot

### 2. Home Assistant — URL et token

**URL :** l'URL de votre HA accessible depuis la machine où tourne AssistantIA.
- Local réseau : `http://192.168.1.XX:8123`
- Via DuckDNS / Nabu Casa : `https://xxx.duckdns.org`

**Token :**
1. Dans HA, cliquer sur votre avatar en bas à gauche
2. Onglet **Sécurité** → **Jetons d'accès longue durée**
3. Cliquer **Créer un jeton**
4. Donner un nom (ex: `AssistantIA`) → copier le token affiché
5. ⚠️ Ce token ne s'affiche qu'une fois — gardez-le

### 3. Anthropic API Key

1. Aller sur [console.anthropic.com](https://console.anthropic.com)
2. Créer un compte → ajouter une carte (crédit requis)
3. **API Keys → Create Key**
4. Copier la clé (commence par `sk-ant-...`)

**Budget :** un usage normal coûte 5-10 €/mois. Mettez `anthropic_monthly_budget_usd: 10` pour commencer, vous ajusterez.

### 4. Méthode de sécurité (code 6 chiffres au démarrage)

Au démarrage, AssistantIA envoie un code à 6 chiffres pour vérifier que c'est bien vous qui accédez au bot.

**Trois méthodes possibles :**

- **`ha_notify`** (recommandé) : utilise les notifications Home Assistant (app mobile). Zéro configuration supplémentaire.
- **`free_mobile`** : SMS gratuit si vous avez un forfait Free Mobile 2 € minimum. Récupérez vos identifiants dans l'espace abonné Free → Mes options → Notifications par SMS.
- **`email`** : email via SMTP. Pour Gmail, créez un [App Password](https://myaccount.google.com/apppasswords).

## Exemple complet

```json
{
  "telegram_token": "123456789:ABCdefGhIJKlmnopQRStuvwxyz",
  "telegram_chat_id": "",
  "ha_url": "http://192.168.1.76:8123",
  "ha_token": "eyJhbGciOiJIUzI1...",
  "anthropic_api_key": "sk-ant-api03-xxxxx...",
  "sms_method": "ha_notify",
  "free_mobile_user": "",
  "free_mobile_pass": "",
  "smtp_host": "",
  "smtp_port": 587,
  "smtp_user": "",
  "smtp_pass": "",
  "mail_dest": "",
  "poll_interval_sec": 2,
  "audit_interval_sec": 1800,
  "anthropic_monthly_budget_usd": 10,
  "deploy_secret": "3f8a9b2c7e1d4f5a6b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a"
}
```

## Modifier la config après installation

1. Éditer `config.json` directement
2. Redémarrer AssistantIA :
   - HA Add-on : bouton **Redémarrer** dans l'interface
   - Docker : `docker compose restart assistantia`
   - Linux natif : `sudo systemctl restart assistantia.service`
   - Manuel : Ctrl+C puis `python3 assistant.py`

## Règles de configuration

- **Ne jamais commit `config.json` sur git** (il est dans `.gitignore` par défaut)
- `deploy_secret` est auto-généré — laissez-le tranquille sauf si vous le régénérez exprès
- `telegram_chat_id` se remplit tout seul au premier message reçu
- Si vous changez de bot Telegram, repartez d'un nouveau `config.json` (le canal se reverrouille)
