# 📚 Leçons fondatrices — Pièges connus par installation

Ce fichier est enrichi par les bêta testeurs. Chaque piège découvert évite des heures de debug aux suivants.

---

## 🧺 Lave-linge

### Pause rinçage confondue avec fin de cycle
- **Symptôme** : le cycle se termine à 30 min au lieu de 90 min
- **Cause** : pause de 5-15 min entre lavage et essorage, puissance < SEUIL_FIN_W
- **Fix** : grâce intelligente basée sur la dernière phase (chauffage → grâce longue, essorage → grâce courte)

### Hublot verrouillé après fin
- **Symptôme** : notification "terminé" mais impossible d'ouvrir
- **Cause** : sécurité hublot 3-5 min après arrêt moteur
- **Fix** : message "Hublot se déverrouille dans ~5 min"

---

## 👕 Sèche-linge

### Défroissage automatique → cycle 300+ min
- **Symptôme** : cycle annoncé à 311 min au lieu de 40 min
- **Cause** : défroissage automatique = rotation basse (10-50W) toutes les 10 min pendant 2-4h. Reset la grâce.
- **Fix** : après le rappel "linge chaud", les consommations < 200W ne resetent plus la grâce

### Cycle doux non détecté
- **Symptôme** : le sèche-linge tourne en mode éco mais aucune notification
- **Cause** : puissance max 50-180W, jamais > SEUIL_CYCLE_W (200W)
- **Fix** : si conso > SEUIL_FIN_W pendant 5 min continue → démarrer le cycle automatiquement

---

## 🍽️ Lave-vaisselle

### Séchage passif
- **Symptôme** : fin de cycle annoncée 30 min trop tôt ou trop tard
- **Cause** : phase de séchage passif (0W) de 10-30 min en fin, puis conso résiduelle
- **Fix** : grâce spécifique lave-vaisselle (GRACE_APRES_VAISSELLE)

---

## ☀️ Solaire / Anker

### ECU glitch 0W entre updates
- **Symptôme** : production solaire alterne entre 500W et 0W
- **Cause** : l'ECU APSystems envoie 0W entre deux mises à jour (intervalle 5 min)
- **Fix** : ignorer les valeurs 0W si la précédente était > 0 et il fait jour

### Anker Solarbank ≠ cycle machine
- **Symptôme** : la prise Anker déclenche un faux cycle machine
- **Cause** : la charge/décharge de la batterie fait varier la puissance de la prise
- **Fix** : exclure la prise Anker du monitoring cycles

---

## 🌡️ PAC / Chauffage

### Thermostat on/off = normal
- **Symptôme** : alerte "PAC allumée/éteinte" en boucle
- **Cause** : le thermostat coupe et relance normalement le compresseur
- **Fix** : ne pas alerter sur climate auto/heat → c'est le mode normal

---

## 📡 Zigbee

### LQI faible après ajout d'appareil
- **Symptôme** : nouvel appareil avec LQI 30-40, performances dégradées
- **Cause** : table de routage pas encore optimisée
- **Fix** : attendre 24h, ou forcer un "Rediscover Network" dans Z2M + changer de canal WiFi si interférence

---

## 📋 Comment contribuer

Ajoutez vos pièges via GitHub Issue "Leçon fondatrice" avec :
1. L'appareil concerné
2. Le symptôme observé
3. La cause identifiée
4. Le fix appliqué (ou souhaité)
