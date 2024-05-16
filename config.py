import configparser
import discord
from discord.ext import commands

# Read properties file
config = configparser.ConfigParser()
config.read('config.properties')

def __parse_int_list_from_string(list_string: str) -> list[int]:
    list_string = list_string.strip("[] ")
    if not list_string:
        return []
    return [int(item) for item in list_string.split(',')]

# Bot configuration
TOKEN = config['DEFAULT'].get('TOKEN')

# Roles and IDs
DEDICATED_CHANNEL_IDS = __parse_int_list_from_string(config['DEFAULT'].get('DEDICATED_CHANNEL_IDS', ''))
PERMITTED_ROLE_IDS = __parse_int_list_from_string(config['DEFAULT'].get('PERMITTED_ROLE_IDS', ''))

# Simple int parsing with default
NOTIFY_ROLE_ID = int(config['DEFAULT'].get('NOTIFY_ROLE_ID', 0))

# Emojis/Reactions
PLUS_1_REACTION = config['DEFAULT'].get('PLUS_1_REACTION')
VOLLEYBALL_EMOJI = config['DEFAULT'].get('VOLLEYBALL_EMOJI')

# Custom emoji parsing
PLUS_1_REACTION_NAME = PLUS_1_REACTION.strip('<>').split(':')[1]
PLUS_1_REACTION_ID = int(PLUS_1_REACTION.strip('<>').split(':')[2] if len(PLUS_1_REACTION.strip('<>').split(':')) == 3 else 0)
PLUS_1_EMOJI = f"<:{PLUS_1_REACTION_NAME}:{PLUS_1_REACTION_ID}>"

LEADER_ID = int(config['DEFAULT'].get('LEADER_ID', 0))

MESSAGE_REMINDER_NOTE = (
    "\n**UWAGA!** Jeżeli ktoś z zapisanych od tej chwili nie zdecyduje się na jednak na udział, proszę poinformować o tym na kanale:\n\n"
    "**1. Pierwszeństwo w udziale mają osoby, które zostały wpisane na listę rezerwową**Jeżeli na liście rezerwowej są dostępni zawodnicy, oznacz odpowiedniego użytkownika i poinformuj o zwolnieniu miejsca.\n\n"
    "**2. Zawodnik rezerwowy ma obowiązek potwierdzić chęć uczestnictwa lub zrezygnować** umożliwiając tym samym zgłoszenie się kolejnej osobie z listy rezerwowej.\n\n"
    "**3. W przypadku braku dalszych zawodników rezerwowych, użyj ogólnego pingu @siatkóweczka, aby poinformować o wolnym miejscu.**\n"
    "**W przypadku niepojawienia się bez wcześniejszego poinformowania będą wyciągane konsekwencje.**\n\n"
    "*Pozdrawiam wszystkie kochane misie* Żᴀᴘᴘsᴏɴ"
)

PARTICIPANTS_LIMIT = 21

# Setup Discord bot
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.members = True
intents.reactions = True
intents.message_content = True

bot = commands.Bot(command_prefix='--', intents=intents)

print("Config init")
