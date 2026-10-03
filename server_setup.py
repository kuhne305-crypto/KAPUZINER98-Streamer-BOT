"""/setup – legt fehlende Rollen, Kategorien und Channels im Kapuziner98-Theme an.
LÖSCHT NICHTS. Was es schon gibt (gleicher Name), wird übersprungen.
Was es unter einem ALTEN Namen gibt (siehe "alt" in config.py), wird umbenannt.
Man kann /setup also jederzeit nochmal ausführen, z. B. nach Änderungen in config.py.

/panel – postet das Regeln-, Reaktionsrollen- oder Autoban-Panel neu.
"""
import logging

import discord
from discord import app_commands
from discord.ext import commands

import config
from autoban import anzahl_aus_embed, autoban_embed, finde_panel as finde_autoban_panel
from streamplan import plan_posten_oder_holen
from utils import _norm, finde_channel, letzte_bot_nachricht
from verify import VerifyView, regeln_embed

log = logging.getLogger("setup")
PO = discord.PermissionOverwrite


def rechte(art: str | None) -> discord.Permissions:
    if art == "admin":
        return discord.Permissions(administrator=True)
    if art == "mod":
        return discord.Permissions(
            kick_members=True, ban_members=True, moderate_members=True,
            manage_messages=True, manage_threads=True, manage_nicknames=True,
            mute_members=True, deafen_members=True, move_members=True, view_audit_log=True,
        )
    return discord.Permissions.none()


def overwrites(guild: discord.Guild, rollen: dict, zugang: str, typ: str) -> dict:
    """Baut die Channel-Rechte. typ: 'text' | 'voice' | 'category'"""
    ev = guild.default_role
    member = rollen.get("member")
    team = [rollen[k] for k in config.TEAM_ROLLEN if rollen.get(k)]
    voice = typ == "voice"
    ow: dict = {}

    keine_threads = dict(create_public_threads=False, create_private_threads=False)

    if zugang == "oeffentlich_info":
        ow[ev] = PO(view_channel=True) if voice else PO(view_channel=True, send_messages=False,
                                                         add_reactions=False, **keine_threads)
    elif zugang == "mitglieder_info":
        ow[ev] = PO(view_channel=False)
        if member:
            ow[member] = PO(view_channel=True, send_messages=False, add_reactions=True, **keine_threads)
    elif zugang == "kuenstler":
        ow[ev] = PO(view_channel=False)
        if member:
            ow[member] = PO(view_channel=True, send_messages=False, add_reactions=True,
                            read_message_history=True, send_messages_in_threads=False, **keine_threads)
        kuenstler = rollen.get("kuenstler")
        if kuenstler:
            ow[kuenstler] = PO(view_channel=True, send_messages=True, attach_files=True, embed_links=True)
    elif zugang == "autoban":
        # Absichtlich für ALLE offen – Spam-Accounts sollen hier reinschreiben können
        ow[ev] = PO(view_channel=True, send_messages=True, attach_files=True, embed_links=True,
                    read_message_history=True, add_reactions=False, **keine_threads)
    elif zugang in ("mitglieder", "voice"):
        ow[ev] = PO(view_channel=False)
        if member:
            if voice or zugang == "voice":
                ow[member] = PO(view_channel=True, connect=True, speak=True)
            else:
                ow[member] = PO(view_channel=True, send_messages=True)
    elif zugang == "team":
        ow[ev] = PO(view_channel=False)

    for r in team:
        if voice:
            ow[r] = PO(view_channel=True, connect=True, speak=True)
        else:
            ow[r] = PO(view_channel=True, send_messages=True, add_reactions=True, manage_messages=True)

    # Bot selbst darf immer alles sehen/schreiben
    ow[guild.me] = (PO(view_channel=True, connect=True) if voice
                    else PO(view_channel=True, send_messages=True, embed_links=True, add_reactions=True,
                            manage_messages=True, mention_everyone=True, read_message_history=True))
    return ow


def finde_kategorie(guild: discord.Guild, kat: dict):
    for name in [kat["name"], *kat.get("alt", [])]:
        for c in guild.categories:
            if c.name.casefold() == name.casefold():
                return c
    return None


def finde_rolle_mit_alt(guild: discord.Guild, daten: dict):
    for name in [daten["name"], *daten.get("alt", [])]:
        r = discord.utils.get(guild.roles, name=name)
        if r:
            return r
    return None


