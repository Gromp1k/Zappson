from discord import Interaction
from discord.ext.commands import Bot

def setup(bot: Bot):
    bot.tree.command(name="info", description="Creates dedicated volleyball event message")(info)

async def info(interaction: Interaction):
    await interaction.response.send_message("Zappson Discord Bot, designed by Gromp1k", ephemeral=True, delete_after=60)