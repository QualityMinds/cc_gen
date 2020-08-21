import pytest
from cc_gen.variation import *


@pytest.fixture
def entity_variation() -> EntityVariation:
    return EntityVariation(
        kind=Kind.Pedestrian,
        name='ped1',
        schema=VariationSchema(
            velocity=[10.0, 20.0],
            orientation=[Direction.North, Direction.South],
            width=[1.0],
            length=[5.0],
            height=[2.0],
            distance_lat=[40, 50],
            distance_long=[45, 55]))


@pytest.fixture
def ego_variation() -> EntityVariation:
    return EntityVariation(
        kind=Kind.Ego,
        name='ego1',
        schema=VariationSchema(
            velocity=[10.0, 20.0],
            orientation=[Direction.North, Direction.South],
            width=[1.0],
            length=[5.0],
            height=[2.0],
            distance_lat=[0],
            distance_long=[0]))


@pytest.fixture
def entity_value_combination() -> List[Any]:
    return [10, Direction.North, 1.0, 5.0, 2.0, 40, 50]


@pytest.fixture
def ego_value_combination() -> List[Any]:
    return [20, Direction.South, 1.0, 5.0, 2.0, 0, 0]


def test_orientation_degrees():
    assert Direction.in_degrees(Direction.North) == 0
    assert Direction.in_degrees(Direction.NorthWest) == 45
    assert Direction.in_degrees(Direction.West) == 90
    assert Direction.in_degrees(Direction.SouthWest) == 135
    assert Direction.in_degrees(Direction.South) == 180
    assert Direction.in_degrees(Direction.SouthEast) == 225
    assert Direction.in_degrees(Direction.East) == 270
    assert Direction.in_degrees(Direction.NorthEast) == 315


def test_num_fields(entity_variation: EntityVariation):
    """ checks if the number of fields are correct """
    ped_var = entity_variation.schema
    assert ped_var.num_fields() == 7


def test_index_mapping_keys(entity_variation: EntityVariation):
    """ checks if all fields occur in the index map """
    ped_var = entity_variation.schema
    index_map = ped_var.get_field_indexes()
    names = ped_var.get_field_names()
    assert all(name in index_map.keys() for name in names)


def test_serialization_entity(entity_variation: EntityVariation):
    """ tests if serialization is correct """
    vd = VariationDimensions([], [entity_variation])
    var = entity_variation.schema
    indexes = var.get_field_indexes()
    xs = vd.to_list()

    assert xs[indexes.get('velocity')] == var.velocity
    assert xs[indexes.get('orientation')] == var.orientation
    assert xs[indexes.get('width')] == var.width
    assert xs[indexes.get('length')] == var.length
    assert xs[indexes.get('height')] == var.height
    assert xs[indexes.get('distance_lat')] == var.distance_lat
    assert xs[indexes.get('distance_long')] == var.distance_long


def test_serialization_all(ego_variation: EntityVariation, entity_variation: EntityVariation):
    """ tests if serialization is correct """
    vd = VariationDimensions([], [ego_variation, entity_variation])
    var_ego = ego_variation.schema
    var_ent = entity_variation.schema

    indexes_ego = var_ego.get_field_indexes()
    indexes_ent = var_ent.get_field_indexes()
    xs = vd.to_list()

    offset = 0
    assert xs[offset + indexes_ego.get('velocity')] == var_ego.velocity
    assert xs[offset + indexes_ego.get('orientation')] == var_ego.orientation
    assert xs[offset + indexes_ego.get('width')] == var_ego.width
    assert xs[offset + indexes_ego.get('length')] == var_ego.length
    assert xs[offset + indexes_ego.get('height')] == var_ego.height
    assert xs[offset + indexes_ego.get('distance_lat')] == var_ego.distance_lat
    assert xs[offset + indexes_ego.get('distance_long')] == var_ego.distance_long

    offset += var_ego.num_fields()
    assert xs[offset + indexes_ent.get('velocity')] == var_ent.velocity
    assert xs[offset + indexes_ent.get('orientation')] == var_ent.orientation
    assert xs[offset + indexes_ent.get('width')] == var_ent.width
    assert xs[offset + indexes_ent.get('length')] == var_ent.length
    assert xs[offset + indexes_ent.get('height')] == var_ent.height
    assert xs[offset + indexes_ent.get('distance_lat')] == var_ent.distance_lat
    assert xs[offset + indexes_ent.get('distance_long')] == var_ent.distance_long


def test_deserialization(entity_variation: EntityVariation, entity_value_combination: List[Any]):
    variation = entity_variation.schema
    instance = variation.instantiate(0, entity_value_combination)
    _assert_compare_combination_with_instance(entity_value_combination, instance, variation)


def test_deserialization_ego(ego_variation: EntityVariation, ego_value_combination: List[Any]):
    variation = ego_variation.schema
    instance = variation.instantiate(0, ego_value_combination)
    _assert_compare_combination_with_instance(ego_value_combination, instance, variation)


def test_deserialization_shifted(entity_variation: EntityVariation,
                                 ego_variation: EntityVariation,
                                 ego_value_combination: List[Any],
                                 entity_value_combination: List[Any]):
    var = entity_variation.schema
    offset = ego_variation.schema.num_fields()
    # arrange: change combination so that offset is not zero
    instance = var.instantiate(offset, ego_value_combination + entity_value_combination)
    # act
    _assert_compare_combination_with_instance(entity_value_combination, instance, var)


def test_deserialization_ego_shifted(entity_variation: EntityVariation,
                                     ego_variation: EntityVariation,
                                     ego_value_combination: List[Any],
                                     entity_value_combination: List[Any]):
    var = ego_variation.schema
    offset = entity_variation.schema.num_fields()
    # arrange: change combination so that offset is not zero
    instance = var.instantiate(offset, entity_value_combination + ego_value_combination)
    # act
    _assert_compare_combination_with_instance(ego_value_combination, instance, var)


def test_instances(entity_variation: EntityVariation,
                   ego_variation: EntityVariation,
                   ego_value_combination: List[Any],
                   entity_value_combination: List[Any]):
    vd = VariationDimensions([], [ego_variation, entity_variation])
    cs = ego_value_combination + entity_value_combination

    # act
    instances = vd.instantiate(cs)
    assert len(instances) == 2

    ego_instance = instances[0]
    ego_variation = ego_variation.schema
    _assert_compare_combination_with_instance(cs, ego_instance.values, ego_variation)

    entity_instance = instances[1]
    entity_variation = entity_variation.schema
    _assert_compare_combination_with_instance(cs, entity_instance.values, entity_variation, ego_variation.num_fields())


def test_variation_setup(entity_variation: EntityVariation, ego_variation: EntityVariation):
    vd = VariationDimensions([], [ego_variation, entity_variation])
    print(vd.to_list())
    xs = vd.to_list()
    assert len(xs) == 14


def _assert_compare_combination_with_instance(combination: List[Any],
                                              values: InstanceValues,
                                              variation: VariationSchema,
                                              offset: int = 0):
    indexes = variation.get_field_indexes()
    # check if values are correctly deserialized
    assert values.velocity == combination[offset + indexes.get('velocity')]
    assert values.orientation == combination[offset + indexes.get('orientation')]
    assert values.width == combination[offset + indexes.get('width')]
    assert values.height == combination[offset + indexes.get('height')]
    assert values.length == combination[offset + indexes.get('length')]
    assert values.distance_lat == combination[offset + indexes.get('distance_lat')]
    assert values.distance_long == combination[offset + indexes.get('distance_long')]
