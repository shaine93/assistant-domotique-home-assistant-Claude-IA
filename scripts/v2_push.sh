#!/bin/bash
set -u
LOG=/home/lolufe/assistant/scripts/e2e_test.log
exec > "$LOG" 2>&1
echo "════════ Heartbeat V2 + Guard patché — $(date -Iseconds) ════════"
cd /home/lolufe/assistant

crontab -l > /tmp/crontab.backup 2>/dev/null || true
crontab -l 2>/dev/null | grep -v 'git_sync.sh' | crontab - 2>/dev/null || true

git add skills.py

if git diff --cached --quiet; then
    echo "(rien à commit)"
else
    git commit -m "Heartbeat v2 : reconstruction propre (15/05/2026)

Nouvelle architecture :
- 3 sensors uniquement (ecojoko_consommation_reseau + ecu_today_energy + ecu_current_power)
- Mode log_only par défaut, bascule auto en alerts après 7 jours
- Tables SQL dédiées : heartbeat_v2 + heartbeat_v2_dryrun
- Cooldown 24h par sensor en mode alerts (anti-spam)
- Helper existant _heartbeat_guard_actif réutilisé et patché

Patch guard solar :
- Ajout états weather : lightning-rainy, partlycloudy, lightning, windy,
  windy-variant, exceptional
- Seuil rain_chance baissé : 60% → 40%
- Seuil cloud_coverage baissé : 80% → 60%

Sensors retirés (causes du spam) :
- sensor.solarbank_e1600_etat_du_cloud (gaps de plusieurs jours = normal)
- sensor.solarbank_e1600_etat_de_charge (pas pertinent en heartbeat)
- sensor.solarbank_e1600_puissance_solaire (couvert par ecu_current_power)
- sensor.ecojoko_consommation_temps_reel (refresh cloud volatile)
- sensor.ecojoko_surplus_de_production (non-critique ROI)
- sensor.ecojoko_humidite_interieure (non-critique)

Validation post-déploiement :
- weather.pavillons_sous_bois = lightning-rainy
- Guard solar étouffe correctement ecu_today_energy + ecu_current_power
- ecojoko_consommation_reseau (guard none) signale un VRAI gap de 125min
- Mode log_only actif jusqu'au 22/05/2026 minimum

Ref obligations CDC v8.2 :
- Règle 5 : alertes filtrées selon météo/horaire
- Règle 2 : vérifié factuellement avant push (table SQL inspectée)
- Règle 3 : tout déployé via deploy_server, zéro SSH

Suite chantier : commande /heartbeat (status/mode/reset) à câbler" 2>&1 | tail -3
fi

echo ""
echo "--- git log ---"
git log --oneline -5

echo ""
echo "--- git push ---"
git push origin main 2>&1 | tail -5

crontab /tmp/crontab.backup 2>/dev/null || true
echo "════════ FIN $(date -Iseconds) ════════"
