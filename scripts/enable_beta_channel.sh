#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# Active le canal bêta-testeur : deploy_server + tunnel Cloudflare
# ⚠️ Lisez docs/BETA_CHANNEL.md AVANT de lancer ce script
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BLUE="\033[1;34m"; GREEN="\033[1;32m"; YELLOW="\033[1;33m"; RED="\033[1;31m"; NC="\033[0m"
info() { echo -e "${BLUE}ℹ${NC} $*"; }
ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC} $*"; }
fail() { echo -e "${RED}✗${NC} $*" >&2; exit 1; }

# ── Confirmation explicite ─────────────────────────────────────────
cat <<WARN

${YELLOW}════════════════════════════════════════════════════════════${NC}
  ${BOLD:-}Vous êtes sur le point d'activer le mode bêta-testeur.${NC}
  Cela expose votre installation à des patches distants.
  Lisez docs/BETA_CHANNEL.md si ce n'est pas déjà fait.
${YELLOW}════════════════════════════════════════════════════════════${NC}

WARN
read -r -p "Continuer ? tapez 'OUI' en majuscules : " confirm
[ "$confirm" = "OUI" ] || fail "Annulé"

# ── Pré-requis ─────────────────────────────────────────────────────
[ -f "${INSTALL_DIR}/config.json" ]       || fail "config.json manquant — lancez ./install.sh d'abord"
[ -f "${INSTALL_DIR}/deploy_server.py" ]  || fail "deploy_server.py manquant dans $INSTALL_DIR"
command -v cloudflared >/dev/null 2>&1    || fail "cloudflared non installé — voir docs/BETA_CHANNEL.md"
command -v jq          >/dev/null 2>&1    || fail "jq non installé (sudo apt install jq)"

USER_NAME="${SUDO_USER:-$USER}"
DEPLOY_SECRET=$(jq -r .deploy_secret "${INSTALL_DIR}/config.json")
[ -n "$DEPLOY_SECRET" ] && [ "$DEPLOY_SECRET" != "null" ] || fail "deploy_secret manquant dans config.json"

# Topic ntfy = préfixe + hash court du secret (déterministe par installation)
TOPIC_SUFFIX=$(echo -n "$DEPLOY_SECRET" | sha256sum | cut -c1-16)
NTFY_TOPIC="assistantia-beta-${TOPIC_SUFFIX}"

info "Topic ntfy pour cette installation : ${BOLD:-}${NTFY_TOPIC}${NC}"

# ── Escalade sudo si nécessaire ────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
    info "Le script a besoin de sudo pour installer les services systemd"
    exec sudo -E INSTALL_DIR="$INSTALL_DIR" NTFY_TOPIC="$NTFY_TOPIC" USER_NAME="$USER_NAME" bash "$0" --sudo-phase
fi

# ── Phase sudo : installer les services ────────────────────────────

# 1. Wrapper tunnel
cat > "${INSTALL_DIR}/tunnel_wrapper.sh" <<WRAPPER
#!/bin/bash
# Wrapper Cloudflare Tunnel : capture URL, publie sur ntfy
set -u
TOPIC="${NTFY_TOPIC}"
URL_FILE="${INSTALL_DIR}/tunnel_url.txt"

TMP=\$(mktemp)
cloudflared tunnel --url http://localhost:8501 > "\$TMP" 2>&1 &
CFD=\$!

cleanup() { kill -TERM \$CFD 2>/dev/null || true; wait \$CFD 2>/dev/null; rm -f "\$TMP"; exit 0; }
trap cleanup TERM INT

tail -f "\$TMP" &
TAIL=\$!

for i in \$(seq 1 60); do
    URL=\$(grep -oE 'https://[a-z0-9-]+\\.trycloudflare\\.com' "\$TMP" 2>/dev/null | head -1)
    if [ -n "\$URL" ]; then
        echo "\$URL" > "\$URL_FILE"
        echo ">>> URL_PUBLISHED: \$URL"
        curl -s -m 10 -d "\$URL" "https://ntfy.sh/\$TOPIC" >/dev/null
        break
    fi
    kill -0 \$CFD 2>/dev/null || { kill \$TAIL 2>/dev/null; rm -f "\$TMP"; exit 1; }
    sleep 0.5
done

wait \$CFD
EXIT=\$?
kill \$TAIL 2>/dev/null
rm -f "\$TMP"
exit \$EXIT
WRAPPER
chmod +x "${INSTALL_DIR}/tunnel_wrapper.sh"
chown "${USER_NAME}:${USER_NAME}" "${INSTALL_DIR}/tunnel_wrapper.sh"
ok "Wrapper tunnel créé"

# 2. Unit file deploy_server
cat > /etc/systemd/system/assistantia-deploy.service <<UNIT
[Unit]
Description=AssistantIA Deploy Server (beta channel)
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=${USER_NAME}
WorkingDirectory=${INSTALL_DIR}
ExecStart=/usr/bin/python3 -u ${INSTALL_DIR}/deploy_server.py
Restart=always
RestartSec=3
StandardOutput=append:${INSTALL_DIR}/deploy_server.log
StandardError=append:${INSTALL_DIR}/deploy_server.log
KillMode=control-group
TimeoutStopSec=10

[Install]
WantedBy=multi-user.target
UNIT

# 3. Unit file tunnel
cat > /etc/systemd/system/assistantia-tunnel.service <<UNIT
[Unit]
Description=AssistantIA Cloudflare Tunnel (beta channel)
After=network-online.target assistantia-deploy.service
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=${USER_NAME}
WorkingDirectory=${INSTALL_DIR}
ExecStart=/bin/bash ${INSTALL_DIR}/tunnel_wrapper.sh
Restart=always
RestartSec=5
StandardOutput=append:${INSTALL_DIR}/tunnel.log
StandardError=append:${INSTALL_DIR}/tunnel.log
KillMode=control-group
TimeoutStopSec=15

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable assistantia-deploy.service assistantia-tunnel.service
systemctl start  assistantia-deploy.service
sleep 2
systemctl start  assistantia-tunnel.service

ok "Services installés et démarrés"

# Attendre l'URL
info "Attente de la première URL tunnel (max 30s)..."
for i in $(seq 1 30); do
    if [ -f "${INSTALL_DIR}/tunnel_url.txt" ]; then
        URL=$(cat "${INSTALL_DIR}/tunnel_url.txt")
        [ -n "$URL" ] && break
    fi
    sleep 1
done

echo
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Mode bêta-testeur activé${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo
echo "  URL tunnel actuelle : ${URL:-(pas encore publiée)}"
echo "  Topic ntfy          : ${NTFY_TOPIC}"
echo
echo "  📤 Communiquez ce topic à Philippe (Telegram, email, forum)"
echo "     pour qu'il puisse vous pousser des patches."
echo
echo "  Désactiver : ./scripts/disable_beta_channel.sh"
echo
