#!/bin/bash
set -u
LOG=/home/lolufe/assistant/scripts/e2e_test.log
exec > "$LOG" 2>&1
echo "════════ CDC v8.0 UPDATE $(date -Iseconds) ════════"
cd /home/lolufe/assistant

# Vérifier qu'il n'est pas ignoré
if grep -q "^Cahier_des_Charges" .gitignore 2>/dev/null; then
    echo "⚠️ Cahier_des_Charges.md est dans .gitignore — on l'ajoute quand même en force"
    GIT_ADD="git add -f Cahier_des_Charges.md"
else
    echo "✅ Cahier non ignoré"
    GIT_ADD="git add Cahier_des_Charges.md"
fi

# Désactiver cron
crontab -l > /tmp/crontab.backup 2>/dev/null || true
crontab -l 2>/dev/null | grep -v 'git_sync.sh' | crontab - 2>/dev/null || true

$GIT_ADD

# Commit (si quelque chose à commiter)
if git diff --cached --quiet; then
    echo "(pas de changement — peut-etre deja commite via git_sync)"
else
    git commit -m "Cahier des Charges v8.0 — Rotation secrets + install v2.0 + fix watchdog

Changements :
- Header : v7.62 -> v8.0, date 19/04 -> 24/04
- Nouvelle section 'Rotation des secrets (24/04/2026)'
  (telegram, HA, anthropic, deploy_secret revoques et regeneres)
- Nouvelle section 'v2.0 - REPO PUBLIC PROPRE ET INSTALLABLE'
  (828 fichiers nettoyes, 19 fichiers d'install, 4 methodes supportees,
   mode beta opt-in strict, repositionnement README sans ROI x10-x20)
- Bug watchdog 401 documente (fix via is_alive() accepte 200 ET 401)
- Bug config.json ownership documente (chown lolufe apres patch sudo)
- Endpoint /config_update documente
- Deploy secret retire des 4 occurrences du bloc de reprise
  (remplace par placeholder + instruction de lecture via SSH)
- Commits publics v2.0 listes" 2>&1 | tail -5
fi

echo ""
echo "--- git log ---"
git log --oneline -4

echo ""
echo "--- git push ---"
git push origin main 2>&1 | tail -5

# Reactiver cron
crontab /tmp/crontab.backup 2>/dev/null || true

echo ""
echo "════════ FIN $(date -Iseconds) ════════"
