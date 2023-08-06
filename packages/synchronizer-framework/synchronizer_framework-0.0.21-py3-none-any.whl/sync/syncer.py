import logging
import math
from dataclasses import dataclass
from typing import List, Set, Dict, Any, Type, Union, Tuple

from sync.backends.inmemory import InMemoryLinkProvider
from sync.datasource import DataSource
from sync.mapping import Mapping, Mode, AttributeMap, DirtyMode
from sync.mixins import Timestamped, LinkProvider
from sync.operations import (
    Addition,
    Linking,
    SkipMissingLink,
    AttributeUpdated,
    SkipUpdateOrphanedEntity,
    DeletedOrphanedEntity,
    CouldNotCreate,
    CouldNotDelete,
)

MODES_TO_PARAMETERS = {
    Mode.LEFT_TO_RIGHT: ("from_attribute", "from_attribute_type_hint", 0),
    Mode.RIGHT_TO_LEFT: ("to_attribute", "to_attribute_type_hint", 1),
}


@dataclass
class Syncer:
    left_ds: DataSource
    right_ds: DataSource
    mappings: List[Mapping]
    link_provider: LinkProvider = InMemoryLinkProvider()

    def __post_init__(self):
        self._preload_data_sources()

    def sync_all(self):
        """
        Synchronizes :attribute:`left_ds` and :attribute:`right_ds` according to rules in :attribute:`mappings`

        :return: a list of operations that happened during synchronization for logging and debugging
        """
        operations = []
        for mapping in self.mappings:
            operations.extend(self.sync_mapping(mapping))
        return operations

    def sync_mapping(self, mapping: Mapping):
        operations = []

        if Mode.LEFT_TO_RIGHT in mapping.modes:
            logging.debug(
                f"Mapping from {mapping.entity_types[0].__name__} to {mapping.entity_types[1].__name__}"
            )
            operations.extend(self._sync_from_to(self.left_ds, self.right_ds, mapping))
        if Mode.RIGHT_TO_LEFT in mapping.modes:
            logging.debug(
                f"Mapping from {mapping.entity_types[1].__name__} to {mapping.entity_types[0].__name__}"
            )
            operations.extend(
                self._sync_from_to(self.right_ds, self.left_ds, mapping.swapped())
            )

        return operations

    def _collect_linked_classes(self, entity_class):
        result = set()
        for mapping in self.mappings:
            if entity_class in mapping.entity_types:
                index = mapping.entity_types.index(entity_class)
                other_class = mapping.entity_types[1 - index]
                # check if class may be created by other_class
                if (index == 0 and Mode.RIGHT_TO_LEFT in mapping.modes) or (
                    index == 1 and Mode.LEFT_TO_RIGHT in mapping.modes
                ):
                    result.add(other_class)
        return result

    def _is_orphaned(self, generating_classes, entity, entity_ds, other_ds):
        len_others = 0
        len_unrefreshed = 0
        for generating_class in generating_classes:
            others = self.link_provider.others(
                entity, entity_ds, generating_class, other_ds
            )
            if others:
                len_others += len(others)
                for other in others:
                    refreshed_other = other_ds.refresh(other)
                    if not refreshed_other:
                        len_unrefreshed += 1
        return 0 < len_others == len_unrefreshed

    def _collect_orphaned_entities(self, entity_ds, entity_class, other_ds):
        generating_classes = self._collect_linked_classes(entity_class)
        return [
            entity
            for entity in entity_ds.find(entity_class)
            if self._is_orphaned(generating_classes, entity, entity_ds, other_ds)
        ]

    def _preload_data_sources(self):
        def preload_data_source_type(attribute, data_source, hint, index, key, mapping):
            path = getattr(key, attribute)
            if isinstance(path, tuple) or (
                getattr(key, hint) is not None and path != "__self__"
            ):
                entity_type = mapping.entity_types[index]
                if not isinstance(path, tuple):
                    path = (path,)
                logging.debug(
                    f"Preloading from {entity_type} path {path} from {data_source}"
                )
                data_source.preload_type(entity_type, path)

        for mode in Mode:
            for mapping in self.mappings:
                for key in mapping.keys:
                    attribute, hint, index = MODES_TO_PARAMETERS[mode]
                    data_source = [self.left_ds, self.right_ds][index]
                    preload_data_source_type(
                        attribute, data_source, hint, index, key, mapping
                    )

    def _upsert_unlinked_entity(
        self,
        from_ds: DataSource,
        from_entity,
        mapping: Mapping,
        data_source: DataSource,
        entity_type: Type,
    ):
        operations = []
        try:
            conditions = self._create_key_value_pairs(
                from_entity,
                mapping.keys,
                from_ds=from_ds,
                to_ds=data_source,
            )
            found_entities = data_source.find(entity_type, conditions)
        except NotLinked as e:
            operations.append(
                SkipMissingLink(from_entity.__class__, entity_type, from_entity)
            )
            logging.warning(e)
            return operations

        if len(found_entities) == 0:
            from_entity_timestamp = self._timestamp(from_entity)

            try:
                non_key_attributes = self._create_key_value_pairs(
                    from_entity,
                    mapping.attributes,
                    from_ds=from_ds,
                    to_ds=data_source,
                )
                to_entity = Syncer._create_entity(
                    conditions, non_key_attributes, entity_type, from_entity_timestamp
                )
            except NotLinked as e:
                operations.append(
                    SkipMissingLink(from_entity.__class__, entity_type, from_entity)
                )
                logging.warning(e)
                return operations

            if not mapping.create or not data_source.create(to_entity):
                logging.warning(f"Could not add {to_entity.__repr__()}")
                operations.append(
                    CouldNotCreate(from_entity.__class__, entity_type, from_entity)
                )
                return operations

            if mapping.dirty_mode == DirtyMode.UPDATE:
                setattr(from_entity, mapping.dirty_attribute_name, False)
                logging.info(
                    f"Removed {mapping.dirty_attribute_name} flag from {from_entity}"
                )
                from_ds.persist(from_entity)

            operations.append(
                Addition(from_entity.__class__, entity_type, from_entity, to_entity)
            )
            logging.info(f"✨ Adding {to_entity.__repr__()}")

            if self.link_provider.link(to_entity, from_entity, data_source, from_ds):
                classes = frozenset(mapping.entity_types)
                entities = frozenset({from_entity, to_entity})
                operations.append(Linking(classes, entities))
        elif len(found_entities) == 1:
            to_entity = next(iter(found_entities))

            if self.link_provider.link(to_entity, from_entity, data_source, from_ds):
                classes = frozenset(mapping.entity_types)
                entities = frozenset({from_entity, to_entity})
                operations.append(Linking(classes, entities))
                operations.extend(
                    self._update_linked_entity(
                        from_ds,
                        from_entity,
                        {to_entity},
                        mapping,
                        to_entity.__class__,
                        data_source,
                    )
                )
        else:
            logging.warning(f"Found more than one result for {conditions}, skipping")

        return operations

    @staticmethod
    def _timestamp(entity) -> int:
        return entity.updated_at() if isinstance(entity, Timestamped) else 0

    @staticmethod
    def _collect_objects_in_paths(entity, paths) -> int:
        entities = set()
        for path in paths:
            entities = entities.union(Syncer._collect_objects_in_path(entity, path))
        logging.debug(f"Found objects in paths of {entity} paths {paths}: {entities}")
        return entities

    @staticmethod
    def _resolve_entity(entity, key):
        if key != "__self__":
            return getattr(entity, key)
        else:
            return entity

    @staticmethod
    def _collect_objects_in_path(entity, path):
        entities = {entity}

        if isinstance(path, tuple) or isinstance(path, list):
            if len(path) > 1:
                key, *rest = path
                next_entity = Syncer._resolve_entity(entity, key)
                if not next_entity:
                    return entities
                entities = entities.union(
                    Syncer._collect_objects_in_path(next_entity, rest)
                )
            elif len(path) == 1:
                key = path[0]
                entities.add(Syncer._resolve_entity(entity, key))
        elif isinstance(path, str):
            entities.add(Syncer._resolve_entity(entity, path))

        return entities

    @staticmethod
    def _biggest_timestamp(entities: List) -> int:
        max_value = 0
        for entity in entities:
            max_value = max(max_value, Syncer._timestamp(entity))
        return max_value

    @staticmethod
    def _set_updated_at(entity: Timestamped, timestamp: int):
        if isinstance(entity, Timestamped):
            logging.debug(f"Setting timestamp of {entity} to {timestamp}")
            entity.update_timestamp(timestamp)

    @staticmethod
    def _is_dirty(mapping, entity):
        try:
            return getattr(entity, mapping.dirty_attribute_name)
        except AttributeError as e:
            logging.warning(
                f"asked to read {mapping.dirty_attribute_name} from {entity} but no such attribute exists"
            )
            raise e

    def _update_linked_entity(
        self,
        from_ds: DataSource,
        from_entity,
        others: List,
        mapping: Mapping,
        to_class: Type,
        to_ds: DataSource,
    ):
        operations = []

        try:
            attributes = {
                **self._create_key_value_pairs(
                    from_entity,
                    mapping.keys,
                    from_ds=from_ds,
                    to_ds=to_ds,
                ),
                **self._create_key_value_pairs(
                    from_entity,
                    mapping.attributes,
                    from_ds=from_ds,
                    to_ds=to_ds,
                ),
            }
        except NotLinked as e:
            logging.warning(e)
            operations.append(
                SkipMissingLink(from_entity.__class__, to_class, from_entity)
            )
            return operations

        # TODO more tests, maybe validate modes
        for to_entity in others:
            refreshed_to_entity = to_ds.refresh(to_entity)

            if not refreshed_to_entity:
                logging.warning(
                    f"Orphaned entities in link from {from_entity}: {to_entity}"
                )
                operations.append(
                    SkipUpdateOrphanedEntity(
                        from_entity.__class__, to_class, from_entity, to_entity
                    )
                )

                continue
            else:
                to_entity = refreshed_to_entity

            if mapping.dirty_mode == DirtyMode.DO_NOT_OVERWRITE and self._is_dirty(
                mapping, to_entity
            ):
                continue

            # guard that to_entity has last been changed before or at the same time as from_entity
            from_entity_objects = Syncer._collect_objects_in_paths(
                from_entity, mapping.from_paths()
            )
            timestamp_from_entity = Syncer._biggest_timestamp(from_entity_objects)
            timestamp_to_entity = Syncer._timestamp(to_entity)
            if timestamp_to_entity > timestamp_from_entity:
                logging.warning(
                    f"Not updating {to_entity}: is newer than {from_entity}"
                )
                continue

            entity_updated = False
            for k, v in attributes.items():
                if k == "__self__":
                    continue
                to_value = getattr(to_entity, k)
                if to_value != v:
                    logging.info(f"👌 Updating {to_entity}.{k} {to_value} -> {v}")
                    setattr(to_entity, k, v)
                    entity_updated = True

                    operations.append(
                        AttributeUpdated(
                            entity=to_entity,
                            attribute=k,
                            old_value=to_value,
                            new_value=v,
                            from_entity=from_entity,
                        )
                    )

            if timestamp_to_entity != timestamp_from_entity:
                self._set_updated_at(to_entity, timestamp_from_entity)
                entity_updated = True
            if entity_updated:
                to_ds.persist(to_entity)
                if mapping.dirty_mode == DirtyMode.UPDATE:
                    setattr(from_entity, mapping.dirty_attribute_name, False)
                    logging.info(
                        f"Removed {mapping.dirty_attribute_name} flag from {from_entity}"
                    )
                    from_ds.persist(from_entity)

        return operations

    def _sync_from_to(
        self,
        from_ds: DataSource,
        to_ds: DataSource,
        mapping: Mapping,
    ):
        operations = []
        from_class, to_class = mapping.entity_types
        from_entities: List = from_ds.find(from_class, mapping.left_conditions)

        for from_entity in from_entities:
            operations.extend(
                self._sync_entity(from_ds, from_entity, to_ds, to_class, mapping)
            )

        if mapping.delete_orphaned_entities:
            operations.extend(self._delete_orphaned_entities(from_ds, to_class, to_ds))

        return operations

    def _delete_orphaned_entities(self, from_ds, to_class, to_ds):
        """
        Deletes orphaned entities in `to_ds`
        """
        operations = []
        for orphaned_entity in self._collect_orphaned_entities(
            to_ds, to_class, from_ds
        ):
            logging.info(f"❌ Trying to delete orphaned entity {orphaned_entity}")
            successful_deletion = to_ds.delete(orphaned_entity)
            if not successful_deletion:
                operations.append(CouldNotDelete(orphaned_entity))
            else:
                self.link_provider.unlink(orphaned_entity, to_ds, from_ds)
                operations.append(DeletedOrphanedEntity(orphaned_entity))
        return operations

    def sync_entity(self, type, id):
        operations = []
        if type in self.left_ds.entity_types():
            from_ds = self.left_ds
            to_ds = self.right_ds
        elif type in self.right_ds.entity_types():
            from_ds = self.right_ds
            to_ds = self.left_ds
        else:
            raise AttributeError(f"Unknown entity type: {type.__name__}")

        from_entity = from_ds.get(type, id)

        for mapping in self.mappings:
            entity_types = mapping.entity_types
            if from_entity.__class__ in entity_types:
                to_class_index = 1 - entity_types.index(from_entity.__class__)
                operations.extend(
                    self._sync_entity(
                        from_ds,
                        from_entity,
                        to_ds,
                        entity_types[to_class_index],
                        mapping,
                    )
                )

        return operations

    def _sync_entity(self, from_ds, from_entity, to_ds, to_class, mapping):
        operations = []

        if mapping.dirty_mode == DirtyMode.UPDATE and not self._is_dirty(
            mapping, from_entity
        ):
            return operations

        others = self.link_provider.others(from_entity, from_ds, to_class, to_ds)
        if not others or not len(others):
            operations.extend(
                self._upsert_unlinked_entity(
                    from_ds, from_entity, mapping, to_ds, to_class
                )
            )
        else:
            operations.extend(
                self._update_linked_entity(
                    from_ds,
                    from_entity,
                    others,
                    mapping,
                    to_class,
                    to_ds,
                )
            )
        return operations

    @staticmethod
    def _update_entity(entity, **kwargs):
        for (key, value) in kwargs.items():
            setattr(entity, key, value)

    @staticmethod
    def _create_entity(
        conditions: Dict[str, Any],
        non_key_attributes: Dict[str, Any],
        to_class: Type,
        timestamp: int = None,
    ):
        to_entity = to_class()
        Syncer._update_entity(to_entity, **conditions)
        Syncer._update_entity(to_entity, **non_key_attributes)
        if timestamp:
            to_entity.update_timestamp(timestamp)
        return to_entity

    def _create_key_value_pairs(
        self,
        from_entity,
        attribute_maps: Set[AttributeMap],
        from_ds: DataSource,
        to_ds: DataSource,
    ):
        attributes = {}

        for attribute_map in attribute_maps:
            value, linked_value = self._resolve_values(
                from_entity,
                attribute_map.from_attribute,
                attribute_map.from_attribute_type_hint,
                attribute_map.to_attribute_type_hint,
                entity_ds=from_ds,
                other_ds=to_ds,
            )
            if not isinstance(attribute_map.to_attribute, str):
                raise MayNotUpdateJoinedAttributes(
                    f"May not update attributes {attribute_map.to_attribute} of {attribute_map.to_attribute_type_hint}"
                )
            attributes[attribute_map.to_attribute] = linked_value or value

        logging.debug(f"attributes: {attributes}")
        return attributes

    def _resolve_values(
        self,
        entity,
        key: Union[str, Tuple],
        from_remote_class: Type = None,
        to_remote_class: Type = None,
        entity_ds: DataSource = None,
        other_ds: DataSource = None,
    ):
        linked_value = None

        if key == "__self__":
            value = entity
        else:
            value = Syncer._resolve_key_value(entity, key)

        #        if value is None:
        #            raise UnableToResolve(f"Cannot resolve {entity}.{key}")

        # If type hint is provided, try to resolve value type via typed link
        if from_remote_class and value:
            if not self.link_provider:
                raise NotLinked(f"No link provider provided")
            linked_values = self.link_provider.others(
                value, entity_ds, to_remote_class, other_ds
            )
            if not linked_values:  # None or empty set
                raise NotLinked(
                    f"Cannot find linked entity of {entity}.{key}. {value} not in {to_remote_class.__name__}"
                )
            if len(linked_values) > 1:
                raise MultiLinkedEntity(
                    f"Cannot resolve a single value from multi-linked entity"
                )
            linked_value = linked_values.pop()

        logging.debug(f"resolve_value({entity},{key})={value},{linked_value}")

        return value, linked_value

    @staticmethod
    def _resolve_key_value(entity, key: str):
        if isinstance(key, tuple) or isinstance(key, list):
            if len(key) > 1:
                next_key, *rest = key
                next_entity = getattr(entity, next_key)
                if not next_entity:
                    return None
                return Syncer._resolve_key_value(next_entity, rest)
            elif len(key) == 1:
                key = key[0]
            else:
                raise AttributeError("key is empty")
        return getattr(entity, key)


class NotLinked(Exception):
    pass


class UnableToResolve(Exception):
    pass


class MultiLinkedEntity(Exception):
    pass


class MayNotUpdateJoinedAttributes(Exception):
    pass
