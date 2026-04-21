#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# AssistantIA Domotique — Installation interactive
# ═══════════════════════════════════════════════════════════════════
# Usage  : ./install.sh [--non-interactive] [--from-env]
# Requis : Python 3.10+, curl, jq
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Couleurs ──────────────────────────────────────────────────────────
# On utilise $'...' pour que les séquences ANSI soient interprétées dès
# l'assignation — elles fonctionnent ainsi avec cat, printf, echo.
BLUE=$'\033[1;34m'; GREEN=$'\033[1;32m'; YELLOW=$'\033[1;33m'
RED=$'\033[1;31m'; NC=$'\033[0m'; BOLD=$'\033[1m'

info()  { printf '%sℹ %s%s\n' "$BLUE" "$NC" "$*"; }
ok()    { printf '%s✓ %s%s\n' "$GREEN" "$NC" "$*"; }
warn()  { printf '%s⚠ %s%s\n' "$YELLOW" "$NC" "$*"; }
fail()  { printf '%s✗ %s%s\n' "$RED" "$NC" "$*" >&2; exit 1; }
title() { printf '\n%s═══ %s ═══%s\n' "$BOLD" "$*" "$NC"; }

# ── Répertoires ───────────────────────────────────────────────────────
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${INSTALL_DIR}/config.json"
ENV_FILE="${INSTALL_DIR}/.env"

# ── Flags ─────────────────────────────────────────────────────────────
NON_INTERACTIVE=0
FROM_ENV=0
for arg in "$@"; do
    case "$arg" in
        --non-interactive) NON_INTERACTIVE=1 ;;
        --from-env)        FROM_ENV=1 ;;
        --help|-h)
            sed -n '3,8p' "$0"; exit 0 ;;
    esac
done

# ═══════════════════════════════════════════════════════════════════
# 1. Pré-requis système
# ═══════════════════════════════════════════════════════════════════
title "Vérification des pré-requis"

check_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        fail "Commande manquante : $1 — installez-la avec : ${2:-$1}"
    fi
    ok "$1 trouvé : $(command -v "$1")"
}

check_cmd python3 "apt install python3"
check_cmd pip3    "apt install python3-pip"
check_cmd curl    "apt install curl"

# Python ≥ 3.10
PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    fail "Python $PY_VER détecté. Il faut au moins Python 3.10."
fi
ok "Python $PY_VER"

# jq recommandé (pour le mode bêta) mais pas bloquant
if ! command -v jq >/dev/null 2>&1; then
    warn "jq non trouvé (optionnel, utile pour le mode bêta). Installez-le : apt install jq"
fi

# ═══════════════════════════════════════════════════════════════════
# 2. Installation des dépendances Python
# ═══════════════════════════════════════════════════════════════════
title "Installation des dépendances Python"

if [ -f "${INSTALL_DIR}/requirements.txt" ]; then
    info "Installation depuis requirements.txt..."
    pip3 install --user --upgrade -r "${INSTALL_DIR}/requirements.txt" 2>&1 | grep -E "Successfully|already|error" || true
    ok "Dépendances installées"
else
    warn "requirements.txt introuvable, installation manuelle..."
    pip3 install --user --upgrade anthropic requests matplotlib
fi

# ═══════════════════════════════════════════════════════════════════
# 3. Récupération des credentials
# ═══════════════════════════════════════════════════════════════════
title "Configuration"

# Si config.json existe déjà, demander confirmation
if [ -f "$CONFIG_FILE" ]; then
    if [ "$NON_INTERACTIVE" -eq 1 ]; then
        info "config.json existe déjà (mode non-interactif), pas de modification"
        exit 0
    fi
    warn "config.json existe déjà."
    read -r -p "Écraser ? [y/N] " overwrite
    [ "${overwrite,,}" = "y" ] || { info "Conservation du config.json existant"; exit 0; }
fi

# Mode --from-env : lire depuis .env
if [ "$FROM_ENV" -eq 1 ]; then
    [ -f "$ENV_FILE" ] || fail "$ENV_FILE introuvable (mode --from-env)"
    info "Chargement depuis $ENV_FILE..."
    # shellcheck disable=SC1090
    set -a; source "$ENV_FILE"; set +a
fi

# Fonction pour demander une valeur avec défaut
ask() {
    local varname="$1" prompt="$2" default="${3:-}" secret="${4:-0}"
    local current="${!varname:-$default}"
    local value=""
    if [ "$NON_INTERACTIVE" -eq 1 ] || [ "$FROM_ENV" -eq 1 ]; then
        value="$current"
    elif [ "$secret" = "1" ]; then
        read -r -s -p "  $prompt ${current:+[masqué, Entrée pour garder] }: " value
        echo
        [ -z "$value" ] && value="$current"
    else
        read -r -p "  $prompt${current:+ [$current]}: " value
        [ -z "$value" ] && value="$current"
    fi
    printf -v "$varname" '%s' "$value"
}

# ─── REQUIS ───
echo
info "Credentials REQUIS (voir README pour les obtenir)"

ask TELEGRAM_TOKEN     "Telegram Bot Token (via @BotFather)" "${TELEGRAM_TOKEN:-}" 1
[ -n "$TELEGRAM_TOKEN" ] || fail "TELEGRAM_TOKEN vide"

ask HA_URL             "URL Home Assistant"                 "${HA_URL:-http://192.168.1.XX:8123}"
[ -n "$HA_URL" ] || fail "HA_URL vide"

ask HA_TOKEN           "HA Long-Lived Token"                "${HA_TOKEN:-}" 1
[ -n "$HA_TOKEN" ] || fail "HA_TOKEN vide"

