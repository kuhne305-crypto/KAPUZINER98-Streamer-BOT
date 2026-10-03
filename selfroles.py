"""Self-Roles per Button. Panels kommen komplett aus config.SELFROLE_PANELS.

Neue Self-Role hinzufügen:
  1. Rolle in config.ROLLEN eintragen
  2. Button im passenden Panel in config.SELFROLE_PANELS eintragen
  3. Bot neu starten, /setup (legt die Rolle an) und /panel art:Self-Roles
"""
import discord
from discord.ext import commands

import config
from utils import finde_rolle

STILE = {
    "lila": discord.ButtonStyle.primary,
    "gruen": discord.ButtonStyle.success,
    "grau": discord.ButtonStyle.secondary,
    "rot": discord.ButtonStyle.danger,
}


class RollenButton(discord.ui.Button):
    def __init__(self, rolle_key: str, label: str, emoji: str | None, stil: str):
        super().__init__(
            label=label,
            emoji=emoji,
            style=STILE.get(stil, discord.ButtonStyle.secondary),
            custom_id=f"kapu:selfrole:{rolle_key}",
        )
        self.rolle_key = rolle_key

    async def callback(self, interaction: discord.Interaction):
        rolle = finde_rolle(interaction.guild, self.rolle_key)
        if rolle is None:
            await interaction.response.send_message(
                "⚠️ Diese Rolle gibt es noch nicht – bitte das Team `/setup` ausführen lassen.",
                ephemeral=True,
            )
            return
        try:
            if rolle in interaction.user.roles:
                await interaction.user.remove_roles(rolle, reason="Self-Role entfernt")
                text = f"➖ **{rolle.name}** wurde entfernt."
            else:
                await interaction.user.add_roles(rolle, reason="Self-Role gewählt")
                text = f"➕ **{rolle.name}** ist jetzt in deinem Deck!"
        except discord.Forbidden:
            text = "⚠️ Ich darf diese Rolle nicht vergeben – die Bot-Rolle muss weiter oben stehen."
        await interaction.response.send_message(text, ephemeral=True)


class PanelView(discord.ui.View):
    def __init__(self, panel: dict):
        super().__init__(timeout=None)
        for b in panel["buttons"]:
            self.add_item(RollenButton(b["rolle"], b["label"], b.get("emoji"), b.get("stil", "grau")))


def panel_embed(panel: dict) -> discord.Embed:
    embed = discord.Embed(title=panel["titel"], description=panel["text"], color=panel.get("farbe", config.Farbe.LILA))
    embed.set_footer(text=f"{config.STREAMER_NAME} · Deck-Auswahl")
    return embed


def alle_panels():
    """Liste aus (Embed, View) für alle Panels."""
    return [(panel_embed(p), PanelView(p)) for p in config.SELFROLE_PANELS]


class SelfRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


async def setup(bot: commands.Bot):
    for p in config.SELFROLE_PANELS:
        bot.add_view(PanelView(p))
    await bot.add_cog(SelfRoles(bot))
