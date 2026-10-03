# Kapuziner98 Discord-Bot

Yu-Gi-Oh × Lunalight × Made in Abyss Theme · Python (discord.py) · läuft auf Railway

## Was der Bot kann

- `/setup` legt alle fehlenden Rollen, Kategorien und Channels im Theme an. Er löscht nichts, und man kann ihn beliebig oft ausführen.
  Mit der Option `bestehende_mitglieder:True` bekommen alle, die schon auf dem Server sind, direkt die Duelist-Rolle.
- Twitch-Live-Alerts: postet automatisch in 🔴│live-beschwörung und pingt die 🔔 Live-Ping-Rolle.
  Je nach Spiel kommt ein eigener Spruch (Master Duel / Rebirth of Souls). Nach dem Stream wird die Nachricht zu „Stream beendet“ mit Dauer.
- Regeln + Verify-Button: Wer die Regeln akzeptiert, bekommt 🃏 Duelist und sieht den ganzen Server.
- Self-Roles per Button in 🎴│deck-auswahl (erweiterbar über `config.py`).
- Willkommens-Nachricht in 👋│ankunft-in-orth.
- `/streamplan setzen | pause | leeren` pflegt den Wochenplan als Embed in 📅│streamplan.
- `/livetest` zeigt dir eine Vorschau vom Live-Alert und prüft die Twitch-Verbindung.
- `/panel` postet das Regeln- oder Self-Role-Panel neu.

---

## Einrichtung (ca. 15 Minuten)

### 1. Discord-Bot erstellen
1. https://discord.com/developers/applications → **New Application** → Name z. B. `Mokona`
2. Links **Bot** → **Reset Token** → Token kopieren (= `DISCORD_TOKEN`)
3. Gleiche Seite, unter *Privileged Gateway Intents*: **Server Members Intent** einschalten → speichern
4. Links **OAuth2** → **URL Generator**:
   - Scopes: `bot` + `applications.commands`
   - Bot Permissions: `Administrator`
   - Link öffnen → Bot auf den Server einladen
5. In Discord: Servereinstellungen → Rollen → **Bot-Rolle ganz nach oben ziehen**

### 2. Twitch-App erstellen (für die Live-Alerts)
1. https://dev.twitch.tv/console/apps → **Register Your Application**
   (dein Twitch-Account braucht dafür 2-Faktor-Authentifizierung)
2. Name: beliebig, z. B. `Kapuziner98 Discord Alerts`
3. OAuth Redirect URL: `http://localhost`
4. Kategorie: `Application Integration`, Client-Typ: `Confidential`
5. Erstellen → **Verwalten** → Client-ID kopieren → **Neues Geheimnis** → Secret kopieren

### 3. Auf Railway hochladen
1. Den Ordner in ein (privates!) GitHub-Repo packen
2. Railway → **New Project** → **Deploy from GitHub repo** → Repo wählen
3. Im Service unter **Variables** eintragen:

   | Variable | Wert |
   |---|---|
   | `DISCORD_TOKEN` | Token aus Schritt 1 |
   | `TWITCH_CLIENT_ID` | aus Schritt 2 |
   | `TWITCH_CLIENT_SECRET` | aus Schritt 2 |
   | `GUILD_ID` | Server-ID (Rechtsklick auf den Server → *Server-ID kopieren*, vorher Entwicklermodus in Discord an) |

4. Deploy läuft automatisch. In den Logs muss `Eingeloggt als …` stehen.

### 4. Im Discord
1. `/setup` ausführen (optional `bestehende_mitglieder: True`)
2. Rollen per Hand vergeben: Streamer, Admins (⚪ Weiße Pfeife), Mods (🔮 Charmer)
3. `/livetest` → prüft, ob Twitch verbunden ist
4. `/streamplan setzen tag:Freitag uhrzeit:20:00 spiel:Master Duel`
5. Alte Channels prüfen: Die sind evtl. noch für alle sichtbar. Verschieben, anpassen oder löschen.

---

## Anpassen

Alles steht in **`config.py`**: Rollen-Namen, Farben, Channels, Regeln, Texte, Sprüche.
Danach neu deployen und `/setup` nochmal ausführen. Neue Sachen werden ergänzt, Bestehendes bleibt.

**Achtung:** Wenn ihr einen Channel oder eine Rolle **in Discord** umbenennt, findet der Bot sie nicht mehr.
Dann entweder den Namen auch in `config.py` ändern oder per Railway-Variable fest verknüpfen,
z. B. `CHANNEL_LIVE_ID=123456789` (Schema: `CHANNEL_<KEY>_ID`, der Key steht in `config.py`).

### Neue Self-Role hinzufügen
1. In `config.py` bei `ROLLEN` eintragen
2. Bei `SELFROLE_PANELS` als Button eintragen (oder ein neues Panel anlegen)
3. Deployen → `/setup` (legt die Rolle an) → `/panel art:Self-Roles`

### Twitch-Sub-Rolle
Sobald Kapuziner98 Affiliate ist: Servereinstellungen → Integrationen → Twitch verbinden.
Discord legt dann eine Sub-Rolle an, die automatisch synchronisiert wird. Die kann man z. B. in
`🦋 Purple Butterfly │ Sub` umbenennen und lila einfärben.
