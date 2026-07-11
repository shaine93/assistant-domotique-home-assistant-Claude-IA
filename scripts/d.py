#!/usr/bin/env python3
import sys, logging
logging.disable(logging.CRITICAL)
sys.path.insert(0, '/home/lolufe/assistant')
from shared import mem_set
mem_set('expediteurs_importants', '[]')
print('Liste nettoyee', flush=True)
