import logging
from typing import List, Type

from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, joinedload

from sync.datasource import DataSource

Session = sessionmaker(expire_on_commit=False)


class JoinedLoads:
    def __init__(self):
        self.joinedloads = dict()

    def add(self, type, jl):
        if not type in self.joinedloads:
            self.joinedloads[type] = set()
        self.joinedloads[type].add(jl)

    def get(self, type):
        return self.joinedloads[type] if type in self.joinedloads else set()


class SQADataSource(DataSource):
    def __init__(
        self,
        url="sqlite+pysqlite:///testdb.sqlite",
        base: Type = declarative_base(),
        create_metadata=True,
    ):
        self.url = url
        self.base = base
        self.engine = create_engine(url, echo=False)
        Session.configure(bind=self.engine)
        if create_metadata:
            base.metadata.create_all(self.engine)
        self.session: Session = Session()
        self.joinedloads = JoinedLoads()

    def create(self, entity: object) -> bool:
        return self.persist(entity)

    def find(self, by_type: Type, by_conditions = dict()) -> List[object]:
        query = self.session.query(by_type)

        for k, v in by_conditions.items():
            query = query.filter(getattr(by_type, k) == v)

        for joinedload in self.joinedloads.get(by_type):
            if joinedload == None:
                continue
            query = query.options(joinedload)

        return query.populate_existing().all()

    def delete(self, entity) -> bool:
        self.session.delete(entity)
        try:
            self.session.commit()
            return True
        except exc.SQLAlchemyError as err:
            logging.exception(msg="Cannot delete", exc_info=err)
            self.session.rollback()
            return False

    def all(self, of_type, limit=None) -> set:
        return self.session.query(of_type).populate_existing().limit(limit).all()

    def refresh(self, entity) -> object:
        if entity:
            logging.debug(f"Refreshing {entity} on session: {self.session}")
            self.session.refresh(entity)
        return entity

    def preload_type(self, preload_type, path) -> bool:
        jl = None
        current_type = preload_type
        for prop in path:
            if SQADataSource._is_relationship(current_type, prop):
                rel = getattr(current_type, prop)
                if not jl:
                    jl = joinedload(rel)
                else:
                    jl = jl.joinedload(rel)
                current_type = SQADataSource._resolve_remote_class(current_type, prop)
            else:
                break
        self.joinedloads.add(preload_type, jl)

    def entity_types(self) -> List[type]:
        return self.base.__subclasses__()

    def persist(self, entity) -> object:
        logging.debug(f"Persisting {entity}")
        self.session.add(entity)
        try:
            self.session.commit()
            return True
        except exc.SQLAlchemyError as err:
            logging.exception(msg="Cannot persist", exc_info=err)
            self.session.rollback()
            return None

    @staticmethod
    def _resolve_remote_class(type_, attribute):
        return type_.__mapper__.relationships.get(attribute).entity.class_

    @staticmethod
    def _is_relationship(type_, attribute):
        return attribute in type_.__mapper__.relationships

    def id(self, entity):
        return entity.id

    def get(self, type, id):
        return self.session.query(type).get(id)

    def __repr__(self):
        return f"SQADataSource(base={self.base}, url={self.url})"
