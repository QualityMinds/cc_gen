from owlready2 import *


def create_root_domain(ontology):
    """ creates base world and rules """

    with ontology:
        # ---
        # things
        # ---

        class Entity(Thing):
            pass

        class Car(Entity):
            pass

        class EgoCar(Car):
            pass

        class Pedestrian(Entity):
            pass

        AllDisjoint([Car, Pedestrian])

        # ---
        # direction
        # ---
        class Direction(Thing):
            def in_degrees(self):
                ds = [north, north_west, west, south_west, south, south_east, east, north_east]
                return 45.0 * ds.index(self)

            def __repr__(self):
                return self.name

            @staticmethod
            def from_string(name: str):
                ds = {
                    'north': north,
                    'north_east': north_east,
                    'east': east,
                    'south_east': south_east,
                    'south': south,
                    'south_west': south_west,
                    'west': west,
                    'north_west': north_west
                }
                return ds.get(name, None)

        north = Direction('north')
        north_east = Direction('north_east')
        east = Direction('east')
        south_east = Direction('south_east')
        south = Direction('south')
        south_west = Direction('south_west')
        west = Direction('west')
        north_west = Direction('north_west')

        Direction.is_a.append(OneOf([north, north_east, east, south_east, south, south_west, west, north_west]))

        AllDisjoint([Entity, Direction])

        # ---
        # entity attributes
        # ---
        
        class has_width(Entity >> float, FunctionalProperty):
            python_name = 'width'

        class has_height(Entity >> float, FunctionalProperty):
            python_name = 'height'

        class has_length(Entity >> float, FunctionalProperty):
            python_name = 'length'

        class has_velocity(Entity >> float, FunctionalProperty):
            python_name = 'velocity'

        class has_direction(Entity >> Direction, FunctionalProperty):
            python_name = 'direction'

        class has_lateral_distance(Entity >> float, FunctionalProperty):
            python_name = 'lateral_distance'

        class has_longitudinal_distance(Entity >> float, FunctionalProperty):
            python_name = 'longitudinal_distance'

        class has_euclidean_distance(Entity >> float, FunctionalProperty):
            python_name = 'euclidean_distance'

        class has_reduced_height(Entity >> float, DataProperty):
            python_name = 'reduced_height'

        # swrl rule:
        # compute the remaining visible height of an entity
        # fixme: a stark oversimplification for occlusion
        Imp('has_reduced_height_rule').set_as_rule("""
            has_lateral_distance(?e1, ?l1),
            greaterThan(?l1, 0),
            
            has_lateral_distance(?e2, ?l2),
            greaterThan(?l2, ?l1),
            
            has_height(?e1, ?h1),
            has_height(?e2, ?h2),
            
            subtract(?delta, ?h2, ?h1) -> has_reduced_height(?e2, ?delta)
        """)
