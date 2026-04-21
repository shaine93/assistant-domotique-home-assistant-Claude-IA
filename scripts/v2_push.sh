#!/bin/bash
set -u
LOG=/home/lolufe/assistant/repo_cleanup.log
exec >> "$LOG" 2>&1
echo ""
echo "════════ V2_PUSH $(date -Iseconds) ════════"
cd /home/lolufe/assistant

# Désactiver le cron temporairement
crontab -l > /tmp/crontab.backup 2>/dev/null || true
crontab -l 2>/dev/null | grep -v 'git_sync.sh' | crontab - 2>/dev/null || true

# Ajouter tous les nouveaux fichiers
git add README.md requirements.txt env.example install.sh Dockerfile \
        docker-compose.yml assistantia.service.template LICENSE \
        scripts/ docs/ addon/Dockerfile addon/config.yaml addon/run.sh

# Supprimer les obsolètes (déjà retirés du disque via /delete)
git add -u addon/Dockerfile.txt assistantia.service.txt 2>/dev/null || true

# État avant commit
echo "--- git status ---"
git status -s

# Commit
git commit -m "Install v2.0: proper README, 4 install methods, docs/, scripts/, LICENSE, .gitignore

- Nouveau README propre pointant vers le vrai repo
- 4 méthodes d'install documentées : HA Add-on, Docker, Linux natif, manuel
- install.sh : wizard CLI interactif (genère config.json)
- Dockerfile racine + docker-compose.yml propre
- scripts/install_systemd.sh : deploy comme service système
- scripts/enable_beta_channel.sh : opt-in pour le mode bêta-testeur
- docs/ : INSTALL, CONFIGURATION, TROUBLESHOOTING, BETA_CHANNEL
- addon/Dockerfile : renommé de .txt (HA Add-on Store le veut sans extension)
- addon/config.yaml : vraie URL GitHub + flag enable_deploy_server opt-in
- LICENSE : MIT
- Secrets rotés, deploy_server désactivé par défaut (opt-in)" || echo "(rien à commiter)"

echo "--- git log ---"
git log --oneline -3

# Push
echo "--- git push ---"
git push origin main 2>&1 | tail -10

# Réactiver le cron
crontab /tmp/crontab.backup 2>/dev/null || true

echo "════════ FIN V2_PUSH $(date -Iseconds) ════════"
