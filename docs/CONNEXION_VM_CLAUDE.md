# 🔌 PROCÉDURE DE CONNEXION CLAUDE → VM AssistantIA

**À lire en premier dans chaque nouvelle conversation. Sans cette procédure, Claude est aveugle.**

> ⚠️ **Note importante** : Ce document est public (suivi par Git). Le secret HMAC et l'identifiant du topic ntfy.sh sont dans un fichier séparé `CONNEXION_VM_SECRETS.md` qui est dans `.gitignore` et **uploadé manuellement dans Claude Projects** uniquement.

---

## 🎯 OBJECTIF

Garantir à Claude un accès direct, autonome et permanent à la VM Google Cloud qui héberge AssistantIA Domotique, sans qu'aucune action manuelle de l'opérateur ne soit requise.

**Règle d'or** : l'opérateur (Philippe) ne doit JAMAIS avoir à SSH-er, copier-coller, ou exécuter une commande sur la VM pour que Claude travaille. Si Claude demande à Philippe de taper quelque chose côté VM pour lire ou patcher du code, c'est un échec d'autonomie.

---

## 🏗️ ARCHITECTURE DE L'ACCÈS

```
                  ┌──────────────────────┐
                  │  Conversation Claude │
                  │   (claude.ai web)    │
                  └──────────┬───────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     Project Knowledge  ntfy.sh    bash_tool (curl)
     (secret HMAC)     (URL tunnel) (requête signée)
              │              │              │
              └──────────────┼──────────────┘
                             ▼
            ┌────────────────────────────────┐
            │  https://<random>.trycloudflare.com │
            │  (tunnel cloudflared sur VM)   │
            └────────────────┬───────────────┘
                             │
                             ▼
            ┌────────────────────────────────┐
            │  deploy_server.py (port 8501)  │
            │  Auth: Bearer (GET) / HMAC (POST) │
            └────────────────┬───────────────┘
                             │
                             ▼
            ┌────────────────────────────────┐
            │  /home/lolufe/assistant/       │
            │  - assistant.py                │
            │  - skills.py                   │
            │  - shared.py                   │
            │  - config.py                   │
            │  - Cahier_des_Charges.md       │
            └────────────────────────────────┘
```

---

## 📋 PROCÉDURE EN 4 ÉTAPES

### Étape 1 — Récupérer le secret HMAC

Le secret est stocké dans le fichier `CONNEXION_VM_SECRETS.md` uploadé dans **Claude Projects → Project knowledge**. Ce fichier n'est jamais commité dans Git.

Si le secret n'est pas accessible via Project knowledge :

1. Tenter `conversation_search` avec la requête `"deploy_server HMAC secret VM"` — il apparaît dans plusieurs conversations passées du projet.
2. Si tout échoue, demander à Philippe la commande VM suivante (à exécuter en local) :
   ```bash
   sudo cat /home/lolufe/assistant/config.json | python3 -c "import json,sys; print(json.load(sys.stdin)['deploy_secret'])"
   ```

### Étape 2 — Récupérer l'URL du tunnel Cloudflare

L'URL tourne à chaque restart de `cloudflared_tunnel.service`. Elle est publiée toutes les heures sur ntfy.sh par un cron côté VM. L'identifiant du topic est dans `CONNEXION_VM_SECRETS.md`.

```bash
TUNNEL=$(curl -s -m 10 "https://ntfy.sh/<TOPIC_NTFY>/json?poll=1&since=24h" \
  | tail -1 \
  | python3 -c "import json,sys; print(json.loads(sys.stdin.read())['message'])")

echo "Tunnel actuel : $TUNNEL"
```

**Important** : toujours prendre le DERNIER message ntfy (le plus récent). Les anciens tunnels sont morts (NXDOMAIN).

### Étape 3 — Vérifier l'accès

```python
import requests

SECRET = "<secret de l'étape 1>"
BASE = "<tunnel de l'étape 2>"
H_GET = {"Authorization": f"Bearer {SECRET}"}

r = requests.get(f"{BASE}/status", headers=H_GET, timeout=20)
assert r.status_code == 200, f"Accès KO : HTTP {r.status_code}"
print(r.json())  # {"status": "ok", "service": "active", ...}
```

