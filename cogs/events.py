from discord import app_commands
from discord.ext import commands
from discord import Interaction

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="create_template", description="Presents form to create new event message template.")
    async def create_template(self, interaction: Interaction):
        await interaction.response.send_message("will do!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
