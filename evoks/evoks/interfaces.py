from abc import ABC, abstractmethod

# TODO: docs


class Triple(ABC):
    """
    Triple interface for all classes that are partially stored in Fuseki.
    """
    @abstractmethod
    def edit_field(self, url: str, type: str, content: str) -> None:
        pass

    @abstractmethod
    def create_field(self, url: str, type: str, content: str) -> str:
        pass

    @abstractmethod
    def delete_field(self, url: str) -> None:
        pass
