from abc import ABC, abstractmethod
from typing import Type

from sync.datasource import DataSource


class Timestamped:
    def updated_at(self):
        pass

    def update_timestamp(self, timestamp):
        pass


class LinkProvider(ABC):
    @abstractmethod
    def link(self, entity, other, entity_ds: DataSource, other_ds: DataSource):
        pass

    @abstractmethod
    def others(
        self, entity, entity_ds: DataSource, other_type: Type, other_ds: DataSource
    ):
        pass

    @abstractmethod
    def unlink(self, entity, entity_ds: DataSource, other_ds: DataSource):
        pass
