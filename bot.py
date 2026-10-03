"""
Kapuziner98 Discord-Bot  ·  Yu-Gi-Oh × Lunalight × Abyss Theme
Start:  python bot.py
"""
import logging
import os

import discord
from discord.ext import commands

import config

try:  # lokal: .env-Datei laden (auf Railway nicht nötig)
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("bot")

ERWEITERUNGEN = [
    "cogs.verify",
    "cogs.selfroles",
    "cogs.welcome",
    "cogs.streamplan",
    "cogs.twitch_alerts",
    "cogs.server_setup",
]


class KapuBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True  # für Willkommens-Nachricht (im Developer Portal aktivieren!)
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name=config.BOT_STATUS),
        )

    async def setup_hook(self):
        for ext in ERWEITERUNGEN:
            await self.load_extension(ext)
            log.info("Geladen: %s", ext)

        guild_id = os.getenv("GUILD_ID")
        if guild_id and guild_id.isdigit():
            guild = discord.Object(id=int(guild_id))
            self.tree.copy_global_to(guild=guild)
            befehle = await self.tree.sync(guild=guild)
            log.info("%d Slash-Befehle für Server %s synchronisiert (sofort verfügbar)", len(befehle), guild_id)
        else:
            befehle = await self.tree.sync()
            log.info("%d Slash-Befehle global synchronisiert (kann bis zu 1 Std. dauern)", len(befehle))

    async def on_ready(self):
        log.info("Eingeloggt als %s (%s) – %d Server", self.user, self.user.id, len(self.guilds))


async def fehler_handler(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    log.exception("Fehler in /%s", interaction.command.name if interaction.command else "?", exc_info=error)
    text = "⚠️ Da ist was schiefgelaufen. Prüf, ob die Bot-Rolle ganz oben steht und Administrator hat."
    if isinstance(error, discord.app_commands.MissingPermissions):
        text = "⛔ Dafür fehlen dir die Rechte."
    try:
        if interaction.response.is_done():
            await interaction.followup.send(text, ephemeral=True)
        else:
            await interaction.response.send_message(text, ephemeral=True)
    except discord.HTTPException:
        pass


def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise SystemExit("DISCORD_TOKEN fehlt! (Railway → Variables)")
    bot = KapuBot()
    bot.tree.on_error = fehler_handler
    bot.run(token, log_handler=None)


if __name__ == "__main__":
    main()
