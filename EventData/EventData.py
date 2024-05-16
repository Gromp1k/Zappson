from abc import ABC, abstractmethod
class EventData(ABC):
    @abstractmethod
    def getData(self) -> tuple:
        pass