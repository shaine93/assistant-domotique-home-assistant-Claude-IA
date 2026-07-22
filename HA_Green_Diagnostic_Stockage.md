# Diagnostic et Nettoyage Stockage — Home Assistant Green (eMMC 32 GB)

> **Date** : 22/07/2026  
> **Auteur** : Philippe (shaine93) — assisté par Claude  
> **Contexte** : HA Green, HA OS 18.1, HA Core 2026.7.3, Supervisor 2026.07.3  
> **Problème initial** : Système = 18.7 GB, Espace libre = 4.3 GB sur 28 GB

---

## TL;DR — Diagnostic final

**Il n'y a pas de fichier fantôme, pas de bug, pas de fuite.** Les 13-18 GB de "Système" sont le poids réel des images containers Docker internes gérées par le Supervisor HA OS. Chaque add-on = un container avec sa propre image. Sur un eMMC 32 GB avec 22+ add-ons, c'est structurellement impossible d'avoir plus de 10 GB libres.

**Solution définitive : déplacer le disque de données sur un SSD USB (128 GB, ~20€).**

---

## Architecture HA OS — Ce qu'il faut comprendre

Même sur un HA Green sans Docker "visible", **HA OS repose sur containerd/Docker en interne** :

- Chaque add-on = 1 container avec sa propre image
- HA Core = 1 container (~3.4 GB)
- Supervisor = 1 container (~500 MB)
- Services internes (DNS, Audio, CLI, Multicast, Observer) = 5 containers

Les images sont stockées dans :
- `/mnt/data/docker/containerd/` — snapshots des images (layers)
- `/mnt/data/docker/rootfs/overlayfs/` — filesystem racine de chaque container

**Ces dossiers sont invisibles** depuis l'interface HA et depuis les add-ons (même avec SSH). Ils apparaissent dans la catégorie "Système" des métriques du disque.

---

## Répartition réelle du disque (diagnostiquée le 22/07/2026)

### Vue globale (`du -sh /mnt/data/* | sort -rh`)

| Dossier | Taille | Contenu |
|---------|--------|---------|
| `/mnt/data/docker/` | **18.5 GB** | Images containers, snapshots, rootfs |
| `/mnt/data/supervisor/` | 5.1 GB | Backups, config HA, données add-ons |
| `/mnt/data/swapfile` | 1.3 GB | Swap système |
| `/mnt/data/logs/` | 499 MB | Journaux systemd |

### Détail Docker

| Sous-dossier | Taille |
|-------------|--------|
| `/mnt/data/docker/containerd/` | 10.1 GB (snapshots images) |
| `/mnt/data/docker/rootfs/overlayfs/` | 8.4 GB (filesystem containers) |

### Détail Supervisor (bind mounts visibles)

| Point de montage | Taille |
|-----------------|--------|
| `/backup` | 2.1 GB (2 sauvegardes automatiques) |
| `/homeassistant` | 1.1 GB (config HA + DB) |
| `/addon_configs` | 261 MB |
| `/var/log/journal` | 480 MB |

### Poids des images containers (22 actives, 10.88 GB total)

| Image | Taille |
|-------|--------|
| HA Core (green-homeassistant:2026.7.3) | 3.38 GB |
| eWeLink iHost Smart Home | 1.16 GB |
| Matter Server | 803 MB |
| Node-RED | 764 MB |
| Google Drive Backup | 512 MB |
| Supervisor | 499 MB |
| Advanced SSH & Web Terminal | 491 MB |
| NetAlertX | 448 MB |
| MariaDB | 442 MB |
| ha-linky | 442 MB |
| Matterbridge | 373 MB |
| Mosquitto | 276 MB |
| Zigbee2MQTT | 276 MB |
| phpMyAdmin | 243 MB |
| Samba | 218 MB |
| Strix | 198 MB |
| Audio (interne) | 131 MB |
| DNS (interne) | 111 MB |
| DuckDNS | 92 MB |
| CLI (interne) | 88 MB |

