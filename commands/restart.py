import os
import sys
from discord import Interaction
from discord.ext.commands import Bot
from configs.zlogger import ZLogger as zl


def setup(bot: Bot):
    @bot.tree.command(name="restart", description="Restarts bot")
    async def restart(interaction: Interaction):
        if await bot.is_owner(interaction.user) and bot.owner_id is not None:
            zl.info("About to restart the bot")
            await interaction.response.send_message("Bot is restarting...")
            os.execv(sys.executable, ['python'] + sys.argv)
