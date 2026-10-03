"""
config.py – Theme, Rollen, Channels und Texte für den Kapuziner98-Server.

Alles, was Namen, Farben und Texte angeht, steht HIER.
Willst du etwas umbenennen? Einfach hier ändern und den alten Namen bei "alt"
eintragen – dann benennt /setup die bestehende Rolle bzw. den Channel automatisch um.

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

# Status vom Bot, wenn nicht live ("Schaut …")
BOT_STATUS = "über Orth 🌙 | twitch.tv/kapuziner98"

# Wie oft Twitch gefragt wird, ob der Stream läuft (Sekunden)
TWITCH_CHECK_INTERVALL = 60
# So viele Offline-Checks am Stück, bevor der Stream als beendet gilt
# (verhindert Doppel-Pings bei kurzen Disconnects)
OFFLINE_CHECKS_BIS_ENDE = 3


# ─────────────────────────────────────────────────────────────
#  FARBEN  (Dunkelgrün + Lila)
# ─────────────────────────────────────────────────────────────
class Farbe:
    LILA_DUNKEL = 0x5B2A86   # Lunalight / Streamer
    LILA = 0x8E44AD          # Fusions-Lila (Haupt-Embedfarbe)
    LILA_HELL = 0xAF7AC5     # Tobiume / VIP
    FLIEDER = 0xE8DAEF       # Weiße Pfeife / Admin
    GRUEN_DUNKEL = 0x145A32  # Abgrund-Grün (Stream beendet)
    GRUEN = 0x1E8449         # Emerald Bird
    SMARAGD = 0x2E8B57       # Duelist (Mitglieder)
    FALLE = 0xC0392B         # Autoban-Warnung


# ─────────────────────────────────────────────────────────────
#  ROLLEN  (Reihenfolge = Reihenfolge im Server, oben → unten)
#
#  rechte:  None    = keine Extra-Rechte
#           "admin" = Administrator
#           "mod"   = Moderationsrechte (Kick, Timeout, Nachrichten verwalten …)
#  alt:     frühere Namen → /setup benennt sie automatisch um
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
    "kuenstler": {
        "name": "🎨 Federkiel │ Künstler",
        "farbe": Farbe.LILA_HELL, "hoist": False, "rechte": None,
    },
    "member": {
        "name": "🃏 Duelist │ Mitglied",
        "farbe": Farbe.SMARAGD, "hoist": False, "rechte": None,
    },
    # ── Ping-Rollen (Reaktionsrollen) ──
    "live_ping": {
        "name": "🔴 Live-Beschwörung │ Stream-Ping",
        "farbe": 0, "hoist": False, "rechte": None,
        "alt": ["🔔 Live-Beschwörung │ Ping"],
    },
    "giveaway_ping": {
        "name": "🎁 Topf der Gier │ Giveaway-Ping",
        "farbe": 0, "hoist": False, "rechte": None,
    },
    "umfrage_ping": {
        "name": "📊 Orakel │ Umfrage-Ping",
        "farbe": 0, "hoist": False, "rechte": None,
    },
    "social_ping": {
        "name": "📱 Weltenreise │ Social-Ping",
        "farbe": 0, "hoist": False, "rechte": None,
    },
}

# Wer zählt als Team (sieht den Team-Bereich, darf überall schreiben, wird nie autogebannt)
TEAM_ROLLEN = ["streamer", "admin", "mod"]


# ─────────────────────────────────────────────────────────────
#  KATEGORIEN & CHANNELS
#
#  zugang:
#    "oeffentlich_info" – jeder sieht es, nur das Team schreibt (auch Unverifizierte)
#    "mitglieder_info"  – nur Duelists sehen es, nur Team/Bot schreibt
#    "mitglieder"       – nur Duelists sehen und schreiben
#    "kuenstler"        – Duelists sehen + reagieren, nur Künstler posten
#    "autoban"          – jeder sieht es, jeder KANN schreiben → wird gebannt
#    "voice"            – Voice für Duelists
#    "team"             – nur Team
#
#  key: interner Name, über den der Bot den Channel findet
#  alt: frühere Namen → /setup benennt automatisch um
# ─────────────────────────────────────────────────────────────
KATEGORIEN = [
    {
        "name": "🟩 FELDZAUBER ┃ ORTH",
        "zugang": "mitglieder_info",
        "channels": [
            {"key": "regeln", "name": "📜│duell-regeln", "typ": "text", "zugang": "oeffentlich_info",
             "topic": "Lies die Regeln und klick auf den Button – dann öffnet sich der Abgrund für dich."},
            {"key": "autoban", "name": "🚨│autoban-fallgrube", "typ": "text", "zugang": "autoban",
             "topic": "⚠️ NICHT REINSCHREIBEN! Wer hier schreibt, wird sofort und dauerhaft gebannt."},
            {"key": "willkommen", "name": "👋│ankunft-in-orth", "typ": "text", "zugang": "oeffentlich_info",
             "topic": "Neue Duelists erreichen die Stadt am Rand des Abgrunds."},
            {"key": "ankuendigungen", "name": "📢│ankündigungen", "typ": "text",
             "topic": "News direkt von Kapuziner98."},
            {"key": "live", "name": "🔴│live-beschwörung", "typ": "text",
             "topic": "Hier wird automatisch gepostet, wenn Kapuziner98 live geht. 🌙"},
            {"key": "streamplan", "name": "📅│streamplan", "typ": "text",
             "topic": "Wann wird beschworen? Hier steht der aktuelle Wochenplan."},
            {"key": "rollen", "name": "🎴│deck-auswahl", "typ": "text",
             "topic": "Stell dein Deck zusammen – hol dir hier per Reaktion deine Rollen."},
        ],
    },
    {
        "name": "🟪 FUSIONSZONE ┃ LUNALIGHT LOUNGE",
        "alt": ["🟪 FUSIONS-ZONE ┃ LUNALIGHT LOUNGE"],
        "zugang": "mitglieder",
        "channels": [
            {"key": "chat", "name": "🌙│mondlicht-chat", "typ": "text",
             "topic": "Der Hauptchat. Lunalight-Fusion: Aus vielen Leuten wird eine Community."},
            {"key": "medien", "name": "🪶│sakuras-federn", "typ": "text",
             "topic": "Screenshots, Clips und Erinnerungen – jede Feder zählt."},
            {"key": "memes", "name": "🏺│topf-der-gier", "typ": "text",
             "topic": "Memes. Ich aktiviere „Topf der Gier“ und ziehe zwei Memes."},
            {"key": "galerie", "name": "🎨│künstler-galerie", "typ": "text", "zugang": "kuenstler",
             "alt": ["🎨│fanart-galerie"],
             "topic": "Hier posten nur Künstler – alle anderen dürfen schauen und reagieren. "
                      "Künstler-Rolle gibt's in der Deck-Auswahl."},
            {"key": "ideen", "name": "💡│ideen-und-wünsche", "typ": "text",
             "topic": "Vorschläge für Stream und Server."},
            {"key": "bot", "name": "🤍│mokona-befehle", "typ": "text",
             "topic": "Bot-Befehle bitte hier rein."},
        ],
    },
    {
        "name": "⚔️ MONSTERZONE ┃ MASTER DUEL",
        "zugang": "mitglieder",
        "channels": [
            {"key": "md_chat", "name": "⚔️│duell-chat", "typ": "text",
             "topic": "Alles rund um Yu-Gi-Oh! Master Duel."},
            {"key": "deckbau", "name": "📋│deckbau-werkstatt", "typ": "text",
             "topic": "Decklisten, Combos, Lunalight- und Charmer-Talk."},
            {"key": "duell_anfragen", "name": "🤝│duell-anfragen", "typ": "text",
             "topic": "Raum-IDs und Freundescodes – such dir hier einen Gegner."},
        ],
    },
    {
        "name": "🍑 RITUAL ┃ 5. DIVISION",
        "zugang": "mitglieder",
        "channels": [
            {"key": "ros_chat", "name": "🍑│hajike-tobiume", "typ": "text",
             "topic": "BLEACH Rebirth of Souls – Hajike, Tobiume!"},
            {"key": "ros_combos", "name": "📖│kido-und-combos", "typ": "text",
             "topic": "Combos, Tipps und Tierlisten für Rebirth of Souls."},
        ],
    },
    {
        "name": "🪶 EXTRA-DECK ┃ DIMENSIONSREISE",
        "zugang": "mitglieder",
        "channels": [
            {"key": "anime", "name": "📚│anime-und-manga", "typ": "text",
             "topic": "Reise durch alle Welten: Anime- und Manga-Talk."},
            {"key": "empfehlungen", "name": "🔭│welten-empfehlungen", "typ": "text",
             "topic": "Was sollte man unbedingt schauen oder lesen?"},
            {"key": "spoiler", "name": "🕳️│spoiler-abgrund", "typ": "text",
             "topic": "Spoiler erlaubt. Betreten auf eigene Gefahr – hier gilt der Fluch des Abgrunds."},
        ],
    },
    {
        "name": "🎙️ SPIELFELD ┃ DUELL-ARENA",
        "alt": ["🕳️ FALLENKARTE ┃ DER ABGRUND", "🟥 FALLENKARTE ┃ DER ABGRUND"],
        "zugang": "voice",
        "channels": [
            {"key": "warteraum", "name": "⏳ Standby-Phase · Warteraum", "typ": "voice",
             "alt": ["🌲 Schicht 1 · Rand des Abgrunds"]},
            {"key": "duell1", "name": "🌙 Duellraum 1 · Lunalight", "typ": "voice",
             "alt": ["⚔️ Schicht 2 · Duell-Arena"]},
            {"key": "duell2", "name": "🔮 Duellraum 2 · Charmer", "typ": "voice",
             "alt": ["🍑 Schicht 3 · 5. Division"]},
            {"key": "duell3", "name": "🍑 Duellraum 3 · 5. Division", "typ": "voice",
             "alt": ["🪶 Schicht 4 · Dimensionsreise"]},
            {"key": "duell4", "name": "🪶 Duellraum 4 · Dimensionsreise", "typ": "voice"},
            {"key": "duell5", "name": "🕳️ Duellraum 5 · Abgrund", "typ": "voice"},
            {"key": "afk", "name": "💀 Reich der Schatten · AFK", "typ": "voice",
             "alt": ["💀 Schicht 6 · Ohne Wiederkehr (AFK)"]},
        ],
    },
    {
        "name": "🔒 VERDECKT ┃ WEISSE PFEIFEN",
        "zugang": "team",
        "channels": [
            {"key": "team_chat", "name": "🛡️│team-chat", "typ": "text",
             "topic": "Nur fürs Team."},
            {"key": "team_notizen", "name": "📋│mod-notizen", "typ": "text",
             "topic": "Verwarnungen, Notizen und Absprachen."},
            {"key": "bot_log", "name": "🤖│bot-log", "typ": "text",
             "topic": "Hier meldet der Bot z. B. Autobans aus der Fallgrube."},
            {"key": "team_vc", "name": "⚪ Team-Besprechung", "typ": "voice"},
        ],
    },
]


# ─────────────────────────────────────────────────────────────
#  REAKTIONSROLLEN  (Panels in #deck-auswahl)
#
#  Reaktion drauf = Rolle bekommen, Reaktion weg = Rolle weg.
#  Neue Rolle: oben in ROLLEN anlegen, hier eintragen, deployen,
#  /setup und dann /panel art:Reaktionsrollen
#
#  Tipp: Emojis OHNE "️" (Variation Selector) nehmen,
#  also z. B. 🔴 🎁 📊 📱 🎨 – die funktionieren als Reaktion am zuverlässigsten.
#  {galerie} wird durch einen Link zur Künstler-Galerie ersetzt.
# ─────────────────────────────────────────────────────────────
REAKTIONS_PANELS = [
    {
        "titel": "🔔 Wofür möchtest du gepingt werden?",
        "intro": "Wähle deine Rollen mit den Reaktionen unten aus!",
        "farbe": Farbe.LILA,
        "rollen": [
            {"emoji": "🔴", "rolle": "live_ping", "label": "Stream-Ping",
             "info": f"wenn {STREAMER_NAME} live geht"},
            {"emoji": "🎁", "rolle": "giveaway_ping", "label": "Giveaway-Ping",
             "info": "bei Gewinnspielen"},
            {"emoji": "📊", "rolle": "umfrage_ping", "label": "Umfrage-Ping",
             "info": "bei Abstimmungen"},
            {"emoji": "📱", "rolle": "social_ping", "label": "Social-Ping",
             "info": "bei neuen Social-Media-Posts"},
        ],
    },
    {
        "titel": "🎨 Bist du Künstler?",
        "intro": ("Du zeichnest, malst oder gestaltest? Hol dir die Künstler-Rolle – "
                  "dann kannst du deine Werke in {galerie} posten.\n"
                  "Alle anderen können sie sich ansehen und darauf reagieren."),
        "farbe": Farbe.LILA_HELL,
        "rollen": [
            {"emoji": "🎨", "rolle": "kuenstler", "label": "Künstler",
             "info": "darf in der Galerie posten"},
        ],
    },
]
REAKTIONS_FOOTER = "Klick einfach auf die passende Reaktion, um die Rolle zu bekommen oder wieder zu entfernen."


# ─────────────────────────────────────────────────────────────
#  AUTOBAN  (Fallgrube für gehackte Spam-Accounts)
# ─────────────────────────────────────────────────────────────
# Nachrichten des gebannten Accounts der letzten X Sekunden serverweit löschen
# (86400 = 24 Stunden, max. 604800 = 7 Tage)
AUTOBAN_NACHRICHTEN_LOESCHEN = 86400
AUTOBAN_GRUND = "Autoban-Fallgrube: gehackter Account / Spam"

AUTOBAN_TITEL = "🚨 FALLENKARTE: BODENLOSE FALLGRUBE 🚨"
AUTOBAN_TEXT = (
    "**Dieser Channel ist eine Falle für gehackte Spam-Accounts!**\n\n"
    "Das bedeutet:\n"
    "**Wer hier etwas schreibt, wird sofort und dauerhaft vom Server gebannt – "
    "ohne Möglichkeit auf Entbannung.**\n\n"
    "🚫 **ALSO HIER NICHTS REINSCHREIBEN!** 🚫\n\n"
    "Wer es trotzdem tut, ist selbst schuld. Der Abgrund gibt nichts zurück. 🕳️"
)
AUTOBAN_STATISTIK_NAME = "📊 Statistik"
# {anzahl} wird automatisch hochgezählt
AUTOBAN_STATISTIK_TEXT = "Bisher verbannte Accounts: **{anzahl}**"


# ─────────────────────────────────────────────────────────────
#  TEXTE
# ─────────────────────────────────────────────────────────────
REGELN_TITEL = "📜 DUELL-REGELN · Willkommen in Orth"
REGELN_INTRO = (
    f"Schön, dass du den Weg zum Server von **{STREAMER_NAME}** gefunden hast!\n"
    "Bevor du in den Abgrund steigst, lies dir bitte kurz die Regeln durch:"
)
REGELN = [
    ("🤝 Respekt im Duell",
     "Kein Hate, keine Beleidigungen, kein Rassismus oder Sexismus. GG statt Salz."),
    ("🚫 Verbotene Karten",
     "Kein NSFW, kein Gore, nichts Illegales – auch nicht im Profilbild oder im Namen."),
    ("📵 Kein Spam",
     "Keine Massen-Pings und keine Fremdwerbung (auch nicht per DM) ohne Erlaubnis vom Team."),
    ("🕳️ Spoiler markieren",
     "Gerade bei Made in Abyss und Tsubasa: ||Spoiler|| nutzen oder ab in den Spoiler-Abgrund."),
    ("🗂️ Richtige Zone",
     "Jeder Channel hat seinen Zweck – poste dort, wo es hingehört."),
    ("🚨 Finger weg von der Fallgrube",
     "Im Autoban-Channel nichts schreiben – wer dort schreibt, wird automatisch gebannt."),
    ("📜 Discord & Twitch",
     "Die Discord-Nutzungsbedingungen und die Twitch-Richtlinien gelten auch hier."),
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

# Live-Alert – Spruch je nach Spiel (Teil des Spielnamens, kleingeschrieben → Spruch)
LIVE_SPRUECHE = {
    "yu-gi-oh": "⚔️ **Es ist Zeit für ein Duell!**",
    "bleach": "🍑 **Hajike, Tobiume!**",
}
LIVE_SPRUCH_STANDARD = "🌙 **Lunalight-Fusion!**"
LIVE_TEXT = "{ping} {spruch} **{name}** beschwört einen Stream!"
ENDE_TEXT = "🌑 Der Mond ist untergegangen – danke fürs Zuschauen!"

# Streamplan
STREAMPLAN_TITEL = f"📅 STREAMPLAN · {STREAMER_NAME}"
STREAMPLAN_INFO = (
    "Alle Zeiten in deutscher Zeit.\n"
    "Hol dir in der Deck-Auswahl den 🔴 Stream-Ping, dann verpasst du nichts!"
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
