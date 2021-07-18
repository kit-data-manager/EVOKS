from abc import ABC, abstractmethod

class Triple(ABC):
    """
    Interface Triple, that classes Term and Vocabulary can use some functions with inheritance.
    """
    @abstractmethod
    def edit_field(self, url : str, type : str, content : str) -> None:
        pass

    @abstractmethod
    def create_field(self, url : str, type : str, content : str) -> str:
        pass

    @abstractmethod
    def delete_field(self, url : str) -> None:
        pass
