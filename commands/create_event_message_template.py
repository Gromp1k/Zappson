from discord import Interaction
from discord.ext.commands import Bot
from discord import app_commands

async def create_new_template(interaction: Interaction, name: str):
    await interaction.channel.send(f"Event template created with name: {name}")

def setup(bot: Bot):
    # Check if the command already exists to avoid re-registering
    @bot.tree.command(name="template", description="Creates new template for event message")
    @app_commands.describe(name="The name of the event template")
    async def wrapper(interaction: Interaction, name: str):
        await create_new_template(interaction, name)

