"""Autoban-Fallgrube: Wer in #autoban-fallgrube schreibt, wird sofort gebannt.

Gedacht gegen gehackte Accounts, die automatisch in jeden Channel Spam posten.
- Team (Admins, Mods, Streamer, Serverbesitzer) wird NIE gebannt – nur die Nachricht wird gelöscht
- Nachrichten des gebannten Accounts der letzten 24 Std. werden serverweit mit gelöscht
- Die Statistik steht direkt im Warn-Embed (keine Datenbank nötig)
- Jeder Bann wird in #bot-log gemeldet
"""
import asyncio
import logging
import re

import discord
from discord.ext import commands

import config
from utils import finde_channel, ist_team, letzte_bot_nachricht

log = logging.getLogger("autoban")
ZAHL = re.compile(r"\*\*(\d+)\*\*")


def autoban_embed(anzahl: int = 0) -> discord.Embed:
    embed = discord.Embed(title=config.AUTOBAN_TITEL, description=config.AUTOBAN_TEXT, color=config.Farbe.FALLE)
    embed.add_field(name=config.AUTOBAN_STATISTIK_NAME,
                    value=config.AUTOBAN_STATISTIK_TEXT.format(anzahl=anzahl), inline=False)
    return embed


def _ist_autoban_panel(msg: discord.Message) -> bool:
    return bool(msg.embeds) and msg.embeds[0].title == config.AUTOBAN_TITEL


def anzahl_aus_embed(embed: discord.Embed) -> int:
    for feld in embed.fields:
        if feld.name == config.AUTOBAN_STATISTIK_NAME:
            treffer = ZAHL.search(feld.value or "")
            if treffer:
                return int(treffer.group(1))
    return 0


async def finde_panel(channel, bot_user):
    return await letzte_bot_nachricht(channel, bot_user, _ist_autoban_panel, limit=50)


class Autoban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.lock = asyncio.Lock()  # damit der Zähler bei mehreren Bans gleichzeitig stimmt

    async def _zaehler_hoch(self, channel):
        async with self.lock:
            panel = await finde_panel(channel, self.bot.user)
            if panel:
                neu = anzahl_aus_embed(panel.embeds[0]) + 1
                await panel.edit(embed=autoban_embed(neu))
            else:  # Panel wurde gelöscht → neu posten
                neu = 1
                await channel.send(embed=autoban_embed(neu))
            return neu

    async def _loggen(self, guild: discord.Guild, text: str, farbe: int):
        ch = finde_channel(guild, "bot_log")
        if ch:
            try:
                await ch.send(embed=discord.Embed(description=text, color=farbe,
                                                  timestamp=discord.utils.utcnow()))
            except discord.HTTPException:
                pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None or message.author.bot:
            return
        channel = finde_channel(message.guild, "autoban")
        if channel is None or message.channel.id != channel.id:
            return

        autor = message.author
        if not isinstance(autor, discord.Member):
            autor = message.guild.get_member(autor.id) or autor

        # Team wird nie gebannt
        if hasattr(autor, "guild_permissions") and ist_team(autor):
            try:
                await message.delete()
                await channel.send(
                    f"{autor.mention} Team-Mitglieder werden nicht gebannt – aber bitte hier nichts posten. 😉",
                    delete_after=8,
                )
            except discord.HTTPException:
                pass
            return

        try:
            await message.guild.ban(
                autor,
                reason=config.AUTOBAN_GRUND,
                delete_message_seconds=config.AUTOBAN_NACHRICHTEN_LOESCHEN,
            )
        except discord.Forbidden:
            log.warning("Keine Rechte, um %s zu bannen", autor)
            try:
                await message.delete()
            except discord.HTTPException:
                pass
            await self._loggen(
                message.guild,
                f"⚠️ **Fallgrube ausgelöst, aber Bann fehlgeschlagen!**\n{autor.mention} (`{autor.id}`)\n"
                "Die Bot-Rolle muss über der Rolle dieser Person stehen und Bann-Rechte haben.",
                config.Farbe.FALLE,
            )
            return
        except discord.HTTPException as err:
            log.warning("Bann fehlgeschlagen: %s", err)
            return

        anzahl = await self._zaehler_hoch(channel)
        log.info("Autoban: %s (%s) – insgesamt %d", autor, autor.id, anzahl)
        await self._loggen(
            message.guild,
            f"🚨 **Fallgrube ausgelöst!**\n**{autor}** (`{autor.id}`) wurde dauerhaft gebannt.\n"
            f"Nachrichten der letzten {config.AUTOBAN_NACHRICHTEN_LOESCHEN // 3600} Std. wurden gelöscht.\n"
            f"Bisher verbannte Accounts: **{anzahl}**",
            config.Farbe.FALLE,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Autoban(bot))
