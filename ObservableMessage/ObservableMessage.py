import asyncio
import discord
from abc import ABC, abstractmethod
class ObservableMessage(ABC):
    @abstractmethod
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        pass

    @abstractmethod
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.User):
        pass
