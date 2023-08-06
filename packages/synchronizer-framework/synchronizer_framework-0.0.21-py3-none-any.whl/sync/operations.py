from dataclasses import dataclass


@dataclass
class Addition:
    from_class: type
    to_class: type
    from_entity: object
    to_entity: object

    def __repr__(self):
        return f"Addition({self.to_entity})"


@dataclass
class Update:
    from_class: type
    to_class: type
    from_entity: object
    to_entity: object

    def __repr__(self):
        return f"Update({self.to_entity})"


@dataclass
class Linking:
    classes: frozenset
    entities: frozenset

    def __repr__(self):
        return f"Linking({self.entities})"


@dataclass
class SkipMissingLink:
    from_class: type
    to_class: type
    from_entity: object

    def __repr__(self):
        return (
            f"SkipMissingLink({self.from_class.__name__} -> {self.to_class.__name__})"
        )


@dataclass
class AttributeUpdated:
    entity: type
    attribute: str
    old_value: any
    new_value: any
    from_entity: object

    def __repr__(self):
        return f"AttributeUpdated({self.entity}.{self.attribute}: {self.old_value} -> {self.new_value} from {self.from_entity})"


@dataclass
class SkipUpdateOrphanedEntity:
    from_class: type
    to_class: type
    from_entity: object
    to_entity: object

    def __repr__(self):
        return f"SkipUpdateOrphanedEntity({self.from_class.__name__} -> {self.to_class.__name__}, {self.from_entity} -> {self.to_entity})"


@dataclass
class DeletedOrphanedEntity:
    entity: object

    def __repr__(self):
        return f"""
            DeletedOrphanedEntity(deleted {self.entity}, because it's orphaned)
        """


@dataclass
class CouldNotCreate:
    from_class: type
    to_class: type
    from_entity: object

    def __repr__(self):
        return f"CouldNotCreate({self.from_class.__name__} -> {self.to_class.__name__})"


@dataclass
class CouldNotDelete:
    entity: object

    def __repr__(self):
        return f"CouldNotDelete(entity={self.entity})"
