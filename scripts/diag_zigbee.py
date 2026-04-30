#!/usr/bin/env python3
import subprocess
print(subprocess.run(["bash","-c","#!/bin/bash
cd /home/lolufe/assistant
echo "--- git status ---"
git status -s
echo ""
echo "--- git log oneline derniers 8 ---"
git log --oneline -8
echo ""
echo "--- Comparaison local vs origin ---"
git fetch origin 2>&1 | tail -2
git log HEAD..origin/main --oneline
echo "(si vide = local à jour avec origin)"
echo ""
echo "--- Date dernière modif fichiers clés ---"
ls -la --time-style=long-iso skills.py shared.py assistant.py LECONS.md README.md Cahier_des_Charges.md 2>/dev/null
"],capture_output=True,text=True).stdout)