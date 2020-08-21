from shapely import affinity
from shapely.geometry import box

from cc_gen.variation import Scene, Direction, Kind


def no_overlap(s: Scene) -> bool:
    def create_box(center, width, length, rotation: float):
        x, y = center
        lbx, lby = (x - width / 2, y - length / 2)
        return affinity.rotate(box(lbx, lby, lbx + width, lby + length), rotation)

    boxes = [create_box([entry.values.distance_lat, entry.values.distance_long],
                         entry.values.width,
                         entry.values.length,
                         Direction.in_degrees(entry.values.orientation))
             for entry in s]
    
    return all(x.intersection(y).area <= 0
               for (i1, x) in enumerate(boxes)
               for (i2, y) in enumerate(boxes)
               if i1 != i2)


def exactly_one_ego_car(s: Scene) -> bool:
    return len([e for e in s if e.kind == Kind.Ego]) == 1


def left_hand_contra_car(s: Scene) -> bool:
    ego_instance = [e for e in s if e.kind == Kind.Ego][0]
    return all(c.values.distance_lat + c.values.width / 2 < (ego_instance.values.distance_lat - ego_instance.values.width / 2) or c.values.orientation != Direction.South
               for c in s if c.kind == Kind.Vehicle)


def restricted_pedestrian_vertical_movement(s: Scene) -> bool:
    vehicles_lat = [c.values.distance_lat for c in s if c.kind in (Kind.Ego, Kind.Vehicle)]
    right_far = max(vehicles_lat)
    return all(p.values.distance_lat > right_far or p.values.orientation not in (Direction.North, Direction.South)
               for p in s if p.kind == Kind.Pedestrian)

