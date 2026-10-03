"""Reaktionsrollen: Reaktion drauf = Rolle bekommen, Reaktion weg = Rolle weg.
Die Panels kommen komplett aus config.REAKTIONS_PANELS.

Funktioniert auch nach einem Bot-Neustart: Der Bot erkennt seine Panels am Titel.
"""
import logging

import discord
from discord.ext import commands

import config
from utils import emoji_norm, finde_channel, finde_rolle

log = logging.getLogger("reaktionsrollen")


def panel_embed(panel: dict, guild: discord.Guild | None = None) -> discord.Embed:
    galerie = finde_channel(guild, "galerie") if guild else None
    intro = panel["intro"].replace("{galerie}", galerie.mention if galerie else "der Künstler-Galerie")
    zeilen = [f"{r['emoji']} — **{r['label']}** ({r['info']})" for r in panel["rollen"]]
    embed = discord.Embed(
        title=panel["titel"],
        description=f"{intro}\n\n" + "\n".join(zeilen),
        color=panel.get("farbe", config.Farbe.LILA),
    )
    embed.set_footer(text=config.REAKTIONS_FOOTER)
    return embed


def panel_zu_titel(titel: str | None) -> dict | None:
    for p in config.REAKTIONS_PANELS:
        if p["titel"] == titel:
            return p
    return None


class ReaktionsRollen(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.panel_nachrichten: dict[int, dict] = {}  # message_id → panel

    # ── Panels posten / wiederfinden ─────────────────────────
    async def panel_posten(self, channel: discord.TextChannel, panel: dict) -> discord.Message:
        msg = await channel.send(embed=panel_embed(panel, channel.guild))
        for r in panel["rollen"]:
            try:
                await msg.add_reaction(r["emoji"])
            except discord.HTTPException:
                log.warning("Emoji %s konnte nicht als Reaktion gesetzt werden", r["emoji"])
        self.panel_nachrichten[msg.id] = panel
        return msg

    async def panels_posten(self, channel: discord.TextChannel, nur_fehlende: bool = True) -> int:
        """Postet alle Panels. nur_fehlende=True → nur die, die es im Channel noch nicht gibt."""
        vorhanden = set()
        if nur_fehlende:
            async for msg in channel.history(limit=50):
                if msg.author.id == self.bot.user.id and msg.embeds:
                    p = panel_zu_titel(msg.embeds[0].title)
                    if p:
                        vorhanden.add(p["titel"])
                        self.panel_nachrichten[msg.id] = p
        anzahl = 0
        for panel in config.REAKTIONS_PANELS:
            if panel["titel"] not in vorhanden:
                await self.panel_posten(channel, panel)
                anzahl += 1
        return anzahl

    async def cache_aufbauen(self):
        for guild in self.bot.guilds:
            channel = finde_channel(guild, "rollen")
            if channel is None:
                continue
            try:
                async for msg in channel.history(limit=50):
                    if msg.author.id == self.bot.user.id and msg.embeds:
                        p = panel_zu_titel(msg.embeds[0].title)
                        if p:
                            self.panel_nachrichten[msg.id] = p
            except discord.HTTPException:
                pass
        log.info("%d Reaktionsrollen-Panel(s) gefunden", len(self.panel_nachrichten))

    @commands.Cog.listener()
    async def on_ready(self):
        await self.cache_aufbauen()

    # ── Reaktionen ───────────────────────────────────────────
    def _eintrag(self, payload: discord.RawReactionActionEvent):
        panel = self.panel_nachrichten.get(payload.message_id)
        if not panel:
            return None, None
        e = emoji_norm(payload.emoji)
        for r in panel["rollen"]:
            if emoji_norm(r["emoji"]) == e:
                return panel, r
        return panel, None

    async def _member(self, guild: discord.Guild, user_id: int):
        m = guild.get_member(user_id)
        if m is None:
            try:
                m = await guild.fetch_member(user_id)
            except discord.HTTPException:
                return None
        return m

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None or payload.user_id == self.bot.user.id:
            return
        panel, eintrag = self._eintrag(payload)
        if panel is None:
            return
        guild = self.bot.get_guild(payload.guild_id)
        member = payload.member or await self._member(guild, payload.user_id)
        if member is None or member.bot:
            return

        if eintrag is None:
            # fremde Reaktion auf dem Panel → wieder entfernen, damit es sauber bleibt
            channel = guild.get_channel(payload.channel_id)
            if channel:
                try:
                    await channel.get_partial_message(payload.message_id).remove_reaction(payload.emoji, member)
                except discord.HTTPException:
                    pass
            return

        rolle = finde_rolle(guild, eintrag["rolle"])
        if rolle and rolle not in member.roles:
            try:
                await member.add_roles(rolle, reason="Reaktionsrolle")
            except discord.HTTPException:
                log.warning("Konnte %s nicht vergeben (Bot-Rolle zu weit unten?)", rolle.name)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None or payload.user_id == self.bot.user.id:
            return
        panel, eintrag = self._eintrag(payload)
        if eintrag is None:
            return
        guild = self.bot.get_guild(payload.guild_id)
        member = await self._member(guild, payload.user_id)
        if member is None:
            return
        rolle = finde_rolle(guild, eintrag["rolle"])
        if rolle and rolle in member.roles:
            try:
                await member.remove_roles(rolle, reason="Reaktionsrolle entfernt")
            except discord.HTTPException:
                log.warning("Konnte %s nicht entfernen", rolle.name)


async def setup(bot: commands.Bot):
    await bot.add_cog(ReaktionsRollen(bot))
