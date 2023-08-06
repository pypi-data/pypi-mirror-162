from typing import Type

from redis.client import Redis

from sync.datasource import DataSource
from sync.mixins import LinkProvider


class RedisLinkProvider(LinkProvider):
    def __init__(self, purge=False, **redis_parameters):
        redis_parameters.update({"decode_responses": True, "encoding": "utf-8"})
        self.redis = Redis(**redis_parameters)
        if purge:
            self.redis.flushdb()

    @staticmethod
    def _generate_link_key(from_type: Type, from_entity_id, to_type: Type):
        return f"{from_type.__name__}:{from_entity_id}:{to_type.__name__}"

    @staticmethod
    def _generate_link_wildcard(from_type: Type, from_entity_id):
        return f"{from_type.__name__}:{from_entity_id}:*"

    @staticmethod
    def _generate_link_value(value_type: Type, value_id):
        return f"{value_type.__name__}:{value_id}"

    def link(self, entity, other, entity_ds: DataSource, other_ds: DataSource):
        self.link_unidirectional(entity, other, entity_ds, other_ds)
        self.link_unidirectional(other, entity, other_ds, entity_ds)
        return True

    def link_unidirectional(
        self, entity, other, entity_ds: DataSource, other_ds: DataSource
    ):
        link_key = RedisLinkProvider._generate_link_key(
            entity.__class__, entity_ds.id(entity), other.__class__
        )
        link_value = RedisLinkProvider._generate_link_value(
            other.__class__, other_ds.id(other)
        )
        self.redis.sadd(link_key, link_value)

    def others(
        self, entity, entity_ds: DataSource, other_type: Type, other_ds: DataSource
    ):
        link_key = RedisLinkProvider._generate_link_key(
            entity.__class__, entity_ds.id(entity), other_type
        )
        values = self.redis.smembers(link_key)
        result = []
        for member_key in values:
            other_type_from_value, value = member_key.split(":")
            if other_type_from_value == other_type.__name__:
                other = other_ds.get(other_type, value)
                result.append(other)

        return result

    def others_by_id(
        self, entity_class, entity_id, other_type: Type, other_ds: DataSource
    ):
        link_key = (
            f"{entity_class.__name__}:{entity_id}:{other_type.__name__}"
        )
        values = self.redis.smembers(link_key)
        result = []
        for member_key in values:
            other_type_from_value, value = member_key.split(":")
            if other_type_from_value == other_type.__name__:
                other = other_ds.get(other_type, value)
                result.append(other)

        return result

    def unlink(self, entity, entity_ds: DataSource, other_ds: DataSource):
        link_wildcard = RedisLinkProvider._generate_link_wildcard(
            entity.__class__, entity_ds.id(entity)
        )
        for key in self.redis.keys(link_wildcard):
            self.redis.smembers(key)
