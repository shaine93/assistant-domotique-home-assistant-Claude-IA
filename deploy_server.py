#!/usr/bin/env python3
# =============================================================================
# Deploy Server v2 — Mécanisme d'autonomie Claude
# Webhook indépendant de assistant.py
# Permet à Claude de : lire/écrire fichiers, patcher, redémarrer
# =============================================================================

import hashlib
import hmac
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

_LOG_LOCK = threading.Lock()

CONFIG_PATH = "/home/lolufe/assistant/config.json"
SCRIPT_PATH = "/home/lolufe/assistant/assistant.py"
ASSISTANT_DIR = "/home/lolufe/assistant"
VERSIONS_DIR = "/home/lolufe/assistant/versions"
DEPLOY_LOG = "/home/lolufe/assistant/deploy.log"
PORT = 8501

# ═══ INFRA ═══
TUNNEL_URL_FILE = "/home/lolufe/assistant/tunnel_url.txt"
NTFY_TOPIC = "assistantia-deploy-8501-secret"
HEARTBEAT_INTERVAL = 3600  # 1h — garde l'URL fraîche dans la fenêtre 24h de ntfy

# Unit files systemd (écrits par /infra_install)
DEPLOY_SERVER_UNIT = """[Unit]
Description=AssistantIA Deploy Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=lolufe
WorkingDirectory=/home/lolufe/assistant
ExecStart=/usr/bin/python3 /home/lolufe/assistant/deploy_server.py
Restart=always
RestartSec=3
StandardOutput=append:/home/lolufe/assistant/deploy_server.log
StandardError=append:/home/lolufe/assistant/deploy_server.log
KillMode=mixed
TimeoutStopSec=10

[Install]
WantedBy=multi-user.target
"""

CLOUDFLARED_TUNNEL_UNIT = """[Unit]
Description=Cloudflare Tunnel for AssistantIA Deploy Server
After=network-online.target deploy_server.service
Wants=network-online.target

[Service]
Type=simple
User=lolufe
WorkingDirectory=/home/lolufe/assistant
ExecStart=/bin/bash /home/lolufe/assistant/tunnel_wrapper.sh
Restart=always
RestartSec=5
StandardOutput=append:/home/lolufe/assistant/tunnel.log
StandardError=append:/home/lolufe/assistant/tunnel.log
KillMode=mixed
TimeoutStopSec=10

[Install]
WantedBy=multi-user.target
"""


ALLOWED_EXTENSIONS = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".sh", ".cfg", ".ini", ".log"}
FORBIDDEN_PATHS = {"config.json"}

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

MAX_DEPLOY_LOG_KB = 500  # Rotation quand le log dépasse 500KB

