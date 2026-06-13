#!/bin/bash
exec > /home/lolufe/assistant/scripts/e2e_test.log 2>&1
cd /home/lolufe/assistant
git add deploy_server.py skills.py shared.py Cahier_des_Charges.md
git commit -m "Chantier fiabilite : patch multi-fichiers + consigne directrice CDC

CDC : ajout PRINCIPE DIRECTEUR consigne n1 'fiabilite croissante'
- detecter ses echecs, proposer corrections validables, apprendre,
  ne jamais contourner les garde-fous ni l humain dans la boucle.

deploy_server.py : /patch etendu aux 3 fichiers (assistant/skills/shared)
- parametre 'target', backup par fichier, _security_checks_for() avec
  elements requis specifiques a chaque fichier
- verification syntaxe AST avant ecriture (rejette tout patch qui
  casserait le code) => protege contre les boucles de crash

skills.py : mode proposition connecte au multi-fichiers
- _proposer_guerison detecte le fichier cible depuis le traceback
- pending stocke 'target', message Telegram affiche le fichier
- patch_apply passe 'target' au /patch

Tests valides : patch skills.py OK, rollback OK, cible invalide rejetee,
syntaxe cassee rejetee, ciblage auto skills.py depuis traceback OK." 2>&1 | tail -4
git push 2>&1 | tail -2
