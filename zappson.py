# Config load
import asyncio
import discord
from utils import *
from config import *

# Initialize global variables
participants = []  # List to store participant data ((user.id, str(emoji), timestamp))
invite_message = None
"""
    start command creates new invite_message and for given period of time listens for its reaction related actions such as adding and removing reactions.

    syntax of the command: 
        --start -date <date_format...> -deadline <date_format...> -leader <false|true or 0|1> -sendlog <false|true or 0|1>

    [Mandatory]
    * Flag '-date' describes date of the event. [Mandatory]

    [Optional]
    * Flag '-deadline' describes deadline for invite_message's listening by bot.
      By default value of flag is included and its value is set to 9 hours before the event date 

    [Optional]
    * Flag '-leader' based on it's value includes or not the leader user in participants buffer at its first position.
        By default the flag is included and its value is set to true. 

    [Optional]
    * Flag '-leader' based on it's value makes bot send or not a message with report after reaching a task deadline to command invoker.
        By default the flag is included and its value is set to true. 
        
    * Valid date_format:
    <DD/MM HH:MM:SS>
    <DD/MM HH:MM>
    <DD/MM HH>
    <DD/MM> 
"""
@bot.command(name="start", help="call gromp1k")
async def start(ctx, *, arg):
    print("== start command==\n\n")
    global event_date, deadline_date, include_leader, send_log, log_file_path, invite_message
    # Attempt to delete the invoking command message
    try:
        if "--start" in ctx.message.content:
            print("invoking message detected")
            await ctx.message.delete()
    except discord.Forbidden:
        #Bot does not have the proper permissions
        print("I do not have permission to delete messages in this channel.")
        return
    except discord.HTTPException as e:
        #Deleting the message fails for other reasons
       print(f"Failed to delete the message due to an error: {e}")
       return
    
    # invite_message is still active, do not process further.
    if invite_message is not None:
        print(f"another invite message seems to be active: {invite_message}")
        return

    #print("invite_message", type(invite_message))
    print(f"Command input received: {arg}")

    if not canUseCommand(ctx):
        print(f"{ctx.author} do not have permission to use this command.")
        return

    # Command parse
    try:
        event_date, deadline_date, include_leader, send_log  = parse_command_args(arg)
        log_file_path = create_log_file(event_date, deadline_date, include_leader)
    except ValueError as parsing_error:
        print(str(parsing_error))
        return
    except StopIteration as iteration_error:
        print(str(iteration_error))
        return

    # Append the leader
    if include_leader is True:
        participants.append((LEADER_ID, VOLLEYBALL_EMOJI, None))
        print("added leader?", participants)

    if deadline_date is None or include_leader is None:
        print(f"Fatal error, input None values:\ndate {event_date}\ndeadline {deadline_date}\ninclude_leader {include_leader}")
        return

    # Send invitation message and add reaction emojis
    invite_message = await ctx.send(f"<@&{NOTIFY_ROLE_ID}> Zapisy na siatkówkę {event_date}:\n"+
                                    f"Przypomnienie: zliczane są wyłącznie reakcje: {VOLLEYBALL_EMOJI} oraz {PLUS_1_EMOJI}\n"+
                                    f"Zapisy trwają do {deadline_date.strftime('%x %X')}\n"+
                                    f"**Kto pierwszy, ten lepszy. Liczba miejsc ograniczona do {PARTICIPANTS_LIMIT}**")
    await invite_message.add_reaction(VOLLEYBALL_EMOJI)
    await invite_message.add_reaction(PLUS_1_REACTION)

    print("send invite_message", type(invite_message), '\n', invite_message.id)

    # Freeze till deadline's reached
    while True:
        current_time = datetime.now(timezone)
        print("current_time", current_time)  #Debug only
        if current_time >= deadline_date:
            print("Deadline has been reached.")
            break

        sleep_time = (deadline_date - current_time).total_seconds() / 2
        if sleep_time > 1 :
            print(f'Going to sleep for seconds: {sleep_time}')
        await asyncio.sleep(sleep_time)


    #Send messages to channel
    message_core_participants, message_substitutes  = create_summary_message_content(
        bot=bot, 
        participants=participants,
        event_date=event_date)
    
    await ctx.send("\n\n\n" + message_core_participants)

    if message_substitutes :
        await ctx.send("\n\n\n" + message_substitutes)
    
    await ctx.send("\n\n\n" + MESSAGE_REMINDER_NOTE)

    if send_log:
        await send_log_file(ctx, invite_message, log_file_path)
        print("send summary_message", '\n')

    #Mark inviting_message content as deprecated.
    old_content = invite_message.content
    new_content = f"**Zapisy zostały zakończone o {deadline_date.strftime('%x %X')}**\n~~{old_content}~~"
    await invite_message.edit(content=new_content)
    print("deprecated invite_message context", type(invite_message), '\n', invite_message)

    # Reset values
    invite_message = None
    participants.clear()
    print("reset:\n", type(invite_message), '\n', invite_message)
    print("\n", participants,  type(participants), '\n')


