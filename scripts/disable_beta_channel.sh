#!/usr/bin/env bash
# Désactive le canal bêta-testeur

set -euo pipefail

BLUE="\033[1;34m"; GREEN="\033[1;32m"; NC="\033[0m"
info() { echo -e "${BLUE}ℹ${NC} $*"; }
ok()   { echo -e "${GREEN}✓${NC} $*"; }

if [ "$EUID" -ne 0 ]; then
    info "Escalade sudo..."
    exec sudo -E bash "$0" "$@"
fi

for svc in assistantia-deploy.service assistantia-tunnel.service; do
    if systemctl is-enabled "$svc" >/dev/null 2>&1 || systemctl is-active "$svc" >/dev/null 2>&1; then
        info "Arrêt de $svc"
        systemctl stop "$svc"    || true
        systemctl disable "$svc" || true
        rm -f "/etc/systemd/system/$svc"
        ok "$svc supprimé"
    fi
done

# Tuer les orphans
pkill -TERM -f "tunnel_wrapper.sh" 2>/dev/null || true
pkill -TERM -f "cloudflared tunnel --url http://localhost:8501" 2>/dev/null || true
sleep 2
pkill -KILL -f "tunnel_wrapper.sh" 2>/dev/null || true
pkill -KILL -f "cloudflared tunnel --url http://localhost:8501" 2>/dev/null || true

systemctl daemon-reload
ok "Mode bêta-testeur désactivé"
echo
echo "AssistantIA continue de tourner normalement."
echo "Vos données (config.json, memory.db) sont intactes."
