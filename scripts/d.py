#!/usr/bin/env python3
import subprocess, os, requests, json

# 1. Générer un audio de test avec espeak si dispo, sinon un ton
# Plus simple : tester l'API Google Speech directement avec un FLAC généré
# Créer un fichier audio parlé via ffmpeg (silence + on verra la reponse API)

# Test réel : l'API Google répond-elle encore ?
# On crée un petit FLAC de 1s (l'important est de voir si l'API renvoie 200 ou une erreur)
os.system('ffmpeg -y -f lavfi -i "sine=frequency=440:duration=1" -ar 16000 -ac 1 -f flac /tmp/test.flac 2>/dev/null')

with open('/tmp/test.flac','rb') as f:
    audio = f.read()
print(f'FLAC genere: {len(audio)} bytes', flush=True)

url = 'http://www.google.com/speech-api/v2/recognize?output=json&lang=fr-FR&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw'
try:
    r = requests.post(url, data=audio, headers={'Content-Type':'audio/x-flac; rate=16000'}, timeout=15)
    print(f'API Google Speech: HTTP {r.status_code}', flush=True)
    print(f'Reponse: {r.text[:300]}', flush=True)
except Exception as e:
    print(f'ERREUR API: {type(e).__name__}: {e}', flush=True)
