#!/bin/bash
cd /home/lolufe/assistant
git add -A
git diff --cached --quiet && exit 0
git commit -m "auto-sync $(date +%Y-%m-%d_%H:%M)" > /dev/null 2>&1
git push > /dev/null 2>&1
echo "$(date): pushed" >> /home/lolufe/assistant/sync.log
