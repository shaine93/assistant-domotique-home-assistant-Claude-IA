#!/bin/bash
exec > /home/lolufe/assistant/scripts/e2e_test.log 2>&1
echo "=== Whoami ==="
whoami
echo ""
echo "=== Test direct git_sync.sh (sans sudo) ==="
/home/lolufe/assistant/git_sync.sh
echo "Exit: $?"
echo ""
echo "=== sync.log ==="
tail -5 /home/lolufe/assistant/sync.log 2>/dev/null

echo ""
echo "=== Vérif credentials git accessibles ==="
ls -la /home/lolufe/.git-credentials 2>&1
cat /home/lolufe/.git-credentials 2>/dev/null | sed 's|ghp_[A-Za-z0-9]*|ghp_***REDACTED***|'
