#!/usr/bin/with-contenv bashio
# ═══ AssistantIA Domotique — HA Add-on ═══
# Le Supervisor fournit l'URL HA + token automatiquement.
# L'utilisateur configure telegram_token + anthropic_api_key.

set -e

APP_DIR="/app"
CONFIG_DIR="/config/assistantia"
CONFIG_FILE="${CONFIG_DIR}/config.json"
DB_FILE="${CONFIG_DIR}/memory.db"

mkdir -p "${CONFIG_DIR}"

# Credentials HA fournis par le Supervisor
HA_URL="http://supervisor/core"
HA_TOKEN="${SUPERVISOR_TOKEN}"

# Options utilisateur
TELEGRAM_TOKEN=$(bashio::config 'telegram_token')
ANTHROPIC_KEY=$(bashio::config 'anthropic_api_key')
SMS_METHOD=$(bashio::config 'sms_method')
BUDGET=$(bashio::config 'anthropic_monthly_budget_usd')
ENABLE_DEPLOY=$(bashio::config 'enable_deploy_server')

# Validation minimale
if [ -z "${TELEGRAM_TOKEN}" ] || [ -z "${ANTHROPIC_KEY}" ]; then
    bashio::log.fatal "telegram_token et anthropic_api_key sont requis"
    exit 1
fi

# Générer config.json si absent ou credentials modifiés
NEED_GEN=1
if [ -f "${CONFIG_FILE}" ]; then
    CURRENT_TOKEN=$(jq -r .telegram_token "${CONFIG_FILE}" 2>/dev/null || echo "")
    if [ "${CURRENT_TOKEN}" = "${TELEGRAM_TOKEN}" ]; then
        NEED_GEN=0
    fi
fi

if [ "${NEED_GEN}" = "1" ]; then
    bashio::log.info "Génération config.json..."
    # Secret HMAC unique pour cette installation
    DEPLOY_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")

    jq -n \
        --arg telegram "${TELEGRAM_TOKEN}" \
        --arg haurl    "${HA_URL}" \
        --arg hatoken  "${HA_TOKEN}" \
        --arg anth     "${ANTHROPIC_KEY}" \
        --arg sms      "${SMS_METHOD}" \
        --arg secret   "${DEPLOY_SECRET}" \
        --argjson budget "${BUDGET}" \
        '{
            telegram_token: $telegram,
            telegram_chat_id: "",
            ha_url: $haurl,
            ha_token: $hatoken,
            anthropic_api_key: $anth,
            sms_method: $sms,
            poll_interval_sec: 2,
            audit_interval_sec: 1800,
            anthropic_monthly_budget_usd: $budget,
            deploy_secret: $secret,
            free_mobile_user: "",
            free_mobile_pass: "",
            smtp_host: "",
            smtp_port: 587,
            smtp_user: "",
            smtp_pass: "",
            mail_dest: ""
        }' > "${CONFIG_FILE}"
    chmod 600 "${CONFIG_FILE}"
    bashio::log.info "config.json généré (HA URL: ${HA_URL})"
fi

# Lier config.json et memory.db depuis /config vers /app (persistance)
ln -sf "${CONFIG_FILE}" "${APP_DIR}/config.json"
if [ -f "${DB_FILE}" ]; then
    ln -sf "${DB_FILE}" "${APP_DIR}/memory.db"
fi

cd "${APP_DIR}"

# Deploy server (opt-in)
if [ "${ENABLE_DEPLOY}" = "true" ]; then
    bashio::log.warning "⚠️  Deploy server ACTIVÉ (mode bêta-testeur)"
    bashio::log.warning "    Voir docs/BETA_CHANNEL.md — expose un port HTTP pour patches distants"
    python3 -u deploy_server.py &
fi

# Script principal
bashio::log.info "Démarrage AssistantIA Domotique..."
exec python3 -u assistant.py