Si HTTP 200 → main confirmée. Sinon : voir section **DÉPANNAGE**.

### Étape 4 — Lire les fichiers du projet

```python
for fname in ["assistant.py", "skills.py", "shared.py", "config.py",
              "Cahier_des_Charges.md", "LECONS.md", "README.md"]:
    r = requests.get(f"{BASE}/read/{fname}", headers=H_GET, timeout=30)
    if r.status_code == 200:
        content = r.json()["content"]
        # ...traiter le contenu
```

---

## 🔑 ENDPOINTS DEPLOY_SERVER

| Méthode | Endpoint | Auth | Usage |
|---|---|---|---|
| GET | `/status` | Bearer | État service, version, taille script |
| GET | `/ls` | Bearer | Liste fichiers du dossier |
| GET | `/read/<fichier>` | Bearer | Lire un fichier |
| GET | `/logs?n=50` | Bearer | Dernières lignes journalctl |
| POST | `/file` | HMAC | Écrire un fichier complet |
| POST | `/patch` | HMAC | Patcher `assistant.py` (mode replace) |
| POST | `/restart` | HMAC | Redémarrer `assistant.service` |
| POST | `/rollback` | HMAC | Annuler dernier deploy |
| POST | `/run_v2_push` | HMAC | Push des sensors v2 vers HA |

### Format HMAC (pour POST)

```python
import hmac, hashlib, json, requests

def post(path, payload, secret, base):
    body = json.dumps(payload).encode()
    sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    headers = {
        "Authorization": f"HMAC {sig}",
        "Content-Type": "application/json"
    }
    return requests.post(f"{base}{path}", data=body, headers=headers, timeout=30)
```

⚠️ **Le HMAC est calculé sur le body brut**, pas sur le path ou des headers. Pas de timestamp, pas de nonce.

---

## 📝 TEMPLATE DÉMARRAGE DE CONVERSATION

Au début de chaque nouvelle conversation, Claude exécute ces étapes dans l'ordre, **sans demander la permission à Philippe** :

```python
# 1. Lire CONNEXION_VM_SECRETS.md depuis Project knowledge → SECRET et NTFY_TOPIC

# 2. Récupérer URL tunnel via ntfy.sh
import subprocess, json
out = subprocess.check_output([
    "curl", "-s", "-m", "10",
    f"https://ntfy.sh/{NTFY_TOPIC}/json?poll=1&since=24h"
], text=True).strip().split("\n")[-1]
TUNNEL = json.loads(out)["message"]

# 3. Vérifier accès
import requests
r = requests.get(f"{TUNNEL}/status",
                 headers={"Authorization": f"Bearer {SECRET}"},
                 timeout=20)
assert r.status_code == 200

# 4. Lire le Cahier des Charges + LECONS pour avoir le contexte projet
for f in ["Cahier_des_Charges.md", "LECONS.md"]:
    r = requests.get(f"{TUNNEL}/read/{f}",
                     headers={"Authorization": f"Bearer {SECRET}"},
                     timeout=30)
    # ... lire et indexer
```

---

## 🚨 DÉPANNAGE

### Cas 1 — DNS du tunnel ne résout plus
**Symptôme** : `Failed to resolve 'xxx.trycloudflare.com'`
**Cause** : Le tunnel a tourné depuis l'URL connue. Cloudflared a redémarré.
**Solution** : Re-récupérer la dernière URL via ntfy.sh (étape 2). Toujours prendre le dernier message.

### Cas 2 — HTTP 401 Non autorisé
**Symptôme** : `{"status": "error", "message": "Non autorisé"}`
**Causes possibles** :
- Mauvais format d'auth : pour GET utiliser `Bearer`, pour POST utiliser `HMAC`
- Secret rotaté côté VM
- HMAC mal calculé : doit être `hmac.new(secret.encode(), body_bytes, hashlib.sha256).hexdigest()`

**Solution** : Vérifier body et signature. Si secret rotaté, mettre à jour `CONNEXION_VM_SECRETS.md` dans Claude Projects.

### Cas 3 — ntfy.sh ne renvoie rien
**Symptôme** : Topic vide ou erreur curl
**Cause** : Le cron VM qui publie l'URL est cassé, ou ntfy.sh est down.
**Solution de secours** : Demander l'URL à Philippe. Fonctionnalité backlog : commande Telegram `/tunnel` qui renverra l'URL active.

