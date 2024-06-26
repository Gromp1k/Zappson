from discord import Interaction
from discord.ext.commands import Bot

def setup(bot: Bot):
    bot.tree.command(name="event", description="Creates dedicated volleyball event message")(start_event)

async def start_event(interaction: Interaction):
    await interaction.channel.send("Event!")
