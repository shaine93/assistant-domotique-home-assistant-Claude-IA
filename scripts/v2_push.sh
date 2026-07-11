#!/bin/bash
exec > /home/lolufe/assistant/scripts/e2e_test.log 2>&1
cd /home/lolufe/assistant
sudo -n /bin/systemctl restart assistant.service
sleep 4
systemctl is-active assistant.service
echo "---"
git add skills.py
git commit -m "Mails : detection ajout/retrait expediteur tolerante au vocal (12/07/2026)

Probleme : 'mail ajoute banque populaire' (vocal, souvent mal transcrit)
ne matchait pas 'mails ajouter ' rigide -> tombait en lecture mails.

Fix : detection par intention (mot proche de mail + mot d action ajoute/
joute/rajoute/retire...), ordre libre, tolerante aux fautes de transcription.
Extraction adresse par regex (domaine/email) ou mots apres l action.
Teste : 5 formulations vocales approximatives OK." 2>&1 | tail -3
git push 2>&1 | tail -2
