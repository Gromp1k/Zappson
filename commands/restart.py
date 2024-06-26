import os
import sys
import logging
from discord import Interaction
from discord.ext.commands import Bot
from zappson import Zappson

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup(bot: Bot):
    @bot.tree.command(name="restart", description="Restarts bot")
    async def restart(interaction: Interaction):
        if await bot.is_owner(interaction.user) and bot.owner_id is not None:
            logger.info("Restarting the bot.")
            await interaction.response.send_message("Bot is restarting...")
            os.execv(sys.executable, ['python'] + sys.argv)
