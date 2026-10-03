"""Kleine Helfer: Rollen & Channels über die Namen aus config.py finden."""
import os

import discord

import config


def _norm(name: str) -> str:
    """Discord schreibt Text-Channels klein und macht aus Leerzeichen Bindestriche."""
    return name.strip().casefold().replace(" ", "-")


def emoji_norm(e: str) -> str:
    """Emoji vergleichbar machen (ohne Variation Selector / Hautfarben-Zusatz)."""
    return str(e).replace("️", "").strip()


def channel_daten(key: str) -> dict | None:
    for kat in config.KATEGORIEN:
        for ch in kat["channels"]:
            if ch["key"] == key:
                return ch
    return None


def channel_name(key: str) -> str | None:
    daten = channel_daten(key)
    return daten["name"] if daten else None


def finde_channel(guild: discord.Guild, key: str):
    """Sucht einen Channel über seinen key (erst aktueller Name, dann alte Namen).
    Optional per Umgebungsvariable überschreibbar, z. B. CHANNEL_LIVE_ID=1234567890."""
    if guild is None:
        return None
    override = os.getenv(f"CHANNEL_{key.upper()}_ID")
    if override and override.isdigit():
        ch = guild.get_channel(int(override))
        if ch:
            return ch
    daten = channel_daten(key)
    if not daten:
        return None
    for name in [daten["name"], *daten.get("alt", [])]:
        for ch in guild.channels:
            if isinstance(ch, discord.CategoryChannel):
                continue
            if ch.name == name or _norm(ch.name) == _norm(name):
                return ch
    return None


def finde_rolle(guild: discord.Guild, key: str) -> discord.Role | None:
    daten = config.ROLLEN.get(key)
    if not daten or guild is None:
        return None
    for name in [daten["name"], *daten.get("alt", [])]:
        r = discord.utils.get(guild.roles, name=name)
        if r:
            return r
    return None


def ist_team(member: discord.Member) -> bool:
    """Team = Team-Rolle ODER Admin-/Moderationsrechte ODER Serverbesitzer."""
    if member.guild.owner_id == member.id:
        return True
    p = member.guild_permissions
    if p.administrator or p.manage_guild or p.manage_messages or p.ban_members:
        return True
    team = {finde_rolle(member.guild, k) for k in config.TEAM_ROLLEN}
    return any(r in team for r in member.roles if r)


async def letzte_bot_nachricht(channel: discord.abc.Messageable, bot_user, pruefen=None, limit=30):
    """Letzte Nachricht vom Bot in einem Channel (optional mit Filter-Funktion)."""
    async for msg in channel.history(limit=limit):
        if msg.author.id == bot_user.id and (pruefen is None or pruefen(msg)):
            return msg
    return None
