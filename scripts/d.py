#!/usr/bin/env python3
import sys, logging
logging.disable(logging.WARNING)
sys.path.insert(0, '/home/lolufe/assistant')
from shared import mem_get, mem_set
import skills, json

fake_msg = 'TypeError: test ciblage | File "/home/lolufe/assistant/skills.py", line 232'
res = skills._proposer_guerison('test_ciblage_skills', fake_msg, nb_occurrences=3)
print('RES=' + str(res))
pending = mem_get('guerison_pending')
if pending:
    p = json.loads(pending)
    print('TARGET=' + str(p.get('target')))
    print('COUT=' + str(p.get('cout_eur')))
mem_set('guerison_pending', '')
print('PURGE_OK')
