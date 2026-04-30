#!/bin/bash
set -u
LOG=/home/lolufe/assistant/scripts/e2e_test.log
exec > "$LOG" 2>&1
echo "════════ CDC v8.1 + README maj $(date -Iseconds) ════════"
cd /home/lolufe/assistant

crontab -l > /tmp/crontab.backup 2>/dev/null || true
crontab -l 2>/dev/null | grep -v 'git_sync.sh' | crontab - 2>/dev/null || true

git add Cahier_des_Charges.md README.md

if git diff --cached --quiet; then
    echo "(rien à commit)"
else
    git commit -m "Doc: CDC v8.1 + README — skill heartbeat_pilier + source ha-linky

Cahier_des_Charges.md (v8.0 → v8.1) :
- Bump version + maj stats (19 skills, 52 commandes, 23 tables)
- Nouveau bloc 'SKILL HEARTBEAT_PILIER' : architecture apprenante 7 jours,
  table sensor_heartbeat, 8 sensors piliers, 3 phases automatiques
- Nouveau bloc 'SOURCE HC/HP INDÉPENDANTE — ha-linky' : Conso API Enedis,
  config Zen Week-End Plus, pièges YAML rencontrés, chantiers ouverts

README.md :
- Nouvelle section 'Données HC/HP fiables — recommandation' dans Pré-requis
- Recommandation ha-linky (Bokub) comme source HC/HP officielle Enedis
- Mention explicite du bug little_monkey sur Zen Week-End Plus
- Caveat J+1 (livraison Enedis le lendemain)

Tous les détails techniques dans LECONS.md (déjà commité)." 2>&1 | tail -3
fi

echo ""
echo "--- git log ---"
git log --oneline -6

echo ""
echo "--- git push ---"
git push origin main 2>&1 | tail -5

crontab /tmp/crontab.backup 2>/dev/null || true

echo "════════ FIN $(date -Iseconds) ════════"
