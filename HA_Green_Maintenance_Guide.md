# Guide Maintenance HA Green — Instructions Claude Code

> **Dernière mise à jour** : 22/07/2026
> **Objectif** : Permettre à tout agent Claude (Code, conversationnel) d'intervenir sur le HA Green de Philippe sans gaspiller de tokens et sans demander à Philippe de SSH ou copier-coller quoi que ce soit.

---

## RÈGLES ABSOLUES

1. **Lis ce document EN ENTIER avant toute action** — chaque token gaspillé en tâtonnement est un échec
2. **Ne jamais demander à Philippe de SSH, copier-coller, ou fournir un secret** — tout est documenté ici
3. **Ne jamais recommander la migration SSD USB** ("Déplacer le disque de données") — déjà tentée, crash complet, 2 jours de restauration. Option EXCLUE définitivement
4. **HA Green = HA OS sur eMMC 32 GB soudé** — chaque écriture inutile use le disque. Minimiser les opérations
5. **Pas de Docker direct** — HA OS gère containerd en interne via le Supervisor. Les commandes `docker` ne fonctionnent que depuis le shell root host, pas depuis les add-ons

---

## ARCHITECTURE HA GREEN

### Matériel

- **Home Assistant Green** — processeur ARM (aarch64), eMMC 32 GB (28 GB utiles), 4 GB RAM
- **eMMC soudé** — non remplaçable, durée de vie limitée (40% usé au 22/07/2026)
- **Clé USB CONFIG** branchée en permanence — fournit l'accès SSH root port 22222

### Réseau

- **IP locale** : `192.168.1.76`
- **URL externe** : `https://philhomeassist.duckdns.org` (box route 443 vers 8123, SSL verify=False)
- **Nom mDNS** : `homeassistant.local`

### Versions (au 22/07/2026)

- HA OS : 18.1
- HA Core : 2026.7.3
- Supervisor : 2026.07.3

### Stockage — Répartition normale

| Catégorie (métriques HA) | Taille normale | Contenu réel |
|--------------------------|---------------|-------------|
| Système | 12-14 GB | Images containers containerd + rootfs overlayfs |
| Données des applications | 1-2 GB | MariaDB, Z2M, données add-ons |
| Config des applications | 0.2 GB | YAML, configs add-ons |
| Sauvegardes | 1-2 GB | Max 2 backups locaux |
| Home Assistant | 1 GB | Config HA, DB, logs |
| Espace libre | **> 8 GB minimum** | En dessous = alerte |

### Structure disque réelle (vue root host)

```
/mnt/data/
  docker/           # 13-18 GB — images containers (NE PAS TOUCHER)
    containerd/     # Snapshots images (layers)
    rootfs/         # Filesystem racine de chaque container
  supervisor/       # 3-5 GB — données HA
    backup/         # Sauvegardes
    homeassistant/  # Config HA
    addons/         # Données add-ons
  swapfile          # 1.3 GB — swap
  logs/             # 200-500 MB — journaux systemd
```

---

## MÉTHODES D'ACCÈS

### Méthode 1 — HA CLI (sans accès root, depuis n'importe quel terminal HA)

Commandes `ha` disponibles directement depuis l'add-on SSH :

```bash
ha os info              # Version OS, boot slots
ha su info              # Supervisor, liste add-ons
ha su repair            # Nettoyage images orphelines (SAFE)
ha backups list         # Lister les sauvegardes
ha backups remove SLUG  # Supprimer une sauvegarde
ha host reboot          # Redémarrer le host
ha hardware info        # Périphériques détectés
ha info                 # Vue globale
```

Limitation : pas d'accès au filesystem host, pas de docker, pas de du/df détaillé.

### Méthode 2 — Root host via SSH port 22222 (accès complet)

Depuis n'importe quelle machine sur le réseau local :

```bash
ssh root@192.168.1.76 -p 22222
```

