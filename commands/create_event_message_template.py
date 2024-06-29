import discord
from discord import Interaction
from discord.ext.commands import Bot
from gui.EventForm import EventFormEmbed

def setup(bot: Bot):
    @bot.tree.command(name="template", description="Creates new template for event message")
    async def create_new_template(interaction: Interaction):
        form_embed = EventFormEmbed()
        embed = form_embed.to_embed()
        view = form_embed.get_view()
        await interaction.response.send_message(embed=embed, view=view)
