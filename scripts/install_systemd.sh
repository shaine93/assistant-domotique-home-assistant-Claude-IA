#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# Déploie AssistantIA comme service systemd (Linux natif / Pi / VM)
# Nécessite sudo pour installer /etc/systemd/system/assistantia.service
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="assistantia.service"
TEMPLATE="${INSTALL_DIR}/assistantia.service.template"
TARGET="/etc/systemd/system/${SERVICE_NAME}"
USER_NAME="${SUDO_USER:-$USER}"

BLUE="\033[1;34m"; GREEN="\033[1;32m"; RED="\033[1;31m"; NC="\033[0m"
info() { echo -e "${BLUE}ℹ${NC} $*"; }
ok()   { echo -e "${GREEN}✓${NC} $*"; }
fail() { echo -e "${RED}✗${NC} $*" >&2; exit 1; }

[ -f "$TEMPLATE" ]                            || fail "Template introuvable : $TEMPLATE"
[ -f "${INSTALL_DIR}/assistant.py" ]          || fail "assistant.py introuvable dans $INSTALL_DIR"
[ -f "${INSTALL_DIR}/config.json" ]           || fail "config.json manquant — lancez ./install.sh d'abord"

if [ "$EUID" -ne 0 ]; then
    info "Ce script doit être lancé avec sudo (pour écrire dans /etc/systemd/system/)"
    exec sudo -E "$0" "$@"
fi

info "Installation du service pour l'utilisateur : $USER_NAME"
info "Dossier d'installation : $INSTALL_DIR"

# Générer le fichier service à partir du template
sed -e "s|__USER__|${USER_NAME}|g" \
    -e "s|__INSTALL_DIR__|${INSTALL_DIR}|g" \
    "$TEMPLATE" > "$TARGET"
chmod 644 "$TARGET"
ok "Service installé : $TARGET"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
ok "Service activé au boot"

info "Démarrage du service..."
systemctl start "$SERVICE_NAME"
sleep 2

if systemctl is-active --quiet "$SERVICE_NAME"; then
    ok "Service actif : $(systemctl is-active $SERVICE_NAME)"
else
    fail "Service n'a pas démarré. Logs : journalctl -u $SERVICE_NAME -n 30"
fi

echo
echo "Commandes utiles :"
echo "  sudo systemctl status  $SERVICE_NAME    # État"
echo "  sudo systemctl restart $SERVICE_NAME    # Redémarrer"
echo "  sudo systemctl stop    $SERVICE_NAME    # Arrêter"
echo "  sudo journalctl -u $SERVICE_NAME -f     # Logs live"
echo "  tail -f ${INSTALL_DIR}/assistant.log    # Logs applicatifs"
