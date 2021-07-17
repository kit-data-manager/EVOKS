from .task import Task
import os


class Copy:
    """
    Class that contains the information about a backup copy
    """

    def __init__(self, task: Task, path: str) -> None:
        """
            Creates a copy object
        Args:
            task (task.Task): task that created this backup copy
            path (str): path where the backup copy can be found
        """

        self.task = task
        self.path = path

    def delete(self) -> None:
        """
        Deletes the backup copy at copy.path

        Raises:
            ValueError: backup copy does not exist
        """
        if os.path.exists(self.path):
            os.remove(self.path)
        else:
            raise ValueError('The backup copy does not exist!')
