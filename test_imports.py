
import os, shutil, subprocess

# Clear __pycache__
cache_dir = "/home/lolufe/assistant/__pycache__"
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)
    print(f"Cleared {cache_dir}")

# List current files
for f in sorted(os.listdir("/home/lolufe/assistant")):
    if f.endswith(".py"):
        size = os.path.getsize(f"/home/lolufe/assistant/{f}")
        print(f"  {f}: {size:,} bytes")

# Test syntax compilation
import py_compile
for f in ["config.py", "shared.py", "skills.py", "assistant.py"]:
    path = f"/home/lolufe/assistant/{f}"
    try:
        py_compile.compile(path, doraise=True)
        print(f"✅ {f} syntax OK")
    except py_compile.PyCompileError as e:
        print(f"❌ {f}: {e}")

# Test import chain
os.chdir("/home/lolufe/assistant")
try:
    result = subprocess.run(
        ["python3", "-c", "from config import *; print('config OK')"],
        capture_output=True, text=True, timeout=10, cwd="/home/lolufe/assistant"
    )
    print(f"config import: {result.stdout.strip()} {result.stderr.strip()[:200]}")
except Exception as e:
    print(f"config import error: {e}")

try:
    result = subprocess.run(
        ["python3", "-c", "from shared import *; print(f'shared OK - {len(dir())} names')"],
        capture_output=True, text=True, timeout=15, cwd="/home/lolufe/assistant"
    )
    print(f"shared import: {result.stdout.strip()}")
    if result.stderr:
        print(f"  stderr: {result.stderr.strip()[:300]}")
except Exception as e:
    print(f"shared import error: {e}")
