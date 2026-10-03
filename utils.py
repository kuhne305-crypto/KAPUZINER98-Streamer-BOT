"""Kleine Helfer: Rollen & Channels über die Namen aus config.py finden."""
import os

import discord

import config


def _norm(name: str) -> str:
    """Discord schreibt Text-Channel klein und macht aus Leerzeichen Bindestriche."""
    return name.strip().lower().replace(" ", "-")


def channel_name(key: str) -> str | None:
    for kat in config.KATEGORIEN:
        for ch in kat["channels"]:
            if ch["key"] == key:
                return ch["name"]
    return None


def finde_channel(guild: discord.Guild, key: str):
    """Sucht einen Channel über seinen key.
    Optional per Umgebungsvariable überschreibbar, z. B. CHANNEL_LIVE_ID=1234567890
    (praktisch, falls ihr Channels später umbenennt)."""
    override = os.getenv(f"CHANNEL_{key.upper()}_ID")
    if override and override.isdigit():
        ch = guild.get_channel(int(override))
        if ch:
            return ch
    name = channel_name(key)
    if not name:
        return None
    for ch in guild.channels:
        if ch.name == name or _norm(ch.name) == _norm(name):
            return ch
    return None


def finde_rolle(guild: discord.Guild, key: str) -> discord.Role | None:
    daten = config.ROLLEN.get(key)
    if not daten:
        return None
    return discord.utils.get(guild.roles, name=daten["name"])


async def letzte_bot_nachricht(channel: discord.abc.Messageable, bot_user, pruefen=None, limit=30):
    """Letzte Nachricht vom Bot in einem Channel (optional mit Filter-Funktion)."""
    async for msg in channel.history(limit=limit):
        if msg.author.id == bot_user.id and (pruefen is None or pruefen(msg)):
            return msg
    return None
