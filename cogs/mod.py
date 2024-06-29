import discord
from discord.ext import commands
from discord.ext.commands import Bot

import discord.ext

class Mod(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
    

    @discord.app_commands.command(description="bans the user from the server")
    async def ban(self, interaction: discord.Interaction):
        await interaction.channel.send("will do!")

    # @discord.app_commands.
    # async def on_message_send(self, message: discord.Message):
    #     # If this contains discord link.
    #     pass

async def setup(bot: Bot):
    await bot.add_cog(Mod(bot))