#!/usr/bin/with-contenv bashio

# ═══ AssistantIA Domotique — HA Add-on ═══
# Le Supervisor fournit l'URL HA + token automatiquement.
# L'utilisateur ne configure que Telegram + Anthropic.

CONFIG_DIR="/app"
CONFIG_FILE="${CONFIG_DIR}/config.json"
DB_FILE="${CONFIG_DIR}/memory.db"

# Récupérer les credentials depuis HA Supervisor (automatique)
HA_URL="http://supervisor/core"
HA_TOKEN="${SUPERVISOR_TOKEN}"

# Récupérer les options configurées par l'utilisateur
TELEGRAM_TOKEN=$(bashio::config 'telegram_token')
ANTHROPIC_KEY=$(bashio::config 'anthropic_api_key')
SMS_METHOD=$(bashio::config 'sms_method')
BUDGET=$(bashio::config 'anthropic_monthly_budget_usd')

# Générer config.json si absent ou si les credentials ont changé
if [ ! -f "${CONFIG_FILE}" ] || [ "$(jq -r .telegram_token ${CONFIG_FILE})" != "${TELEGRAM_TOKEN}" ]; then
    bashio::log.info "Génération de config.json..."
    cat > "${CONFIG_FILE}" << EOCFG
{
    "telegram_token": "${TELEGRAM_TOKEN}",
    "telegram_chat_id": "",
    "ha_url": "${HA_URL}",
    "ha_token": "${HA_TOKEN}",
    "anthropic_api_key": "${ANTHROPIC_KEY}",
    "sms_method": "${SMS_METHOD}",
    "poll_interval_sec": 2,
    "audit_interval_sec": 1800,
    "anthropic_monthly_budget_usd": ${BUDGET}
}
EOCFG
    bashio::log.info "Config générée — HA URL: ${HA_URL}"
fi

# Copier la DB persistante si elle existe dans /config
if [ -f "/config/assistantia/memory.db" ]; then
    cp /config/assistantia/memory.db "${DB_FILE}" 2>/dev/null || true
fi

# Lancer le Deploy Server en arrière-plan
bashio::log.info "Démarrage Deploy Server sur :8501..."
python3 deploy_server.py &

# Lancer le script principal
bashio::log.info "Démarrage AssistantIA Domotique..."
cd /app
python3 assistant.py

# Sauvegarder la DB en cas d'arrêt
mkdir -p /config/assistantia
cp "${DB_FILE}" /config/assistantia/memory.db 2>/dev/null || true
