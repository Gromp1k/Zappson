from datetime import datetime, timedelta
import discord
import pytz
import os
import shlex
from dateutil.parser import parse
from discord.ext import commands
from config import DEDICATED_CHANNEL_IDS, PERMITTED_ROLE_IDS, PARTICIPANTS_LIMIT
from constants import TIME_FORMAT

timezone = pytz.timezone('Europe/Warsaw')

def can_use_command(interaction: discord.Interaction) -> bool:
    # Check if the command is used in the dedicated channel
    if interaction.channel_id not in DEDICATED_CHANNEL_IDS:
        return False

    # Check if the user has any of the permitted roles
    user_role_ids = {role.id for role in interaction.user.roles}
    if any(role_id in user_role_ids for role_id in PERMITTED_ROLE_IDS):
        return True

    return False

def parse_command_args(args: str) -> tuple[datetime, datetime, bool, bool]:
    # Default values
    current_year = datetime.now().year
    event_date_str = ""
    deadline_str = ""
    include_leader = True
    send_log = False

    # Parse arguments using shlex for handling quoted strings properly
    args = shlex.split(args)
    it = iter(args)
    current_flag = None

    # Helper function to process each flag
    def process_flag(flag, value):
        nonlocal event_date_str, deadline_str, include_leader, send_log
        if flag == '-date':
            event_date_str = value
        elif flag == '-deadline':
            deadline_str = value
        elif flag == '-leader':
            include_leader = value.lower() == 'true'
        elif flag == '-sendlog':
            send_log = value.lower() == 'true'
        else:
            raise ValueError(f"Invalid flag given: {flag}")

    try:
        for arg in it:
            if arg.startswith('-'):
                current_flag = arg  # Set the current flag
            elif current_flag in ['-date', '-deadline']:
                value = arg
                # Check if the next argument is a time component
                next_arg = next(it, None)
                if next_arg and not next_arg.startswith('-'):
                    value += f" {next_arg}"  # Append time component if present
                else:
                    it = iter([next_arg] + list(it)) if next_arg else it  # Put back the argument for next iteration
                process_flag(current_flag, value)
                current_flag = None
            elif current_flag in ['-leader', '-sendlog']:
                process_flag(current_flag, arg)
                current_flag = None
            else:
                raise ValueError(f"Invalid flag given: {arg}")  # Raise error for unrecognized flags
    except StopIteration:
        raise ValueError("Error: Argument for a flag is missing.")  # Raise error if an argument is missing

    # Ensure timezone is defined for date manipulation
    timezone = pytz.timezone('Europe/Warsaw')

    # Helper function to parse date and time strings
    def parse_date(date_str: str) -> datetime:
        date_formats = ["%d/%m %H:%M", "%d/%m %H", "%d/%m"]  # Supported date formats
        for fmt in date_formats:
            try:
                date = datetime.strptime(date_str, fmt).replace(year=current_year)
                if fmt == "%d/%m":
                    date = date.replace(hour=23, minute=59)  # Default time for date only
                elif fmt == "%d/%m %H":
                    date = date.replace(minute=0)  # Default minutes for date and hour
                return timezone.localize(date)  # Localize the date to the specified timezone
            except ValueError:
                continue
        raise ValueError("Invalid date format.")  # Raise error if none of the formats match

    # Parse date argument
    if event_date_str:
        try:
            event_date = parse_date(event_date_str)
        except (ValueError, TypeError):
            raise ValueError("Invalid event date format.")
    else:
        raise ValueError("The -date parameter is mandatory.")

    # Parse deadline argument
    if deadline_str:
        try:
            deadline_date = parse_date(deadline_str)
        except (ValueError, TypeError):
            raise ValueError("Invalid deadline date format.")
    else:
        deadline_date = event_date - timedelta(hours=9)  # Default deadline is 9 hours before the event

    if event_date <= deadline_date:
        raise ValueError("Event date must be later than the deadline date.")  # Ensure event date is after the deadline

    # Pretty print of final flag values
    print(f"-date set to {event_date.strftime(TIME_FORMAT)}")
    print(f"-deadline set to {deadline_date.strftime(TIME_FORMAT)}")
    print(f"-leader set to {include_leader}")
    print(f"-sendlog set to {send_log}")

    return event_date, deadline_date, include_leader, send_log



def create_summary_message_content(bot: discord.Client, participants: list[tuple[int, str, str]], event_date: datetime) -> tuple[str, str]:
    if not participants:
        return "Nikt się nie zapisał... Lamusy", ""
    
    message_core_participants = f"\n\n**Wyniki zapisów na siatkówkę w dniu {event_date.strftime(TIME_FORMAT)}:**\n\n"
    
    for i, (user_id, emoji, timestamp) in enumerate(participants[:PARTICIPANTS_LIMIT], start=1):
        message_core_participants += f"**{i}** <@{user_id}> {emoji} o __{timestamp}__\n"

    message_substitutes = ""
    if len(participants) > PARTICIPANTS_LIMIT:
        message_substitutes += "\n\n\n**Rezerwowi:**\n\n"
        for i, (user_id, emoji, timestamp) in enumerate(participants[PARTICIPANTS_LIMIT:], start=1):
            message_substitutes += f"*{i}* <@{user_id}> {emoji} o __{timestamp}__\n"

    return message_core_participants, message_substitutes

def create_log_file(event_date: datetime, deadline: datetime, include_leader: bool) -> str:
    log_directory = './log/'
    os.makedirs(log_directory, exist_ok=True)
    log_file_name = f"log_{event_date.strftime(TIME_FORMAT)}.txt"
    log_file_path = os.path.join(log_directory, log_file_name)

    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Log {datetime.now(timezone).isoformat()}\n")
        log_file.write(f"Data spotkania: {event_date.strftime(TIME_FORMAT)}\n")
        log_file.write(f"Deadline głosowania: {deadline.strftime(TIME_FORMAT)}\n")
        log_file.write(f"Uwzględniono Kasię: {'Tak' if include_leader else 'Nie'}\n")
    
    return log_file_path

def parse_env_list(env_var: str) -> list[int]:
    raw_list = os.getenv(env_var, "").strip('[] ').replace(' ', '')
    return [int(x) for x in raw_list.split(',')] if raw_list else []

def format_participants(list_name: str, participants: list[tuple[int, str, str]]) -> str:
    formatted_string = f"List of {list_name}:\n"
    formatted_string += f"{'User ID':<20} {'Emoji':<6} {'Timestamp'}\n"
    formatted_string += "-" * 50 + "\n"
    
    for user_id, emoji, timestamp in participants:
        formatted_string += f"{user_id:<20} {emoji:<6} {timestamp}\n"
    
    return formatted_string
