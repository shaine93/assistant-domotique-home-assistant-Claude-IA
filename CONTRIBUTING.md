# Contribuer à AssistantIA Domotique

Merci de votre intérêt ! Voici comment participer.

## 🧪 Devenir bêta testeur

C'est la contribution la plus utile. On cherche **10 installations différentes** :

- Avec/sans panneaux solaires
- Avec/sans pompe à chaleur
- Zigbee, Matter, Z-Wave, WiFi — tous protocoles
- Appartement ou maison
- EDF, TotalEnergies, Engie, Octopus, Ekwateur, Mint...

**Pour participer** : ouvrez une issue "Bêta testeur" avec votre configuration.

## 🐛 Signaler un bug

Utilisez le template **Bug Report** dans les issues. Incluez :

1. La commande ou l'action qui a échoué
2. Le message d'erreur (screenshot Telegram)
3. Les logs (`/logs` sur Telegram ou les 20 dernières lignes du fichier)
4. Votre config : HA version, protocoles utilisés, solaire ou pas

## 💡 Proposer une fonctionnalité

Utilisez le template **Feature Request**. Les meilleures idées viennent des vrais usages quotidiens.

## 🔧 Contribuer du code

1. Fork le repo
2. Créez une branche : `git checkout -b ma-feature`
3. Testez : `python3 -m pytest tests.py`
4. Commit : `git commit -m "feat: description courte"`
5. Push + Pull Request

### Conventions

- **Langue** : code en anglais (variables, fonctions), messages utilisateur en français
- **Style** : snake_case, docstrings, pas de print() en production (log.info/debug)
- **Tests** : chaque nouvelle commande doit avoir un test dans tests.py
- **Doctrine** : pas de workaround, résolution root-cause. Backup avant chaque modification.

## 📦 Ajouter un fournisseur d'énergie

Le script supporte déjà 6 fournisseurs français (EDF, TotalEnergies, Engie, Octopus, Ekwateur, Mint) avec 20+ offres.

Pour ajouter un fournisseur ou une offre :

1. Trouvez les tarifs officiels (prix kWh HP, HC, base, abonnement)
2. Ouvrez une issue "Nouveau fournisseur" avec les détails
3. Ou ajoutez directement dans le dictionnaire `FOURNISSEURS` du script

## 📚 Ajouter un profil d'appareil

Si vous avez un appareil non encore reconnu (ballon thermodynamique, borne de recharge, sèche-serviettes, pompe piscine...) :

1. Notez la consommation typique (puissance, durée cycle, phases)
2. Ouvrez une issue "Nouvel appareil" avec ces infos
3. Le script apprendra le profil et l'ajoutera à la bibliothèque partagée
