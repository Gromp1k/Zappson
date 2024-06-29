import discord
from discord.ui import View

class SingleSelect(discord.ui.Select):
    def __init__(self, options: list):
        select_options = [discord.SelectOption(label=option) for option in options]
        super().__init__(placeholder="Choose an option...", min_values=1, max_values=1, options=select_options)

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]
        await interaction.response.defer()
        await interaction.message.edit(content=f"Selected option: {selected_option}", view=self.view)

class SingleSelectView(View):
    def __init__(self, options: list):
        super().__init__()
        self.add_item(SingleSelect(options))
