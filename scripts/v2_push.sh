#!/bin/bash
set -u
LOG=/home/lolufe/assistant/scripts/e2e_test.log
exec > "$LOG" 2>&1
echo "════════ FIX ZEN WEEK-END PLUS $(date -Iseconds) ════════"
cd /home/lolufe/assistant

crontab -l > /tmp/crontab.backup 2>/dev/null || true
crontab -l 2>/dev/null | grep -v 'git_sync.sh' | crontab - 2>/dev/null || true

git add skills.py LECONS.md

if git diff --cached --quiet; then
    echo "(rien à commit)"
else
    git commit -m "Fix: skill heartbeat — vider _HEARTBEAT_SENSORS_TARIF (Zen Week-End Plus)

Le tarif EDF Zen Week-End Plus n'est pas supporté par little_monkey v1.2.4.
Les capteurs sensor.ecojoko_consommation_hc_reseau et _hp_reseau restent
en unknown indéfiniment, déclenchant de fausses alertes heartbeat.

Décision : décocher ces capteurs côté little_monkey (configuration HA)
pour les faire disparaître. En conséquence, vider _HEARTBEAT_SENSORS_TARIF
dans skills.py pour ne plus tenter de surveiller des entités absentes.

Le découpage HC/HP est conservé via les autres détecteurs du bot
(Linky/ZLinky/ESPHome/Tempo) en fallback. Pas de perte fonctionnelle." 2>&1 | tail -3
fi

echo ""
echo "--- git log ---"
git log --oneline -4

echo ""
echo "--- git push ---"
git push origin main 2>&1 | tail -5

crontab /tmp/crontab.backup 2>/dev/null || true

echo ""
echo "════════ FIN $(date -Iseconds) ════════"