# Event handler for reaction addition
@bot.event
async def on_reaction_add(reaction, user):
    global invite_message
    # Skip bot's own reactions
    if user == bot.user:
        return

    # End if invite_message is no longer 'active'
    if invite_message is None:
        return

    # Ignore messages other that an invite message
    if reaction.message.id != invite_message.id:
        return
    
    # Handle custom server emoji and standard emoji
    if (isinstance(reaction.emoji, discord.Emoji) and reaction.emoji.id == PLUS_1_REACTION_ID) or (reaction.emoji == VOLLEYBALL_EMOJI):
        emoji_type = "plus1" if isinstance(reaction.emoji, discord.Emoji) else "volleyball"
        print(f"{user.id} {user.name} on_reaction_add -> {emoji_type}")
        handle_add_record(user, reaction.emoji)

    # Unmatching emote, ignore
    else:
        return          

    # If at least one player has reacted remove bot's reaction placeholder
    if reaction.count > 1 and bot.user in [user async for user in reaction.users()]: 
        await reaction.message.remove_reaction(reaction.emoji, bot.user)

    
# Function adds new record to one of available buffers - participants or substitiutes
def handle_add_record(user, emoji):
    global participants
    timestamp = datetime.now(timezone).strftime('%x %X')

    # Check if any record matches the user ID and emoji
    matches_record = any(record[0] == user.id and record[1] == str(emoji) for record in participants)

    # If no matching record is found, append the new record
    if not matches_record:
        participants.append((user.id, str(emoji), timestamp))
    else:
        # Should not happen - matching record found, remain first attempt unchanged
        print(f"Undefined behaviour: attempt to add record: {user.id} {str(emoji)} {timestamp}\nWhen another record already matches{matches_record}\n")

    # Write data to log file
    log("add", user, emoji)

# Event handler for reaction removal
@bot.event
async def on_reaction_remove(reaction, user):
    global invite_message
    # Skip bot's own reactions
    if user == bot.user:
        #print(f"bot is the user")
        return

    # Check if the reaction is on the current invite_message
    if invite_message is None:
        print(f"inviting message doesnt exist")
        return
    
    # Ignore if is not related to invite_message
    if reaction.message.id != invite_message.id:
        return
    
    # Handle custom server emoji and standard emoji
    if (isinstance(reaction.emoji, discord.Emoji) and reaction.emoji.id == PLUS_1_REACTION_ID) or (reaction.emoji == VOLLEYBALL_EMOJI):
        emoji_type = "plus1" if isinstance(reaction.emoji, discord.Emoji) else "volleyball"
        print(f"{user.id} {user.name} on_reaction_remove -> {emoji_type}")
        hadle_remove_record(user, reaction.emoji)

    # Unsupported emoji, do not process.
    else:
        return 

    # Check if the bot's reaction is the only one left and if so, add it back as a placeholder
    if reaction.count < 1:
        await reaction.message.add_reaction(reaction.emoji)


# Function to remove participant data from the buffer
def hadle_remove_record(user, emoji):
    global participants
    # Filter out the user and emoji combination
    target_record = (user.id, str(emoji))
    # First, try to find and remove the record in participants
    for record in participants:
        if (record[0], record[1]) == target_record:
            participants.remove(record)
            print("remove_from_participants", target_record)
            break
    log("remove", user, emoji)       


# Adjust the function signature to accept log_file_path
def log(action, user, emoji):
    global participants
    action_word = "Dodano" if action == "add" else "Usunięto"
    emoji_text = emoji if emoji == VOLLEYBALL_EMOJI else '+1'
    log_message = f"{action_word} pozycję: {user.name} {user.id} {emoji_text}\n"
    print(log_message)
    log_participants = format_participants("Participants",participants)
    print(log_participants)
    with open(log_file_path, 'a') as f:
        f.write(log_message + "\n")
        f.write(log_participants + "\n")


# Function to send the log file to the user who initiated the invitation session
async def send_log_file(ctx, invite_message, log_file_path):
    # Ensure the directory exists
    if not os.path.isfile(log_file_path):
        await ctx.send("Error: Log file could not be created.")
        return

    # Create a discord.File object for the log file
    file_to_send = discord.File(log_file_path, filename=os.path.basename(log_file_path))

    # Prepare the embed message
    embed = discord.Embed(
        title="Siatkówka",
        description="Siemano, to log z ostatniego zapisu na siatkówkę, poniżej znajdziesz link do konkretnej wiadomości na kanale",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Data", value=invite_message.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
    embed.add_field(name="Link", value=f"[Jump to Message]({invite_message.jump_url})", inline=False)
    embed.set_footer(text="Pozdrawiam cieplutko, Żappson")
    
    if ctx.me.avatar:
        embed.set_author(name=ctx.me.display_name, icon_url=ctx.me.avatar.url)
    
    try:
        await ctx.author.send(embed=embed, file=file_to_send)
    except discord.Forbidden:
        await ctx.send(f"{ctx.author.mention}, Byczku, bo nie mogłem ci raportu wysłać z zapisów, weź sprawdź swoje ustawienia!")

# Main function to run the bot
def main():
    bot.run(TOKEN)


if __name__ == '__main__':
    main()