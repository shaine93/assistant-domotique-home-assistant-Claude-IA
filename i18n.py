# =============================================================================
# LOCALISATION FR/EN — AssistantIA Domotique
# =============================================================================
# Toutes les chaînes utilisateur dans un seul fichier.
# Le script charge la langue depuis config.json ("lang": "fr" ou "en").
# =============================================================================

LANG = {
    "fr": {
        # Cycles
        "cycle_start": "🔄 {nom} en marche",
        "cycle_power": "Puissance : {watts}W | {heure}",
        "cycle_solar_cover": "☀️ Couverture solaire : {pct}%",
        "cycle_end": "✅ {nom} terminé — {duree} min",
        "cycle_cost_solar_free": "☀️ {kwh} kWh — 100% solaire, gratuit !",
        "cycle_cost_solar_partial": "💰 {kwh} kWh — {cout}€ ({pct}% solaire, économie {eco}€)",
        "cycle_cost_grid": "💰 {kwh} kWh — {cout}€",
        "cycle_month_savings": "📈 Ce mois : {euros}€ économisés",

        # Rappels
        "rappel_linge_chaud": "👕 {nom} — Linge chaud !\nSéchage terminé ({duree} min).\nSortez le linge — plus facile à plier.\n⏳ Défroissage possible, fin dans ~{grace} min.",
        "rappel_lave_linge": "🧺 {nom} — Cycle terminé !\nDurée : {duree} min.\n🚪 Hublot se déverrouille dans ~5 min.\nPréparez le sèche-linge ou l'étendoir.",
        "rappel_vaisselle": "🍽️ {nom} — Vaisselle prête !\nCycle terminé ({duree} min).\n⚠️ Attention vaisselle chaude — laissez refroidir 10 min.",
        "rappel_autre": "✅ {nom} — Cycle en fin.\nDurée : {duree} min.",

        # Sniper
        "sniper_on": "🎯 Mode sniper activé — polling {sec}s",
        "sniper_off": "😴 Mode veille — polling {sec}s",

        # Appareils
        "appareil_question": "🔌 Quel appareil est branché sur :\n**{nom}** ?",
        "appareil_restant": "({nb} prise(s) restante(s))",
        "appareil_done": "✅ Configuration des appareils terminée !\nLe script sait maintenant quel appareil est sur chaque prise.",
        "appareil_lave_linge": "🧺 Lave-linge",
        "appareil_seche_linge": "👕 Sèche-linge",
        "appareil_lave_vaisselle": "🍽️ Lave-vaisselle",
        "appareil_congelateur": "❄️ Congélateur",
        "appareil_autre": "🔌 Autre",
        "appareil_ignorer": "⬜ Ignorer",

        # Wizard
        "wizard_welcome": "🏠 BIENVENUE — AssistantIA Domotique",
        "wizard_ha_url": "📡 ÉTAPE 1/4 — Home Assistant\nEnvoyez-moi l'URL de votre Home Assistant.",
        "wizard_ha_token": "📡 ÉTAPE 2/4 — Token d'accès\nEnvoyez-moi votre token HA longue durée (eyJ...)",
        "wizard_anthropic": "🧠 ÉTAPE 3/4 — Clé API Anthropic\nEnvoyez-moi la clé (sk-ant-...)",
        "wizard_sms": "🔐 ÉTAPE 4/4 — Sécurité (code de déverrouillage)",
        "wizard_complete": "🎉 CONFIGURATION TERMINÉE",

        # Erreurs
        "erreur_titre": "🔴 {nb} ERREUR(S) DÉTECTÉE(S)",
    },
    "en": {
        # Cycles
        "cycle_start": "🔄 {nom} started",
        "cycle_power": "Power: {watts}W | {heure}",
        "cycle_solar_cover": "☀️ Solar coverage: {pct}%",
        "cycle_end": "✅ {nom} done — {duree} min",
        "cycle_cost_solar_free": "☀️ {kwh} kWh — 100% solar, free!",
        "cycle_cost_solar_partial": "💰 {kwh} kWh — {cout}€ ({pct}% solar, saved {eco}€)",
        "cycle_cost_grid": "💰 {kwh} kWh — {cout}€",
        "cycle_month_savings": "📈 This month: {euros}€ saved",

        # Rappels
        "rappel_linge_chaud": "👕 {nom} — Warm clothes!\nDrying done ({duree} min).\nTake out now — easier to fold.\n⏳ Anti-crease running, ~{grace} min left.",
        "rappel_lave_linge": "🧺 {nom} — Cycle done!\nDuration: {duree} min.\n🚪 Door unlocks in ~5 min.\nPrepare the dryer or clothesline.",
        "rappel_vaisselle": "🍽️ {nom} — Dishes ready!\nCycle done ({duree} min).\n⚠️ Caution: dishes are hot — wait 10 min.",
        "rappel_autre": "✅ {nom} — Cycle ending.\nDuration: {duree} min.",

        # Sniper
        "sniper_on": "🎯 Sniper mode — polling {sec}s",
        "sniper_off": "😴 Idle mode — polling {sec}s",

        # Appareils
        "appareil_question": "🔌 What appliance is on:\n**{nom}**?",
        "appareil_restant": "({nb} plug(s) remaining)",
        "appareil_done": "✅ Appliance setup complete!\nThe script now knows what's on each plug.",
        "appareil_lave_linge": "🧺 Washing machine",
        "appareil_seche_linge": "👕 Dryer",
        "appareil_lave_vaisselle": "🍽️ Dishwasher",
        "appareil_congelateur": "❄️ Freezer",
        "appareil_autre": "🔌 Other",
        "appareil_ignorer": "⬜ Ignore",

        # Wizard
        "wizard_welcome": "🏠 WELCOME — AssistantIA Home",
        "wizard_ha_url": "📡 STEP 1/4 — Home Assistant\nSend me your Home Assistant URL.",
        "wizard_ha_token": "📡 STEP 2/4 — Access token\nSend me your HA long-lived token (eyJ...)",
        "wizard_anthropic": "🧠 STEP 3/4 — Anthropic API key\nSend me the key (sk-ant-...)",
        "wizard_sms": "🔐 STEP 4/4 — Security (unlock code)",
        "wizard_complete": "🎉 SETUP COMPLETE",

        # Erreurs
        "erreur_titre": "🔴 {nb} ERROR(S) DETECTED",
    }
}

def t(key, **kwargs):
    """Traduit une clé dans la langue configurée."""
    lang = "fr"  # Default, overridden by config
    try:
        from assistant import CFG
        lang = CFG.get("lang", "fr")
    except Exception:
        pass
    texts = LANG.get(lang, LANG["fr"])
    template = texts.get(key, LANG["fr"].get(key, key))
    try:
        return template.format(**kwargs)
    except Exception:
        return template
