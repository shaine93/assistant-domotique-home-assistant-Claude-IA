#!/bin/bash
exec > /home/lolufe/assistant/scripts/e2e_test.log 2>&1
python3 /home/lolufe/assistant/scripts/diag_zigbee.py
