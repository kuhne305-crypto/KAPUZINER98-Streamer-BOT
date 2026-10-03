"""
config.py – Theme, Rollen, Channels und Texte für den Kapuziner98-Server.

Alles was Namen, Farben und Texte angeht, steht HIER.
Willst du was umbenennen? Einfach hier ändern – der restliche Code sucht
Rollen und Channels über diese Namen.

Theme:  Yu-Gi-Oh-Spielfeld  +  Lunalight & Charmer  +  Momo Hinamori (Bleach)
        +  Tsubasa Chronicle  +  Made in Abyss
Farben: Dunkelgrün & Lila
"""

# ─────────────────────────────────────────────────────────────
#  TWITCH
# ─────────────────────────────────────────────────────────────
TWITCH_LOGIN = "kapuziner98"
TWITCH_URL = f"https://www.twitch.tv/{TWITCH_LOGIN}"
STREAMER_NAME = "Kapuziner98"

# Status vom Bot, wenn nicht live ("Schaut ...")
BOT_STATUS = "über Orth 🌙 | twitch.tv/kapuziner98"

# Wie oft Twitch gefragt wird, ob der Stream läuft (Sekunden)
TWITCH_CHECK_INTERVALL = 60
# So viele "offline"-Checks am Stück, bevor der Stream als beendet gilt
# (verhindert Doppel-Pings bei kurzen Disconnects)
OFFLINE_CHECKS_BIS_ENDE = 3


# ─────────────────────────────────────────────────────────────
#  FARBEN  (Dunkelgrün + Lila)
# ─────────────────────────────────────────────────────────────
class Farbe:
    LILA_DUNKEL = 0x5B2A86   # Lunalight / Streamer
    LILA = 0x8E44AD          # Fusion-Lila (Haupt-Embedfarbe)
    LILA_HELL = 0xAF7AC5     # Tobiume / VIP
    FLIEDER = 0xE8DAEF       # Weiße Pfeife / Admin
    GRUEN_DUNKEL = 0x145A32  # Abgrund-Grün (Stream beendet)
    GRUEN = 0x1E8449         # Emerald Bird
    SMARAGD = 0x2E8B57       # Duelist (Mitglieder)


# ─────────────────────────────────────────────────────────────
#  ROLLEN  (Reihenfolge = Reihenfolge im Server, oben → unten)
#
#  rechte:  None      = keine Extra-Rechte
#           "admin"   = Administrator
#           "mod"     = Moderations-Rechte (Kick, Timeout, Nachrichten verwalten …)
# ─────────────────────────────────────────────────────────────
ROLLEN = {
    "streamer": {
        "name": "🌙 Lunalight Leo Dancer │ Streamer",
        "farbe": Farbe.LILA_DUNKEL, "hoist": True, "rechte": None,
    },
    "admin": {
        "name": "⚪ Weiße Pfeife │ Admin",
        "farbe": Farbe.FLIEDER, "hoist": True, "rechte": "admin",
    },
    "mod": {
        "name": "🔮 Charmer │ Moderator",
        "farbe": Farbe.LILA, "hoist": True, "rechte": "mod",
    },
    "vip": {
        "name": "🍑 Tobiume │ VIP",
        "farbe": Farbe.LILA_HELL, "hoist": True, "rechte": None,
    },
    "stamm": {
        "name": "🐦 Emerald Bird │ Stammzuschauer",
        "farbe": Farbe.GRUEN, "hoist": True, "rechte": None,
    },
    "member": {
        "name": "🃏 Duelist │ Mitglied",
        "farbe": Farbe.SMARAGD, "hoist": False, "rechte": None,
    },
    # ── Self-Roles ──
    "live_ping": {
        "name": "🔔 Live-Beschwörung │ Ping",
        "farbe": 0, "hoist": False, "rechte": None,
    },
    # Weitere Self-Roles kommen hier rein (Beispiele folgen) …
}

# Wer zählt als Team (sieht Team-Bereich, darf überall schreiben)
TEAM_ROLLEN = ["streamer", "admin", "mod"]


