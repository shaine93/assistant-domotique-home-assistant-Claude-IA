#!/usr/bin/env python3
"""
STUB — sync_to_telegram.py
==========================
Ce fichier est un stub créé pour stopper le spam dans sync.log
("No such file or directory") causé par un cron orphelin.

ACTION ROOT-CAUSE REQUISE (côté SSH) :
    crontab -e
    → chercher la ligne qui appelle sync_to_telegram.py
    → la supprimer
    → puis rm ce fichier

Créé le 2026-04-18 17:44:05
"""
import sys, os
# Log pour tracer combien de fois le cron tourne encore
try:
    with open('/home/lolufe/assistant/sync.log', 'a') as f:
        from datetime import datetime
        f.write(f"{datetime.now().isoformat()}: stub sync_to_telegram.py appelé — nettoyer le cron\n")
except Exception:
    pass
sys.exit(0)
