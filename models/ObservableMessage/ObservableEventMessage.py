from abc import abstractmethod
from typing import Iterator
import ObservableMessage
from enum import Enum

class ParticipantData:
    def __init__(self, user_id: int, emoji: str, timestamp: str):
        self.user_id = user_id
        self.emoji = emoji
        self.timestamp = timestamp

    def __iter__(self) -> Iterator[tuple[int, str, str]]:
        return iter((self.user_id, self.emoji, self.timestamp))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, ParticipantData):
            return NotImplemented
        return (self.user_id == other.user_id and 
                self.emoji == other.emoji and 
                self.timestamp == other.timestamp)
    
    def __hash__(self) -> int:
        return hash((self.user_id, self.emoji, self.timestamp))

class ObservableEventMessage(ObservableMessage):

    class ParticipantsOrder(Enum):
        FIFO = 'fifo'
        LIFO = 'lifo'
        RANDOM = 'random'



    def __init__(self, 
        participants_limit: int = None,
        participants_order: ParticipantsOrder = ParticipantsOrder.FIFO,
        participants: set[ParticipantData] = {}):
        self.__participants_limit = participants_limit
        self.__participants_order = participants_order
        self.__participants = participants

    @abstractmethod
    async def generate_report(self):
        pass

    # sets users participation limit
    def set_participants_limit(self, participants_limit: int = None):
        self.__participants_limit = participants_limit

    # sets type of order for participatns
    def set_participants_order(self, participants_order: ParticipantsOrder = ParticipantsOrder.FIFO):
        self.__participants_limit = participants_order

    # sets participants
    def set_participants(self, participants: set[ParticipantData] = {}):
        self.__participants = participants

    