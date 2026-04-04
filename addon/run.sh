#!/usr/bin/with-contenv bashio

# Read config from HA add-on options
CONFIG_PATH="/app/config.json"

TELEGRAM_TOKEN=$(bashio::config 'telegram_token')
TELEGRAM_CHAT_ID=$(bashio::config 'telegram_chat_id')
HA_TOKEN=$(bashio::config 'ha_token')
ANTHROPIC_KEY=$(bashio::config 'anthropic_api_key')
SMS_METHOD=$(bashio::config 'sms_method')
FREE_USER=$(bashio::config 'free_mobile_user')
FREE_PASS=$(bashio::config 'free_mobile_pass')
BUDGET=$(bashio::config 'anthropic_monthly_budget_usd')

# Build config.json
cat > "$CONFIG_PATH" << EOF
{
  "telegram_token": "${TELEGRAM_TOKEN}",
  "telegram_chat_id": "${TELEGRAM_CHAT_ID}",
  "ha_url": "http://supervisor/core",
  "ha_token": "${HA_TOKEN}",
  "anthropic_api_key": "${ANTHROPIC_KEY}",
  "sms_method": "${SMS_METHOD}",
  "free_mobile_user": "${FREE_USER}",
  "free_mobile_pass": "${FREE_PASS}",
  "anthropic_monthly_budget_usd": ${BUDGET}
}
EOF

bashio::log.info "AssistantIA Domotique starting..."

cd /app
exec python3 assistant.py
