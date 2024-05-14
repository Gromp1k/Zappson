import discord
from discord.ext import commands
from discord import app_commands
from utils import *
from config import *
from ObservableMessage.VolleyballEventObservableMessage import VolleyballEventObservableMessage
from datetime import datetime, timezone, timedelta
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True

# Initialize the bot with a command prefix (even if it won't be used for slash commands)
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

volleyball_events: list[VolleyballEventObservableMessage] = []

@tree.command(name="info")
async def info(interaction: discord.Interaction):
    await interaction.response.send_message("Zappson Discord Bot, designed by Gromp1k")

@tree.command(name="event", description="Creates dedicated volleyball event message")
@app_commands.describe(
    date="Date of the event (DD/MM HH:MM:SS or similar formats). This argument is mandatory.",
    deadline="Deadline for the invite message (optional). By default is set 9 hours before the event's date.",
    leader="Include leader in participants list (true/false). True by default",
    sendlog="Send log to command invoker (true/false). True by default"
)
async def start(interaction: discord.Interaction, date: str, deadline: str = None, leader: bool = True, sendlog: bool = True):
    arg: str = f"-date {date}"
    if deadline:
        arg += f" -deadline {deadline}"
    arg += f" -leader {leader} -sendlog {sendlog}"

    volleyball_event = VolleyballEventObservableMessage(bot, interaction, arg)
    volleyball_events.append(volleyball_event)
    await volleyball_event.start()

@bot.event
async def on_ready():
    logging.info(r"""
 ______                                        
|___  /                                        
   / /   __ _  _ __   _ __   ___   ___   _ __  
  / /   / _` || '_ \ | '_ \ / __| / _ \ | '_ \ 
./ /___| (_| || |_) || |_) |\__ \| (_) || | | |
\_____/ \__,_|| .__/ | .__/ |___/ \___/ |_| |_|
              | |    | |                       
              |_|    |_|                       
 _                 _____                                 __   _    
| |               |  __ \                               /  | | |   
| |__   _   _     | |  \/ _ __   ___   _ __ ___   _ __  `| | | | __
| '_ \ | | | |    | | __ | '__| / _ \ | '_ ` _ \ | '_ \  | | | |/ /
| |_) || |_| |    | |_\ \| |   | (_) || | | | | || |_) |_| |_|   < 
|_.__/  \__, |     \____/|_|    \___/ |_| |_| |_|| .__/ \___/|_|\_\
         __/ |                                   | |               
        |___/                                    |_|               
""")
    try:
        # Set status to syncing
        await bot.change_presence(activity=discord.Game(name="Syncing commands..."))
        
        # Sync commands globally
        await tree.sync()
        logging.info(f'Logged in as {bot.user}!')
        logging.info("Commands synced successfully!")
        
        # Print all registered commands
        logging.info("Registered commands:")
        for command in await tree.fetch_commands():
            logging.info(command)
        
        # Set status back to online after sync
        await bot.change_presence(status=discord.Status.online)
    except discord.errors.Forbidden as e:
        logging.error(f'Forbidden error during on_ready: {e}')
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Sync Error"))
    except Exception as e:
        logging.error(f'Error during on_ready: {e}')
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Sync Error"))

@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    for event in volleyball_events:
        if isinstance(event, VolleyballEventObservableMessage):
            await event.on_reaction_add(reaction, user)

@bot.event
async def on_reaction_remove(reaction: discord.Reaction, user: discord.User):
    for event in volleyball_events:
        if isinstance(event, VolleyballEventObservableMessage):
            await event.on_reaction_remove(reaction, user)

async def cleanup_expired_events():
    while True:
        current_time: datetime = datetime.now(timezone.utc)
        for event in volleyball_events[:]:
            if event.deadline_date and current_time >= event.deadline_date:
                volleyball_events.remove(event)
        await asyncio.sleep(60)  # Check every minute

async def main():
    async with bot:
        bot.loop.create_task(cleanup_expired_events())
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
