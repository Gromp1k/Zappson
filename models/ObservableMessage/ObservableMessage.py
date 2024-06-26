import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta

class ObservableMessage:
    def __init__(self, bot, channel_id, content, duration):
        self.bot = bot
        self.channel_id = channel_id
        self.content = content
        self.duration = duration
        self.message = None
    
    async def send(self):
        channel = self.bot.get_channel(self.channel_id)
        self.message = await channel.send(self.content)
        self.start_time = datetime.now()

      