ask ANTHROPIC_API_KEY  "Anthropic API Key"                  "${ANTHROPIC_API_KEY:-}" 1
[ -n "$ANTHROPIC_API_KEY" ] || fail "ANTHROPIC_API_KEY vide"

# ─── OPTIONNEL ───
echo
info "Options (Entrée pour valeurs par défaut)"

ask ANTHROPIC_MONTHLY_BUDGET_USD "Budget mensuel USD" "${ANTHROPIC_MONTHLY_BUDGET_USD:-10}"
ask SMS_METHOD                   "Méthode code sécurité (free_mobile|ha_notify|email)" "${SMS_METHOD:-ha_notify}"

FREE_MOBILE_USER="${FREE_MOBILE_USER:-}"
FREE_MOBILE_PASS="${FREE_MOBILE_PASS:-}"
SMTP_HOST="${SMTP_HOST:-smtp.gmail.com}"
SMTP_PORT="${SMTP_PORT:-587}"
SMTP_USER="${SMTP_USER:-}"
SMTP_PASS="${SMTP_PASS:-}"
MAIL_DEST="${MAIL_DEST:-}"

case "$SMS_METHOD" in
    free_mobile)
        ask FREE_MOBILE_USER "Free Mobile identifiant" "$FREE_MOBILE_USER"
        ask FREE_MOBILE_PASS "Free Mobile clé"         "$FREE_MOBILE_PASS" 1
        ;;
    email)
        ask SMTP_HOST "SMTP host"     "$SMTP_HOST"
        ask SMTP_PORT "SMTP port"     "$SMTP_PORT"
        ask SMTP_USER "SMTP user"     "$SMTP_USER"
        ask SMTP_PASS "SMTP password" "$SMTP_PASS" 1
        ask MAIL_DEST "Email destinataire" "$MAIL_DEST"
        ;;
    ha_notify) : ;;
    *) warn "SMS_METHOD inconnue: $SMS_METHOD — utilisation de ha_notify"; SMS_METHOD=ha_notify ;;
esac

# ═══════════════════════════════════════════════════════════════════
# 4. Génération config.json
# ═══════════════════════════════════════════════════════════════════
title "Génération config.json"

python3 - <<PYEOF
import json, os, secrets
cfg = {
    "telegram_token":               os.environ.get("TELEGRAM_TOKEN",""),
    "telegram_chat_id":             "",
    "ha_url":                       os.environ.get("HA_URL",""),
    "ha_token":                     os.environ.get("HA_TOKEN",""),
    "anthropic_api_key":            os.environ.get("ANTHROPIC_API_KEY",""),
    "free_mobile_user":             os.environ.get("FREE_MOBILE_USER",""),
    "free_mobile_pass":             os.environ.get("FREE_MOBILE_PASS",""),
    "smtp_host":                    os.environ.get("SMTP_HOST",""),
    "smtp_port":                    int(os.environ.get("SMTP_PORT","587") or 587),
    "smtp_user":                    os.environ.get("SMTP_USER",""),
    "smtp_pass":                    os.environ.get("SMTP_PASS",""),
    "mail_dest":                    os.environ.get("MAIL_DEST",""),
    "sms_method":                   os.environ.get("SMS_METHOD","ha_notify"),
    "poll_interval_sec":            2,
    "audit_interval_sec":           1800,
    "anthropic_monthly_budget_usd": int(os.environ.get("ANTHROPIC_MONTHLY_BUDGET_USD","10") or 10),
    "deploy_secret":                secrets.token_hex(32),
}
with open("${CONFIG_FILE}", "w") as f:
    json.dump(cfg, f, indent=2)
os.chmod("${CONFIG_FILE}", 0o600)
print(f"✓ config.json écrit ({len(cfg)} clés, permissions 600)")
PYEOF

export TELEGRAM_TOKEN HA_URL HA_TOKEN ANTHROPIC_API_KEY
export FREE_MOBILE_USER FREE_MOBILE_PASS SMTP_HOST SMTP_PORT SMTP_USER SMTP_PASS MAIL_DEST
export SMS_METHOD ANTHROPIC_MONTHLY_BUDGET_USD

# ═══════════════════════════════════════════════════════════════════
# 5. Test des credentials
# ═══════════════════════════════════════════════════════════════════
title "Test des credentials"

# HA
info "Test Home Assistant..."
if curl -sf -m 10 -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/" >/dev/null 2>&1; then
    ok "Home Assistant : connexion OK"
else
    warn "Home Assistant injoignable ou token invalide (vous pourrez corriger dans config.json)"
fi

# Telegram
info "Test Telegram..."
if curl -sf -m 10 "https://api.telegram.org/bot$TELEGRAM_TOKEN/getMe" >/dev/null 2>&1; then
    ok "Telegram : bot valide"
else
    warn "Telegram token invalide (vous pourrez corriger dans config.json)"
fi

# ═══════════════════════════════════════════════════════════════════
# 6. Prochaines étapes
# ═══════════════════════════════════════════════════════════════════
title "Installation terminée"

cat <<INFO

  ${BOLD}Prochaines étapes :${NC}

  1. Lancer le bot :
     ${BLUE}python3 assistant.py${NC}

  2. Envoyer un message quelconque à votre bot Telegram
     → le chat_id se détecte automatiquement au premier message

  3. Le bot vous guide pour la suite (questionnaire appareils, tarif, etc.)

  ${BOLD}Déploiement en service :${NC}
    ${BLUE}./scripts/install_systemd.sh${NC}       Linux/Pi/VM
    ${BLUE}docker compose up -d${NC}                Docker
    Voir docs/INSTALL.md pour HA Add-on

  ${BOLD}Aide :${NC}  /aide dans Telegram     │     ${BOLD}Docs :${NC}  docs/

INFO
