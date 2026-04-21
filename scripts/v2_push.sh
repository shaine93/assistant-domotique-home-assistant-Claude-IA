#!/bin/bash
set -u
LOG=/home/lolufe/assistant/scripts/e2e_test.log
exec > "$LOG" 2>&1
echo "════════ README v2 UPDATE $(date -Iseconds) ════════"
cd /home/lolufe/assistant

# Désactiver cron
crontab -l > /tmp/crontab.backup 2>/dev/null || true
crontab -l 2>/dev/null | grep -v 'git_sync.sh' | crontab - 2>/dev/null || true

git add README.md

# Vérifier qu'il y a bien quelque chose à commiter
if git diff --cached --quiet; then
    echo "(aucun changement)"
else
    git commit -m "README v2: retrait des promesses de ROI non tenables

Refonte du README suite aux retours du forum HACF (5 avril 2026) :
- Retrait de la promesse ×10 à ×20 et des chiffres d'économies typiques
  qui ne peuvent pas etre garantis selon l'installation
- Repositionnement : agent IA conversationnel, pas machine a economies
- Ajout d'une section explicite 'En quoi c'est different d'une automation
  classique ?' pour repondre a la question de la valeur ajoutee
- Ajout de la roadmap Groq/Ollama en reponse aux objections de cout API
- Section 'Etat du projet' explicitant le statut beta honnetement
- Le script mesure toujours ses economies via /roi, l'utilisateur
  juge du rapport cout/benefice avec ses propres chiffres" 2>&1 | tail -3
fi

echo ""
echo "--- git log ---"
git log --oneline -3

echo ""
echo "--- git push ---"
git push origin main 2>&1 | tail -5

# Reactiver cron
crontab /tmp/crontab.backup 2>/dev/null || true

echo ""
echo "════════ FIN $(date -Iseconds) ════════"
