import discord
from discord.ui import View, Button

class CheckboxButton(Button):
    def __init__(self, label: str, checked: bool = False):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.checked = checked
        self.label_text = label
        self.update_label()

    def update_label(self):
        self.style = discord.ButtonStyle.green if self.checked else discord.ButtonStyle.secondary
        self.label = f"{'[x]' if self.checked else '[ ]'} {self.label_text}"

    async def callback(self, interaction: discord.Interaction):
        self.checked = not self.checked
        self.update_label()
        await interaction.message.edit(view=self.view)

class CheckboxView(View):
    def __init__(self, options: list):
        super().__init__()
        self.buttons = [CheckboxButton(label=option) for option in options]
        for button in self.buttons:
            self.add_item(button)

    def get_checked_options(self):
        return [button.label_text for button in self.buttons if button.checked]
