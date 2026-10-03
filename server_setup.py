"""/setup – legt fehlende Rollen, Kategorien und Channels im Kapuziner98-Theme an.
LÖSCHT NICHTS. Was es schon gibt (gleicher Name), wird übersprungen.
Man kann /setup also jederzeit nochmal ausführen, z. B. nach neuen Einträgen in config.py.

/panel – postet Regeln- oder Self-Role-Panels neu.
"""
import logging

import discord
from discord import app_commands
from discord.ext import commands

import config
from selfroles import alle_panels
from streamplan import plan_posten_oder_holen
from verify import VerifyView, regeln_embed
from utils import _norm, finde_channel, letzte_bot_nachricht

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

    kein_schreiben = dict(send_messages=False, add_reactions=False,
                          create_public_threads=False, create_private_threads=False)

    if zugang == "oeffentlich_info":
        ow[ev] = PO(view_channel=True, **({} if voice else kein_schreiben))
    elif zugang == "mitglieder_info":
        ow[ev] = PO(view_channel=False)
        if member:
            ow[member] = PO(view_channel=True, send_messages=False,
                            create_public_threads=False, create_private_threads=False)
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
                    else PO(view_channel=True, send_messages=True, embed_links=True,
                            manage_messages=True, mention_everyone=True, read_message_history=True))
    return ow


def finde_kategorie(guild: discord.Guild, name: str):
    for c in guild.categories:
        if c.name.casefold() == name.casefold():
            return c
    return None


class ServerSetup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ─────────────────────────────────────────────────────────
    @app_commands.command(name="setup", description="Legt fehlende Rollen & Channels im Kapuziner98-Theme an (löscht nichts)")
    @app_commands.describe(bestehende_mitglieder="Allen, die schon auf dem Server sind, direkt die Duelist-Rolle geben?")
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    async def setup_cmd(self, interaction: discord.Interaction, bestehende_mitglieder: bool = False):
        await interaction.response.defer(ephemeral=True, thinking=True)
        guild = interaction.guild
        hinweise: list[str] = []
        neu = {"rollen": 0, "kategorien": 0, "channels": 0, "panels": 0}

        if not guild.me.guild_permissions.administrator:
            hinweise.append("⚠️ Der Bot hat kein **Administrator**-Recht – manche Schritte können fehlschlagen.")

        # ── 1. Rollen ────────────────────────────────────────
        rollen: dict[str, discord.Role] = {}
        for key, d in config.ROLLEN.items():
            r = discord.utils.get(guild.roles, name=d["name"])
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
            hinweise.append("⚠️ Zieh die **Bot-Rolle** in den Servereinstellungen ganz nach oben und führ `/setup` nochmal aus.")

        # ── 2. Kategorien & Channels ─────────────────────────
        kanaele: dict[str, discord.abc.GuildChannel] = {}
        for kat in config.KATEGORIEN:
            kategorie = finde_kategorie(guild, kat["name"])
            if kategorie is None:
                kategorie = await guild.create_category(
                    kat["name"], overwrites=overwrites(guild, rollen, kat["zugang"], "category"),
                    reason="Kapuziner98 Setup",
                )
                neu["kategorien"] += 1

            for ch in kat["channels"]:
                vorhanden = finde_channel(guild, ch["key"])
                if vorhanden:
                    kanaele[ch["key"]] = vorhanden
                    continue
                zugang = ch.get("zugang", kat["zugang"])
                try:
                    if ch["typ"] == "voice":
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

        # AFK-Channel setzen, falls noch keiner eingestellt ist
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

        rollen_ch = kanaele.get("rollen")
        if rollen_ch:
            for embed, view in alle_panels():
                da = await letzte_bot_nachricht(
                    rollen_ch, self.bot.user,
                    lambda m, t=embed.title: bool(m.embeds) and m.embeds[0].title == t)
                if not da:
                    await rollen_ch.send(embed=embed, view=view)
                    neu["panels"] += 1

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
            title="✅ Setup abgeschlossen – Lunalight Fusion!",
            color=config.Farbe.LILA,
            description=(
                f"**Neu angelegt:** {neu['rollen']} Rollen · {neu['kategorien']} Kategorien · "
                f"{neu['channels']} Channels · {neu['panels']} Panels\n"
                + (f"**Duelist-Rolle verteilt an:** {verifiziert} Mitglieder\n" if bestehende_mitglieder else "")
                + "\nBestehendes wurde **nicht** angefasst. Alte Channels sind evtl. noch für alle sichtbar – "
                  "die könnt ihr jetzt in Ruhe verschieben oder löschen."
            ),
        )
        if hinweise:
            embed.add_field(name="Hinweise", value="\n".join(hinweise)[:1024], inline=False)
        embed.add_field(
            name="Nächste Schritte",
            value=(
                "• Streamer-, Admin- & Mod-Rollen per Hand vergeben\n"
                "• `/streamplan setzen` für den Wochenplan\n"
                "• `/livetest` prüft die Twitch-Verbindung"
            ),
            inline=False,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    # ─────────────────────────────────────────────────────────
    @app_commands.command(name="panel", description="Regeln- oder Self-Role-Panel neu posten")
    @app_commands.describe(art="Welches Panel?")
    @app_commands.choices(art=[
        app_commands.Choice(name="Regeln + Verify-Button", value="regeln"),
        app_commands.Choice(name="Self-Roles (alle Panels)", value="selfroles"),
    ])
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction, art: app_commands.Choice[str]):
        key = "regeln" if art.value == "regeln" else "rollen"
        channel = finde_channel(interaction.guild, key)
        if channel is None:
            await interaction.response.send_message("⚠️ Channel nicht gefunden – erst `/setup` ausführen.",
                                                    ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        if art.value == "regeln":
            await channel.send(embed=regeln_embed(), view=VerifyView())
        else:
            for embed, view in alle_panels():
                await channel.send(embed=embed, view=view)
        await interaction.followup.send(f"✅ Gepostet in {channel.mention}. Alte Panels kannst du löschen.",
                                        ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerSetup(bot))
