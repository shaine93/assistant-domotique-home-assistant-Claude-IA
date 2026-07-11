#!/bin/bash
exec > /home/lolufe/assistant/scripts/e2e_test.log 2>&1
cd /home/lolufe/assistant
git add skills.py
git commit -m "Mails : liste d'expediteurs importants definie par Philippe (12/07/2026)

- Philippe definit ses expediteurs importants (banque, employeur, avocat...)
  stockes dans mem 'expediteurs_importants'
- cmd_mails marque d'office ces mails en prioritaires (bloc en tete),
  Claude ne trie que le reste
- Commandes : 'mails ajouter X', 'mails retirer X', 'mails liste'
- Affiche desormais TOUS les mails classes (plus de 'rien important' dans le vide)
- Fix : gestion du cas ou tous les mails sont prioritaires (pas d appel Claude)" 2>&1 | tail -3
git push 2>&1 | tail -2