# ─────────────────────────────────────────────────────────────
#  KATEGORIEN & CHANNELS
#
#  zugang:
#    "oeffentlich_info"  – jeder sieht es, nur Team schreibt (auch Unverifizierte)
#    "mitglieder_info"   – nur Duelists sehen es, nur Team/Bot schreibt
#    "mitglieder"        – nur Duelists sehen & schreiben
#    "voice"             – Voice für Duelists
#    "team"              – nur Team
#
#  key: interner Name, über den der Bot den Channel findet
#       (z. B. "live" = Channel für Live-Alerts)
# ─────────────────────────────────────────────────────────────
KATEGORIEN = [
    {
        "name": "🟩 FELDZAUBER ┃ ORTH",
        "zugang": "mitglieder_info",
        "channels": [
            {"key": "regeln", "name": "📜│duell-regeln", "typ": "text", "zugang": "oeffentlich_info",
             "topic": "Lies die Regeln und klick auf den Button – dann öffnet sich der Abgrund für dich."},
            {"key": "willkommen", "name": "👋│ankunft-in-orth", "typ": "text", "zugang": "oeffentlich_info",
             "topic": "Neue Duelists erreichen die Stadt am Rand des Abgrunds."},
            {"key": "ankuendigungen", "name": "📢│ankündigungen", "typ": "text",
             "topic": "News direkt von Kapuziner98."},
            {"key": "live", "name": "🔴│live-beschwörung", "typ": "text",
             "topic": "Hier wird automatisch gepostet, wenn Kapuziner98 live geht. 🌙"},
            {"key": "streamplan", "name": "📅│streamplan", "typ": "text",
             "topic": "Wann wird beschworen? Der aktuelle Wochenplan."},
            {"key": "rollen", "name": "🎴│deck-auswahl", "typ": "text",
             "topic": "Stell dein Deck zusammen – hol dir hier deine Rollen."},
        ],
    },
    {
        "name": "🟪 FUSIONS-ZONE ┃ LUNALIGHT LOUNGE",
        "zugang": "mitglieder",
        "channels": [
            {"key": "chat", "name": "🌙│mondlicht-chat", "typ": "text",
             "topic": "Der Haupt-Chat. Lunalight Fusion: aus vielen Leuten wird eine Community."},
            {"key": "medien", "name": "🪶│sakuras-federn", "typ": "text",
             "topic": "Screenshots, Clips & Erinnerungen – jede Feder zählt."},
            {"key": "memes", "name": "🏺│topf-der-gier", "typ": "text",
             "topic": "Memes. Ich aktiviere Topf der Gier und ziehe zwei Memes."},
            {"key": "fanart", "name": "🎨│fanart-galerie", "typ": "text",
             "topic": "Eure Kunstwerke."},
            {"key": "ideen", "name": "💡│ideen-und-wünsche", "typ": "text",
             "topic": "Vorschläge für Stream & Server."},
            {"key": "bot", "name": "🤍│mokona-befehle", "typ": "text",
             "topic": "Bot-Befehle hier rein."},
        ],
    },
    {
        "name": "⚔️ MONSTERZONE ┃ MASTER DUEL",
        "zugang": "mitglieder",
        "channels": [
            {"key": "md_chat", "name": "⚔️│duell-chat", "typ": "text",
             "topic": "Alles rund um Yu-Gi-Oh! Master Duel."},
            {"key": "deckbau", "name": "📋│deckbau-werkstatt", "typ": "text",
             "topic": "Decklisten, Combos, Lunalight- & Charmer-Talk."},
            {"key": "duell_anfragen", "name": "🤝│duell-anfragen", "typ": "text",
             "topic": "Raum-IDs & Freundescodes – such dir einen Gegner."},
        ],
    },
    {
        "name": "🍑 RITUAL ┃ 5. DIVISION",
        "zugang": "mitglieder",
        "channels": [
            {"key": "ros_chat", "name": "🍑│hajike-tobiume", "typ": "text",
             "topic": "BLEACH Rebirth of Souls – Hajike, Tobiume!"},
            {"key": "ros_combos", "name": "📖│kido-und-combos", "typ": "text",
             "topic": "Combos, Tipps & Tier-Listen für Rebirth of Souls."},
        ],
    },
    {
        "name": "🪶 EXTRA-DECK ┃ DIMENSIONSREISE",
        "zugang": "mitglieder",
        "channels": [
            {"key": "anime", "name": "📚│anime-und-manga", "typ": "text",
             "topic": "Reise durch alle Welten: Anime & Manga-Talk."},
            {"key": "empfehlungen", "name": "🔭│welten-empfehlungen", "typ": "text",
             "topic": "Was sollte man unbedingt schauen oder lesen?"},
            {"key": "spoiler", "name": "🕳️│spoiler-abgrund", "typ": "text",
             "topic": "Spoiler erlaubt. Betreten auf eigene Gefahr – der Fluch des Abgrunds gilt."},
        ],
    },
    {
        "name": "🕳️ FALLENKARTE ┃ DER ABGRUND",
        "zugang": "voice",
        "channels": [
            {"key": "vc1", "name": "🌲 Schicht 1 · Rand des Abgrunds", "typ": "voice"},
            {"key": "vc2", "name": "⚔️ Schicht 2 · Duell-Arena", "typ": "voice"},
            {"key": "vc3", "name": "🍑 Schicht 3 · 5. Division", "typ": "voice"},
            {"key": "vc4", "name": "🪶 Schicht 4 · Dimensionsreise", "typ": "voice"},
            {"key": "afk", "name": "💀 Schicht 6 · Ohne Wiederkehr (AFK)", "typ": "voice"},
        ],
    },
    {
        "name": "🔒 VERDECKT ┃ WEISSE PFEIFEN",
        "zugang": "team",
        "channels": [
            {"key": "team_chat", "name": "🛡️│team-chat", "typ": "text",
             "topic": "Nur fürs Team."},
            {"key": "team_notizen", "name": "📋│mod-notizen", "typ": "text",
             "topic": "Verwarnungen, Notizen, Absprachen."},
            {"key": "team_vc", "name": "⚪ Team-Besprechung", "typ": "voice"},
        ],
    },
]


