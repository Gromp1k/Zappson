import asyncio
import discord
from datetime import datetime
from utils import can_use_command, parse_command_args, create_log_file, create_summary_message_content, format_participants, timezone
from config import *
from ObservableMessage.ObservableMessage import ObservableMessage
import os

class VolleyballEventObservableMessage(ObservableMessage):
    def __init__(self, bot, interaction, args):
        self.bot = bot
        self.interaction = interaction
        self.args = args
        self.participants = []
        self.invite_message = None
        self.log_file_path = None
        self.event_date = None
        self.deadline_date = None
        self.include_leader = None
        self.send_log = None

    async def start(self):
        try:
            await self.interaction.response.defer()
        except discord.HTTPException as e:
            print(f"Failed to defer the interaction response due to an error: {e}")
            return

        print(f"Command input received: {self.args}")

        if not can_use_command(self.interaction):
            print(f"{self.interaction.user} does not have permission to use this command.")
            await self.interaction.followup.send(f"{self.interaction.user.mention}, you do not have permission to use this command.", ephemeral=True)
            return

        try:
            self.event_date, self.deadline_date, self.include_leader, self.send_log = parse_command_args(self.args)
            self.log_file_path = create_log_file(self.event_date, self.deadline_date, self.include_leader)
        except ValueError as parsing_error:
            print(str(parsing_error))
            await self.interaction.followup.send(f"Error parsing command arguments: {parsing_error}", ephemeral=True)
            return

        if self.include_leader:
            self.participants.append((LEADER_ID, VOLLEYBALL_EMOJI, None))

        self.invite_message = await self.interaction.followup.send(
            content=f"<@&{NOTIFY_ROLE_ID}> Zapisy na siatkówkę {self.event_date}:\n"
                    f"Przypomnienie: zliczane są wyłącznie reakcje: {VOLLEYBALL_EMOJI} oraz {PLUS_1_EMOJI}\n"
                    f"Zapisy trwają do {self.deadline_date.strftime('%x %X')}\n"
                    f"**Kto pierwszy, ten lepszy. Liczba miejsc ograniczona do {PARTICIPANTS_LIMIT}**"
        )
        await self.invite_message.add_reaction(VOLLEYBALL_EMOJI)
        await self.invite_message.add_reaction(PLUS_1_REACTION)

        while datetime.now(timezone) < self.deadline_date:
            sleep_time = (self.deadline_date - datetime.now(timezone)).total_seconds() / 2
            await asyncio.sleep(max(sleep_time, 1))

        message_core_participants, message_substitutes = create_summary_message_content(self.bot, self.participants, self.event_date)
        await self.interaction.followup.send(message_core_participants)
        if message_substitutes:
            await self.interaction.followup.send(message_substitutes)
        await self.interaction.followup.send(MESSAGE_REMINDER_NOTE)

        if self.send_log:
            await self.send_log_file(self.interaction, self.invite_message, self.log_file_path)

        old_content = self.invite_message.content
        new_content = f"**Zapisy zostały zakończone o {self.deadline_date.strftime('%x %X')}**\n~~{old_content}~~"
        await self.invite_message.edit(content=new_content)

        self.invite_message = None
        self.participants.clear()

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user == self.bot.user:
            return

        if self.invite_message is None or reaction.message.id != self.invite_message.id:
            return

        if (isinstance(reaction.emoji, discord.Emoji) and reaction.emoji.id == PLUS_1_REACTION_ID) or (reaction.emoji == VOLLEYBALL_EMOJI):
            self.handle_add_record(user, reaction.emoji)

        if reaction.count > 1 and self.bot.user in [u async for u in reaction.users()]:
            await reaction.message.remove_reaction(reaction.emoji, self.bot.user)

    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.User):
        if user == self.bot.user or self.invite_message is None or reaction.message.id != self.invite_message.id:
            return

        if (isinstance(reaction.emoji, discord.Emoji) and reaction.emoji.id == PLUS_1_REACTION_ID) or (reaction.emoji == VOLLEYBALL_EMOJI):
            self.handle_remove_record(user, reaction.emoji)

        if reaction.count < 1:
            await reaction.message.add_reaction(reaction.emoji)

    def handle_add_record(self, user, emoji):
        timestamp = datetime.now(timezone).strftime('%x %X')
        if not any(record[0] == user.id and record[1] == str(emoji) for record in self.participants):
            self.participants.append((user.id, str(emoji), timestamp))
            self.log("add", user, emoji)
        else:
            print(f"Undefined behaviour: attempt to add duplicate record: {user.id} {str(emoji)} {timestamp}")

    def handle_remove_record(self, user, emoji):
        target_record = (user.id, str(emoji))
        for record in self.participants:
            if (record[0], record[1]) == target_record:
                self.participants.remove(record)
                self.log("remove", user, emoji)
                break

    def log(self, action, user, emoji):
        action_word = "Dodano" if action == "add" else "Usunięto"
        emoji_text = emoji if emoji == VOLLEYBALL_EMOJI else '+1'
        log_message = f"{action_word} pozycję: {user.name} {user.id} {emoji_text}\n"
        formatted_participants = format_participants("Participants", self.participants)
        with open(self.log_file_path, 'a') as f:
            f.write(log_message + "\n")
            f.write(formatted_participants + "\n")

    async def send_log_file(self, interaction, invite_message, log_file_path):
        if not os.path.isfile(log_file_path):
            await interaction.followup.send("Error: Log file could not be created.", ephemeral=True)
            return

        file_to_send = discord.File(log_file_path, filename=os.path.basename(log_file_path))
        embed = discord.Embed(
            title="Siatkówka",
            description="Siemano, to log z ostatniego zapisu na siatkówkę, poniżej znajdziesz link do konkretnej wiadomości na kanale",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Data", value=invite_message.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
        embed.add_field(name="Link", value=f"[Jump to Message]({invite_message.jump_url})", inline=False)
        embed.set_footer(text="Pozdrawiam cieplutko, Żappson")

        if interaction.user.avatar:
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)

        try:
            await interaction.user.send(embed=embed, file=file_to_send)
        except discord.Forbidden:
            await interaction.followup.send(f"{interaction.user.mention}, Byczku, bo nie mogłem ci raportu wysłać z zapisów, weź sprawdź swoje ustawienia!", ephemeral=True)

    async def cleanup(self):
        if self.invite_message is not None:
            try:
                await self.invite_message.delete()
            except discord.HTTPException as e:
                print(f"Failed to delete the invite message due to an error: {e}")
        else:
            print("invite_message is None, nothing to delete")
