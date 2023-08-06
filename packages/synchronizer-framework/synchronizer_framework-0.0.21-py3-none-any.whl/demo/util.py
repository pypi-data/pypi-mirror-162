from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import MANYTOONE

from sync.mixins import Timestamped


class Repr:
    def __repr__(self):
        columns = self.__table__.columns.values()
        column_key_value = [
            f"{column.name}={getattr(self, column.name)}"
            for column in columns
            if not column.name.endswith("_id")
        ]
        relationship_key_value = [
            f"{relationship[0]}={getattr(self, relationship[0])}"
            for relationship in self.__mapper__.relationships.items()
            if relationship[1].direction == MANYTOONE
        ]
        return f"{self.__class__.__name__}({', '.join([*column_key_value, *relationship_key_value])})"


class UpdatedAt(Timestamped):
    _updated_at = Column(DateTime, default=datetime.utcnow)

    def updated_at(self):
        if not self._updated_at or not self._updated_at.timestamp():
            return 0
        else:
            return self._updated_at.timestamp()

    def update_timestamp(self, timestamp):
        self._updated_at = datetime.utcfromtimestamp(timestamp)
