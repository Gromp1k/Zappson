import importlib
import os
import discord
from config import *
from commands import * 
import logging
from logging import log as log

class Zappson(commands.Bot):
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
    def init(self, token=TOKEN):
        try:
            self().run(token=token, reconnect=True)
        except Exception as e:
            print(e)

    async def on_ready(self):
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
            await self.__load_commands()
            logging.info(f'Logged in as {self.user}!')
            # Sync commands globally
            await self.tree.sync()
            logging.info("Commands synced successfully!")
            
            # Print all registered commands
            logging.info("Registered commands:")
            for command in await self.tree.fetch_commands():
                logging.info(command)
            
            # Set status back to online after sync
            await self.change_presence(status=discord.Status.online, activity=discord.Game(name="Ready to go!"))
        except discord.errors.Forbidden as e:
            logging.error(f'Forbidden error during on_ready: {e}')
        except Exception as e:
            logging.error(f'Error during on_ready: {e}')
    
    async def __load_commands(self):
        commands_dir = './commands'
        for filename in os.listdir(commands_dir):
            if filename.endswith('.py'):
                filepath = os.path.join(commands_dir, filename)
                spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, 'setup'):
                    module.setup(self)

if __name__ == '__main__':
    Zappson.init()