class ServerSetup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ─────────────────────────────────────────────────────────
    @app_commands.command(name="setup",
                          description="Legt fehlende Rollen & Channels im Kapuziner98-Theme an (löscht nichts)")
    @app_commands.describe(bestehende_mitglieder="Allen, die schon auf dem Server sind, direkt die Duelist-Rolle geben?")
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    async def setup_cmd(self, interaction: discord.Interaction, bestehende_mitglieder: bool = False):
        await interaction.response.defer(ephemeral=True, thinking=True)
        guild = interaction.guild
        hinweise: list[str] = []
        neu = {"rollen": 0, "kategorien": 0, "channels": 0, "panels": 0, "umbenannt": 0}

        if not guild.me.guild_permissions.administrator:
            hinweise.append("⚠️ Der Bot hat kein **Administrator**-Recht – manche Schritte können fehlschlagen.")

        # ── 1. Rollen ────────────────────────────────────────
        rollen: dict[str, discord.Role] = {}
        for key, d in config.ROLLEN.items():
            r = finde_rolle_mit_alt(guild, d)
            if r is None:
                try:
                    r = await guild.create_role(
                        name=d["name"], colour=discord.Colour(d["farbe"]), hoist=d["hoist"],
                        mentionable=False, permissions=rechte(d["rechte"]), reason="Kapuziner98 Setup",
                    )
                    neu["rollen"] += 1
                except discord.HTTPException as err:
                    hinweise.append(f"⚠️ Rolle `{d['name']}` ging nicht: {err.text}")
                    continue
            elif r.name != d["name"]:
                try:
                    await r.edit(name=d["name"], colour=discord.Colour(d["farbe"]), reason="Kapuziner98 Setup – neuer Name")
                    neu["umbenannt"] += 1
                except discord.HTTPException:
                    hinweise.append(f"⚠️ Rolle `{r.name}` konnte nicht umbenannt werden.")
            rollen[key] = r

        # Rollen in Theme-Reihenfolge direkt unter die Bot-Rolle sortieren
        top = guild.me.top_role.position
        sortierbar = [rollen[k] for k in config.ROLLEN if k in rollen and rollen[k].position < top]
        if neu["rollen"] and top - len(sortierbar) >= 1:
            try:
                await guild.edit_role_positions(
                    positions={r: top - 1 - i for i, r in enumerate(sortierbar)},
                    reason="Kapuziner98 Setup – Rollen sortieren",
                )
            except discord.HTTPException:
                hinweise.append("⚠️ Rollen konnten nicht automatisch sortiert werden – bitte kurz per Hand ziehen.")
        elif neu["rollen"]:
            hinweise.append("⚠️ Zieh die **Bot-Rolle** in den Servereinstellungen ganz nach oben "
                            "und führ `/setup` nochmal aus.")

        # ── 2. Kategorien & Channels ─────────────────────────
        kanaele: dict[str, discord.abc.GuildChannel] = {}
        for kat in config.KATEGORIEN:
            kategorie = finde_kategorie(guild, kat)
            if kategorie is None:
                kategorie = await guild.create_category(
                    kat["name"], overwrites=overwrites(guild, rollen, kat["zugang"], "category"),
                    reason="Kapuziner98 Setup",
                )
                neu["kategorien"] += 1
            elif kategorie.name.casefold() != kat["name"].casefold():
                try:
                    await kategorie.edit(name=kat["name"], reason="Kapuziner98 Setup – neuer Name")
                    neu["umbenannt"] += 1
                except discord.HTTPException:
                    hinweise.append(f"⚠️ Kategorie `{kategorie.name}` konnte nicht umbenannt werden.")

            for ch in kat["channels"]:
                zugang = ch.get("zugang", kat["zugang"])
                typ = "voice" if ch["typ"] == "voice" else "text"
                vorhanden = finde_channel(guild, ch["key"])

                if vorhanden:
                    # Unter altem Namen gefunden → umbenennen + neue Rechte setzen
                    if _norm(vorhanden.name) != _norm(ch["name"]):
                        extra = {"topic": ch["topic"]} if typ == "text" and ch.get("topic") else {}
                        try:
                            await vorhanden.edit(
                                name=ch["name"], category=kategorie,
                                overwrites=overwrites(guild, rollen, zugang, typ),
                                reason="Kapuziner98 Setup – neuer Name", **extra,
                            )
                            neu["umbenannt"] += 1
                        except discord.HTTPException:
                            hinweise.append(f"⚠️ `{vorhanden.name}` konnte nicht umbenannt werden.")
                    kanaele[ch["key"]] = vorhanden
                    continue

                try:
                    if typ == "voice":
                        neu_ch = await guild.create_voice_channel(
                            ch["name"], category=kategorie,
                            overwrites=overwrites(guild, rollen, zugang, "voice"), reason="Kapuziner98 Setup",
                        )
                    else:
                        extra = {"topic": ch["topic"]} if ch.get("topic") else {}
                        neu_ch = await guild.create_text_channel(
                            ch["name"], category=kategorie,
                            overwrites=overwrites(guild, rollen, zugang, "text"), reason="Kapuziner98 Setup",
                            **extra,
                        )
                    kanaele[ch["key"]] = neu_ch
                    neu["channels"] += 1
                except discord.HTTPException as err:
                    hinweise.append(f"⚠️ Channel `{ch['name']}` ging nicht: {err.text}")

        # AFK-Channel (Reich der Schatten) setzen, falls noch keiner eingestellt ist
        afk = kanaele.get("afk")
        if afk and guild.afk_channel is None:
            try:
                await guild.edit(afk_channel=afk, afk_timeout=900, reason="Kapuziner98 Setup")
            except discord.HTTPException:
                pass

        # ── 3. Panels posten (nur wenn noch nicht vorhanden) ──
        regeln_ch = kanaele.get("regeln")
        if regeln_ch:
            da = await letzte_bot_nachricht(
                regeln_ch, self.bot.user,
                lambda m: bool(m.embeds) and m.embeds[0].title == config.REGELN_TITEL)
            if not da:
                await regeln_ch.send(embed=regeln_embed(), view=VerifyView())
                neu["panels"] += 1

        autoban_ch = kanaele.get("autoban")
        if autoban_ch and not await finde_autoban_panel(autoban_ch, self.bot.user):
            await autoban_ch.send(embed=autoban_embed(0))
            neu["panels"] += 1

        rollen_ch = kanaele.get("rollen")
        rr = self.bot.get_cog("ReaktionsRollen")
        if rollen_ch and rr:
            neu["panels"] += await rr.panels_posten(rollen_ch, nur_fehlende=True)

        plan_ch = kanaele.get("streamplan")
        if plan_ch:
            await plan_posten_oder_holen(plan_ch, self.bot.user)

        # ── 4. Optional: bestehende Mitglieder verifizieren ──
        verifiziert = 0
        if bestehende_mitglieder and rollen.get("member"):
            if not guild.chunked:
                await guild.chunk()
            for m in guild.members:
                if not m.bot and rollen["member"] not in m.roles:
                    try:
                        await m.add_roles(rollen["member"], reason="Setup: bestehendes Mitglied")
                        verifiziert += 1
                    except discord.HTTPException:
                        pass

        # ── Zusammenfassung ──────────────────────────────────
        embed = discord.Embed(
            title="✅ Setup abgeschlossen – Lunalight-Fusion!",
            color=config.Farbe.LILA,
            description=(
                f"**Neu angelegt:** {neu['rollen']} Rollen · {neu['kategorien']} Kategorien · "
                f"{neu['channels']} Channels · {neu['panels']} Panels\n"
                f"**Umbenannt:** {neu['umbenannt']}\n"
                + (f"**Duelist-Rolle verteilt an:** {verifiziert} Mitglieder\n" if bestehende_mitglieder else "")
                + "\nGelöscht wurde **nichts**. Alte Channels sind evtl. noch für alle sichtbar – "
                  "die könnt ihr jetzt in Ruhe verschieben oder löschen."
            ),
        )
        if hinweise:
            embed.add_field(name="Hinweise", value="\n".join(hinweise)[:1024], inline=False)
        embed.add_field(
            name="Nächste Schritte",
            value=(
                "• Streamer-, Admin- und Mod-Rollen per Hand vergeben\n"
                "• Bot-Rolle ganz nach oben ziehen (sonst kann die Fallgrube nicht bannen)\n"
                "• `/streamplan setzen` für den Wochenplan\n"
                "• `/livetest` prüft die Twitch-Verbindung"
            ),
            inline=False,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    # ─────────────────────────────────────────────────────────
    @app_commands.command(name="panel", description="Regeln-, Reaktionsrollen- oder Autoban-Panel neu posten")
    @app_commands.describe(art="Welches Panel?")
    @app_commands.choices(art=[
        app_commands.Choice(name="Regeln + Verify-Button", value="regeln"),
        app_commands.Choice(name="Reaktionsrollen (alle Panels)", value="rollen"),
        app_commands.Choice(name="Autoban-Fallgrube", value="autoban"),
    ])
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction, art: app_commands.Choice[str]):
        channel = finde_channel(interaction.guild, art.value)
        if channel is None:
            await interaction.response.send_message("⚠️ Channel nicht gefunden – erst `/setup` ausführen.",
                                                    ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        if art.value == "regeln":
            await channel.send(embed=regeln_embed(), view=VerifyView())
        elif art.value == "autoban":
            alt = await finde_autoban_panel(channel, self.bot.user)
            await channel.send(embed=autoban_embed(anzahl_aus_embed(alt.embeds[0]) if alt else 0))
        else:
            rr = self.bot.get_cog("ReaktionsRollen")
            await rr.panels_posten(channel, nur_fehlende=False)
        await interaction.followup.send(
            f"✅ Gepostet in {channel.mention}. Das alte Panel kannst du löschen "
            "(bei Reaktionsrollen funktionieren alte Panels aber auch weiter).",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerSetup(bot))
