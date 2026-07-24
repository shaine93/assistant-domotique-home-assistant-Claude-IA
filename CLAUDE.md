# CLAUDE.md — Point d'entrée pour tout agent Claude

> **Ce fichier est lu automatiquement par Claude Code au démarrage de chaque session.**
> **Lis les documents référencés AVANT toute action. Chaque token gaspillé en tâtonnement est un échec.**

---

## Projet

**AssistantIA Domotique** — agent IA autonome Python qui pilote Home Assistant via Telegram + Claude API.
Propriétaire : Philippe (shaine93).
Principe fondateur : **Philippe paye des tokens API pour gagner sur sa facture EDF (ROI mesurable).**

---

## Documents obligatoires à lire selon le contexte

### Bot AssistantIA (skills.py, assistant.py, config.py, shared.py)

1. **`Cahier_des_Charges.md`** — architecture, modules, flux de données
2. **`LECONS.md`** — erreurs passées et solutions, NE PAS les refaire
3. **`README.md`** — dépendances, installation, configuration

### Home Assistant Green (maintenance, stockage, add-ons)

4. **`HA_Green_Maintenance_Guide.md`** — TOUT ce qu'il faut savoir pour intervenir sur le HA Green : accès root, procédures, interdits, add-ons, plan de survie eMMC
5. **`HA_Green_Diagnostic_Stockage.md`** — diagnostic complet du 22/07/2026, répartition disque, root cause de l'espace "Système"

---

## Accès infrastructure

### Deploy server (VM OVH — bot AssistantIA)

- Tunnel URL : récupérer via `curl https://ntfy.sh/assistantia-deploy-8501-secret/json?poll=1&since=24h` (prendre le dernier message contenant trycloudflare)
- Auth : Bearer pour GET, HMAC-SHA256 pour POST
- Secret HMAC : préfixe `5a0667aada` — récupérer le secret complet dans l'historique des conversations (query: "deploy_server HMAC secret")
- Endpoints : `/read/<file>`, `/file`, `/patch`, `/restart`, `/status`, `/run_v2_push`

### Home Assistant Green

- IP locale : `192.168.1.76`
- URL externe : `https://philhomeassist.duckdns.org`
- SSH root host : `ssh root@192.168.1.76 -p 22222` (clé USB CONFIG branchée en permanence)
- Terminal add-on : Advanced SSH & Web Terminal (protection mode désactivé)
- Accès partiel via nsenter : `nsenter -t 1 -m -u -i -n -- /bin/bash`

---

## Règles non négociables

1. **Philippe ne fait JAMAIS de SSH ou copier-coller** — l'agent doit être autonome
2. **Ne jamais recommander la migration SSD USB sur HA Green** — crash complet déjà vécu
3. **Vérifier factuellement avant de proposer** — lire la doc, tester via deploy server
4. **Préserver le contexte existant** — lire avant de patcher, jamais dupliquer de clé YAML
5. **Dire la vérité technique même quand elle fâche** — pas de mensonge agréable
6. **Documenter en continu** — LECONS.md, Cahier_des_Charges.md, commits GitHub systématiques
7. **Architecture 4 fichiers** : config.py, shared.py, skills.py, assistant.py — ne pas fragmenter
8. **HA Green = pas de Docker direct**, uniquement add-ons HA OS
9. **MariaDB pour recorder**, purge_keep_days: 30, stats long terme infinies
10. **Telegram = unique interface utilisateur** du bot

---

*Dernière mise à jour : 22/07/2026*
