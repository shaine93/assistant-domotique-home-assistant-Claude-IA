#!/usr/bin/env python3
import subprocess
with open("/proc/loadavg") as f: print(f"loadavg: {f.read().strip()}")
with open("/proc/meminfo") as f:
    for line in f:
        if line.startswith(("MemTotal:", "MemFree:", "MemAvailable:")):
            print(f"  {line.strip()}")
print("\n=== processus ===")
r = subprocess.run(["ps","auxf"], capture_output=True, text=True)
for line in r.stdout.split("\n"):
    if "assistant.py" in line or "deploy_server" in line or "cloudflared" in line:
        print(line[:220])
print("\n=== 25 dernieres lignes log ===")
try:
    with open("/home/lolufe/assistant/assistant.log") as f: lines = f.readlines()
    for l in lines[-25:]:
        if any(k in l.lower() for k in ["error","warning","timeout","retry","claude","anthropic","telegram","sendMessage"]):
            print(l.rstrip()[:280])
except Exception as e: print(f"err: {e}")
