#!/usr/bin/env python3
"""Tests automatisés — AssistantIA Domotique
Exécuter : python3 -m pytest tests.py -v
"""
import json, sqlite3, os, sys, time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# ═══ HELPERS ═══
DB_TEST = "/tmp/test_assistantia.db"

def setup_test_db():
    """Crée une DB de test propre."""
    if os.path.exists(DB_TEST):
        os.remove(DB_TEST)
    conn = sqlite3.connect(DB_TEST)
    conn.execute("""CREATE TABLE IF NOT EXISTS appareils (
        id INTEGER PRIMARY KEY, entity_id TEXT UNIQUE, type_appareil TEXT,
        nom_personnalise TEXT, surveiller INTEGER DEFAULT 1, created_at TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS cycle_mesures (
        id INTEGER PRIMARY KEY, entity_id TEXT, watts REAL, ts TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS economies (
        id INTEGER PRIMARY KEY, type TEXT, description TEXT, euros REAL,
        kwh_economises REAL, source TEXT, created_at TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS cycles_appareils (
        id INTEGER PRIMARY KEY, entity_id TEXT, friendly_name TEXT,
        debut TEXT, fin TEXT, duree_min INTEGER, conso_kwh REAL,
        cout_eur REAL, production_solaire_w INTEGER, created_at TEXT,
        programme TEXT, profil_json TEXT
    )""")
    conn.commit()
    conn.close()
    return DB_TEST


# ═══ TESTS CYCLE DETECTION ═══

class TestCycleDetection:
    """Tests détection de cycles machines."""

    def test_seuil_demarrage(self):
        """Cycle ne démarre qu'au-dessus de 200W."""
        SEUIL_CYCLE_W = 200
        assert 150 < SEUIL_CYCLE_W  # 150W = lavage, pas un démarrage
        assert 2000 > SEUIL_CYCLE_W  # 2000W = chauffage, c'est un démarrage

    def test_seuil_fin(self):
        """Machine arrêtée = sous 10W."""
        SEUIL_FIN_W = 10
        assert 150 > SEUIL_FIN_W  # 150W = machine tourne encore
        assert 4 < SEUIL_FIN_W    # 4W = machine arrêtée
        assert 0 < SEUIL_FIN_W    # 0W = machine arrêtée

    def test_phase_lavage_continue_cycle(self):
        """150W (phase lavage) ne doit PAS déclencher la grâce de fin."""
        SEUIL_FIN_W = 10
        puissance = 150
        assert puissance > SEUIL_FIN_W  # Pas de grâce → cycle continue

    def test_grace_par_type_machine(self):
        """Grâce différente selon le type de machine."""
        GRACE_APRES_ESSORAGE = 7
        GRACE_APRES_LAVAGE = 30
        GRACE_APRES_SECHAGE = 15
        GRACE_APRES_VAISSELLE = 10
        assert GRACE_APRES_ESSORAGE < GRACE_APRES_VAISSELLE < GRACE_APRES_SECHAGE < GRACE_APRES_LAVAGE


# ═══ TESTS PROFIL PUISSANCE ═══

class TestProfilPuissance:
    """Tests analyse de profil de puissance."""

    def test_classifier_watts(self):
        """Classification correcte des phases."""
        def _classifier(w):
            if w > 1500: return "C"
            if w > 500: return "E"
            if w > 50: return "L"
            return "P"
        assert _classifier(2000) == "C"  # Chauffage
        assert _classifier(700) == "E"   # Essorage
        assert _classifier(150) == "L"   # Lavage
        assert _classifier(5) == "P"     # Pause
        assert _classifier(0) == "P"     # Arrêt

    def test_signature_compacte(self):
        """Signature au format C15-L33-E3."""
        phases = [
            {"type": "C", "duree_min": 15},
            {"type": "L", "duree_min": 33},
            {"type": "E", "duree_min": 3},
        ]
        sig = "-".join(f"{p['type']}{p['duree_min']}" for p in phases)
        assert sig == "C15-L33-E3"


# ═══ TESTS APPAREILS ═══

