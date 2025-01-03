"""
Handles the input conversion into a q state tuple that can be used for decision making (used as the keys in the q table)
"""

from typing import Any

from python_prototypes.field_tools import get_manhattan_distance
from python_prototypes.field_types import GameGridInformation, PlayerState
from python_prototypes.q_categorizer import (
    DISTANCE_CATEGORY_RETRIEVER,
    DistanceCategories,
    WaterRiskCategories,
    WATER_RISK_CATEGORY_RETRIEVER,
)
from python_prototypes.reaper.q_state_types import (
    ReaperQState,
    get_default_enemies_relation,
    get_default_tanker_enemies_relation,
    get_default_water_relations,
)


def calculate_reaper_q_state(game_grid_information: GameGridInformation, player_state: PlayerState) -> ReaperQState:
    """
    Takes the game input and converts it into a reaper q state tuple

    :param game_grid_information:
    :param player_state:
    :return:
    """
    water_reaper_relation = get_water_enemy_relations(
        game_grid_information.wreck_id_to_grid_coord, player_state, game_grid_information.enemy_reaper_id_to_grid_coord
    )
    water_other_relation = get_water_enemy_relations(
        game_grid_information.wreck_id_to_grid_coord, player_state, game_grid_information.enemy_others_id_to_grid_coord
    )
    tanker_enemy_relation = get_tanker_enemy_relations(
        game_grid_information.tanker_id_to_grid_coord,
        player_state,
        game_grid_information.enemy_reaper_id_to_grid_coord,
        game_grid_information.enemy_others_id_to_grid_coord,
    )
    player_reaper_relation = get_player_enemy_relation(
        game_grid_information.enemy_reaper_id_to_grid_coord,
        player_state,
        game_grid_information.wreck_id_to_grid_coord,
        game_grid_information.tanker_id_to_grid_coord,
    )
    player_other_enemy_relation = get_player_enemy_relation(
        game_grid_information.enemy_others_id_to_grid_coord,
        player_state,
        game_grid_information.wreck_id_to_grid_coord,
        game_grid_information.tanker_id_to_grid_coord,
    )

    is_super_power_available = player_state.rage >= 30

    state = ReaperQState(
        water_reaper_relation=water_reaper_relation,
        water_other_relation=water_other_relation,
        tanker_enemy_relation=tanker_enemy_relation,
        player_reaper_relation=player_reaper_relation,
        player_other_relation=player_other_enemy_relation,
        super_power_available=is_super_power_available,
    )
    return state


def get_player_enemy_relation(
    enemy_object_id_to_grid_coords: dict[Any, tuple[int, int]],
    player_state: PlayerState,
    wreck_id_to_grid_coords: dict[Any, tuple[int, int]],
    tanker_id_to_grid_coords: dict[Any, tuple[int, int]],
) -> dict[tuple[str, str], list[int]]:
    """
    Sometimes the reaper doesn't go for wrecks, neither tries to get close
    to reapers. It can try to ram into enemies. This relation mapping gives
    input for that decision

    :param enemy_object_id_to_grid_coords:
    :param player_state:
    :param wreck_id_to_grid_coords:
    :param tanker_id_to_grid_coords:
    :return: the mapping is keyed by the distance category to the enemy
        and the enemy's distance category to wreck or tankers
        so the key ranges from (close, close) to (far, medium) - 6 possible
        keys
    """
    player_enemy_relations = get_default_enemies_relation()
    player_coordinate = player_state.reaper_state.grid_coordinate
    enemy_id_to_category_mapping = {}

    for enemy_object_id, enemy_object_coordinate in enemy_object_id_to_grid_coords.items():
        manhattan_distance = get_manhattan_distance(
            coordinate_a=enemy_object_coordinate, coordinate_b=player_coordinate
        )
        distance_category = DISTANCE_CATEGORY_RETRIEVER.get_category(manhattan_distance=manhattan_distance)
        closest_water_distance_category = get_closest_water_distance_category(
            enemy_unit_coordinate=enemy_object_coordinate,
            wreck_id_to_grid_coords=wreck_id_to_grid_coords,
            tanker_id_to_grid_coords=tanker_id_to_grid_coords,
        )
        if closest_water_distance_category == DistanceCategories.far.name:
            continue
        player_enemy_relations[(distance_category.name, closest_water_distance_category)].append(enemy_object_id)
        enemy_id_to_category_mapping[enemy_object_id] = (distance_category.name, closest_water_distance_category)

    return player_enemy_relations


