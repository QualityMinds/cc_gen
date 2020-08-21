import math
from typing import Callable, Iterator, Tuple, Dict, Any, List, Optional
from matplotlib import transforms
from owlready2 import Ontology, World, sync_reasoner_pellet, Thing
from cc_gen.variation import VariationDimensions, Scene, Kind, EntityInstance
import matplotlib.pyplot as plt


class SceneGenerator:
    def __init__(self,
                 variation_dimensions: VariationDimensions,
                 domain_factory: Callable[[Ontology], None],
                 base_iri: str,
                 max_tries: Optional[int] = None,
                 debug: bool = False):
        self.variation_dimensions = variation_dimensions
        self.domain_factory = domain_factory
        self.base_iri = base_iri
        self.iterations = 0
        self.max_tries = max_tries
        self.debug = debug

    @property
    def num_rounds(self):
        return self.iterations

    @staticmethod
    def save_as_xml(file: str, ontology: Ontology):
        if not file.endswith(".rdf.xml"):
            file = file + ".rdf.xml"
        ontology.save(file)

    @staticmethod
    def save_as_png(file: str, scene: Scene, ontology: Ontology, **kwargs):
        def draw_entity(plot, center, width, length, orientation, v, color):
            x, y = center
            lb = (x - width / 2, y - length / 2)
            rect = plot.Rectangle(lb, width, length, fill=True, linewidth=0, color=color)
            t = transforms.Affine2D().rotate_deg_around(x, y, orientation) + plot.gca().transData
            rect.set_transform(t)
            plot.gca().add_patch(rect)
            arrow = plot.arrow(x, y, 0, .2 * v, length_includes_head=True, head_width=0.4, color='gray', zorder=100)
            arrow.set_transform(t)
            plot.gca().add_patch(arrow)

        unit_len = kwargs.get('unit_len', 15)

        plt.figure()
        plt.axes().set_aspect('equal')
        plt.axis([-unit_len, unit_len] * 2)
        plt.axis('on')

        def colorize(entity, default_color='black'):
            types = [t.name for t in type(entity).ancestors()]
            if 'EgoCar' in types:
                return kwargs.get('ego_color', 'lightblue')
            elif 'Car' in types:
                return kwargs.get('vehicle_color', 'lightgreen')
            elif 'Pedestrian' in types:
                return kwargs.get('pedestrian_color', 'red')
            else:
                return default_color
        
        ego = [e for e in scene if e.kind == Kind.Ego][0]
        entities: List[ontology.Entity] = [ontology[i.name] for i in scene]
        for e in entities:
            draw_entity(plt,
                        (ego.values.distance_lat + e.lateral_distance, ego.values.distance_long + e.longitudinal_distance),
                        e.width,
                        e.length,
                        e.direction.in_degrees(),
                        e.velocity,
                        colorize(e))

        if not file.endswith('.png'):
            file += '.png'

        plt.savefig(file)
        plt.close()

    @staticmethod
    def instantiate_scene(scene: Scene, ontology: Ontology) -> Ontology:
        with ontology:
            def common_attributes(x: EntityInstance) -> Dict[str, Any]:
                result = {
                    'velocity': x.values.velocity,
                    'direction': ontology.Direction.from_string(x.values.orientation),
                    'length': x.values.length,
                    'width': x.values.width,
                    'height': x.values.height,
                    'lateral_distance': x.values.distance_lat,
                    'longitudinal_distance': x.values.distance_long,
                    'euclidean_distance': math.sqrt((x.values.distance_lat or 0) ** 2 +
                                                    (x.values.distance_long or 0) ** 2)
                }
                return result

            entities: Dict[str, Tuple[EntityInstance, Thing]] = {}

            for car in [e for e in scene if e.kind == Kind.Vehicle]:
                car_onto = ontology.Car(car.name, **common_attributes(car))
                entities[car.name] = (car, car_onto)

            for ped in [e for e in scene if e.kind == Kind.Pedestrian]:
                ped_onto = ontology.Pedestrian(ped.name, **common_attributes(ped))
                entities[ped.name] = (ped, ped_onto)

            for ego in [e for e in scene if e.kind == Kind.Ego]:
                ego_onto = ontology.EgoCar(ego.name, **common_attributes(ego))
                entities[ego.name] = (ego, ego_onto)

            return ontology

    def __iter__(self) -> Iterator[Optional[Tuple[Ontology, Scene]]]:
        for index, scene in enumerate(self.variation_dimensions):
            self.iterations += 1
            if scene is not None:
                world = World(backend='sqlite', filename=':memory:', dbname=f"scene_db_{index:04}")
                with world.get_ontology(self.base_iri) as onto:
                    self.domain_factory(onto)
                    self.instantiate_scene(scene, onto)

                    try:
                        sync_reasoner_pellet(x=world,
                                             infer_data_property_values=True,
                                             infer_property_values=True,
                                             debug=self.debug)
                    except Exception as e:
                        onto.save("error.rdf.xml")
                        raise e
                    yield onto, scene
            else:
                yield None
            if self.max_tries is not None and self.iterations >= self.max_tries:
                break
