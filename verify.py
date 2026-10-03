"""Regeln + Verify-Button: Wer die Regeln akzeptiert, bekommt die Duelist-Rolle."""
import discord
from discord.ext import commands

import config
from utils import finde_channel, finde_rolle


def regeln_embed() -> discord.Embed:
    embed = discord.Embed(
        title=config.REGELN_TITEL,
        description=config.REGELN_INTRO,
        color=config.Farbe.LILA,
    )
    for i, (titel, text) in enumerate(config.REGELN, start=1):
        embed.add_field(name=f"{i}. {titel}", value=text, inline=False)
    embed.set_footer(text=config.REGELN_FOOTER)
    return embed


class VerifyView(discord.ui.View):
    """Dauerhafter Button – funktioniert auch nach Bot-Neustart."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label=config.VERIFY_BUTTON_LABEL,
        emoji=config.VERIFY_BUTTON_EMOJI,
        style=discord.ButtonStyle.success,
        custom_id="kapu:verify",
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        rolle = finde_rolle(interaction.guild, "member")
        if rolle is None:
            await interaction.response.send_message(
                "⚠️ Die Duelist-Rolle fehlt – bitte ein Teammitglied `/setup` ausführen lassen.",
                ephemeral=True,
            )
            return

        if rolle in interaction.user.roles:
            await interaction.response.send_message(
                "Du bist schon Duelist – viel Spaß im Abgrund! 🕳️", ephemeral=True
            )
            return

        try:
            await interaction.user.add_roles(rolle, reason="Regeln akzeptiert")
        except discord.Forbidden:
            await interaction.response.send_message(
                "⚠️ Ich darf dir die Rolle nicht geben. Die Bot-Rolle muss in der "
                "Rollenliste ÜBER der Duelist-Rolle stehen.",
                ephemeral=True,
            )
            return

        rollen_ch = finde_channel(interaction.guild, "rollen")
        hinweis = f"\nIn {rollen_ch.mention} kannst du dir per Reaktion deine Ping-Rollen holen!" if rollen_ch else ""
        await interaction.response.send_message(
            f"🃏 **Willkommen, Duelist!** Du hast jetzt Zugriff auf den ganzen Server.{hinweis}",
            ephemeral=True,
        )


class Verify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


async def setup(bot: commands.Bot):
    bot.add_view(VerifyView())
    await bot.add_cog(Verify(bot))
