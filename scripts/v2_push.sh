#!/bin/bash
set -u
LOG=/home/lolufe/assistant/scripts/e2e_test.log
exec > "$LOG" 2>&1
echo "════════ SKILL HEARTBEAT_PILIER $(date -Iseconds) ════════"
cd /home/lolufe/assistant

# Désactiver cron pour éviter conflit
crontab -l > /tmp/crontab.backup 2>/dev/null || true
crontab -l 2>/dev/null | grep -v 'git_sync.sh' | crontab - 2>/dev/null || true

git add skills.py LECONS.md

if git diff --cached --quiet; then
    echo "(rien à committer)"
else
    git commit -m "Skill: heartbeat_pilier — surveillance apprenante des sensors énergétiques

Première brique de la solution propre au bug détection offline (24/04/2026).

Périmètre : 8 sensors énergétiques piliers (Ecojoko x4 + APSystems x2 + Anker x2)
+ 2 sensors HC/HP traités séparément (1 update/jour à minuit, seuil 26h).

Architecture :
- Table sensor_heartbeat (entity_id PK, median_sec, p95_sec, p99_sec, ...)
- Phase apprentissage : 7 jours d'observation silencieuse
- Phase calibration : calcul des seuils depuis /api/history HA
- Phase surveillance : alerte si gap > P99x2 (warning) ou P99x5 (critique)
- Recompute hebdomadaire pour s'adapter aux saisons

Commande Telegram : /heartbeat (status uniquement, reset via SQL en SSH).

Validation conjointe avec Philippe avant code (4 décisions D1-D4).

Suite à la rétrospective : pas de seuil hardcodé car les sensors ont des
comportements très différents (gaps nocturnes légitimes vs vraies pannes)." 2>&1 | tail -3
fi

echo ""
echo "--- git log ---"
git log --oneline -5

echo ""
echo "--- git push ---"
git push origin main 2>&1 | tail -5

# Restaurer cron
crontab /tmp/crontab.backup 2>/dev/null || true

echo ""
echo "════════ FIN $(date -Iseconds) ════════"
