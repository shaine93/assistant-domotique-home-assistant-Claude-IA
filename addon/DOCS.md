# AssistantIA Domotique

## Configuration

Après installation de l'add-on, configurez ces 2 paramètres dans l'onglet **Configuration** :

1. **telegram_token** — Token de votre bot Telegram (créé via @BotFather)
2. **anthropic_api_key** — Clé API Anthropic (console.anthropic.com)

L'URL Home Assistant et le token sont configurés **automatiquement** par le Supervisor.

## Premier démarrage

1. Démarrez l'add-on
2. Envoyez un message à votre bot Telegram → le chat_id est détecté automatiquement
3. Le bot vous pose quelques questions : méthode de sécurité, tarif électricité, appareils sur les prises
4. C'est tout — l'assistant surveille votre maison

## Commandes

Tapez `/aide` dans Telegram pour voir toutes les commandes disponibles.

## Support

- GitHub Issues pour les bugs
- `/probleme <description>` pour que l'IA diagnostique et propose un fix
