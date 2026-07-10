#!/bin/bash
exec > /home/lolufe/assistant/scripts/e2e_test.log 2>&1
cd /home/lolufe/assistant
git add LECONS.md
git commit -m "Doc : transcription vocale Telegram operationnelle (verifiee 10/07)" 2>&1 | tail -2
git push 2>&1 | tail -1