def log_deploy(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    try:
        with _LOG_LOCK:
            with open(DEPLOY_LOG, "a") as f:
                f.write(line + "\n")
            # Rotation si trop gros
            if os.path.getsize(DEPLOY_LOG) > MAX_DEPLOY_LOG_KB * 1024:
                with open(DEPLOY_LOG, "r") as f:
                    lines = f.readlines()
                with open(DEPLOY_LOG, "w") as f:
                    f.writelines(lines[-1000:])  # Garder les 1000 dernières lignes
    except Exception:
        pass

def verify_auth(headers, body=b""):
    cfg = load_config()
    secret = cfg.get("deploy_secret", "")
    if not secret:
        return False
    auth_header = headers.get("Authorization", "")
    if not auth_header.startswith("HMAC "):
        return False
    provided_hmac = auth_header[5:]
    expected_hmac = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(provided_hmac, expected_hmac)

def verify_token_simple(headers):
    cfg = load_config()
    secret = cfg.get("deploy_secret", "")
    if not secret:
        return False
    auth_header = headers.get("Authorization", "")
    return auth_header == f"Bearer {secret}"

def _resolve_path(filepath):
    if not os.path.isabs(filepath):
        filepath = os.path.join(ASSISTANT_DIR, filepath)
    filepath = os.path.realpath(filepath)
    if not filepath.startswith(ASSISTANT_DIR):
        return None
    return filepath

def _extract_version(code):
    for line in code.split("\n"):
        if line.strip().startswith("VERSION") and "=" in line:
            parts = line.split("=", 1)
            return parts[1].strip().strip('"').strip("'")
    return "unknown"

def _security_checks(code):
    required = ["def main():", "def traiter_message(", "def telegram_send(", "CFG = load_config()"]
    for r in required:
        if r.lower() not in code.lower():
            return f"Elément requis manquant: {r}"
    forbidden = ["os.system('rm -rf", "shutil.rmtree('/'", "subprocess.run(['rm'"]
    for f in forbidden:
        if f in code:
            return f"Code dangereux: {f[:30]}"
    return None

# === ACTIONS ===

def action_read(filepath=None):
    if filepath is None:
        filepath = SCRIPT_PATH
    else:
        filepath = _resolve_path(filepath)
        if not filepath:
            return {"status": "error", "message": "Chemin non autorisé"}
    try:
        with open(filepath, "r") as f:
            content = f.read()
        return {
            "status": "ok", "path": filepath,
            "lines": len(content.split("\n")),
            "size_kb": round(len(content) / 1024, 1),
            "content": content,
            "version": _extract_version(content) if filepath == SCRIPT_PATH else None,
            "timestamp": datetime.now().isoformat()
        }
    except FileNotFoundError:
        return {"status": "error", "message": f"Fichier non trouvé: {filepath}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def action_write_file(data):
    filepath = data.get("path", "")
    content = data.get("content", "")
    if not filepath or not content:
        return {"status": "error", "message": "path et content requis"}
    resolved = _resolve_path(filepath)
    if not resolved:
        return {"status": "error", "message": f"Chemin non autorisé: {filepath}"}
    _, ext = os.path.splitext(resolved)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        return {"status": "error", "message": f"Extension non autorisée: {ext}"}
    basename = os.path.basename(resolved)
    if basename in FORBIDDEN_PATHS:
        return {"status": "error", "message": f"Fichier protégé: {basename}"}
    try:
        if os.path.exists(resolved):
            backup_name = f"{basename}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(resolved, os.path.join(VERSIONS_DIR, backup_name))
        os.makedirs(os.path.dirname(resolved), exist_ok=True)
        with open(resolved, "w") as f:
            f.write(content)
        log_deploy(f"✅ Fichier écrit: {resolved} ({len(content.split(chr(10)))} lignes)")
        return {"status": "ok", "path": resolved, "lines": len(content.split("\n")),
                "size_kb": round(len(content) / 1024, 1), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def action_delete_file(data):
    """Supprime un fichier du dossier assistant (sécurisé)"""
    filepath = data.get("path", "")
    if not filepath:
        return {"status": "error", "message": "path requis"}

    # Sécurité : uniquement dans le dossier assistant, pas de ..
    if ".." in filepath or filepath.startswith("/"):
        return {"status": "error", "message": "Chemin interdit"}

    full_path = os.path.join(ASSISTANT_DIR, filepath)

    # Interdire de supprimer les fichiers critiques
    PROTEGE = {"assistant.py", "deploy_server.py", "config.json", "memory.db"}
    if os.path.basename(full_path) in PROTEGE:
        return {"status": "error", "message": f"Fichier protégé : {filepath}"}

    if not os.path.exists(full_path):
        return {"status": "error", "message": f"Fichier inexistant : {filepath}"}

    try:
        os.remove(full_path)
        log_deploy(f"Fichier supprimé : {filepath}")
        return {"status": "ok", "deleted": filepath, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def action_list_files(subdir=""):
    target = os.path.join(ASSISTANT_DIR, subdir) if subdir else ASSISTANT_DIR
    target = os.path.realpath(target)
    if not target.startswith(ASSISTANT_DIR):
        return {"status": "error", "message": "Chemin non autorisé"}
    try:
        entries = []
        for item in sorted(os.listdir(target)):
            full = os.path.join(target, item)
            rel = os.path.relpath(full, ASSISTANT_DIR)
            if os.path.isdir(full):
                entries.append({"name": rel, "type": "dir"})
            else:
                entries.append({"name": rel, "type": "file", "size_kb": round(os.path.getsize(full) / 1024, 1)})
        return {"status": "ok", "path": os.path.relpath(target, ASSISTANT_DIR), "entries": entries}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def action_patch(data):
    mode = data.get("mode", "full")
    backup_name = f"assistant_pre_deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    backup_path = os.path.join(VERSIONS_DIR, backup_name)
    try:
        shutil.copy2(SCRIPT_PATH, backup_path)
    except Exception as e:
        return {"status": "error", "message": f"Backup impossible: {e}"}

    if mode == "full":
        new_code = data.get("code", "")
        if not new_code or len(new_code) < 1000:
            return {"status": "error", "message": "Code trop court"}
        checks = _security_checks(new_code)
        if checks:
            return {"status": "error", "message": f"Sécurité: {checks}"}
        try:
            with open(SCRIPT_PATH, "w") as f:
                f.write(new_code)
            return {"status": "ok", "mode": "full", "lines": len(new_code.split("\n")),
                    "backup": backup_name, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            shutil.copy2(backup_path, SCRIPT_PATH)
            return {"status": "error", "message": f"Rollback: {e}"}

    elif mode == "replace":
        old_str = data.get("old_str", "")
        new_str = data.get("new_str", "")
        if not old_str:
            return {"status": "error", "message": "old_str vide"}
        try:
            with open(SCRIPT_PATH, "r") as f:
                code = f.read()
            count = code.count(old_str)
            if count == 0:
                return {"status": "error", "message": "old_str non trouvé dans le script"}
            if count > 1:
                return {"status": "error", "message": f"old_str trouvé {count} fois — ambigu"}
            code = code.replace(old_str, new_str)
            checks = _security_checks(code)
            if checks:
                return {"status": "error", "message": f"Sécurité post-patch: {checks}"}
            with open(SCRIPT_PATH, "w") as f:
                f.write(code)
            return {"status": "ok", "mode": "replace", "backup": backup_name,
                    "timestamp": datetime.now().isoformat()}
        except Exception as e:
            shutil.copy2(backup_path, SCRIPT_PATH)
            return {"status": "error", "message": f"Rollback: {e}"}
    return {"status": "error", "message": f"Mode inconnu: {mode}"}

def action_probe_sudo():
    """Test non-destructif des droits sudo requis pour le bootstrap infra."""
    tests = [(["sudo", "-n", "-l"], "sudo_-l")]
    results = {}
    for cmd, label in tests:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            results[label] = {"rc": r.returncode,
                              "stdout": (r.stdout or "").strip()[:4000],
                              "stderr": (r.stderr or "").strip()[:500]}
        except Exception as e:
            results[label] = {"error": str(e)[:200]}
    # Nettoyage
    try: subprocess.run(["sudo", "-n", "rm", "-f", "/tmp/__sudo_cp_probe"],
                        capture_output=True, timeout=5)
    except: pass
    ok = all(r.get("rc") == 0 for r in results.values())
    return {"status": "ok" if ok else "partial", "can_bootstrap": ok, "tests": results}


def action_infra_install():
    """Installe les unit files systemd + daemon-reload + enable.
    N'effectue PAS de start/restart — handoff séparé."""
    try:
        # Écriture dans /tmp (propriétaire = lolufe, pas de sudo)
        with open("/tmp/deploy_server.service", "w") as f:
            f.write(DEPLOY_SERVER_UNIT)
        with open("/tmp/cloudflared_tunnel.service", "w") as f:
            f.write(CLOUDFLARED_TUNNEL_UNIT)

        steps = []
        for unit in ["deploy_server.service", "cloudflared_tunnel.service"]:
            r = subprocess.run(
                ["sudo", "-n", "cp", f"/tmp/{unit}", f"/etc/systemd/system/{unit}"],
                capture_output=True, text=True, timeout=10)
            steps.append((f"cp {unit}", r.returncode, (r.stderr or "").strip()[:200]))
            if r.returncode != 0:
                return {"status": "error", "steps": steps}

        r = subprocess.run(["sudo", "-n", "systemctl", "daemon-reload"],
                           capture_output=True, text=True, timeout=10)
        steps.append(("daemon-reload", r.returncode, (r.stderr or "").strip()[:200]))
        if r.returncode != 0:
            return {"status": "error", "steps": steps}

        for svc in ["deploy_server.service", "cloudflared_tunnel.service"]:
            r = subprocess.run(["sudo", "-n", "systemctl", "enable", svc],
                               capture_output=True, text=True, timeout=10)
            steps.append((f"enable {svc}", r.returncode,
                          (r.stderr or r.stdout or "").strip()[:200]))

        log_deploy("✅ Systemd units installés + activés au boot")
        return {"status": "ok", "steps": steps,
                "installed": ["deploy_server.service", "cloudflared_tunnel.service"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def action_infra_status():
    """État de tous les services + URL tunnel courante."""
    services = ["deploy_server.service", "cloudflared_tunnel.service", "assistant.service"]
    result = {}
    for svc in services:
        try:
            a = subprocess.run(["systemctl", "is-active", svc],
                               capture_output=True, text=True, timeout=5)
            e = subprocess.run(["systemctl", "is-enabled", svc],
                               capture_output=True, text=True, timeout=5)
            p = subprocess.run(["systemctl", "show", svc, "--property=MainPID,ExecMainStartTimestamp"],
                               capture_output=True, text=True, timeout=5)
            result[svc] = {
                "active": a.stdout.strip() or a.stderr.strip()[:60],
                "enabled": e.stdout.strip() or e.stderr.strip()[:60],
                "info": p.stdout.strip().replace("\n", " | ")[:200]
            }
        except Exception as ex:
            result[svc] = {"error": str(ex)[:200]}

    tunnel_url = None
    try:
        with open(TUNNEL_URL_FILE) as f:
            tunnel_url = f.read().strip()
    except Exception:
        pass

    # Est-ce que JE tourne sous systemd ?
    my_pid = os.getpid()
    ps = subprocess.run(["ps", "-o", "ppid,cmd", "-p", str(my_pid)],
                        capture_output=True, text=True, timeout=5)
    ppid_line = ps.stdout.strip().split("\n")[-1] if ps.stdout else ""
    under_systemd = False
    try:
        ppid = int(ppid_line.strip().split()[0])
        # Si PPID == 1 (init/systemd), c'est systemd qui nous gère
        under_systemd = (ppid == 1)
    except Exception:
        pass

    return {"status": "ok", "services": result, "tunnel_url": tunnel_url,
            "my_pid": my_pid, "my_ppid_line": ppid_line,
            "under_systemd": under_systemd,
            "timestamp": datetime.now().isoformat()}


def action_infra_handoff():
    """Tue le process actuel (nohup) et laisse systemd démarrer une instance fraîche.
    Script lancé en arrière-plan détaché → réponse envoyée avant la mort du process."""
    my_pid = os.getpid()
    script = f"""#!/bin/bash
set -u
sleep 3
# Étape 1: démarrer le service systemd (échouera à bind le port tant qu'on vit,
# mais Restart=always retentera après notre mort)
sudo -n systemctl start deploy_server.service 2>&1 | logger -t infra_handoff
# Étape 2: tuer le process courant (nohup orphan)
sudo -n kill -TERM {my_pid} 2>&1 | logger -t infra_handoff
sleep 2
# Étape 3: s'assurer que systemd a bien rebind
sudo -n systemctl restart deploy_server.service 2>&1 | logger -t infra_handoff
# Étape 4: handoff tunnel aussi
sleep 1
# Tuer les éventuels orphans cloudflared + tunnel_wrapper
pkill -TERM -f "tunnel_wrapper.sh" 2>&1 | logger -t infra_handoff || true
pkill -TERM -f "cloudflared tunnel --url http://localhost:8501" 2>&1 | logger -t infra_handoff || true
sleep 2
sudo -n systemctl restart cloudflared_tunnel.service 2>&1 | logger -t infra_handoff
"""
    script_path = "/tmp/infra_handoff.sh"
    with open(script_path, "w") as f:
        f.write(script)
    os.chmod(script_path, 0o755)
    # Fork-and-forget, détaché de notre session
    subprocess.Popen(["bash", script_path], start_new_session=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log_deploy(f"🔄 Handoff systemd programmé dans 3s (pid {my_pid} sera tué)")
    return {"status": "ok", "message": "Handoff systemd en cours (~10s)",
            "pid_to_kill": my_pid,
            "expected_new_tunnel_url": "publiée sur ntfy.sh après ~5s"}


def _heartbeat_loop():
    """Toutes les HEARTBEAT_INTERVAL secondes, republie l'URL tunnel sur ntfy.sh.
    Garde l'URL fraîche dans la fenêtre 24h de ntfy, même si le tunnel n'a pas redémarré."""
    while True:
        try:
            time.sleep(HEARTBEAT_INTERVAL)
            if os.path.exists(TUNNEL_URL_FILE):
                with open(TUNNEL_URL_FILE) as f:
                    url = f.read().strip()
                if url.startswith("https://"):
                    subprocess.run(
                        ["curl", "-s", "-m", "10", "-d", url, f"https://ntfy.sh/{NTFY_TOPIC}"],
                        capture_output=True, timeout=15)
                    log_deploy(f"💓 heartbeat: {url}")
        except Exception as e:
            log_deploy(f"❌ heartbeat: {e}")


def action_restart_self():
    """Re-exec le deploy_server lui-même (bootstrap d'une nouvelle version).
    Réponse envoyée d'abord, puis exec dans un thread après 1s."""
    def _delayed_exec():
        time.sleep(1)
        log_deploy("🔄 Deploy Server self-restart (os.execv)")
        try:
            os.execv(sys.executable, [sys.executable, os.path.abspath(__file__)])
        except Exception as e:
            log_deploy(f"❌ execv échoué: {e}")
            os._exit(1)
    threading.Thread(target=_delayed_exec, daemon=False).start()
    return {"status": "ok", "message": "Redémarrage deploy_server dans ~1s",
            "timestamp": datetime.now().isoformat()}

def action_restart():
    try:
        subprocess.run(["sudo", "systemctl", "restart", "assistant"], capture_output=True, text=True, timeout=30)
        time.sleep(2)
        status = subprocess.run(["sudo", "systemctl", "is-active", "assistant"], capture_output=True, text=True, timeout=10)
        is_active = status.stdout.strip() == "active"
        if is_active:
            log_deploy("✅ assistant.service redémarré")
            return {"status": "ok", "service": "active", "timestamp": datetime.now().isoformat()}
        return {"status": "error", "service": status.stdout.strip()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def action_rollback():
    try:
        backups = sorted([f for f in os.listdir(VERSIONS_DIR) if f.startswith("assistant_pre_deploy_")])
        if not backups:
            return {"status": "error", "message": "Aucun backup trouvé"}
        last_backup = os.path.join(VERSIONS_DIR, backups[-1])
        shutil.copy2(last_backup, SCRIPT_PATH)
        log_deploy(f"✅ Rollback vers {backups[-1]}")
        subprocess.run(["sudo", "systemctl", "restart", "assistant"], capture_output=True, timeout=30)
        return {"status": "ok", "restored": backups[-1], "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def action_status():
    try:
        result = subprocess.run(["sudo", "systemctl", "is-active", "assistant"], capture_output=True, text=True, timeout=10)
        with open(SCRIPT_PATH, "r") as f:
            code = f.read()
        backups = sorted([f for f in os.listdir(VERSIONS_DIR) if f.endswith(".py")])
        return {"status": "ok", "service": result.stdout.strip(),
                "script_lines": len(code.split("\n")), "script_size_kb": round(len(code) / 1024, 1),
                "version": _extract_version(code), "backups": len(backups),
                "last_backup": backups[-1] if backups else None, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def action_logs(n=50):
    try:
        with open("/home/lolufe/assistant/assistant.log", "r") as f:
            lines = f.readlines()
        return {"status": "ok", "lines": [l.rstrip() for l in lines[-n:]], "total_lines": len(lines)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# === HTTP HANDLER ===

class DeployHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not verify_token_simple(self.headers):
            self._respond(401, {"status": "error", "message": "Non autorisé"})
            return
        if self.path == "/read":
            self._respond(200, action_read())
        elif self.path.startswith("/read/"):
            self._respond(200, action_read(self.path[6:]))
        elif self.path == "/status":
            self._respond(200, action_status())
        elif self.path.startswith("/ask"):
            # API vocale pour Google Home / Alexa
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            question = params.get("q", [""])[0]
            if not question:
                self._respond(400, {"status": "error", "message": "Paramètre q manquant"})
            else:
                try:
                    # Écrire la question dans un fichier, l'assistant la traite
                    q_path = os.path.join(ASSISTANT_DIR, "vocal_question.json")
                    a_path = os.path.join(ASSISTANT_DIR, "vocal_answer.json")
                    import time as _t
                    with open(q_path, "w") as f:
                        json.dump({"q": question, "ts": _t.time()}, f)
                    # Attendre la réponse (max 30s)
                    for _ in range(60):
                        _t.sleep(0.5)
                        if os.path.exists(a_path):
                            try:
                                with open(a_path) as f:
                                    answer = json.load(f)
                                if answer.get("ts", 0) > _t.time() - 35:
                                    os.remove(a_path)
                                    self._respond(200, answer)
                                    return
                            except Exception:
                                pass
                    self._respond(504, {"status": "error", "message": "Timeout"})
                except Exception as e:
                    self._respond(500, {"status": "error", "message": str(e)})
        elif self.path.startswith("/logs"):
            n = 50
            if "n=" in self.path:
                try: n = int(self.path.split("n=")[1])
                except: pass
            self._respond(200, action_logs(n))
        elif self.path == "/ping":
            self._respond(200, {"status": "ok", "message": "deploy_server v2 alive"})
        elif self.path == "/infra_status":
            self._respond(200, action_infra_status())
        elif self.path == "/sudo_probe":
            self._respond(200, action_probe_sudo())
        elif self.path.startswith("/ls"):
            subdir = self.path[4:] if len(self.path) > 4 else ""
            self._respond(200, action_list_files(subdir))
        else:
            self._respond(404, {"status": "error", "message": "Endpoint inconnu"})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        if not verify_auth(self.headers, body):
            self._respond(401, {"status": "error", "message": "Non autorisé"})
            return
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._respond(400, {"status": "error", "message": "JSON invalide"})
            return
        if self.path == "/patch":
            self._respond(200, action_patch(data))
        elif self.path == "/restart":
            self._respond(200, action_restart())
        elif self.path == "/restart_self":
            self._respond(200, action_restart_self())
        elif self.path == "/infra_install":
            self._respond(200, action_infra_install())
        elif self.path == "/infra_handoff":
            self._respond(200, action_infra_handoff())
        elif self.path == "/rollback":
            self._respond(200, action_rollback())
        elif self.path == "/file":
            self._respond(200, action_write_file(data))
        elif self.path == "/delete":
            self._respond(200, action_delete_file(data))
        elif self.path == "/deploy":
            patch_result = action_patch(data)
            if patch_result["status"] != "ok":
                self._respond(200, patch_result)
                return
            restart_result = action_restart()
            self._respond(200, {"status": "ok" if restart_result["status"] == "ok" else "partial",
                "patch": patch_result, "restart": restart_result, "timestamp": datetime.now().isoformat()})
        else:
            self._respond(404, {"status": "error", "message": "Endpoint inconnu"})

    def _respond(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, format, *args):
        log_deploy(f"HTTP {args[0] if args else ''}")

def main():
    os.makedirs(VERSIONS_DIR, exist_ok=True)
    log_deploy(f"🚀 Deploy Server v2 démarré sur port {PORT}")
    threading.Thread(target=_heartbeat_loop, daemon=True).start()
    log_deploy(f"💓 Heartbeat ntfy.sh activé (chaque {HEARTBEAT_INTERVAL}s)")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), DeployHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log_deploy("🛑 Deploy Server arrêté")
        server.server_close()

if __name__ == "__main__":
    main()