Prérequis : la clé USB CONFIG avec authorized_keys doit être branchée sur le Green (elle l'est en permanence).

Depuis ce shell on a accès à : du, df, docker, journalctl, mount, tout /mnt/data/.

### Méthode 3 — nsenter (accès partiel depuis l'add-on SSH)

Si le port 22222 n'est pas accessible (intervention à distance sans VPN) :

1. Ouvrir le terminal **Advanced SSH & Web Terminal** (protection mode désactivé)
2. Taper :

```bash
nsenter -t 1 -m -u -i -n -- /bin/bash
```

Donne accès à : filesystem host en lecture, df, find, du.
PAS accès à : docker, journalctl, mount.

### Méthode 4 — Deploy server (pour le bot AssistantIA, pas pour le HA Green)

Le deploy server tourne sur la VM OVH, PAS sur le HA Green. Voir CLAUDE_BOOTSTRAP.md pour l'accès au deploy server. Utile uniquement pour pousser des fichiers sur le repo GitHub ou patcher skills.py.

---

## PROCÉDURES DE MAINTENANCE

### Diagnostic espace disque (5 min, depuis root host port 22222)

```bash
echo "=== Vue globale ==="
du -sh /mnt/data/* | sort -rh

echo "=== Docker détail ==="
du -sh /mnt/data/docker/* | sort -rh

echo "=== Images actives ==="
docker system df
docker image ls --format "table {{.Size}}\t{{.Repository}}:{{.Tag}}" | sort -rh | head -20

echo "=== Journaux ==="
journalctl --disk-usage

echo "=== Gros fichiers ==="
find /mnt/data -type f -size +100M 2>/dev/null | head -20
```

### Nettoyage standard (quand espace libre inférieur à 8 GB)

Étape 1 — Repair Supervisor (toujours commencer par là) :
```bash
ha su repair
```

Étape 2 — Purge images Docker (depuis root host, tous les add-ons DOIVENT tourner) :
```bash
docker image prune -a
```

Étape 3 — Purge journaux (depuis root host) :
```bash
journalctl --rotate
journalctl --vacuum-time=2d
```

Étape 4 — Vérifier les backups :
```bash
ha backups list
ha backups remove SLUG
```

### Après une mise à jour HA Core

Chaque mise à jour de HA Core télécharge une nouvelle image de 3.4 GB. L'ancienne reste temporairement. Après la mise à jour, toujours lancer :

```bash
ha su repair
```

Depuis root host si possible :
```bash
docker image prune -a
```

---

## CE QU'IL NE FAUT JAMAIS FAIRE

- **Recommander "Déplacer le disque de données" vers SSD USB** — crash complet déjà vécu, 2 jours de restauration
- **Installer Whisper, Piper, VS Code, ESPHome compilateur** — 500 MB à 1.5 GB chacun, trop lourd pour 32 GB
- **Dépasser 18 add-ons** — seuil critique de stockage sur eMMC 32 GB
- **Écrire en boucle sur le disque** (scripts de monitoring fréquent) — accélère l'usure eMMC
- **ha os datadisk wipe** — efface TOUT, factory reset
- **Supprimer des fichiers dans /mnt/data/docker/ manuellement** — casse containerd, peut bricker le système
- **Désinstaller MariaDB, Z2M, Mosquitto, Linky, DuckDNS** — add-ons critiques

---

## ADD-ONS INSTALLÉS (au 22/07/2026)

### Critiques — NE JAMAIS TOUCHER

| Add-on | Slug | Taille | Rôle |
|--------|------|--------|------|
| Zigbee2MQTT | 45df7312_zigbee2mqtt | 276 MB | Pilote 110+ devices Zigbee |
| MariaDB | core_mariadb | 442 MB | Recorder (purge_keep_days: 30) |
| Mosquitto | core_mosquitto | 276 MB | Broker MQTT |
| ha-linky | cf6b56a3_linky | 442 MB | Données Linky/EDF |
| DuckDNS | core_duckdns | 92 MB | DNS dynamique |
| Samba | core_samba | 218 MB | Partage réseau |
| Advanced SSH | a0d7b954_ssh | 491 MB | Accès terminal |

### Importants — Garder

| Add-on | Slug | Taille | Rôle |
|--------|------|--------|------|
| Google Drive Backup | cebe7a76_hassio_google_drive_backup | 512 MB | Sauvegardes cloud |
| Node-RED | a0d7b954_nodered | 764 MB | Automations visuelles |
| Matter Server | core_matter_server | 803 MB | Protocole Matter |
| Matterbridge | 246dd49f_matterbridge | 373 MB | Bridge Matter |
| phpMyAdmin | a0d7b954_phpmyadmin | 243 MB | Admin MariaDB |
| NetAlertX | db21ed7f_netalertx | 448 MB | Surveillance réseau |
| eWeLink Smart Home | 81bc2df9_ewelink | 1.16 GB | Portail Adyx + devices |
| Strix | 691a7230_strix | 198 MB | Gestion HA |
| HACS | cb646a50_get | — | Intégrations communautaires |

### Désinstallés (22/07/2026, gain 5.5 GB)

- core_whisper (reconnaissance vocale IA)
- core_piper (synthèse vocale IA)
- a0d7b954_vscode (VS Code Server)
- core_configurator (éditeur, redondant)
- 81bc2df9_sonoff_dongle_flasher_for_ihost (usage unique)

---

## PLAN DE SURVIE eMMC

### Prévention usure

- **Backup réseau vers NAS Synology DS214** — configurer un partage SMB pour que les sauvegardes n'écrivent PAS sur le eMMC
- **Limiter les entités recorder** — exclure les sensors à haute fréquence inutiles
- **Pas de swap si possible** — le swapfile (1.3 GB) est un tueur de flash

### Quand le eMMC lâchera (inévitable)

1. Acheter un **Raspberry Pi 4 (4GB) ou Pi 5** (environ 60 euros)
2. Flasher HA OS sur un **SSD USB 128 GB** (environ 20 euros) — pas de carte SD
3. Booter le Pi sur le SSD
4. Restaurer le backup depuis le NAS — 30 minutes, tout revient
5. Le Zigbee2MQTT fonctionne si on garde le même dongle USB Zigbee

Budget migration : environ 80-100 euros | Temps : 1 heure

---

## HISTORIQUE INTERVENTIONS

| Date | Action | Résultat |
|------|--------|---------|
| 22/07/2026 | Diagnostic complet via root host port 22222 | 18.5 GB Docker (containerd + rootfs) identifié |
| 22/07/2026 | Désinstallation 5 add-ons inutilisés | Gain 5.5 GB (Système 18.7 vers 13.2 GB) |
| 22/07/2026 | docker image prune -a | Gain 52 MB (1 image orpheline) |
| 22/07/2026 | ha su repair | Nettoyage Supervisor OK |
| 22/07/2026 | Config accès root port 22222 | Clé USB CONFIG branchée en permanence |

---

*Ce document est la référence pour toute intervention sur le HA Green de Philippe.*
*Ne pas gaspiller de tokens à redécouvrir ce qui est documenté ici.*
*Repo : https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA*
