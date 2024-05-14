from datetime import datetime, timedelta
import pytz
import os
import shlex
from dateutil.parser import parse
from discord.ext import commands
from config import DEDICATED_CHANNEL_IDS, PERMITTED_ROLE_IDS, PARTICIPANTS_LIMIT

timezone = pytz.timezone('Europe/Warsaw')

def can_use_command(interaction) -> bool:
    # Check if the command is used in the dedicated channel
    if interaction.channel_id not in DEDICATED_CHANNEL_IDS:
        return False

    # Check if the user has any of the permitted roles
    user_role_ids = {role.id for role in interaction.user.roles}
    if any(role_id in user_role_ids for role_id in PERMITTED_ROLE_IDS):
        return True

    return False

def parse_command_args(args: str):
    # Default values
    current_year = datetime.now().year
    event_date_str = None
    deadline_str = None
    include_leader = True
    send_log = False

    # Parse arguments
    args = shlex.split(args)
    it = iter(args)
    try:
        for arg in it:
            if arg == '-date':
                event_date_str = next(it, None)
            elif arg == '-deadline':
                deadline_str = next(it, None)
            elif arg == '-leader':
                include_leader = next(it, None).lower() == 'true'
            elif arg == '-sendlog':
                send_log = next(it, None).lower() == 'true'
            else:
                raise ValueError(f"Invalid flag given: {arg}")
    except StopIteration:
        raise ValueError("Error: Argument for a flag is missing.")

    # Ensure timezone is defined for date manipulation
    timezone = pytz.timezone('Europe/Warsaw')

    # Parse date argument
    if event_date_str:
        try:
            event_date = parse(f"{event_date_str} {current_year}", dayfirst=True)
            event_date = timezone.localize(event_date)
        except (ValueError, TypeError):
            raise ValueError("Invalid event date format.")
    else:
        raise ValueError("The -date parameter is mandatory.")

    # Parse deadline argument
    if deadline_str:
        try:
            deadline_date = parse(f"{deadline_str} {current_year}", dayfirst=True)
            deadline_date = timezone.localize(deadline_date)
        except (ValueError, TypeError):
            raise ValueError("Invalid deadline date format.")
    else:
        deadline_date = event_date - timedelta(hours=9)

    if event_date <= deadline_date:
        raise ValueError("Event date must be later than the deadline date.")

    return event_date, deadline_date, include_leader, send_log

def create_summary_message_content(bot, participants: list, event_date):
    if not participants:
        return "Nikt się nie zapisał... Lamusy", ""
    
    message_core_participants = f"\n\n**Wyniki zapisów na siatkówkę w dniu {event_date}:**\n\n"
    
    for i, (user_id, emoji, timestamp) in enumerate(participants[:PARTICIPANTS_LIMIT], start=1):
        user = bot.get_user(user_id)
        user_mention = user.mention if user else f"User ID {user_id}"
        message_core_participants += f"**{i}** {user_mention} {emoji} o __{timestamp}__\n"

    message_substitutes = ""
    if len(participants) > PARTICIPANTS_LIMIT:
        message_substitutes += "\n\n\n**Rezerwowi:**\n\n"
        for i, (user_id, emoji, timestamp) in enumerate(participants[PARTICIPANTS_LIMIT:], start=1):
            user = bot.get_user(user_id)
            user_mention = user.mention if user else f"User ID {user_id}"
            message_substitutes += f"*{i}* {user_mention} {emoji} o __{timestamp}__\n"

    return message_core_participants, message_substitutes

def create_log_file(event_date, deadline, include_leader):
    log_directory = './log/'
    os.makedirs(log_directory, exist_ok=True)
    log_file_name = f"log_{event_date.strftime('%Y-%m-%d')}.txt"
    log_file_path = os.path.join(log_directory, log_file_name)

    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Log {datetime.now(timezone).isoformat()}\n")
        log_file.write(f"Data spotkania: {event_date.strftime('%d/%m/%Y %H:%M:%S')}\n")
        log_file.write(f"Deadline głosowania: {deadline.strftime('%d/%m/%Y %H:%M:%S')}\n")
        log_file.write(f"Uwzględniono Kasię: {'Tak' if include_leader else 'Nie'}\n")
    
    return log_file_path

def parse_env_list(env_var: str) -> list[int]:
    raw_list = os.getenv(env_var, "").strip('[] ').replace(' ', '')
    return [int(x) for x in raw_list.split(',')] if raw_list else []

def format_participants(list_name, participants):
    formatted_string = f"List of {list_name}:\n"
    formatted_string += f"{'User ID':<20} {'Emoji':<6} {'Timestamp'}\n"
    formatted_string += "-" * 50 + "\n"
    
    for user_id, emoji, timestamp in participants:
        formatted_string += f"{user_id:<20} {emoji:<6} {timestamp}\n"
    
    return formatted_string
