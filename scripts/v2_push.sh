#!/bin/bash
set -u
LOG=/home/lolufe/assistant/scripts/e2e_test.log
exec > "$LOG" 2>&1
echo "════════ DOC fin journée 29/04 $(date -Iseconds) ════════"
cd /home/lolufe/assistant

crontab -l > /tmp/crontab.backup 2>/dev/null || true
crontab -l 2>/dev/null | grep -v 'git_sync.sh' | crontab - 2>/dev/null || true

git add LECONS.md

if git diff --cached --quiet; then
    echo "(rien à commit)"
else
    git commit -m "Doc: sensors Ecojoko HC/HP fantômes supprimés - clôture 29/04/2026

Confirmation que les entités sensor.ecojoko_consommation_hc_reseau et
_hp_reseau étaient des entités orphelines (HA garde les entités après
décochage de l'intégration source).

Suppression manuelle via Paramètres → Appareils et services → Entités
→ engrenage → Supprimer. État final propre.

Reste comme chantier ouvert : patch AssistantIA pour exploiter les
statistiques ha-linky (à faire dans une session dédiée à froid)." 2>&1 | tail -3
fi

echo ""
echo "--- git log ---"
git log --oneline -4

echo ""
echo "--- git push ---"
git push origin main 2>&1 | tail -5

crontab /tmp/crontab.backup 2>/dev/null || true

echo "════════ FIN $(date -Iseconds) ════════"
