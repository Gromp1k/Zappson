from discord import Interaction
from discord.ext.commands import Bot

def setup(bot: Bot):
    @bot.tree.command(name="event", description="Creates dedicated volleyball event message")
    async def start_event(interaction: Interaction, date: str, deadline: str = None, leader: bool = True, sendlog: bool = True):
        await interaction.channel.send("Event!")
        user = interaction.user

        # check permissions 
        dm_channel = await user.create_dm()
        await dm_channel.send("Please fill out the form below:")

       
