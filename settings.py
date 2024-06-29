import configparser
from logging.config import dictConfig
import pathlib
import logging

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

BASE_DIR = pathlib.Path(__file__).parent
CMDS_DIR = BASE_DIR / "cmds"
COGS_DIR = BASE_DIR / "cogs"


LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard": {"format": "%(levelname)-10s - %(name)-15s : %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/infos.log",
            "mode": "w",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "bot": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "discord": {
            "handlers": ["console2", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)
