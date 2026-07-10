#!/bin/bash
# Watchdog AssistantIA — vérifie deploy_server local + tunnel externe.
# v2 (10/07/2026) : lit l'URL tunnel depuis ntfy (source de vérité) au lieu
# du fichier tunnel_url.txt qui n'était plus alimenté. Branché sur timer 3min.

LOG="/home/lolufe/assistant/watchdog.log"
NTFY="https://ntfy.sh/assistantia-deploy-8501-secret"
STATE_FILE="/home/lolufe/assistant/watchdog.state"

log() { echo "[$(date -Iseconds)] $*" >> "$LOG"; }

http_code() {
    curl -s -m 6 -o /dev/null -w "%{http_code}" "$1" 2>/dev/null
}

is_alive() {
    [ "$1" = "200" ] || [ "$1" = "401" ]
}

# ── 1. deploy_server local ───────────────────────────────────────────
LOCAL_CODE=$(http_code "http://127.0.0.1:8501/ping")
if ! is_alive "$LOCAL_CODE"; then
    log "❌ deploy_server local KO (HTTP=$LOCAL_CODE) → restart"
    sudo -n /bin/systemctl restart deploy_server.service
    echo "deploy_restarted=$(date -Iseconds)" > "$STATE_FILE"
    exit 0
fi

# ── 2. Récupérer l'URL tunnel depuis ntfy (dernier message 24h) ──────
URL=$(curl -s -m 8 "$NTFY/json?poll=1&since=24h" 2>/dev/null | tail -1 | grep -oE 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' | head -1)
if [ -z "$URL" ]; then
    log "⚠️  pas d'URL ntfy récente → restart tunnel (republiera l'URL)"
    sudo -n /bin/systemctl restart cloudflared_tunnel.service
    echo "tunnel_restarted_nourl=$(date -Iseconds)" > "$STATE_FILE"
    exit 0
fi

# ── 3. Test ping via le tunnel externe ───────────────────────────────
TUNNEL_CODE=$(http_code "$URL/ping")
if ! is_alive "$TUNNEL_CODE"; then
    log "⚠️  tunnel KO (HTTP=$TUNNEL_CODE) sur $URL → restart"
    sudo -n /bin/systemctl restart cloudflared_tunnel.service
    echo "tunnel_restarted=$(date -Iseconds)" > "$STATE_FILE"
    exit 0
fi

# ── 4. Tout va bien : marquer OK + tronquer log si > 200KB ───────────
echo "ok=$(date -Iseconds) tunnel=$URL" > "$STATE_FILE"
SIZE=$(stat -c %s "$LOG" 2>/dev/null || echo 0)
if [ "$SIZE" -gt 204800 ]; then
    tail -500 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi
exit 0
