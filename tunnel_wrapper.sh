#!/bin/bash
# Wrapper: lance le tunnel et publie l'URL sur ntfy.sh
TOPIC="assistantia-deploy-8501-secret"

cloudflared tunnel --url http://localhost:8501 2>&1 | while read line; do
    echo "$line"
    URL=$(echo "$line" | grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com')
    if [ -n "$URL" ]; then
        echo "$URL" > /home/lolufe/assistant/tunnel_url.txt
        curl -s -d "$URL" ntfy.sh/$TOPIC > /dev/null
        echo ">>> URL publiée: $URL"
    fi
done
