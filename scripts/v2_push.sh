#!/bin/bash
exec > /home/lolufe/assistant/scripts/e2e_test.log 2>&1
cd /home/lolufe/assistant
echo "=== Remote URL ==="
git remote get-url origin
echo "=== Branche ==="
git branch --show-current
echo "=== Fichiers canal/tuto presents ==="
ls -1 CANAL_CLAUDE.md CLAUDE.md 2>/dev/null
