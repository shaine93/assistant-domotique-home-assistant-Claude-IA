#!/usr/bin/env python3
import sys, logging
logging.disable(logging.WARNING)
sys.path.insert(0, '/home/lolufe/assistant')
from shared import *
import skills

print('=== 1. Ajouter Amazon comme test ===', flush=True)
print(skills.traiter_message('mails ajouter amazon.fr'), flush=True)
print(flush=True)
print('=== 2. Voir la liste ===', flush=True)
print(skills.traiter_message('mails liste'), flush=True)
print(flush=True)
print('=== 3. Lecture mails (Amazon doit etre en prioritaire) ===', flush=True)
print(skills.cmd_mails(), flush=True)
print(flush=True)
print('=== 4. Retirer Amazon ===', flush=True)
print(skills.traiter_message('mails retirer amazon.fr'), flush=True)