def get_closest_water_distance_category(
    enemy_unit_coordinate: tuple[int, int],
    wreck_id_to_grid_coords: dict[Any, tuple[int, int]],
    tanker_id_to_grid_coords: dict[Any, tuple[int, int]],
) -> str:
    """

    :param enemy_unit_coordinate:
    :param wreck_id_to_grid_coords:
    :param tanker_id_to_grid_coords:
    :return: distance category of the enemy unit to water related objects (wreck, tanker)
        Currently we are interested in close and medium only!
    TODO:
        - let's generalize these functions, we are repeating the same
        pattern over and over again
        - first try to refactor everything into a new package and then its
        easier to look at repeating patterns
    """
    worst_distance_category = DistanceCategories.far
    for wreck_id, wreck_coordinate in wreck_id_to_grid_coords.items():
        manhattan_distance = get_manhattan_distance(coordinate_a=wreck_coordinate, coordinate_b=enemy_unit_coordinate)
        distance_category = DISTANCE_CATEGORY_RETRIEVER.get_category(manhattan_distance=manhattan_distance)
        if distance_category.value < worst_distance_category.value:
            worst_distance_category = distance_category

    for tanker_id, tanker_coordinate in tanker_id_to_grid_coords.items():
        manhattan_distance = get_manhattan_distance(coordinate_a=tanker_coordinate, coordinate_b=enemy_unit_coordinate)
        distance_category = DISTANCE_CATEGORY_RETRIEVER.get_category(manhattan_distance=manhattan_distance)
        if distance_category.value < worst_distance_category.value:
            worst_distance_category = distance_category

    return worst_distance_category.name


def get_tanker_enemy_relations(
    tanker_id_to_grid_coord: dict[Any, tuple[int, int]],
    player_state: PlayerState,
    enemy_reaper_id_to_grid_coord: dict[Any, tuple[int, int]],
    enemy_others_grid_state: dict[Any, tuple[int, int]],
) -> dict[tuple[str, str], list[int]]:
    """
    The reaper can decide to get closer to tankers (because they can become
    wrecks potentially in the future)


    :param tanker_id_to_grid_coord:
    :param player_state:
    :param enemy_reaper_id_to_grid_coord:
    :param enemy_others_grid_state:
    :return: the resulting dict is keyed by (distance category, risk category)
        ranging from (close, safe) to (far, dangerous)
    """
    tanker_enemies_relation = get_default_tanker_enemies_relation()
    player_coordinate = player_state.reaper_state.grid_coordinate
    tanker_id_category_mapping = {}

    for tanker_id, tanker_coordinate in tanker_id_to_grid_coord.items():
        manhattan_distance = get_manhattan_distance(coordinate_a=tanker_coordinate, coordinate_b=player_coordinate)
        distance_category = DISTANCE_CATEGORY_RETRIEVER.get_category(manhattan_distance=manhattan_distance)
        closest_enemy_reaper_category = get_tanker_closest_enemy_category(
            tanker_coordinate=tanker_coordinate,
            enemy_reaper_id_coordinates=enemy_reaper_id_to_grid_coord,
            enemy_others_id_coordinates=enemy_others_grid_state,
        )
        tanker_enemies_relation[(distance_category.name, closest_enemy_reaper_category)].append(tanker_id)
        tanker_id_category_mapping[tanker_id] = (distance_category.name, closest_enemy_reaper_category)

    return tanker_enemies_relation


