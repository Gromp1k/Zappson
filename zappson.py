import discord
from discord.ext import commands
import settings
from settings import logger

class Zappson(commands.Bot):
    '''
    Custom Client for zappson.py - Created by Gromp1k
    '''
    def __init__(self):
        # Setup Discord bot
        intents = discord.Intents.default()
        intents.guilds = True
        intents.messages = True
        intents.members = True
        intents.reactions = True
        intents.message_content = True

        super().__init__(command_prefix="/", intents=intents)
        self.owner_id = 350370126693924885
        

    @classmethod
    def init(cls, token= settings.TOKEN):
        try:
            cls().run(token=token, reconnect=True, root_logger=True)
        except Exception as e:
            print(e)

    async def on_ready(self):
        logger.info(r"""
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
            logger.info(f'{self.user} {self.user.id}!')

            for cog_file in settings.COGS_DIR.glob("*.py"):
                if cog_file != "__init__.py":
                    ext_name = f"cogs.{cog_file.name[:-3]}"
                    await self.load_extension(ext_name)
                    logger.info(f"Loaded {ext_name}")

            # Lists all text channels in the guilds
            # for guild in self.guilds:
            #     logging.info(f"Guild: {guild.name}")
            #     for channel in guild.text_channels:
            #         logging.info(f" - {channel.name} (ID: {channel.id})")
            
            await self.tree.sync(guild=None)

            # Set status back to online after sync
            await self.change_presence(status=discord.Status.online, activity=discord.Game(name="Ready to go!"))
        except discord.errors.Forbidden as e:
            logger.error(f'Forbidden error during on_ready: {e}')
        except Exception as e:
            logger.error(f'Error during on_ready: {e}')
        #Replace with your channel ID and desired log file path

if __name__ == '__main__':
    Zappson.init()
