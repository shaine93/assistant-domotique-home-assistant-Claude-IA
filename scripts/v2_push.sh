#!/bin/bash
exec > /home/lolufe/assistant/scripts/e2e_test.log 2>&1
sudo -n /bin/systemctl restart assistant.service
sleep 3
systemctl status assistant.service --no-pager | head -5
