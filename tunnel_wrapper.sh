#!/bin/bash
# Wrapper systemd-friendly : exec cloudflared, capture URL, publie sur ntfy.
# IMPORTANT : ce wrapper N'écrit PAS sur tunnel.log (systemd s'en occupe via StdOut).
set -u
TOPIC="assistantia-deploy-8501-secret"
URL_FILE="/home/lolufe/assistant/tunnel_url.txt"

# Lance cloudflared en arrière-plan, redirige sa sortie vers stdout du wrapper
TMP_LOG=$(mktemp)
cloudflared tunnel --url http://localhost:8501 > "$TMP_LOG" 2>&1 &
CFD_PID=$!

# Cleanup propre quand on meurt (SIGTERM de systemd)
cleanup() {
    kill -TERM "$CFD_PID" 2>/dev/null || true
    wait "$CFD_PID" 2>/dev/null
    rm -f "$TMP_LOG"
    exit 0
}
trap cleanup TERM INT

# Tee le tmp_log vers stdout en arrière-plan pour que systemd le voie
tail -f "$TMP_LOG" &
TAIL_PID=$!

# Attendre l'URL (max 30s)
URL=""
for i in $(seq 1 60); do
    URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$TMP_LOG" 2>/dev/null | head -1)
    if [ -n "$URL" ]; then
        echo "$URL" > "$URL_FILE"
        echo ">>> URL_PUBLISHED: $URL"
        curl -s -m 10 -d "$URL" "https://ntfy.sh/$TOPIC" >/dev/null
        break
    fi
    # Si cloudflared meurt prématurément, on sort
    if ! kill -0 "$CFD_PID" 2>/dev/null; then
        echo ">>> ERREUR: cloudflared est mort avant publication de l'URL"
        kill "$TAIL_PID" 2>/dev/null
        rm -f "$TMP_LOG"
        exit 1
    fi
    sleep 0.5
done

if [ -z "$URL" ]; then
    echo ">>> ERREUR: pas d'URL après 30s"
fi

# On reste vivant tant que cloudflared tourne
wait "$CFD_PID"
EXIT=$?
kill "$TAIL_PID" 2>/dev/null
rm -f "$TMP_LOG"
exit "$EXIT"
