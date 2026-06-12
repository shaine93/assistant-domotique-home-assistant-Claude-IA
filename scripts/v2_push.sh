#!/bin/bash
exec > /home/lolufe/assistant/scripts/e2e_test.log 2>&1
cd /home/lolufe/assistant
python3 -c "import ast; ast.parse(open('shared.py').read()); print('OK syntaxe')"
echo "=== Restart ==="
sudo -n /bin/systemctl restart assistant.service
sleep 5
echo "=== Statut + log déverrouillage ==="
systemctl is-active assistant.service
tail -20 /home/lolufe/assistant/assistant.log | grep -iE "déverrouill|verrouill|canal" | tail -5
