#!/bin/bash
set -u
LOG=/home/lolufe/assistant/scripts/e2e_test.log
exec > "$LOG" 2>&1
echo "════════ DOC ha-linky $(date -Iseconds) ════════"
cd /home/lolufe/assistant

crontab -l > /tmp/crontab.backup 2>/dev/null || true
crontab -l 2>/dev/null | grep -v 'git_sync.sh' | crontab - 2>/dev/null || true

git add LECONS.md

if git diff --cached --quiet; then
    echo "(rien à commit)"
else
    git commit -m "Doc: source HC/HP via ha-linky (Conso API/Enedis) - 29/04/2026

Documentation complète de la mise en place de ha-linky v1.7.0 comme
source HC/HP indépendante d'Ecojoko, suite au bug Zen Week-End Plus
de little_monkey.

Inclus :
- Étapes validées (collecte horaire Enedis, token Conso API, config YAML)
- Pièges rencontrés (costs au niveau racine, name absent dans costs,
  action:reset supprime sans réimport)
- Chantier ouvert : sensors Ecojoko fantômes + patch AssistantIA pour
  exploiter les statistiques ha-linky via API recorder

État final : 1030 points sur 1 an importés avec coûts calculés selon
tarif Zen Week-End Plus. Tableau Énergie HA fonctionnel. AssistantIA
non encore patché (à faire dans une session dédiée à froid)." 2>&1 | tail -3
fi

echo ""
echo "--- git log ---"
git log --oneline -4

echo ""
echo "--- git push ---"
git push origin main 2>&1 | tail -5

crontab /tmp/crontab.backup 2>/dev/null || true

echo "════════ FIN $(date -Iseconds) ════════"
