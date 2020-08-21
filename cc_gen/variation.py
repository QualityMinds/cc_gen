from dataclasses import dataclass, fields
from enum import Enum
from typing import List, Dict, Any, Iterator, Callable, Tuple, Optional
from allpairspy import AllPairs


class Direction:
    North = 'north'
    NorthEast = 'north_east'
    East = 'east'
    SouthEast = 'south_east'
    South = 'south'
    SouthWest = 'south_west'
    West = 'west'
    NorthWest = 'north_west'

    @staticmethod
    def in_degrees(name: str) -> float:
        ds = [Direction.North,
              Direction.NorthWest,
              Direction.West,
              Direction.SouthWest,
              Direction.South,
              Direction.SouthEast,
              Direction.East,
              Direction.NorthEast]

        return ds.index(name) * 45.0


class Kind(Enum):
    Pedestrian = 'ped'
    Vehicle = 'vehicle'
    Ego = 'ego'


@dataclass
class InstanceValues:
    velocity: float
    orientation: str
    width: float
    length: float
    height: float
    distance_lat: float
    distance_long: float


@dataclass
class EntityInstance:
    kind: Kind
    name: str
    values: InstanceValues


@dataclass
class VariationSchema:
    velocity: List[float]
    orientation: List[str]
    width: List[float]
    length: List[float]
    height: List[float]
    distance_lat: List[float]
    distance_long: List[float]

    def num_fields(self) -> int:
        return len(fields(self))

    def get_field_names(self) -> List[str]:
        return [f.name for f in fields(self)]

    def get_field_indexes(self) -> Dict[str, int]:
        return dict(zip(self.get_field_names(), range(self.num_fields())))

    def resolve(self, offset: int, combination: List[Any]) -> Dict[str, Any]:
        index_map = self.get_field_indexes()
        result = dict((k, combination[offset + index_map.get(k)]) for k in index_map)
        return result

    def instantiate(self, offset: int, combination: List[Any]) -> InstanceValues:
        return InstanceValues(**self.resolve(offset, combination))


@dataclass
class EntityVariation:
    kind: Kind
    name: str
    schema: VariationSchema


"""
define a scene as a list of instantiated entities
"""
Scene = List[EntityInstance]


class VariationDimensions:
    def __init__(self,
                 filters: Optional[List[Callable[[Scene], bool]]],
                 variations: List[EntityVariation]):
        self.filters = filters
        self.variations = variations

    def to_list(self) -> List[List[Any]]:
        result = [getattr(v.schema, f.name) for v in self.variations for f in fields(v.schema)]
        return result

    def instantiate(self, combination: List[Any]) -> Scene:
        index = 0
        result = []
        for v in self.variations:
            instance = EntityInstance(v.kind, v.name, v.schema.instantiate(index, combination))
            result.append(instance)
            index += v.schema.num_fields()
        return result

    def __iter__(self) -> Iterator[Optional[Scene]]:
        for entry in AllPairs(self.to_list()):
            scene = self.instantiate(entry)
            yield scene if not self.filters or all(f(scene) for f in self.filters) else None