def get_tanker_closest_enemy_category(
    tanker_coordinate, enemy_reaper_id_coordinates, enemy_others_id_coordinates
) -> str:
    """

    :param tanker_coordinate:
    :param enemy_reaper_id_coordinates:
    :param enemy_others_id_coordinates:
    :return: currently a string, but its based on `WaterRiskCategories`

    TODO:
        - this can be expensive (to iterate through all enemies, but there
        are not too many). We can just look at the n neighbors and do the
        categorization based on that (change this to an OOP approach with
        different implementations)
        - this function can be generalized together with `get_water_closest_enemy_category`
    """
    worst_risk_category = WaterRiskCategories.safe
    for enemy_reaper_id, enemy_reaper_coordinate in enemy_reaper_id_coordinates.items():
        manhattan_distance = get_manhattan_distance(
            coordinate_a=tanker_coordinate, coordinate_b=enemy_reaper_coordinate
        )
        risk_category = WATER_RISK_CATEGORY_RETRIEVER.get_category(manhattan_distance=manhattan_distance)
        if risk_category.value < worst_risk_category.value:
            worst_risk_category = risk_category

        if worst_risk_category == WaterRiskCategories.dangerous:
            return worst_risk_category.name

    for enemy_others_id, enemy_others_coordinate in enemy_others_id_coordinates.items():
        manhattan_distance = get_manhattan_distance(
            coordinate_a=tanker_coordinate, coordinate_b=enemy_others_coordinate
        )
        risk_category = WATER_RISK_CATEGORY_RETRIEVER.get_category(manhattan_distance=manhattan_distance)
        if risk_category.value < worst_risk_category.value:
            worst_risk_category = risk_category

        if worst_risk_category == WaterRiskCategories.dangerous:
            return worst_risk_category.name

    return worst_risk_category.name


def get_water_enemy_relations(
    wreck_id_to_grid_coord: dict[Any, tuple[int, int]],
    player_state: PlayerState,
    enemy_id_to_grid_coord: dict[Any, tuple[int, int]],
) -> dict[tuple[str, str], list[int]]:
    """
    water reaper relation is keyed by the distance category and a riskiness
    of the given water (wreck)
    i.e. how far the given wreck is, and how risky it is to be harvested

    :param wreck_id_to_grid_coord:
    :param player_state:
    :param enemy_id_to_grid_coord:
    :return: the resulting dict is keyed by (distance category, risk category)
        ranging from (close, safe) to (far, dangerous)

    TODO:
        - this can be expensive (to iterate through the reapers, but there
        are not too many). We can just look at the n neighbors and do the
        categorization based on that (change this to an OOP approach with
        different implementations)
    """
    water_reaper_relation = get_default_water_relations()
    player_reaper_coordinate = player_state.reaper_state.grid_coordinate
    wreck_id_category_mapping = {}
    for wreck_id, wreck_coordinate in wreck_id_to_grid_coord:

        manhattan_distance = get_manhattan_distance(
            coordinate_a=player_reaper_coordinate, coordinate_b=wreck_coordinate
        )
        distance_category = DISTANCE_CATEGORY_RETRIEVER.get_category(manhattan_distance=manhattan_distance)
        closest_enemy_reaper_category = get_water_closest_enemy_category(
            wreck_coordinate=wreck_coordinate,
            enemy_object_id_coordinates=enemy_id_to_grid_coord,
        )

        water_reaper_relation[(distance_category.name, closest_enemy_reaper_category)].append(wreck_id)
        wreck_id_category_mapping[wreck_id] = (distance_category.name, closest_enemy_reaper_category)

    return water_reaper_relation


def get_water_closest_enemy_category(
    wreck_coordinate: tuple[int, int], enemy_object_id_coordinates: dict[Any, tuple[int, int]]
) -> str:
    """


    :param wreck_coordinate:
    :param enemy_object_id_coordinates:
    :return:

    TODO:
        - this can be expensive (to iterate through the reapers, but there
        are not too many). We can just look at the n neighbors and do the
        categorization based on that (change this to an OOP approach with
        different implementations)
    """
    worst_risk_category = WaterRiskCategories.safe
    for enemy_reaper_id, enemy_reaper_coordinate in enemy_object_id_coordinates.items():
        manhattan_distance = get_manhattan_distance(coordinate_a=wreck_coordinate, coordinate_b=enemy_reaper_coordinate)
        risk_category = WATER_RISK_CATEGORY_RETRIEVER.get_category(manhattan_distance=manhattan_distance)
        if risk_category.value < worst_risk_category.value:
            worst_risk_category = risk_category

        if worst_risk_category == WaterRiskCategories.dangerous:
            return worst_risk_category.name

    return worst_risk_category.name