# ─────────────────────────────────────────────────────────────
#  SELF-ROLES  (Panels in #deck-auswahl)
#
#  Jedes Panel = ein Embed mit Buttons. Button klicken = Rolle an,
#  nochmal klicken = Rolle weg.
#  stil: "lila" | "gruen" | "grau" | "rot"
#
#  >>> Hier kommen später die weiteren Self-Roles rein <<<
#  (Rolle oben in ROLLEN anlegen, dann hier als Button eintragen)
# ─────────────────────────────────────────────────────────────
SELFROLE_PANELS = [
    {
        "id": "benachrichtigungen",
        "titel": "🔔 BENACHRICHTIGUNGEN",
        "text": (
            f"Willst du gepingt werden, wenn **{STREAMER_NAME}** live geht?\n"
            "Klick auf den Button – nochmal klicken nimmt die Rolle wieder weg."
        ),
        "farbe": Farbe.LILA,
        "buttons": [
            {"rolle": "live_ping", "label": "Live-Beschwörung", "emoji": "🔔", "stil": "lila"},
        ],
    },
]


# ─────────────────────────────────────────────────────────────
#  TEXTE
# ─────────────────────────────────────────────────────────────
REGELN_TITEL = "📜 DUELL-REGELN · Willkommen in Orth"
REGELN_INTRO = (
    f"Schön, dass du den Weg zum Server von **{STREAMER_NAME}** gefunden hast!\n"
    "Bevor du in den Abgrund steigst, lies dir kurz die Regeln durch:"
)
REGELN = [
    ("🤝 Respekt im Duell",
     "Kein Hate, keine Beleidigungen, kein Rassismus oder Sexismus. GG statt Salz."),
    ("🚫 Verbotene Karten",
     "Kein NSFW, kein Gore, nichts Illegales – auch nicht im Profilbild oder Namen."),
    ("📵 Kein Spam",
     "Keine Massen-Pings, keine Fremdwerbung (auch nicht per DM) ohne Erlaubnis vom Team."),
    ("🕳️ Spoiler markieren",
     "Gerade bei Made in Abyss & Tsubasa: ||Spoiler|| nutzen oder ab in den Spoiler-Abgrund."),
    ("🗂️ Richtige Zone",
     "Jeder Channel hat seinen Zweck – poste da, wo es hingehört."),
    ("📜 Discord & Twitch",
     "Die Discord-Nutzungsbedingungen und Twitch-Richtlinien gelten auch hier."),
    ("⚪ Das Team hat das letzte Wort",
     "Weiße Pfeifen (Admins) und Charmer (Mods) entscheiden. Probleme? Schreib das Team an."),
]
REGELN_FOOTER = "Klick auf den Button, um die Regeln zu akzeptieren. Hajike, Tobiume! 🍑"
VERIFY_BUTTON_LABEL = "Regeln akzeptieren"
VERIFY_BUTTON_EMOJI = "🃏"

WILLKOMMEN_TITEL = "🌙 Ein neuer Duelist erreicht Orth!"
# {user} = Erwähnung, {regeln} = Link zum Regel-Channel, {server} = Servername
WILLKOMMEN_TEXT = (
    "Hey {user}, willkommen auf dem Server von **" + STREAMER_NAME + "**!\n\n"
    "Lies dir die {regeln} durch und klick auf den Button – "
    "dann öffnet sich der Abgrund für dich. 🕳️"
)

# Live-Alert – Spruch je nach Spiel (Teil des Spielnamens, klein geschrieben → Spruch)
LIVE_SPRUECHE = {
    "yu-gi-oh": "⚔️ **Es ist Zeit für ein Duell!**",
    "bleach": "🍑 **Hajike, Tobiume!**",
}
LIVE_SPRUCH_STANDARD = "🌙 **Lunalight Fusion!**"
LIVE_TEXT = "{ping} {spruch} **{name}** beschwört einen Stream!"
ENDE_TEXT = "🌑 Der Mond ist untergegangen – danke fürs Zuschauen!"

# Streamplan
STREAMPLAN_TITEL = f"📅 STREAMPLAN · {STREAMER_NAME}"
STREAMPLAN_INFO = (
    "Alle Zeiten in deutscher Zeit.\n"
    "Hol dir in der Deck-Auswahl die 🔔 Live-Ping-Rolle, dann verpasst du nichts!"
)
STREAMPLAN_TAGE = [
    ("Montag", "🌙"),
    ("Dienstag", "🔮"),
    ("Mittwoch", "🍑"),
    ("Donnerstag", "🪶"),
    ("Freitag", "🕳️"),
    ("Samstag", "🃏"),
    ("Sonntag", "🦋"),
]
STREAMPLAN_PAUSE = "*Pause – der Mond ruht*"
