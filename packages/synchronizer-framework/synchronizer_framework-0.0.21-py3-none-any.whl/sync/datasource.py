from abc import abstractmethod, ABC
from typing import List, Type

from deprecation import deprecated


class DataSource(ABC):
    @abstractmethod
    def entity_types(self) -> List[type]:
        pass

    @abstractmethod
    def create(self, entity) -> bool:
        pass

    @abstractmethod
    def find(self, by_type, by_conditions=dict()) -> List:
        pass

    @abstractmethod
    def delete(self, entity) -> bool:
        pass

    @abstractmethod
    @deprecated(details="Use find instead", deprecated_in="0.0.20")
    def all(self, of_type, limit=None) -> List:
        pass

    @abstractmethod
    def refresh(self, entity):
        pass

    @abstractmethod
    def preload_type(self, preload_type: Type, path: List[str]) -> bool:
        pass

    @abstractmethod
    def persist(self, entity):
        pass

    @abstractmethod
    def id(self, entity):
        pass

    @abstractmethod
    def get(self, type, id):
        pass
