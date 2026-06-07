#!/bin/bash
exec > /home/lolufe/assistant/scripts/e2e_test.log 2>&1
sudo -n /bin/systemctl restart assistant.service
sleep 5
echo "=== Status ==="
systemctl is-active assistant.service
echo ""
echo "=== Log demarrage ==="
tail -30 /home/lolufe/assistant/assistant.log | grep -iE "veille|integrite|RAS|fantome|demarrage|init"