---

## Actions de nettoyage réalisées (22/07/2026)

### Add-ons désinstallés (gain : ~5.4 GB)

| Add-on | Taille estimée | Raison |
|--------|---------------|--------|
| core_whisper | ~1.5 GB | Non utilisé (reconnaissance vocale IA) |
| core_piper | ~500 MB | Non utilisé (synthèse vocale IA) |
| a0d7b954_vscode | ~1 GB | Non utilisé (VS Code Server) |
| core_configurator | ~130 MB | Redondant |
| sonoff_dongle_flasher | ~100 MB | Usage unique (flash dongle) |

### Autres nettoyages

| Action | Commande | Gain |
|--------|----------|------|
| Repair Supervisor | `ha su repair` | Nettoyage états incohérents |
| Purge images orphelines | `docker image prune -a` | 52 MB |

### Résultat

- **Avant** : Système 18.7 GB, Libre 4.3 GB
- **Après** : Système 13.2 GB, Libre 9.9 GB
- **Gain total** : ~5.5 GB

---

## Procédures de maintenance

### Accès root host (port 22222 via clé USB)

L'accès root au host HA OS est nécessaire pour diagnostiquer les problèmes de stockage. L'add-on SSH (même Advanced) ne donne accès qu'au container.

1. Préparer une clé USB formatée **FAT32**, partition nommée **CONFIG** (majuscules)
2. Générer une clé SSH sur le Mac : `ssh-keygen -t ed25519`
3. Copier la clé publique : `cp ~/.ssh/id_ed25519.pub /Volumes/CONFIG/authorized_keys`
4. Vérifier : le fichier doit s'appeler exactement `authorized_keys` (pas `.pub`, pas `.txt`)
5. Éjecter la clé USB du Mac, la brancher sur le HA Green
6. Redémarrer le host : `ha host reboot` (depuis le terminal HA)
7. Connexion depuis le Mac : `ssh root@192.168.1.76 -p 22222`

**Alternative sans clé USB** (depuis Advanced SSH avec Protection mode désactivé) :
```bash
nsenter -t 1 -m -u -i -n -- /bin/bash
```
Note : accès limité — pas de mount, pas de journalctl, pas de docker.

### Script de diagnostic complet (à lancer en root host)

```bash
echo "=== Vue globale ==="
du -sh /mnt/data/* | sort -rh

echo "=== Docker détail ==="
du -sh /mnt/data/docker/* | sort -rh

echo "=== Docker images ==="
docker system df
docker image ls --format "table {{.Size}}\t{{.Repository}}:{{.Tag}}" | sort -rh | head -20

echo "=== Containerd snapshots ==="
du -sh /mnt/data/docker/containerd/daemon/*/* | sort -rh | head -10

echo "=== Rootfs overlayfs ==="
du -sh /mnt/data/docker/rootfs/overlayfs/* | sort -rh | head -10

echo "=== Supervisor ==="
du -sh /mnt/data/supervisor/* | sort -rh

echo "=== Journaux ==="
journalctl --disk-usage

echo "=== Gros fichiers ==="
find /mnt/data -type f -size +100M 2>/dev/null | head -20
```

### Nettoyage périodique (en root host)

```bash
# Purger images Docker orphelines (tous les add-ons doivent tourner)
docker image prune -a

# Purger journaux systemd (garder 2 jours)
journalctl --rotate
journalctl --vacuum-time=2d

# Repair Supervisor
ha su repair

# Purge recorder HA (via Services dans l'UI HA)
# Service: recorder.purge / keep_days: 30 / repack: true
```

### Commandes HA CLI utiles (sans accès root)

```bash
ha os info              # Version OS, état boot slots
ha su info              # État Supervisor, add-ons installés
ha su repair            # Nettoyage Supervisor
ha backups list         # Lister les sauvegardes
ha backups remove <slug> # Supprimer une sauvegarde
ha host reboot          # Redémarrer le host
ha hardware info        # Voir les périphériques détectés
```

