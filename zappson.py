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

volleyball_events = []

@tree.command(name="info")
async def info(interaction: discord.Interaction, item: str):
    await interaction.response.send_message("Zappson Discord Bot, designed by Gromp1k")

@tree.command(name="start", description="Start a volleyball event")
@app_commands.describe(
    date="Date of the event (DD/MM HH:MM:SS or similar formats)",
    deadline="Deadline for the invite message (optional)",
    leader="Include leader in participants list (true/false)",
    sendlog="Send log to command invoker (true/false)"
)
async def start(interaction: discord.Interaction, date: str, deadline: str = None, leader: bool = True, sendlog: bool = True):
    arg = f"-date {date}"
    if deadline:
        arg += f" -deadline {deadline}"
    arg += f" -leader {leader} -sendlog {sendlog}"

    volleyball_event = VolleyballEventObservableMessage(bot, interaction, arg)
    volleyball_events.append(volleyball_event)
    await volleyball_event.start()

@bot.event
async def on_ready():
    logging.info('Bot is ready.')
    try:
        # Sync commands globally
        await tree.sync()
        logging.info(f'Logged in as {bot.user}!')
        logging.info("Commands synced successfully!")
        
        # Print all registered commands
        logging.info("Registered commands:")
        for command in await tree.fetch_commands():
            logging.info(command)
    except discord.errors.Forbidden as e:
        logging.error(f'Forbidden error during on_ready: {e}')
    except Exception as e:
        logging.error(f'Error during on_ready: {e}')

@bot.event
async def on_reaction_add(reaction, user):
    for event in volleyball_events:
        if isinstance(event, VolleyballEventObservableMessage):
            await event.on_reaction_add(reaction, user)

@bot.event
async def on_reaction_remove(reaction, user):
    for event in volleyball_events:
        if isinstance(event, VolleyballEventObservableMessage):
            await event.on_reaction_remove(reaction, user)

async def cleanup_expired_events():
    while True:
        current_time = datetime.now(timezone.utc)
        for event in volleyball_events[:]:
            if event.deadline_date and current_time >= event.deadline_date:
                await event.cleanup()
                volleyball_events.remove(event)
        await asyncio.sleep(60)  # Check every minute

async def main():
    async with bot:
        bot.loop.create_task(cleanup_expired_events())
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