### Cas 4 — `/status` HTTP 502/503
**Symptôme** : Tunnel répond, mais erreur interne
**Cause** : `deploy_server.service` est down sur la VM.
**Solution** : Demander à Philippe : `sudo systemctl restart deploy_server.service`. Pas de moyen de le redémarrer à distance puisque c'est lui-même qui sert l'API.

### Cas 5 — Project knowledge inaccessible / fichier secrets manquant
**Symptôme** : Pas de `CONNEXION_VM_SECRETS.md` dans le contexte
**Solution dans l'ordre** :
1. `conversation_search` avec des termes neutres : `"deploy_server HMAC"`, `"vm_client.py secret"`
2. Si rien : demander à Philippe d'exporter via la commande VM (étape 1)
3. Re-uploader le fichier secrets dans Claude Projects après récupération

---

## 🔮 AMÉLIORATIONS FUTURES (priorité décroissante)

### 1. URL stable au lieu de tunnel quick
**Problème** : `trycloudflare.com` est éphémère par design.
**Pistes alternatives** :
- Cloudflare Tunnel nommé (pas quick) avec sous-domaine fixe (gratuit, demande un compte Cloudflare lié au domaine)
- Utiliser `philhomeassist.duckdns.org:8501` directement (port forwarding sur la box Bouygues — déjà configuré pour HA)
- Sous-domaine perso DNS-pointé vers la VM

**Recommandation** : Cloudflare Tunnel nommé sur sous-domaine de duckdns ou domaine perso. C'est l'option la plus pro et gratuite.

### 2. Heartbeat de la procédure de connexion
**Problème** : Si la chaîne casse silencieusement (cron ntfy mort, deploy_server crashé), Claude le découvre seulement à la connexion suivante.
**Piste** : Une commande Telegram `/connexion` qui teste toute la chaîne et envoie un rapport quotidien à Philippe.

### 3. Endpoint `/tunnel` qui renvoie l'URL courante
**Problème** : Si ntfy.sh tombe, plus de canal de découverte.
**Piste** : Endpoint sur deploy_server (oui, c'est circulaire mais utile pour tester) qui répond avec `{"tunnel": os.getenv("TUNNEL_URL")}`. Le wrapper `tunnel_wrapper.sh` exporte déjà cette variable.

### 4. Rotation programmée du secret
**Problème** : Secret stable depuis ~2 mois. Bonne pratique sécu : rotation trimestrielle.
**Piste** : Script `rotate_secret.sh` qui génère un nouveau token, met à jour `config.json`, restart deploy_server, et envoie le nouveau secret à Philippe via Telegram (pour qu'il mette à jour `CONNEXION_VM_SECRETS.md` dans Claude Projects).

---

## 📅 HISTORIQUE

| Date | Évènement |
|---|---|
| 2026-03-11 | Création initiale `deploy_server.py` (v1, port 8501) |
| 2026-03-15 | v2 deploy_server : ajout `/file`, `/ls`, `/read/<fichier>` |
| 2026-04-19 | Mise en place tunnel Cloudflare quick + cron ntfy.sh |
| 2026-04-24 | Repo public sur GitHub, secrets retirés du code |
| 2026-05-05 | Documentation formalisée pour Claude Projects (ce document) |
| 2026-05-05 | Séparation publique/privée : secrets isolés dans `CONNEXION_VM_SECRETS.md` (gitignore) |

---

## 🎬 RÈGLE FINALE

Si Claude rentre dans une conversation et **n'a pas immédiatement la main sur la VM** (même après les 4 étapes), il doit :

1. Lever l'alerte **explicitement** : "Je n'ai pas la main sur la VM, voici ce qui bloque : [cause]"
2. **Ne pas inventer** ou faire semblant d'avoir l'accès en demandant à Philippe de copier-coller des sorties de fichiers
3. Demander UNE seule action à Philippe : la solution prescrite dans la section DÉPANNAGE correspondante au cas

**Sans la main sur la VM, Claude n'est qu'un consultant sur les fichiers en pièces jointes — pas un opérateur autonome. Cette différence est la genèse même du projet AssistantIA.**