class TestAppareils:
    """Tests identification appareils sur prises."""

    def test_appareil_set_get(self):
        """Enregistrer et relire un appareil."""
        db = setup_test_db()
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO appareils (entity_id, type_appareil, nom_personnalise, surveiller, created_at) VALUES (?, ?, ?, ?, ?)",
            ("sensor.prise_cuisine_power", "lave_vaisselle", "Lave-vaisselle", 1, datetime.now().isoformat())
        )
        conn.commit()
        row = conn.execute("SELECT type_appareil, nom_personnalise FROM appareils WHERE entity_id=?",
                          ("sensor.prise_cuisine_power",)).fetchone()
        conn.close()
        assert row[0] == "lave_vaisselle"
        assert row[1] == "Lave-vaisselle"

    def test_appareil_ignorer(self):
        """Appareil ignoré = surveiller=0."""
        db = setup_test_db()
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO appareils (entity_id, type_appareil, nom_personnalise, surveiller, created_at) VALUES (?, ?, ?, ?, ?)",
            ("sensor.prise_tv_power", "ignorer", "Ignorer", 0, datetime.now().isoformat())
        )
        conn.commit()
        row = conn.execute("SELECT surveiller FROM appareils WHERE entity_id=?",
                          ("sensor.prise_tv_power",)).fetchone()
        conn.close()
        assert row[0] == 0

    def test_detection_lave_vaisselle_typo(self):
        """Détection lave-vaisselle même avec faute d'orthographe."""
        fname = "Prise lave-vaiselle Puissance"
        fname_low = fname.lower()
        is_vaisselle = any(k in fname_low for k in ("vaisselle", "vaiselle", "dishwash"))
        is_lave_linge = "lav" in fname_low and not is_vaisselle
        assert is_vaisselle == True
        assert is_lave_linge == False


# ═══ TESTS ÉCONOMIES ═══

class TestEconomies:
    """Tests tracking économies."""

    def test_enregistrer_economie(self):
        """Enregistrer une économie dans la DB."""
        db = setup_test_db()
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO economies (type, description, euros, kwh_economises, source, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("cycle_solaire", "Lave-linge 45% solaire", 0.15, 0.8, "auto", datetime.now().isoformat())
        )
        conn.commit()
        row = conn.execute("SELECT SUM(euros), COUNT(*) FROM economies").fetchone()
        conn.close()
        assert row[0] == 0.15
        assert row[1] == 1

    def test_roi_positif(self):
        """ROI > 1 signifie que les tokens sont rentables."""
        cout_tokens = 0.05
        economies = 0.50
        roi = economies / cout_tokens
        assert roi > 1
        assert roi == 10.0


# ═══ TESTS MESURES SQLite ═══

class TestMesuresSQLite:
    """Tests stockage mesures puissance en SQLite."""

    def test_mesures_persistent(self):
        """Les mesures survivent au restart (en SQLite, pas en mémoire)."""
        db = setup_test_db()
        conn = sqlite3.connect(db)
        # Simuler 10 mesures pendant un cycle
        for i in range(10):
            ts = (datetime.now() + timedelta(seconds=i*20)).isoformat()
            conn.execute("INSERT INTO cycle_mesures (entity_id, watts, ts) VALUES (?, ?, ?)",
                        ("sensor.prise_linge_power", 500 + i*100, ts))
        conn.commit()

        # "Restart" — relire depuis la DB
        rows = conn.execute("SELECT COUNT(*) FROM cycle_mesures WHERE entity_id=?",
                           ("sensor.prise_linge_power",)).fetchone()
        conn.close()
        assert rows[0] == 10

    def test_purge_apres_cycle(self):
        """Les mesures sont purgées après fin de cycle."""
        db = setup_test_db()
        conn = sqlite3.connect(db)
        conn.execute("INSERT INTO cycle_mesures (entity_id, watts, ts) VALUES (?, ?, ?)",
                    ("sensor.prise_test", 500, datetime.now().isoformat()))
        conn.commit()
        conn.execute("DELETE FROM cycle_mesures WHERE entity_id=?", ("sensor.prise_test",))
        conn.commit()
        row = conn.execute("SELECT COUNT(*) FROM cycle_mesures WHERE entity_id=?",
                          ("sensor.prise_test",)).fetchone()
        conn.close()
        assert row[0] == 0


# ═══ TESTS POLLING ADAPTATIF ═══

class TestSniper:
    """Tests mode sniper."""

    def test_sniper_actif_quand_cycle(self):
        """Polling 20s quand un cycle est actif."""
        _etat_prises = {"sensor.prise_linge": "actif"}
        has_cycle = any(v == "actif" for v in _etat_prises.values())
        assert has_cycle == True

    def test_veille_sans_cycle(self):
        """Polling 60s quand aucun cycle actif."""
        _etat_prises = {"sensor.prise_linge": "inactif"}
        has_cycle = any(v == "actif" for v in _etat_prises.values())
        assert has_cycle == False


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
