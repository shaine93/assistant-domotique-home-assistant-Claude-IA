# Changelog

Toutes les modifications notables de ce projet.

## [7.60] - 2026-03-31

### Ajouté
- **Alertes dynamiques (watches)** : créez des alertes en langage naturel ("Préviens-moi si un onduleur passe offline"), vérifiées chaque minute
- **Tool Use HA** : pilotez vos appareils via Claude ("Ouvre la serrure", "Allume le salon") avec confirmation boutons ✅/❌
- **Projection facture EDF** : estimation fin de mois basée sur la consommation réelle (HP/HC/WE)
- **Contexte enrichi** : économies mois en cours + mois précédent injectées dans le contexte Claude
- Table SQLite `watches` : entity_pattern, condition, state_value, message, cooldown
- Commandes `/watches` et `/alertes`
- Pattern matching glob pour groupes d'entités (ex: `sensor.ecu_*`)
- 10 domaines HA supportés : lock, light, switch, cover, climate, fan, vacuum, media_player, scene, script

### Corrigé
- Calendrier : timeout API augmenté (10s → 15s) pour éviter les échecs intermittents
- Contexte intelligent : économies SQLite et projection EDF visibles par Claude
- Tool use : plus de message "Je n'ai pas compris" quand les boutons sont envoyés
- Tool use : plus de double confirmation (texte Claude supprimé quand l'outil est utilisé)

## [7.58] - 2026-03-28

### Ajouté
- Briefing matin complet : météo, calendrier, trajet Waze, pic solaire prévu, poubelles
- Bilans automatiques : hebdo (dimanche 20h), mensuel (1er à 10h)
- Graphiques Telegram : courbes énergie du jour via matplotlib
- Signatures cycles : empreinte numérique des programmes machines
- Restart intelligent : cycles restaurés après redémarrage
- Menu /commandes avec boutons Telegram par catégorie

### Corrigé
- Score résilience : succès ET échecs logués correctement
- Filtre anti-spam : ne bloque plus les réponses aux commandes
- Détection fin de cycle : grâce intelligente par type machine

## [7.34] - 2026-03-22

### Ajouté
- Setup Wizard Telegram guidé (0 CLI après le git clone)
- SMS multi-provider : Free Mobile, HA Notify, Email
- Moteur économies proactif (0 token, toutes les 5 min)
- Profil foyer (8 questions) + questionnaire appareils (3 catégories)
- Tarification : 6 fournisseurs France, 20+ offres
- Détection universelle : Matter, Zigbee, Z-Wave, WiFi
- Dashboard Lovelace (/dashboard → push sensors HA)
- Multi-utilisateur Telegram
- Intégration calendrier HA
- Score intelligence /100

## [7.0] - 2026-03-13

### Ajouté
- Moteur intelligence 10 phases : baselines, skills, expertise, hypothèses
- Score /100 avec 4 dimensions
- Auto-guérison : Claude Sonnet lit et patche le script

## [1.0] - 2026-02-26

### Premier lancement
- Polling Telegram + Home Assistant API + Claude Haiku
- Commandes de base : /energie, /audit, /zigbee
