from cc_gen.generator import SceneGenerator
from cc_gen.plausibility_filters import no_overlap
from cc_gen.root_domain import create_root_domain
from cc_gen.variation import EntityVariation, VariationSchema, Direction, Kind, Scene, VariationDimensions


BASE_IRI = "http://occd-test.com"


def test_generator():
    variations = [
        EntityVariation(
            kind=Kind.Ego,
            name='ego',
            schema=VariationSchema(
                velocity=[25],
                orientation=[Direction.North],
                width=[1.8],
                length=[4.5],
                height=[1.8],
                distance_lat=[0],
                distance_long=[0]
            )
        ),

        EntityVariation(
            kind=Kind.Pedestrian,
            name='ped',
            schema=VariationSchema(
                velocity=[10],
                orientation=[Direction.North, Direction.SouthEast],
                width=[0.5],
                length=[0.3],
                height=[1.8],
                distance_lat=[10],
                distance_long=[10]
            )
        )
    ]

    variation_dimensions = VariationDimensions([], variations)
    generator = SceneGenerator(variation_dimensions, create_root_domain, base_iri=BASE_IRI)
    result = [s for _, s in generator]
    assert len(result) == 2


def test_scene_is_plausible_no_overlap():
    variations = [
        *[EntityVariation(
            kind=Kind.Vehicle,
            name=f'car_{i}',
            schema=VariationSchema(
                velocity=[0],
                orientation=[Direction.NorthEast],
                width=[1.8],
                length=[4.5],
                height=[1.5],
                distance_lat=[5],
                distance_long=[-2.5 + 4 * i]
            )
        ) for i in range(3)]
    ]

    variation_dimensions = VariationDimensions([], variations)
    generator = SceneGenerator(variation_dimensions, create_root_domain, BASE_IRI)
    assert all(no_overlap(s) for _, s in generator)


def test_scene_is_plausible_longitudinal_disjoint():
    def distances_unequal(scene: Scene) -> bool:
        import itertools
        pairs = list(itertools.combinations(scene, 2))
        return all(a.values.distance_long != b.values.distance_long for a, b in pairs if a != b)

    variations = [
        *[EntityVariation(
            kind=Kind.Vehicle,
            name=f'car_{i}',
            schema=VariationSchema(
                velocity=[0],
                orientation=[Direction.North],
                width=[1.8],
                length=[4.5],
                height=[1.5],
                distance_lat=[5],
                distance_long=[-2, 3, 8]
            )
        ) for i in range(3)]
    ]

    variation_dimensions = VariationDimensions([no_overlap], variations)
    generator = SceneGenerator(variation_dimensions, create_root_domain, BASE_IRI)
    assert all(distances_unequal(r[1]) for r in generator if r)
