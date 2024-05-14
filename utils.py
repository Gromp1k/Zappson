from datetime import datetime, timedelta
import pytz
import os
import shlex
from dateutil.parser import parse
from discord.ext import commands
from config import DEDICATED_CHANNEL_IDS, PERMITTED_ROLE_IDS, PARTICIPANTS_LIMIT

timezone = pytz.timezone('Europe/Warsaw')

def canUseCommand(ctx: commands.Context) -> bool:
    # Check if the command is used in the dedicated channel
    if ctx.channel.id not in DEDICATED_CHANNEL_IDS:
        return False

    # Check if the user has any of the permitted roles
    user_role_ids = {role.id for role in ctx.author.roles}
    if any(role_id in user_role_ids for role_id in PERMITTED_ROLE_IDS):
        return True

    return False

def parse_command_args(args: str):
    print("def parse_command_args(args: str):")
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
                raise StopIteration(f"Invalid flag given: {arg}")
    except StopIteration:
        print("Error: Argument for a flag is missing.")
        return
    
    # Ensure timezone is defined for date manipulation
    timezone = pytz.timezone('Europe/Warsaw')

    # Parse date argument
    if event_date_str:
        parts = event_date_str.split()
        try:
            date_str = f"{parts[0]}/{current_year}"
            parts.pop(0)
            #print("event_date_str parts:", parts, " date_str: ", date_str)
            if len(parts) == 0:
                # DD/MM format
                event_date = datetime.strptime(date_str, "%d/%m/%Y")
            elif len(parts) == 1 and ':' not in parts[0]:
                # DD/MM HH format
                event_date = datetime.strptime(f"{date_str} {parts[0]}", "%d/%m/%Y %H")
            elif len(parts) == 1:
                # DD/MM HH:MM format
                event_date = datetime.strptime(f"{date_str} {parts[0]}", "%d/%m/%Y %H:%M")
            else:
                # DD/MM HH:MM:SS format
                event_date = datetime.strptime(event_date_str, "%d/%m %H:%M:%S/%Y")
        except ValueError:
            raise ValueError("Invalid event date format.")
    else:
        raise ValueError("The -date parameter is mandatory.")

    # Localize event date to the specified timezone
    event_date = timezone.localize(event_date)

    # Parse deadline argument
    if deadline_str:
        parts = deadline_str.split()
        try:
            date_str = f"{parts[0]}/{current_year}"
            parts.pop(0)
            #print("deadline_str parts:", parts, " date_str: ", date_str)
            if len(parts) == 0:
                # DD/MM format
                deadline_date = datetime.strptime(date_str, "%d/%m/%Y")
            elif len(parts) == 1 and ':' not in parts[0]:
                # DD/MM HH format
                deadline_date = datetime.strptime(f"{date_str} {parts[0]}", "%d/%m/%Y %H")
            elif len(parts) == 1:
                # DD/MM HH:MM format
                deadline_date = datetime.strptime(f"{date_str} {parts[0]}", "%d/%m/%Y %H:%M")
            else:
                # DD/MM HH:MM:SS format
                deadline_date = datetime.strptime(deadline_str, "%d/%m %H:%M:%S/%Y")
        except ValueError:
            raise ValueError("Invalid deadline format.")
    else:
        # Default deadline is 9 hours before the event date if no deadline provided
        deadline_date = event_date - timedelta(hours=9)

    # Localize deadline date to the specified timezone
    deadline_date = timezone.localize(deadline_date)

    # Check if the event_date is greater than or equal to the deadline_date
    if event_date <= deadline_date:
        raise ValueError("Event date must be later than the deadline date.")

    # Parse optional leader flag if given or take default value
    if include_leader:
        include_leader = include_leader in [True, '1']

    # Parse optional sendlog flag if given or take default value
    if send_log:
        print("-sendlog in args_dict: ", send_log )
        send_log = send_log in [True, '1']

    print(f"Parsed params:\nevent_date {event_date}\ndeadline_date {deadline_date}\ninclude_leader {include_leader}\nsend_log {send_log}\n")
    return event_date, deadline_date, include_leader, send_log


def create_summary_message_content(bot, participants: list, event_date) :
    if not participants:
        return "Nikt się nie zapisał... Lamusy", ""
    
    # Start the summary message
    message_core_participants = f"\n\n**Wyniki zapisów na siatkówkę w dniu {event_date}:**\n\n"
    
    i = 1
    range = min(len(participants),PARTICIPANTS_LIMIT)
    # Get first 21 participants as a game core
    for user_id, emoji, timestamp in participants[:range]:
        user = bot.get_user(user_id)  # Retrieve the user object from the user ID
        if user:
            user_mention = user.mention  # Get the mention string for the user
        else:
            user_mention = f"User ID {user_id}"  # Fallback if the user object isn't found
        
        # Add the user mention, emoji, and timestamp to the message
        message_core_participants += f"**{i}** {user_mention} {emoji} o __{timestamp}__\n"
        i += 1

    i = 1
    message_substitutes = ""
    # If total participants count is greater that PARTICIPANTS_LIMIT, treat rest of the buffer as substitutes.
    if len(participants) > PARTICIPANTS_LIMIT:
         message_substitutes += "\n\n\n**Rezerwowi:**\n\n"
         for user_id, emoji, timestamp in participants[PARTICIPANTS_LIMIT:]:
            user = bot.get_user(user_id)  # Retrieve the user object from the user ID
            if user:
                user_mention = user.mention  # Get the mention string for the user
            else:
                user_mention = f"User ID {user_id}"  # Fallback if the user object isn't found
                # Add the user mention, emoji, and timestamp to the message
            message_substitutes += f"*{i}* {user_mention} {emoji} o __{timestamp}__\n"
            i += 1

    return message_core_participants, message_substitutes


def create_log_file(event_date, deadline, include_leader):
    log_directory = './log/'
    os.makedirs(log_directory, exist_ok=True)  # Ensure the directory exists
    log_file_name = f"log_{event_date.strftime('%Y-%m-%d')}.txt"
    log_file_path = os.path.join(log_directory, log_file_name)

    # Create or open the log file
    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Log {datetime.now(timezone).isoformat()}\n")
        log_file.write(f"Data spotkania: {event_date.strftime('%d/%m/%Y %H:%M:%S')}\n")
        log_file.write(f"Deadline głosowania: {deadline.strftime('%d/%m/%Y %H:%M:%S')}\n")
        log_file.write(f"Uwzględniono Kasię: {'Tak' if include_leader else 'Nie'}\n")
    
    print(f'create_log_file : {log_file_path}')
    return log_file_path

def parse_env_list(env_var: str) -> list[int]:
    raw_list = os.getenv(env_var, "").strip('[] ').replace(' ', '')
    return [int(x) for x in raw_list.split(',')] if raw_list else []

def format_participants(list_name, participants):
    # Header for the formatted string
    formatted_string = f"List of {list_name}:\n"
    formatted_string += f"{'User ID':<20} {'Emoji':<6} {'Timestamp'}\n"
    formatted_string += "-" * 50 + "\n"
    
    # Formatting each participant entry
    for user_id, emoji, timestamp in participants:
        formatted_string += f"{user_id:<20} {emoji:<6} {timestamp}\n"
    
    return formatted_string