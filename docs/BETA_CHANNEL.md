# 🧪 Mode bêta-testeur — Canal de patches à distance

> ⚠️ **Mode opt-in, désactivé par défaut.**
> Si vous êtes un utilisateur normal, **vous n'avez pas besoin de ce mode**. AssistantIA fonctionne très bien sans.

## Qu'est-ce que le mode bêta ?

Le mode bêta installe un composant supplémentaire — `deploy_server` — qui permet au mainteneur du projet (Philippe) de pousser des correctifs sur votre installation **à distance**, sans SSH.

C'est utile si :
- Vous êtes dans le cercle des 10 bêta-testeurs qui ont accepté ce canal
- Vous voulez recevoir les correctifs automatiques dès qu'un bug est trouvé et fixé chez un autre utilisateur
- Vous voulez profiter de la fonction « apprentissage collectif » (les leçons découvertes chez un testeur bénéficient à tous)

C'est **inutile** si :
- Vous voulez juste faire tourner AssistantIA chez vous, sans connexion avec le mainteneur
- Vous préférez valider manuellement chaque mise à jour via `git pull`
- Vous n'avez pas envie d'exposer un port HTTP supplémentaire (même via tunnel)

## Implications de sécurité — à lire avant d'activer

Activer le mode bêta-testeur signifie :

1. **Un port 8501 est ouvert localement** — le deploy_server écoute sur `127.0.0.1:8501`
2. **Un tunnel Cloudflare Quick Tunnel est créé** — il expose le port 8501 sur une URL publique HTTPS (ex: `https://xxx-yyy.trycloudflare.com`)
3. **L'URL est publiée sur [ntfy.sh](https://ntfy.sh)** — sur un topic secret que seul Philippe connaît
4. **Toutes les requêtes qui modifient l'état sont authentifiées** par une signature HMAC-SHA256 avec le secret unique de votre installation (`deploy_secret` dans `config.json`)

**Ce que Philippe peut faire avec votre autorisation :**
- Lire le code source de votre installation
- Appliquer un patch Python (`deploy_server.py`, `skills.py`, etc.)
- Redémarrer les services AssistantIA
- Consulter les logs

**Ce que Philippe ne peut PAS faire :**
- Lire votre `config.json` (fichier protégé côté serveur)
- Exécuter des commandes shell arbitraires hors du répertoire d'installation
- Accéder à d'autres services sur votre réseau
- Lire votre `memory.db` (vos données perso restent chez vous)

**Risques résiduels :**
- Si le `deploy_secret` fuite (vol physique de la machine, compromission), un attaquant peut pousser des patches malveillants
- Si Cloudflare est compromis au niveau du tunnel, idem
- Ces risques sont réels mais faibles — c'est pourquoi le mode est opt-in

## Activer le mode bêta

### Pré-requis

- `cloudflared` installé sur la machine :
  ```bash
  # Debian/Ubuntu/Pi
  wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
  sudo dpkg -i cloudflared-linux-amd64.deb
  # (ou -arm64.deb sur Pi 4/5)
  ```
- `curl`, `jq`

### Activation

Depuis votre installation AssistantIA :

```bash
cd <dossier-assistantia>
./scripts/enable_beta_channel.sh
```

Le script va :
1. Installer deux services systemd : `deploy_server.service` et `cloudflared_tunnel.service`
2. Installer un watchdog (`infra_watchdog.timer`) qui vérifie la santé toutes les 2 min
3. Publier l'URL tunnel courante sur ntfy.sh (topic dérivé de votre `deploy_secret`)
4. Vous afficher le topic à communiquer à Philippe pour qu'il puisse se connecter

**Vous devez ensuite envoyer le topic à Philippe** (par Telegram, email, forum HACF) pour qu'il puisse pousser des patches chez vous. Sans ce topic, personne ne peut se connecter.

### Désactiver

```bash
./scripts/disable_beta_channel.sh
```

Supprime les trois services systemd et tue les tunnels. Votre installation redevient une installation standard.

## Ce qui se passe concrètement

Une fois activé :

- Les services `deploy_server.service` et `cloudflared_tunnel.service` tournent en permanence
- Toutes les heures, l'URL tunnel est republiée sur ntfy.sh (fenêtre 24h)
- Le watchdog vérifie toutes les 2 min que les services répondent, et les redémarre automatiquement si KO
- Au reboot de la machine, tout redémarre automatiquement

## Journalisation

Toutes les actions (lectures, patches, restarts) sont loguées côté serveur dans :
- `deploy.log` — actions du deploy_server
- `watchdog.log` — check-ups périodiques
- `handoff.log` — migrations / bootstrap

Vous pouvez les consulter à tout moment.

## Questions fréquentes

**Q : Philippe peut-il voir mes secrets (telegram_token, ha_token, anthropic_api_key) ?**
R : Non. `config.json` est explicitement protégé (`FORBIDDEN_PATHS = {"config.json"}` dans le code du deploy_server). Seuls les fichiers de code Python sont lisibles.

**Q : Et si je refuse un patch ?**
R : Les patches ne s'appliquent pas automatiquement — Philippe les pousse et ils s'appliquent, mais vous pouvez faire un `/rollback` à tout moment pour revenir à la version précédente. Tous les patches font un backup automatique.

**Q : Puis-je activer ça temporairement ?**
R : Oui. Activez pour recevoir un fix, puis désactivez avec `disable_beta_channel.sh`.

**Q : Est-ce nécessaire pour utiliser AssistantIA ?**
R : **Non, absolument pas.** AssistantIA fonctionne de manière autonome sans ce mode. Vous recevrez juste les mises à jour via `git pull` classique au lieu d'automatiquement.
