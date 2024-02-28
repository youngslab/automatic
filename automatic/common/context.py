


from abc import ABC, abstractmethod
from .descriptor import Descriptor

class Context(ABC):
    @abstractmethod
    def activate(self, desc:Descriptor):
        pass

    @abstractmethod
    def click(self, desc:Descriptor):
        pass

    @abstractmethod
    def type(self, desc:Descriptor, text:str):
        pass
