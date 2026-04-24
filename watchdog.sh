#!/bin/bash
# Watchdog AssistantIA — vérifie deploy_server local + tunnel externe
#
# Correction (24/04/2026) : le test local accepte maintenant 401 comme 200.
# Un 401 prouve que le deploy_server écoute et a traité la requête — il refuse
# juste l'auth manquante, ce qui est le comportement normal. L'ancienne
# version utilisait 'curl -sf' qui échouait sur tout HTTP >= 400, ce qui
# provoquait un restart en boucle du deploy_server toutes les 2 min.

LOG="/home/lolufe/assistant/watchdog.log"
URL_FILE="/home/lolufe/assistant/tunnel_url.txt"
STATE_FILE="/home/lolufe/assistant/watchdog.state"

log() { echo "[$(date -Iseconds)] $*" >> "$LOG"; }

# Teste une URL : renvoie le code HTTP, ou "000" si injoignable
http_code() {
    curl -s -m 5 -o /dev/null -w "%{http_code}" "$1" 2>/dev/null
}

# Un service deploy_server "vivant" retourne 200 (ping avec auth) ou 401 (sans auth).
# Tout autre code ou timeout = KO.
is_alive() {
    local code="$1"
    [ "$code" = "200" ] || [ "$code" = "401" ]
}

# ── 1. Test deploy_server local ──────────────────────────────────────
LOCAL_CODE=$(http_code "http://127.0.0.1:8501/ping")
if ! is_alive "$LOCAL_CODE"; then
    log "❌ deploy_server local KO (HTTP=$LOCAL_CODE) → restart"
    sudo -n systemctl restart deploy_server.service
    echo "deploy_restarted=$(date -Iseconds)" > "$STATE_FILE"
    exit 0
fi

# ── 2. Test présence URL tunnel ──────────────────────────────────────
URL=$(cat "$URL_FILE" 2>/dev/null)
if [ -z "$URL" ]; then
    log "⚠️  pas d'URL dans $URL_FILE → restart tunnel"
    sudo -n systemctl restart cloudflared_tunnel.service
    echo "tunnel_restarted=$(date -Iseconds)" > "$STATE_FILE"
    exit 0
fi

# ── 3. Test ping via le tunnel externe ───────────────────────────────
TUNNEL_CODE=$(http_code "$URL/ping")
if ! is_alive "$TUNNEL_CODE"; then
    log "⚠️  tunnel KO (HTTP=$TUNNEL_CODE) sur $URL → restart"
    sudo -n systemctl restart cloudflared_tunnel.service
    echo "tunnel_restarted=$(date -Iseconds)" > "$STATE_FILE"
fi

# ── 4. Tronquer le log s'il dépasse 200KB ───────────────────────────
SIZE=$(stat -c %s "$LOG" 2>/dev/null || echo 0)
if [ "$SIZE" -gt 204800 ]; then
    tail -500 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi

exit 0
