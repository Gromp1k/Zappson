import discord
from discord.ui import Button

from gui.SingleSelectView import SingleSelectView


class EventFormEmbed:
    def __init__(self):
        self.name = "New Event Template Form"
        self.description = "Please fill out the following form:"
        self.single_select_view = SingleSelectView(["no-limit", "limited"])

    def to_embed(self):
        embed = discord.Embed(title=self.name, description=self.description, color=discord.Color.blue())
        embed.add_field(name="Options", value="Select your options below:", inline=False)
        return embed

    def get_view(self):
        view = self.single_select_view
        view.add_item(ConfirmationButton(self))
        return view

class ConfirmationButton(Button):
    def __init__(self, form):
        super().__init__(label="Confirm", style=discord.ButtonStyle.green)
        self.form = form

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.form.single_select_view.children[0].values[0]
        await interaction.message.edit(content=f"Form submitted with option: {selected_option}", view=None)
