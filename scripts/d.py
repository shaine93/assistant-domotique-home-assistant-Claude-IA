#!/usr/bin/env python3
import json, imaplib, os

# 1. Lire le mot de passe depuis /home/debian/.imap_pass
try:
    with open('/home/debian/.imap_pass') as f:
        pwd = f.read().strip()
    print(f'Fichier lu : {len(pwd)} caracteres', flush=True)
except PermissionError:
    print('PERMISSION_DENIED sur /home/debian/.imap_pass', flush=True)
    pwd = None
except Exception as e:
    print(f'ERREUR lecture: {e}', flush=True)
    pwd = None

if pwd:
    # 2. Tester IMAP
    try:
        m = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        m.login('lolufe@gmail.com', pwd)
        m.select('INBOX')
        typ, data = m.search(None, 'UNSEEN')
        n = len(data[0].split()) if data[0] else 0
        print(f'SUCCES IMAP : {n} non lus', flush=True)
        m.logout()
        # 3. Ranger dans config.json
        p = '/home/lolufe/assistant/config.json'
        c = json.load(open(p))
        c['imap_user'] = 'lolufe@gmail.com'
        c['imap_pass'] = pwd
        json.dump(c, open(p,'w'), indent=2, ensure_ascii=False)
        print('Enregistre dans config.json (imap_user + imap_pass)', flush=True)
    except Exception as e:
        print(f'ECHEC IMAP: {e}', flush=True)
