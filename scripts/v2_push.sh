#!/bin/bash
exec > /home/lolufe/assistant/scripts/e2e_test.log 2>&1
TOKEN=$(python3 -c "import json; print(json.load(open('/home/lolufe/assistant/config.json'))['ha_token'])")
BASE=$(python3 -c "import json; print(json.load(open('/home/lolufe/assistant/config.json'))['ha_url'])")

echo "=== Trigger automation sonnette G410 ==="
curl -sk -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"automation.sonnette_g410_popup_mac_notif_xiaomi","skip_condition":true}' \
  "$BASE/api/services/automation/trigger"
echo ""
