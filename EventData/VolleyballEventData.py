from datetime import datetime
from EventData.EventData import EventData

class VolleyballEventData(EventData):
    def __init__(self, event_date: datetime, deadline_date: datetime, include_leader: bool, send_log: bool):
        self.event_date: datetime = event_date
        self.deadline_date: datetime = deadline_date
        self.include_leader: bool = include_leader
        self.send_log: bool = send_log

    def getData(self) -> tuple:
        return (self.event_date, self.deadline_date, self.include_leader, self.send_log)   