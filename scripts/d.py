#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/lolufe/assistant')
from shared import *
from skills import role_get_all
from config import ROLES_DEFINIS

roles = role_get_all()
print(f'role_get_all() retourne {len(roles)} roles:', flush=True)
for k in roles.keys():
    print(f'  - {k}', flush=True)

print(f'\nROLES_DEFINIS contient {len(ROLES_DEFINIS)} roles:', flush=True)
for k in ROLES_DEFINIS.keys():
    in_roles = '✅' if k in roles else '❌'
    print(f'  {in_roles} {k}', flush=True)

print(f'\n=== Calcul ===')
print(f'len(roles) = {len(roles)}')
print(f'len(ROLES_DEFINIS) = {len(ROLES_DEFINIS)}')
print(f'non_assignes = len(ROLES_DEFINIS) - len(roles) = {len(ROLES_DEFINIS) - len(roles)}')
