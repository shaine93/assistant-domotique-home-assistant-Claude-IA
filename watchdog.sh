#!/bin/bash
# Watchdog AssistantIA — vérifie deploy_server local + tunnel externe
LOG="/home/lolufe/assistant/watchdog.log"
URL_FILE="/home/lolufe/assistant/tunnel_url.txt"
STATE_FILE="/home/lolufe/assistant/watchdog.state"

log() { echo "[$(date -Iseconds)] $*"; }

# 1. Test deploy_server local
if ! curl -sf -m 5 http://127.0.0.1:8501/ping >/dev/null 2>&1; then
    log "❌ deploy_server local KO → restart"
    sudo -n systemctl restart deploy_server.service
    echo "deploy_restarted=$(date -Iseconds)" > "$STATE_FILE"
    exit 0
fi

# 2. Test tunnel externe
URL=$(cat "$URL_FILE" 2>/dev/null)
if [ -z "$URL" ]; then
    log "⚠️  pas d'URL dans $URL_FILE → restart tunnel"
    sudo -n systemctl restart cloudflared_tunnel.service
    exit 0
fi

# 3. Test ping via le tunnel (curl ne suit pas l'auth donc on accepte 401)
HTTP=$(curl -s -m 8 -o /dev/null -w "%{http_code}" "$URL/ping" 2>/dev/null)
if [ "$HTTP" != "401" ] && [ "$HTTP" != "200" ]; then
    log "⚠️  tunnel KO (HTTP=$HTTP) sur $URL → restart"
    sudo -n systemctl restart cloudflared_tunnel.service
    echo "tunnel_restarted=$(date -Iseconds)" > "$STATE_FILE"
fi

# Tronquer le log s'il dépasse 200KB
SIZE=$(stat -c %s "$LOG" 2>/dev/null || echo 0)
if [ "$SIZE" -gt 204800 ]; then
    tail -500 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi
