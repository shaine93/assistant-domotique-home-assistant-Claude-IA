<p align="center">
  <h1 align="center">🏠 AssistantIA Domotique</h1>
  <p align="center"><strong>L'antivirus de votre maison — propulsé par Claude AI</strong></p>
  <p align="center"><em>v7.39 — 11 814 lignes — 51 commandes — 10 skills — 22 tables</em></p>
</p>

---

**AssistantIA** est un agent IA autonome qui surveille votre maison 24/7 via Home Assistant. Il apprend vos habitudes, détecte les anomalies, optimise votre consommation, et vous fait économiser de l'argent — chaque jour.

**Le business model** : chaque euro en tokens produit 10-20€ d'économies. Le script se finance par ses propres résultats.

---

## 🧬 Pourquoi ce script existe

> L'utilisateur paie des tokens avec les économies que le script génère.

Le script surveille tout (Zigbee, Matter, Z-Wave, WiFi), détecte vos appareils, apprend votre profil, et vous pousse des actions chaque jour pour économiser. Avec ou sans panneaux solaires.

**Ce qu'il fait chaque jour automatiquement :**

| Heure | Ce qui se passe |
|-------|-----------------|
| **7h00** | Briefing matin : bilan hier + conseil du jour (HC/solaire/standby) |
| **En continu** | Surveillance 51 commandes, 22 tables, 11 threads |
| **Pic solaire** | "2700W dispo ! Lancez une machine → 0.32€ gratuit" |
| **Standby oublié** | "TV en veille 12W → 1.8€/mois. Coupez ou dites à Google" |
| **Machine lancée** | "🧺 Lave-linge en marche — estimation 0.18€ (solaire 45%)" |
| **Machine finie** | "🧺 Terminé — 1.23 kWh — 0.18€. Hublot déverrouillé." |
| **Sèche-linge** | "👕 Linge chaud ! Sortez-le — plus facile à plier." |
| **21h00** | Bilan du soir : total du jour par source + cumul mois |

### Il s'adapte à VOTRE maison

Au premier lancement, le script pose des questions :

**Profil foyer** (8 questions) : combien de personnes, présence, solaire, chauffage, eau chaude, assistant vocal, objectif.

**Appareils sur prises** (1 question par prise) : lave-linge, sèche-linge, lave-vaisselle, congélateur, coupe-veille (TV/PC), monitoring énergie, ou ignorer.

Ensuite il adapte tout : avec solaire → alertes pic solaire. Sans solaire → conseils HP/HC. Avec Google Nest → commandes vocales dans les alertes.

### Claude AI = votre développeur

```
/probleme Je veux une alerte quand le congélateur dépasse 100W
```

Claude Sonnet lit les 11 814 lignes, propose un patch, vous appuyez ✅. Pas de code, pas de terminal.

---

## 🚀 Déploiement

### Ce qu'il faut préparer (10 min)

| # | Quoi | Où |
|---|------|----|
| 1 | **Bot Telegram** | `@BotFather` → `/newbot` → token |
| 2 | **Token HA** | Profil → Tokens longue durée |
| 3 | **URL HA** | `http://192.168.1.XX:8123` |
| 4 | **Clé Anthropic** | `console.anthropic.com` (~5-10€/mois) |

### Sur quel matériel ?

| Machine | Coût | Idéal pour |
|---------|------|------------|
| **HA Add-on** | 0€ | Déjà sur HA OS → 1 clic |
| **Raspberry Pi 4/5** | 40-80€ | Dédié, 5W |
| **VM Cloud gratuite** | 0€ | Oracle/Google free tier |
| **NAS Synology** | 0€ | Docker, déjà allumé |

### Installation

**HA Add-on (2 min)** : Paramètres → Add-ons → Dépôts → URL GitHub → Installer → Config → Démarrer

**Script (5 min)** :
```bash
git clone https://github.com/votre-repo/assistantia-domotique.git
cd assistantia-domotique && pip install anthropic requests
python3 assistant.py
```

**Docker** :
```bash
docker run -d --name assistantia --restart unless-stopped \
  -v assistantia_data:/app/data -p 8501:8501 \
  ghcr.io/votre-repo/assistantia-domotique:latest
```

Le wizard Telegram guide tout le reste. **15 minutes. Ensuite vous ne touchez plus rien.**

---

## 🤝 Mise en service — Claude Opus 4.6

Le déploiement assisté se fait via **Claude Opus 4.6 étendu**. Collez le Cahier des Charges + votre matériel. Opus gère tout.

---

## 🔌 Détection universelle

Le script détecte **tout** ce qui apparaît dans Home Assistant — Zigbee, Matter, Z-Wave, WiFi, ESPHome, IP. Chaque nouvelle entité est notifiée avec le protocole détecté et les faits HA. Pas de supposition.

Les prises avec mesure de puissance déclenchent automatiquement le questionnaire : "C'est quoi sur cette prise ?"

## 💰 Combien ça rapporte ?

| Poste | Montant |
|-------|---------|
| Script | **Gratuit** (MIT) |
| Tokens Claude | ~5-10€/mois (diminue avec le temps) |
| Économies typiques | **40-80€/an** |
| **ROI** | **x10 à x20** |

> Le mois 6 coûte moins que le mois 1. L'expertise est locale, les tokens diminuent, les économies augmentent.

## 🗺️ Roadmap — tout est fait

- [x] 51 commandes Telegram + langage naturel
- [x] 25 rôles universels (0 entity_id en dur)
- [x] Mode sniper : polling 20s/60s adaptatif
- [x] Profil foyer (8 questions → skills)
- [x] 3 catégories appareils (cycles / coupe-veille / monitoring)
- [x] Moteur économies proactif (briefing 7h, pic solaire, standby, HP/HC, bilan 21h)
- [x] Détection universelle (Matter, Zigbee, Z-Wave, WiFi)
- [x] Mesures SQLite temps réel (survit aux restarts)
- [x] Grâce intelligente par machine + rappels immédiats
- [x] Tarification 6 fournisseurs FR
- [x] Auto-correction erreurs
- [x] HA Add-on + Docker + systemd
- [x] Tests pytest + i18n FR/EN
- [x] Multi-utilisateur + calendrier HA + dashboard Lovelace

**v2.0 — En cours :**
- [ ] **Repo GitHub public** + README vitrine + screenshots Telegram
- [ ] **10 bêta testeurs** (forum HA Community, Reddit, Discord)
- [ ] Bilan hebdo automatique (dimanche 20h, arrive tout seul)
- [ ] Graphiques Telegram (courbes conso/solaire en image)
- [ ] Briefing matin complet (météo + calendrier + solaire + poubelles)
- [ ] Comparaison mois/mois ("ce mois -18% vs le mois dernier")
- [ ] Auto-guérison testée bout en bout + rollback automatique

## 📜 License

MIT — Utilisez, modifiez, partagez librement.

---

<p align="center">
  <strong>AssistantIA Domotique — L'antivirus de votre maison.</strong><br>
  <em>Il apprend votre maison. Vous le configurez en parlant. Claude AI le fait évoluer.</em><br>
  <em>Chaque jour, il vous fait gagner de l'argent.</em>
</p>