---

## Stratégie long terme : rester sur eMMC 32 GB

**⚠️ La migration SSD USB ("Déplacer le disque de données") a déjà été tentée et a provoqué un crash complet avec 2 jours de remise en service. Cette option est EXCLUE.**

### Contraintes à respecter

- **Maximum ~18 add-ons** pour rester sous 15 GB de "Système"
- **Après chaque mise à jour HA Core** : lancer `ha su repair` pour purger les anciennes images (gain typique : 500 MB - 1.5 GB)
- **Ne jamais installer d'add-ons lourds** (Whisper, Piper, VS Code, ESPHome compilateur) — chacun pèse 500 MB - 1.5 GB
- **Sauvegardes** : max 2 en local, exporter vers le NAS Synology DS214

### Monitoring recommandé

Créer un sensor template dans HA pour surveiller l'espace disque :

```yaml
template:
  - sensor:
      - name: "Espace disque libre"
        unit_of_measurement: "GB"
        state: >
          {{ (states.sensor.disk_free.state | float(0)) }}
```

Créer une automatisation d'alerte si l'espace libre passe sous 5 GB.

### Maintenance trimestrielle (via SSH root port 22222)

```bash
# 1. Purge images orphelines
docker image prune -a

# 2. Purge journaux
journalctl --rotate
journalctl --vacuum-time=2d

# 3. Repair Supervisor
ha su repair

# 4. Vérifier la répartition
du -sh /mnt/data/* | sort -rh
docker image ls --format "table {{.Size}}\t{{.Repository}}:{{.Tag}}" | sort -rh | head -20
```

---

## Références communautaires

- [HA Green storage 99% full](https://community.home-assistant.io/t/home-assistant-green-storage-permanently-99-full-no-backups-possible-cause-not-identifiable/966541)
- [Running out of space on HA Green](https://community.home-assistant.io/t/running-out-of-space-on-home-assistant-green/872068)
- [Overlay2 bloating storage](https://community.home-assistant.io/t/overlay2-what-is-that-thing-why-is-it-bloating-my-storage/690909)
- [Docker overlay2 consuming all disk space](https://community.home-assistant.io/t/hassio-docker-overlay2-folder-consuming-all-disk-space/174278)
- [Debug HA OS (accès port 22222)](https://developers.home-assistant.io/docs/operating-system/debugging/)
- [Common tasks HA OS](https://www.home-assistant.io/common-tasks/os/)

---

## Leçons apprises

1. **"Système" dans les métriques HA = images containers Docker internes** — pas des fichiers temporaires ou des logs cachés
2. **HA OS utilise containerd** (depuis les versions récentes), pas Docker classique — les chemins ont changé (`/mnt/data/docker/containerd/` au lieu de `overlay2` direct)
3. **L'add-on SSH officiel ne permet pas `login` en root host** — il faut Advanced SSH & Web Terminal (Frenck) avec Protection mode désactivé, ou la méthode clé USB sur port 22222
4. **`nsenter -t 1 -m -u -i -n -- /bin/bash`** permet un accès partiel au host depuis l'add-on SSH avancé, mais sans mount ni docker
5. **`docker image prune -a`** ne libère presque rien si tous les containers tournent — le vrai gain vient de la désinstallation d'add-ons inutilisés
6. **Sur eMMC 32 GB, la limite pratique est ~15 add-ons** avant de manquer d'espace
7. **Nabucasa support ne peut pas aider** sur ce sujet — c'est un problème d'architecture, pas un bug
8. **"Déplacer le disque de données" vers SSD USB est risqué** — tentative faite, crash complet, 2 jours de restauration. Ne plus jamais essayer
9. **La gestion du eMMC 32 GB se fait par la discipline** : limiter les add-ons, purger après les mises à jour, monitorer l'espace

---

*Document créé le 22/07/2026 — Philippe / AssistantIA Domotique*
*Repo : https://github.com/shaine93/assistant-domotique-home-assistant-Claude-IA*
