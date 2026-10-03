"""Streamplan als Embed im #streamplan-Channel.

Der Plan wird direkt in der Bot-Nachricht gespeichert (keine Datenbank nötig –
perfekt für Railway, wo Dateien bei jedem Neustart weg sind).

/streamplan setzen  tag uhrzeit spiel   → Tag eintragen
/streamplan pause   tag                 → Tag auf Pause setzen
/streamplan leeren                      → ganze Woche auf Pause
"""
import discord
from discord import app_commands
from discord.ext import commands

import config
from utils import finde_channel, letzte_bot_nachricht

TAGE = [t for t, _ in config.STREAMPLAN_TAGE]
TAG_CHOICES = [app_commands.Choice(name=t, value=t) for t in TAGE]


def leerer_plan() -> dict:
    return {t: None for t in TAGE}


def plan_aus_embed(embed: discord.Embed) -> dict:
    plan = leerer_plan()
    for feld in embed.fields:
        for tag in TAGE:
            if feld.name.endswith(tag):
                plan[tag] = None if feld.value == config.STREAMPLAN_PAUSE else feld.value
    return plan


def plan_embed(plan: dict) -> discord.Embed:
    embed = discord.Embed(
        title=config.STREAMPLAN_TITEL,
        description=config.STREAMPLAN_INFO,
        color=config.Farbe.LILA,
        url=config.TWITCH_URL,
    )
    for tag, emoji in config.STREAMPLAN_TAGE:
        embed.add_field(name=f"{emoji} {tag}", value=plan.get(tag) or config.STREAMPLAN_PAUSE, inline=False)
    embed.set_footer(text="Zuletzt aktualisiert")
    embed.timestamp = discord.utils.utcnow()
    return embed


def _ist_plan(msg: discord.Message) -> bool:
    return bool(msg.embeds) and msg.embeds[0].title == config.STREAMPLAN_TITEL


async def finde_plan_nachricht(channel, bot_user):
    return await letzte_bot_nachricht(channel, bot_user, _ist_plan, limit=50)


async def plan_posten_oder_holen(channel, bot_user) -> discord.Message:
    msg = await finde_plan_nachricht(channel, bot_user)
    if msg:
        return msg
    return await channel.send(embed=plan_embed(leerer_plan()))


class Streamplan(commands.Cog):
    gruppe = app_commands.Group(
        name="streamplan",
        description="Streamplan verwalten",
        guild_only=True,
        default_permissions=discord.Permissions(manage_guild=True),
    )

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _aendern(self, interaction: discord.Interaction, aenderung):
        channel = finde_channel(interaction.guild, "streamplan")
        if channel is None:
            await interaction.response.send_message(
                "⚠️ Kein Streamplan-Channel gefunden – erst `/setup` ausführen.", ephemeral=True
            )
            return
        await interaction.response.defer(ephemeral=True)
        msg = await plan_posten_oder_holen(channel, self.bot.user)
        plan = plan_aus_embed(msg.embeds[0])
        aenderung(plan)
        await msg.edit(embed=plan_embed(plan))
        await interaction.followup.send(f"✅ Streamplan aktualisiert: {msg.jump_url}", ephemeral=True)

    @gruppe.command(name="setzen", description="Einen Stream-Tag eintragen")
    @app_commands.describe(tag="Wochentag", uhrzeit="z. B. 20:00 oder 19–23 Uhr", spiel="z. B. Master Duel")
    @app_commands.choices(tag=TAG_CHOICES)
    async def setzen(self, interaction: discord.Interaction, tag: app_commands.Choice[str],
                     uhrzeit: app_commands.Range[str, 1, 30], spiel: app_commands.Range[str, 1, 100]):
        def aendern(plan):
            plan[tag.value] = f"**{uhrzeit}** · {spiel}"
        await self._aendern(interaction, aendern)

    @gruppe.command(name="pause", description="Einen Tag auf Pause setzen")
    @app_commands.choices(tag=TAG_CHOICES)
    async def pause(self, interaction: discord.Interaction, tag: app_commands.Choice[str]):
        def aendern(plan):
            plan[tag.value] = None
        await self._aendern(interaction, aendern)

    @gruppe.command(name="leeren", description="Die ganze Woche auf Pause setzen")
    async def leeren(self, interaction: discord.Interaction):
        def aendern(plan):
            plan.update(leerer_plan())
        await self._aendern(interaction, aendern)


async def setup(bot: commands.Bot):
    await bot.add_cog(Streamplan(bot))
