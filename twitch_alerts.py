"""Twitch-Live-Alerts: postet automatisch in #live-beschwörung, wenn Kapuziner98 live geht.

- fragt jede Minute die Twitch-API (Helix) ab
- pingt die 🔔 Live-Ping-Rolle
- aktualisiert die Nachricht bei Spiel-/Titelwechsel
- macht nach Stream-Ende "Stream beendet" + Dauer draus
- übersteht Bot-Neustarts (findet seine Nachricht über die Stream-ID wieder)

Benötigt: TWITCH_CLIENT_ID und TWITCH_CLIENT_SECRET (dev.twitch.tv/console)
"""
import logging
import os
import time
from datetime import datetime, timezone

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands, tasks

import config
from utils import finde_channel, finde_rolle

log = logging.getLogger("twitch")

ENDE_TITEL = "🌑 Stream beendet"


def _zeit(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def _dauer_text(start: datetime) -> str:
    sek = max(0, int((datetime.now(timezone.utc) - start).total_seconds()))
    std, rest = divmod(sek, 3600)
    return f"{std} Std. {rest // 60} Min." if std else f"{rest // 60} Min."


def _spruch(spiel: str) -> str:
    spiel = (spiel or "").lower()
    for teil, spruch in config.LIVE_SPRUECHE.items():
        if teil in spiel:
            return spruch
    return config.LIVE_SPRUCH_STANDARD


def _stream_button() -> discord.ui.View:
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Zum Stream", emoji="🌙", url=config.TWITCH_URL))
    return view


class TwitchAlerts(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client_id = os.getenv("TWITCH_CLIENT_ID")
        self.client_secret = os.getenv("TWITCH_CLIENT_SECRET")
        self.session: aiohttp.ClientSession | None = None
        self.token: str | None = None
        self.profilbild: str | None = None

        self.aktuell: dict | None = None          # aktuell angekündigter Stream
        self.nachricht: discord.Message | None = None
        self.offline_zaehler = 0
        self.erster_check = True

    # ── Lifecycle ────────────────────────────────────────────
    async def cog_load(self):
        if not self.client_id or not self.client_secret:
            log.warning("TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET fehlen – Live-Alerts sind AUS.")
            return
        self.session = aiohttp.ClientSession()
        self.check.change_interval(seconds=config.TWITCH_CHECK_INTERVALL)
        self.check.start()

    async def cog_unload(self):
        self.check.cancel()
        if self.session:
            await self.session.close()

    # ── Twitch-API ───────────────────────────────────────────
    async def _token_holen(self):
        async with self.session.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            },
        ) as r:
            r.raise_for_status()
            self.token = (await r.json())["access_token"]

    async def _helix(self, pfad: str, params: dict) -> list:
        if not self.token:
            await self._token_holen()
        for versuch in range(2):
            headers = {"Client-ID": self.client_id, "Authorization": f"Bearer {self.token}"}
            async with self.session.get(
                f"https://api.twitch.tv/helix/{pfad}", params=params, headers=headers
            ) as r:
                if r.status == 401 and versuch == 0:  # Token abgelaufen → neu holen
                    await self._token_holen()
                    continue
                r.raise_for_status()
                return (await r.json()).get("data", [])
        return []

    async def stream_holen(self) -> dict | None:
        daten = await self._helix("streams", {"user_login": config.TWITCH_LOGIN})
        return next((s for s in daten if s.get("type") == "live"), None)

    # ── Discord-Teil ─────────────────────────────────────────
    def _guild(self) -> discord.Guild | None:
        gid = os.getenv("GUILD_ID")
        if gid and gid.isdigit():
            return self.bot.get_guild(int(gid))
        return self.bot.guilds[0] if self.bot.guilds else None

    def live_embed(self, s: dict) -> discord.Embed:
        start = _zeit(s["started_at"])
        e = discord.Embed(title=(s.get("title") or "Live!")[:256], url=config.TWITCH_URL, color=config.Farbe.LILA)
        e.set_author(name=f"{s['user_name']} ist LIVE auf Twitch", url=config.TWITCH_URL, icon_url=self.profilbild)
        e.add_field(name="🎮 Spiel", value=s.get("game_name") or "—", inline=True)
        e.add_field(name="⏰ Live seit", value=f"<t:{int(start.timestamp())}:R>", inline=True)
        bild = s["thumbnail_url"].replace("{width}", "1280").replace("{height}", "720")
        e.set_image(url=f"{bild}?v={int(time.time())}")  # Cache-Buster, sonst altes Vorschaubild
        if self.profilbild:
            e.set_thumbnail(url=self.profilbild)
        e.set_footer(text=f"Stream-ID: {s['id']} · twitch.tv/{config.TWITCH_LOGIN}")
        e.timestamp = start
        return e

    def ende_embed(self, titel: str, spiel: str | None, stream_id: str, dauer: str | None) -> discord.Embed:
        e = discord.Embed(title=ENDE_TITEL, description=f"**{titel}**", url=config.TWITCH_URL,
                          color=config.Farbe.GRUEN_DUNKEL)
        e.set_author(name=config.STREAMER_NAME, url=config.TWITCH_URL, icon_url=self.profilbild)
        if spiel:
            e.add_field(name="🎮 Spiel", value=spiel, inline=True)
        if dauer:
            e.add_field(name="⏱️ Dauer", value=dauer, inline=True)
        if self.profilbild:
            e.set_thumbnail(url=self.profilbild)
        e.set_footer(text=f"Stream-ID: {stream_id} · beendet")
        return e

    async def _suche_alert(self, channel, nur_id: str | None = None):
        """Findet die letzte (noch nicht beendete) Live-Nachricht vom Bot."""
        async for msg in channel.history(limit=30):
            if msg.author.id != self.bot.user.id or not msg.embeds:
                continue
            emb = msg.embeds[0]
            footer = emb.footer.text or ""
            if "Stream-ID:" not in footer or emb.title == ENDE_TITEL:
                continue
            if nur_id is None or f"Stream-ID: {nur_id} " in footer + " ":
                return msg
        return None

    async def _presence(self, s: dict | None):
        if s:
            akt = discord.Streaming(name=(s.get("title") or "Live")[:128], url=config.TWITCH_URL)
        else:
            akt = discord.Activity(type=discord.ActivityType.watching, name=config.BOT_STATUS)
        try:
            await self.bot.change_presence(activity=akt)
        except Exception:
            pass

    async def _ankuendigen(self, channel, s: dict):
        rolle = finde_rolle(channel.guild, "live_ping")
        text = config.LIVE_TEXT.format(
            ping=rolle.mention if rolle else "",
            spruch=_spruch(s.get("game_name")),
            name=s["user_name"],
        ).strip()
        return await channel.send(
            content=text,
            embed=self.live_embed(s),
            view=_stream_button(),
            allowed_mentions=discord.AllowedMentions(roles=[rolle] if rolle else False),
        )

    # ── Haupt-Loop ───────────────────────────────────────────
    @tasks.loop(seconds=60)
    async def check(self):
        try:
            await self._check()
        except Exception:
            log.exception("Fehler beim Twitch-Check (nächster Versuch beim nächsten Durchlauf)")

    async def _check(self):
        guild = self._guild()
        channel = finde_channel(guild, "live") if guild else None
        if channel is None:
            return

        try:
            s = await self.stream_holen()
        except aiohttp.ClientError as err:
            log.warning("Twitch nicht erreichbar: %s", err)
            return  # zählt NICHT als offline

        if s:
            self.offline_zaehler = 0

            if self.aktuell is None:
                # Neustart des Bots während Stream? Dann alte Nachricht übernehmen statt neu pingen
                alt = await self._suche_alert(channel, nur_id=s["id"])
                if alt:
                    self.nachricht = alt
                    await alt.edit(embed=self.live_embed(s))
                else:
                    self.nachricht = await self._ankuendigen(channel, s)
                    log.info("Live-Alert gepostet (Stream %s)", s["id"])
                await self._presence(s)

            elif (s["id"] != self.aktuell["id"]
                  or s.get("title") != self.aktuell.get("title")
                  or s.get("game_id") != self.aktuell.get("game_id")):
                # kurzer Neustart / Titel- oder Spielwechsel → Nachricht aktualisieren, kein neuer Ping
                if self.nachricht:
                    try:
                        await self.nachricht.edit(embed=self.live_embed(s))
                    except discord.NotFound:
                        self.nachricht = None
                await self._presence(s)

            self.aktuell = s

        else:
            if self.aktuell:
                self.offline_zaehler += 1
                if self.offline_zaehler >= config.OFFLINE_CHECKS_BIS_ENDE:
                    if self.nachricht:
                        try:
                            await self.nachricht.edit(
                                content=config.ENDE_TEXT,
                                embed=self.ende_embed(
                                    self.aktuell.get("title") or "Stream",
                                    self.aktuell.get("game_name"),
                                    self.aktuell["id"],
                                    _dauer_text(_zeit(self.aktuell["started_at"])),
                                ),
                                allowed_mentions=discord.AllowedMentions.none(),
                            )
                        except discord.NotFound:
                            pass
                    log.info("Stream %s beendet", self.aktuell["id"])
                    self.aktuell = None
                    self.nachricht = None
                    self.offline_zaehler = 0
                    await self._presence(None)

            elif self.erster_check:
                # Stream lief, während der Bot aus war → alte Live-Nachricht abschließen
                alt = await self._suche_alert(channel)
                if alt:
                    emb = alt.embeds[0]
                    sid = (emb.footer.text or "").split("Stream-ID:")[1].split("·")[0].strip()
                    spiel = next((f.value for f in emb.fields if "Spiel" in f.name), None)
                    await alt.edit(
                        content=config.ENDE_TEXT,
                        embed=self.ende_embed(emb.title or "Stream", spiel, sid, None),
                        allowed_mentions=discord.AllowedMentions.none(),
                    )
                await self._presence(None)

        self.erster_check = False

    @check.before_loop
    async def vor_loop(self):
        await self.bot.wait_until_ready()
        try:
            users = await self._helix("users", {"login": config.TWITCH_LOGIN})
            if users:
                self.profilbild = users[0].get("profile_image_url")
        except Exception:
            log.warning("Konnte Twitch-Profilbild nicht laden.")

    # ── Test-Befehl ──────────────────────────────────────────
    @app_commands.command(name="livetest", description="Zeigt dir eine Vorschau vom Live-Alert (nur für dich)")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def livetest(self, interaction: discord.Interaction):
        if not self.session:
            await interaction.response.send_message(
                "⚠️ Live-Alerts sind aus: TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET fehlen.", ephemeral=True
            )
            return
        await interaction.response.defer(ephemeral=True)
        try:
            s = await self.stream_holen()
        except Exception as err:
            await interaction.followup.send(f"⚠️ Twitch-Fehler: `{err}` – stimmen Client-ID & Secret?",
                                            ephemeral=True)
            return
        status = "🔴 Gerade LIVE" if s else "⚫ Gerade offline – Beispiel-Vorschau"
        if not s:
            s = {
                "id": "TEST", "user_name": config.STREAMER_NAME, "title": "Lunalight gegen den Rest der Welt!",
                "game_name": "Yu-Gi-Oh! Master Duel", "game_id": "0",
                "started_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "thumbnail_url": "https://static-cdn.jtvnw.net/ttv-static/404_preview-{width}x{height}.jpg",
            }
        ch = finde_channel(interaction.guild, "live")
        rolle = finde_rolle(interaction.guild, "live_ping")
        info = (f"{status}\nTwitch-Verbindung: ✅\nLive-Channel: {ch.mention if ch else '❌ fehlt'}\n"
                f"Ping-Rolle: {rolle.mention if rolle else '❌ fehlt'}\n\n"
                + config.LIVE_TEXT.format(ping="@Ping", spruch=_spruch(s.get('game_name')), name=s['user_name']))
        await interaction.followup.send(info, embed=self.live_embed(s), view=_stream_button(), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(TwitchAlerts(bot))
