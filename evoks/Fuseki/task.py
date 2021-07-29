import datetime
from typing import Optional


class Task:
    """
    Class that contains the information about a Fuseki task 
    """

    def __init__(self, type: str, id: str, started: datetime.date, finished: Optional[datetime.date], success: Optional[bool]) -> None:
        """
        Creates a task object
        Args:
            type (str): task type, assigned by Fuseki
            id (str): unique id of task
            started (datetime.date): Date when task got started
            finished (Optional[datetime.date]): Optional value. None if task is not finished yet
            success (Optional[bool]): Optional value. None if task is not finished yet
        """
        self.type = type
        self.id = id
        self.started = started
        self.finished = finished
        self.success = success
