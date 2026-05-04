#!/bin/bash
set -u
LOG=/home/lolufe/assistant/scripts/e2e_test.log
exec > "$LOG" 2>&1
echo "════════ CDC v8.2 — OBLIGATIONS DE CLAUDE — $(date -Iseconds) ════════"
cd /home/lolufe/assistant

crontab -l > /tmp/crontab.backup 2>/dev/null || true
crontab -l 2>/dev/null | grep -v 'git_sync.sh' | crontab - 2>/dev/null || true

git add Cahier_des_Charges.md skills.py

if git diff --cached --quiet; then
    echo "(rien à commit)"
else
    git commit -m "v8.2: OBLIGATIONS DE CLAUDE en tête CDC + heartbeat piliers vidé temporairement

Cahier_des_Charges.md (v8.1 → v8.2) :
- Bump version + maj date 04/05/2026
- Nouvelle section CRITIQUE 'OBLIGATIONS DE CLAUDE' insérée en tête,
  juste après l'en-tête, avant Infrastructure
- 10 règles + principe fondateur (ROI tokens vs économies EDF)
- Format HMAC documenté (hashlib.sha256 simple, Bearer/HMAC distincts)
- Tunnel via ntfy.sh/assistantia-deploy-8501-secret
- Erreurs typiques à proscrire listées (name dans costs, action reset,
  préfixe sensor.linky, plage horaire Zen Week-End+)
- Décisions architecturales actées rappelées
- Mention Évolutions v8.2 : Dashboard Énergie HC/HP + utility_meter
  Zen Week-End Plus + section OBLIGATIONS

skills.py :
- _HEARTBEAT_SENSORS_PILIERS = [] vidée temporairement
- Raison : harcèlement météo sur Solarbank (35W jour de pluie = normal)
- TODO : reconstruire avec corrélation météo + heure solaire

Contexte session 04/05/2026 :
- Dashboard Énergie HC/HP créé (3 onglets : Aujourd'hui / Mois / Année)
- 6 utility_meter conso_zwep_*_hc/hp + 11 sensors templates cout_*
- Automation ZWEP bascule HC/HP selon Zen Week-End+ (mer/sam/dim entiers)
- input_select.tarif_courant ajouté
- Format HMAC du deploy_server retrouvé via lecture du source code" 2>&1 | tail -3
fi

echo ""
echo "--- git log ---"
git log --oneline -5

echo ""
echo "--- git push ---"
git push origin main 2>&1 | tail -5

crontab /tmp/crontab.backup 2>/dev/null || true

echo "════════ FIN $(date -Iseconds) ════════"
