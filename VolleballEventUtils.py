from datetime import timedelta
import discord
import pytz
import os
from EventData.VolleyballEventData import *
from settings import DEDICATED_CHANNEL_IDS, PERMITTED_ROLE_IDS, PARTICIPANTS_LIMIT
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

def parse_command_args(event_date_str: str, deadline_str: str, include_leader: bool, send_log: bool) -> VolleyballEventData:   
    # Parse -date glag value
    if event_date_str:
        try:
            event_date: datetime = parse_date(event_date_str)
        except (ValueError, TypeError):
            raise ValueError("Invalid event date format.")
    else:
        raise ValueError("The -date parameter is mandatory.")

    # Parse -deadline flag value
    if deadline_str:
        try:
            deadline_date: datetime = parse_date(deadline_str)
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

    return VolleyballEventData(event_date, deadline_date, include_leader, send_log);

# Helper function to parse date and time strings
def parse_date(date_str: str) -> datetime:
    print(f"parse_date({date_str})")
    current_year = datetime.now().year
    timezone = pytz.timezone('Europe/Warsaw')
    date_formats = ["%d/%m %H:%M", "%d/%m %H", "%d/%m"]
    
    for date_format in date_formats:
        try:
            if date_format == "%d/%m %H:%M":
                date = datetime.strptime(date_str, date_format)
            elif date_format == "%d/%m %H":
                date = datetime.strptime(date_str, date_format)
                date = date.replace(minute=0)
            elif date_format == "%d/%m":
                date = datetime.strptime(date_str, date_format)
                date = date.replace(hour=23, minute=59)
            else:
                continue
            date = date.replace(year=current_year)
            date = timezone.localize(date)
            return date
        
        except ValueError:
            continue
    
    raise ValueError("Date string does not match any of the expected formats.")
    
    
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

def create_log_file(event_data: VolleyballEventData) -> str:
    event_date: datetime
    deadline: datetime
    include_leader: bool

    event_date, deadline, include_leader, _ = event_data.getData();

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

def format_participants(participants: list[tuple[int, str, str]]) -> str:

    if len(participants) == 0:
        return "participants are empty"

    formatted_string = f"List of pariticipants:\n"
    formatted_string += f"{'User ID':<20} {'Emoji':<6} {'Timestamp'}\n"
    formatted_string += "-" * 50 + "\n"
    
    for user_id, emoji, timestamp in participants:
        formatted_string += f"{user_id:<20} {emoji:<6} {timestamp}\n"
    
    return formatted_string
