"""Willkommens-Nachricht, wenn jemand dem Server beitritt.
WICHTIG: Im Discord Developer Portal muss 'Server Members Intent' an sein."""
import discord
from discord.ext import commands

import config
from utils import finde_channel


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            return
        channel = finde_channel(member.guild, "willkommen")
        if channel is None:
            return

        regeln = finde_channel(member.guild, "regeln")
        regeln_text = regeln.mention if regeln else "Regeln"

        embed = discord.Embed(
            title=config.WILLKOMMEN_TITEL,
            description=config.WILLKOMMEN_TEXT.format(
                user=member.mention, regeln=regeln_text, server=member.guild.name
            ),
            color=config.Farbe.LILA,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Du bist Duelist Nr. {member.guild.member_count} 🌙")

        try:
            await channel.send(content=member.mention, embed=embed,
                               allowed_mentions=discord.AllowedMentions(users=True))
        except discord.HTTPException:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
