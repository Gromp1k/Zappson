
import discord
from discord.ext import commands

class MessageListener(commands.Cog):
    def __init__(self, bot: commands.Bot, channel_id = 466616249531498497, log_file = "random.txt"):
        self.bot = bot
        self.channel_id = channel_id
        self.log_file = log_file

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages sent by the bot itself
        if message.author == self.bot.user:
            return
        
        # Check if the message is sent in the specified channel
        if message.channel.id == self.channel_id:
            # Log message content and sender name to a file
            with open(self.log_file, 'a') as f:
                f.write(f"Message from {message.author.name}: {message.content}\n")

def setup(bot: commands.Bot, channel_id: int, log_file: str):
    bot.add_cog(MessageListener(bot, channel_id, log_file))
