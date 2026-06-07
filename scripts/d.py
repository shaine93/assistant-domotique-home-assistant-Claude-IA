#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/lolufe/assistant')
from shared import veille_integrite_au_demarrage
print(veille_integrite_au_demarrage(), flush=True)
