from abc import ABC, abstractmethod

class Triple(ABC):

    @abstractmethod
    def edit_field(self, url : str, type : str, content : str):
        pass

    @abstractmethod
    def create_field(self, url : str, type : str, content : str):
        pass

    @abstractmethod
    def delete_field(self, url : str):
        pass
