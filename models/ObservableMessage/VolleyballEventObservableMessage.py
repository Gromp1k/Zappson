import asyncio
import discord
from datetime import datetime
from EventData.VolleyballEventData import VolleyballEventData
from constants import TIME_FORMAT
import VolleballEventUtils
from VolleballEventUtils import timezone
from settings import *
import os

class VolleyballEventObservableMessage:
    def __init__(self, 
                 bot: discord.Client, 
                 interaction: discord.Interaction,
                 event_data: VolleyballEventData):
        self.bot: discord.Client = bot
        self.interaction: discord.Interaction = interaction
        self.participants: list[tuple[int, str, str]] = []
        self.invite_message: discord.Message = None
        self.log_file_path: str = None
        self.event_data = event_data

    async def start(self):
        event_date: datetime
        deadline_date: datetime
        include_leader: bool
        send_log: bool 
        event_date, deadline_date, include_leader, send_log = self.event_data.getData()
        self.log_file_path = f"{str(event_date)}" # TODO: make somethin unique.  
        if include_leader:
            self.participants.append((LEADER_ID, VOLLEYBALL_EMOJI, None))

        channel = self.interaction.channel
        try:
            self.invite_message = await channel.send(
                content=f"<@&{NOTIFY_ROLE_ID}> Zapisy na siatkówkę {event_date.strftime(TIME_FORMAT)}:\n"
                        f"Przypomnienie: zliczane są wyłącznie reakcje: {VOLLEYBALL_EMOJI} oraz {PLUS_1_EMOJI}\n"
                        f"Zapisy trwają do {deadline_date.strftime(TIME_FORMAT)}\n"
                        f"**Kto pierwszy, ten lepszy. Liczba miejsc ograniczona do {PARTICIPANTS_LIMIT}**"
            )
            await self.invite_message.add_reaction(VOLLEYBALL_EMOJI)
            await self.invite_message.add_reaction(PLUS_1_REACTION)
        except Exception as e:
            print(f"Error sending invite message: {e}")
            await self.interaction.followup.send("Failed to send invite message.", ephemeral=True)
            return

        while datetime.now(timezone) < deadline_date:
            sleep_time = (deadline_date - datetime.now(timezone)).total_seconds() / 2
            await asyncio.sleep(max(sleep_time, 1))

        message_core_participants, message_substitutes = VolleballEventUtils.create_summary_message_content(self.bot, self.participants, event_date)
        await channel.send(message_core_participants)
        if message_substitutes:
            await channel.send(message_substitutes)
        await channel.send(MESSAGE_REMINDER_NOTE)

        old_content = self.invite_message.content
        new_content = f"**Zapisy zostały zakończone o {deadline_date.strftime(TIME_FORMAT)}**\n~~{old_content}~~"
        await self.invite_message.edit(content=new_content)

        if send_log:
            print(f"\'self.log_file_path\'")
            await self.send_log_file(self.interaction, self.invite_message, self.log_file_path)

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
            # Present the ResignrationEventMessageView first, on it's callback or desttuctor* activate self.handle_remove_record(user, reaction.emoji)
            await self.bot.handle_remove_record(user, str(reaction))
            #await self.__sendResignationMessage(user, reaction)
            #self.handle_remove_record(user, reaction.emoji)

        if reaction.count < 1:
            await reaction.message.add_reaction(reaction.emoji)

    def handle_add_record(self, user: discord.User, emoji: str):
        timestamp = datetime.now(timezone).strftime('%x %X')
        if not any(record[0] == user.id and record[1] == str(emoji) for record in self.participants):
            self.participants.append((user.id, str(emoji), timestamp))
            self.log("add", user, emoji)
        else:
            print(f"Undefined behaviour: attempt to add duplicate record: {user.id} {str(emoji)} {timestamp}")

    def handle_remove_record(self, user: discord.User, emoji: str):
        target_record = (user.id, str(emoji))
        for record in self.participants:
            if (record[0], record[1]) == target_record:
                self.participants.remove(record)
                self.log("remove", user, emoji)
                break
        
    def log(self, action: str, user: discord.User, emoji: str):
        action_word = "Dodano" if action == "add" else "Usunięto"
        emoji_text = emoji if emoji == VOLLEYBALL_EMOJI else '+1'
        log_message = f"{action_word} pozycję: {user.name} {user.id} {emoji_text}\n"
        formatted_participants = VolleballEventUtils.format_participants(self.participants)
        with open(self.log_file_path, 'a') as f:
            f.write(log_message + "\n")
            f.write(formatted_participants + "\n")
        logging.info(log_message)
        logging.info(VolleballEventUtils.format_participants(self.participants))

    async def send_log_file(self, interaction: discord.Interaction, invite_message: discord.Message, log_file_path: str):
        if not os.path.isfile(log_file_path):
            await interaction.channel.send("Error: Log file could not be created.")
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
            await interaction.channel.send(f"{interaction.user.mention}, Byczku, bo nie mogłem ci raportu wysłać z zapisów, weź sprawdź swoje ustawienia!")

    async def cleanup(self):
        if self.invite_message is not None:
            try:
                await self.invite_message.delete()
            except discord.HTTPException as e:
                print(f"Failed to delete the invite message due to an error: {e}")
        else:
            print("invite_message is None, nothing to delete")


    async def __sendResignationMessage(self, user: discord.User, reaction: discord.Reaction):
        if not isinstance(self.invite_message.channel, discord.channel.TextChannel):
            return
        print("about to sessage_handler.send_custom_message")
        message_handler = CustomMessageHandler(self, user, reaction)
        await message_handler.send_custom_message()


from discord.ui import Button, View
class CustomMessageHandler:
    def __init__(self, observedMessage: VolleyballEventObservableMessage, user: discord.User, reaction: discord.Reaction):
        self.observedMessage = observedMessage
        self.user = user
        self.reaction = reaction

    async def send_custom_message(self, ):
        embed = discord.Embed(
            title="Uwaga!",
            description="some text botton",
            color=discord.Color.red()
        )
        view = ResignrationEventMessageView(self)
        print(f"about to send view {self.observedMessage}")
        channel = await self.user.create_dm()
        await channel.send(embed=embed, view=view, delete_after=30)
        #await observedMessage.interaction.channel.send()
        #await observedMessage.interaction.followup(content="Test content", embed=embed, view=view)

class ResignrationEventMessageView(View):
    def __init__(self, handler: CustomMessageHandler):
        super().__init__()
        self.handler = handler
        self.add_item(self.ResignButton(handler))

    class ResignButton(Button):
        def __init__(self, handler: CustomMessageHandler):
            super().__init__(label="Delete", style=discord.ButtonStyle.danger)
            self.observedMessage = handler.observedMessage
            self.user = handler.user
            self.reaction = handler.reaction

        async def callback(self, interaction: discord.Interaction):
            if self.observedMessage.invite_message is not None:
                print(f"Callback from {self} for ObservableMessage {self.observedMessage} -> remove")
                self.observedMessage.handle_remove_record(self.user, str(self.reaction))
            #pass