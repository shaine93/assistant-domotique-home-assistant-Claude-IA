# 🔧 Dépannage — AssistantIA Domotique

## Le bot ne répond pas sur Telegram

**Vérifications :**

1. Le service tourne-t-il ?
   - HA Add-on : onglet **Journal** de l'add-on
   - Docker : `docker compose logs --tail=100 assistantia`
   - Linux : `sudo systemctl status assistantia.service`

2. Le token Telegram est-il valide ?
   ```bash
   curl "https://api.telegram.org/bot<VOTRE_TOKEN>/getMe"
   ```
   Doit retourner `{"ok":true,"result":{...}}`. Sinon le token est mauvais.

3. Avez-vous envoyé le **premier message** au bot ?
   Le bot détecte votre `chat_id` seulement après votre premier message. Envoyez « hello ».

4. Le canal est-il verrouillé ? (code 6 chiffres non saisi)
   Attendez le code par SMS / notif HA / email et tapez-le dans Telegram.

## Le bot ne voit pas mes appareils Home Assistant

**Vérifications :**

1. L'URL HA est-elle joignable depuis la machine du bot ?
   ```bash
   curl -H "Authorization: Bearer <HA_TOKEN>" http://<HA_IP>:8123/api/
   ```
   Doit retourner `{"message":"API running."}`.

2. Le token HA a-t-il bien accès ?
   ```bash
   curl -H "Authorization: Bearer <HA_TOKEN>" http://<HA_IP>:8123/api/states | head
   ```

3. Relancer le scan manuellement depuis Telegram : `/scan`

## Erreur "Rate limit exceeded" côté Anthropic

Votre clé API a atteint sa limite. Options :

- Attendre quelques minutes
- Augmenter le quota dans [console.anthropic.com](https://console.anthropic.com) → **Limits**
- Ajuster `anthropic_monthly_budget_usd` dans `config.json`

## Le bot crash au démarrage

**Erreur "ModuleNotFoundError"** — dépendances manquantes :
```bash
pip3 install --user --upgrade -r requirements.txt
```

**Erreur "FileNotFoundError: config.json"** — relancer le wizard :
```bash
./install.sh
```

**Erreur "sqlite3.DatabaseError"** — base corrompue. Sauvegarde + reset :
```bash
mv memory.db memory.db.broken
# Le bot recréera une nouvelle DB au démarrage.
```

## Le bot envoie trop (ou pas assez) de notifications

Ajuster dans Telegram :

- `/commandes` — voir toutes les commandes
- `/budget` — vérifier la consommation API
- `/debug` — état des threads

**Désactiver temporairement une alerte :** `/watches` pour voir les alertes actives, `/watches supprimer <id>` pour en retirer une.

## Les cycles machines ne sont pas détectés

1. Vérifier qu'une prise est bien associée à une machine : `/appareils`
2. Sinon, reconfigurer : `/appareils reset` → le questionnaire repart
3. Vérifier que la prise a bien un capteur de puissance en Watt : `/surveillance`

## Les économies ne s'affichent pas

`/roi` demande plusieurs cycles complets pour calibrer. Comptez 1 semaine pour voir les premiers chiffres.

## Mode bêta-testeur : `/restart_self` ne fonctionne pas

Lire [docs/BETA_CHANNEL.md](BETA_CHANNEL.md) — le deploy_server doit être activé (opt-in) et le tunnel Cloudflare doit tourner.

## Relancer de zéro

Pour repartir propre, en préservant vos credentials :

```bash
# Sauvegarder
cp config.json config.json.backup
cp memory.db memory.db.backup

# Nettoyer
rm memory.db
rm -rf __pycache__

# Redémarrer
sudo systemctl restart assistantia.service   # (ou docker compose restart)
```

## Obtenir de l'aide

1. **`/probleme <description>`** dans Telegram — Claude diagnostique votre problème
2. **Logs détaillés** :
   - HA Add-on : onglet Journal
   - Docker : `docker compose logs --tail=200 assistantia`
   - Linux : `sudo journalctl -u assistantia.service -n 200`
3. **GitHub Issues** : https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA/issues
4. **Forum HACF** : https://forum.hacf.fr/t/assistantia-domotique-lia-qui-gere-votre-maison-pendant-que-vous-dormez/78164
