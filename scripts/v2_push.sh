#!/bin/bash
exec > /home/lolufe/assistant/scripts/e2e_test.log 2>&1
echo "--- Installation websockets ---"
pip3 install websockets --break-system-packages 2>&1 | tail -3
python3 -c "import websockets; print('OK websockets', websockets.__version__)" 2>&1
