import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
import re
from datetime import datetime
from utils.link_tracker import LinkTracker  # Import the LinkTracker class

class Dev(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.link_tracker = LinkTracker()  # Initialize the LinkTracker

    @app_commands.command(name="load_cog", description="Loads a specified cog")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def load_cog(self, interaction: Interaction, cog: str):
        await interaction.response.defer(ephemeral=True)  # Defer the response to avoid timeout
        try:
            await self.bot.load_extension(f"cogs.{cog.lower()}")
            await interaction.followup.send(f"Cog {cog} loaded successfully.", ephemeral=True, delete_after=10)
        except Exception as e:
            await interaction.followup.send(f"Error loading cog {cog}: {e}", ephemeral=True, delete_after=10)

    @app_commands.command(name="unload_cog", description="Unloads a specified cog")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def unload_cog(self, interaction: Interaction, cog: str):
        await interaction.response.defer(ephemeral=True)  # Defer the response to avoid timeout
        try:
            await self.bot.unload_extension(f"cogs.{cog.lower()}")
            await interaction.followup.send(f"Cog {cog} unloaded successfully.", ephemeral=True, delete_after=10)
        except Exception as e:
            await interaction.followup.send(f"Error unloading cog {cog}: {e}", ephemeral=True, delete_after=10)

    @app_commands.command(name="reset", description="Reloads a specified cog")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def reset(self, interaction: Interaction, cog: str):
        await interaction.response.defer(ephemeral=True)  # Defer the response to avoid timeout
        try:
            self.bot.reload_extension(f"cogs.{cog.lower()}")
            await interaction.followup.send(f"Cog {cog} reloaded successfully.", ephemeral=True, delete_after=10)
        except Exception as e:
            await interaction.followup.send(f"Error reloading cog {cog}: {e}", ephemeral=True, delete_after=10)

    @load_cog.error
    @unload_cog.error
    @reset.error
    async def command_error(self, interaction: Interaction, error: app_commands.AppCommandError):
        if interaction.response.is_done():
            await interaction.followup.send("You are missing the required permissions to run this command.", ephemeral=True, delete_after=10)
        else:
            await interaction.response.send_message("You are missing the required permissions to run this command.", ephemeral=True, delete_after=10)

    async def get_active_invite_links(self, guild: discord.Guild):
        active_invites = await guild.invites()
        invite_links = [invite.url for invite in active_invites]
        return invite_links

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        # Regex pattern to match Discord Nitro scam links and server invites
        discord_link_regex = r"(https?://)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com/invite)/[a-zA-Z0-9]+|discord-gift\.(com|net|org|xyz)/[a-zA-Z0-9]+"

        match = re.search(discord_link_regex, message.content)

        if match:
            link = match.group(0)
            await message.channel.send(link + " detected!")  # Inform about detected link

            # Get active invite links for the guild
            active_invite_links = await self.get_active_invite_links(message.guild)

            if link in active_invite_links:
                await message.channel.send("This is an active invite link for the guild.")
                return

            if self.link_tracker.is_banned(link):
                await message.channel.send("boom, banned !")
                try:
                    # Ban user
                    await message.author.ban(reason="Posting a banned Discord link. Zappson test!")
                    
                    # Delete related messages
                    async for msg in message.channel.history(limit=100):  # Adjust the limit as needed
                        if link in msg.content:
                            await msg.delete()

                    # Send proof to a dedicated channel
                    log_channel = discord.utils.get(message.guild.channels, id=737445203295862846)  # Replace 'ban-logs' with your log channel name
                    if log_channel:
                        embed = discord.Embed(title="hokus pokus, czary mary - nie umiem rymować, rozdaję bany!", color=discord.Color.red())
                        embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=False)
                        embed.add_field(name="Powód", value="Wrzucanie linków NSFW", inline=False)
                        embed.set_footer(text=f"Ban Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                        await log_channel.send(embed=embed)
                except discord.Forbidden:
                    await message.channel.send("I do not have permission to kick this user.")
                except discord.HTTPException as e:
                    await message.channel.send(f"An error occurred: {e}")

            else:
                self.link_tracker.add_link(link)
                #await message.channel.send("added !")

async def setup(bot: commands.Bot):
    await bot.add_cog(Dev(bot))
